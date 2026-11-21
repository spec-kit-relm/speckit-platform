#!/usr/bin/env python3
"""relm-sdd — Relm's spec-driven-development guardrails.

One stdlib-only script, used three ways:
  * by engineers locally          (python relm_sdd.py spec-lint)
  * by the reusable CI workflows  (.github/workflows/sdd-gates.yml, contract-check.yml)
  * by the SDD Guild              (build / package / catalog / constitution-sync)

Subcommands
  build               Regenerate preset constitution templates + governance history snapshots
  package             Build deterministic preset/extension zips into dist/
  catalog             Regenerate catalogs/*.json (with sha256 of the deterministic zips)
  constitution-check  Verify synced Part A/B blocks in a repo constitution (drift check)
  constitution-sync   Replace Part A/B blocks with the current governance versions
  spec-lint           Lint specs/*/spec.md (traceability, Given/When/Then, clarifications)
  pr-check            Verify a pull request declares a feature or a lane (ORG-1, ORG-9)
  agent-files-check   Verify AGENTS.md / CLAUDE.md / copilot instructions / constitution exist
  contract-check      Verify contract version bumps and read-only vendored contracts (ORG-3)

Exit code 0 = pass, 1 = rule violation, 2 = usage/config error.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

PLATFORM_ROOT = Path(__file__).resolve().parent.parent
ORG = "spec-kit-relm"
PLATFORM_REPO = f"https://github.com/{ORG}/speckit-platform"

BLOCK_RE = re.compile(
    r"<!-- BEGIN RELM:(?P<name>[A-Z0-9-]+) v(?P<version>\d+\.\d+\.\d+)(?P<meta>[^>]*)-->"
    r"(?P<body>.*?)"
    r"<!-- END RELM:(?P=name) -->",
    re.S,
)
FEATURE_ID_RE = re.compile(r"\bRELM-(\d+)\b")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

# Which team overlay each preset carries.
TEAM_PRESETS = {
    "relm-backend": "backend",
    "relm-frontend": "frontend",
    "relm-qa": "qa",
    "relm-product": "product",
}

failures: list[str] = []
warnings: list[str] = []


# --------------------------------------------------------------------------- helpers
def fail(msg: str, file: str | None = None) -> None:
    failures.append(msg)
    loc = f" file={file}" if file else ""
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error{loc}::{msg}")
    else:
        print(f"FAIL  {msg}" + (f"  [{file}]" if file else ""))


def warn(msg: str, file: str | None = None) -> None:
    warnings.append(msg)
    loc = f" file={file}" if file else ""
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::warning{loc}::{msg}")
    else:
        print(f"WARN  {msg}" + (f"  [{file}]" if file else ""))


def ok(msg: str) -> None:
    print(f"ok    {msg}")


def finish() -> int:
    print(f"\n{len(failures)} failure(s), {len(warnings)} warning(s)")
    return 1 if failures else 0


def semver(v: str) -> tuple[int, int, int]:
    m = SEMVER_RE.match(v)
    if not m:
        raise ValueError(f"not a semver: {v}")
    return tuple(int(x) for x in m.groups())  # type: ignore[return-value]


def fragment_path(governance: Path, name: str) -> Path:
    if name == "ORG-BASELINE":
        return governance / "org-baseline.md"
    if name.startswith("TEAM-"):
        return governance / "overlays" / f"{name[5:].lower()}.md"
    raise KeyError(name)


def read_fragment(path: Path) -> re.Match:
    text = path.read_text(encoding="utf-8")
    m = BLOCK_RE.search(text)
    if not m:
        raise ValueError(f"{path}: no RELM block found")
    return m


def current_fragments(governance: Path) -> dict[str, re.Match]:
    out = {"ORG-BASELINE": read_fragment(governance / "org-baseline.md")}
    for p in sorted((governance / "overlays").glob("*.md")):
        m = read_fragment(p)
        out[m["name"]] = m
    return out


def history_path(governance: Path, name: str, version: str) -> Path:
    return governance / "history" / name / f"{version}.md"


# --------------------------------------------------------------------------- build
CONSTITUTION_HEADER = """# [PROJECT_NAME] Constitution

> **How this constitution is layered (Relm SDD).**
> Part A is the organization baseline and Part B is the team overlay. Both are synced from
> `spec-kit-relm/speckit-platform` and MUST NOT be edited in this repository. Part C holds this
> repository's own amendments: they may add or tighten rules, never relax Parts A or B.
> Every Spec Kit command reads this file; `/speckit.analyze` treats any MUST violation as CRITICAL.

"""

CONSTITUTION_PART_C = """
## Part C — Repository Amendments (MUST)

<!--
  Owned by THIS repository. Replace the placeholders below with 3–6 rules that are specific
  to this repository (stack, layout, domain invariants, interfaces it owns).
  Rules: prefix IDs with the repo code (e.g. ORD-1), add or tighten only, name the check.
-->

### [REPO_CODE]-1 [RULE_NAME]
[RULE_DESCRIPTION]
*Check: [CHECK]*

### [REPO_CODE]-2 [RULE_NAME]
[RULE_DESCRIPTION]
*Check: [CHECK]*

### Exceptions
None. <!-- Format: | Rule | Exception | ADR | Owner | Expires | -->

## Repository governance
- Part C is amended by pull request in this repository, approved by the CODEOWNERS of
  `.specify/memory/`, on a dedicated `governance/*` branch (never inside a feature branch).
- Parts A and B change only through the automated governance sync pull request.

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
"""


def cmd_build(args: argparse.Namespace) -> int:
    gov = PLATFORM_ROOT / "governance"
    frags = current_fragments(gov)
    outputs: dict[Path, str] = {}

    org = frags["ORG-BASELINE"]
    outputs[PLATFORM_ROOT / "presets/relm-org/templates/constitution-template.md"] = (
        CONSTITUTION_HEADER + org.group(0) + "\n"
    )
    for preset, team in TEAM_PRESETS.items():
        m = frags[f"TEAM-{team.upper()}"]
        outputs[PLATFORM_ROOT / f"presets/{preset}/templates/constitution-template.md"] = (
            "\n" + m.group(0) + "\n" + CONSTITUTION_PART_C
        )
    # history snapshots: one immutable file per released version of every block
    for name, m in frags.items():
        outputs[history_path(gov, name, m["version"])] = m.group(0) + "\n"

    # versions manifest consumed by humans, CI and the propagation bot
    versions = {name: m["version"] for name, m in frags.items()}
    outputs[gov / "versions.json"] = json.dumps(versions, indent=2, sort_keys=True) + "\n"

    stale = 0
    for path, content in outputs.items():
        existing = path.read_text(encoding="utf-8") if path.exists() else None
        if existing == content:
            continue
        is_history = "history" in path.parts
        if is_history and existing is not None:
            fail(f"history snapshot {path.relative_to(PLATFORM_ROOT)} differs from the current "
                 f"fragment with the same version — bump the fragment version", str(path))
            stale += 1
            continue
        if args.check:
            fail(f"{path.relative_to(PLATFORM_ROOT)} is stale — run `python scripts/relm_sdd.py build`",
                 str(path))
            stale += 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            ok(f"wrote {path.relative_to(PLATFORM_ROOT)}")
    if not stale:
        ok("presets and governance history are up to date")
    return finish()


# --------------------------------------------------------------------------- package / catalog
FIXED_TS = (2026, 1, 1, 0, 0, 0)
SKIP = {".DS_Store", "__pycache__"}


def deterministic_zip(src: Path) -> bytes:
    buf = io.BytesIO()
    # ZIP_STORED + fixed modes: byte-identical on every machine (deflate output varies across zlib builds)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
        for p in sorted(src.rglob("*"), key=lambda x: x.as_posix()):
            if p.is_dir() or any(part in SKIP for part in p.parts):
                continue
            info = zipfile.ZipInfo(p.relative_to(src).as_posix(), FIXED_TS)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_STORED
            zf.writestr(info, p.read_bytes())
    return buf.getvalue()


def simple_yaml_scalar(text: str, key: str) -> str | None:
    m = re.search(rf'^\s*{re.escape(key)}:\s*"?([^"\n#]+?)"?\s*(?:#.*)?$', text, re.M)
    return m.group(1).strip() if m else None


def components() -> list[dict]:
    comps = []
    for kind, manifest in (("preset", "preset.yml"), ("extension", "extension.yml")):
        for d in sorted((PLATFORM_ROOT / f"{kind}s").glob("*/")):
            mf = d / manifest
            if not mf.exists():
                continue
            text = mf.read_text(encoding="utf-8")
            comps.append({
                "kind": kind,
                "dir": d,
                "id": simple_yaml_scalar(text, "id"),
                "name": simple_yaml_scalar(text, "name"),
                "version": simple_yaml_scalar(text, "version"),
                "description": simple_yaml_scalar(text, "description"),
                "speckit_version": simple_yaml_scalar(text, "speckit_version"),
                "templates": len(re.findall(r'type:\s*"template"', text)),
                "commands": len(re.findall(r'type:\s*"command"', text))
                if kind == "preset" else len(re.findall(r'^\s*- name:\s*"speckit\.', text, re.M)),
            })
    return comps


def asset_name(c: dict) -> str:
    return f"{c['id']}-{c['version']}.zip"


def cmd_package(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for c in components():
        data = deterministic_zip(c["dir"])
        (out / asset_name(c)).write_bytes(data)
        ok(f"{asset_name(c)}  sha256={hashlib.sha256(data).hexdigest()}")
    return finish()


def cmd_catalog(args: argparse.Namespace) -> int:
    tag = args.tag
    catalogs = {"preset": {}, "extension": {}}
    for c in components():
        digest = hashlib.sha256(deterministic_zip(c["dir"])).hexdigest()
        rel = c["dir"].relative_to(PLATFORM_ROOT).as_posix()
        entry = {
            "id": c["id"],
            "name": c["name"],
            "version": c["version"],
            "description": c["description"],
            "author": "Relm SDD Guild",
            "repository": PLATFORM_REPO,
            "documentation": f"{PLATFORM_REPO}/blob/main/{rel}/README.md",
            "download_url": f"{PLATFORM_REPO}/releases/download/{tag}/{asset_name(c)}",
            "sha256": digest,
            "license": "MIT",
            "requires": {"speckit_version": c["speckit_version"]},
            "provides": {"templates": c["templates"], "commands": c["commands"]},
            "tags": ["relm", "internal"],
        }
        catalogs[c["kind"]][c["id"]] = entry
    stale = 0
    for kind, entries in catalogs.items():
        key = f"{kind}s"
        path = PLATFORM_ROOT / "catalogs" / f"{key}.json"
        doc = {
            "schema_version": "1.0",
            "updated_at": "2026-11-21T00:00:00Z",
            "catalog_url": f"https://raw.githubusercontent.com/{ORG}/speckit-platform/main/catalogs/{key}.json",
            key: entries,
        }
        content = json.dumps(doc, indent=2) + "\n"
        existing = path.read_text(encoding="utf-8") if path.exists() else None
        if existing == content:
            continue
        if args.check:
            fail(f"catalogs/{key}.json is stale — run `python scripts/relm_sdd.py catalog --tag {tag}`")
            stale += 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            ok(f"wrote catalogs/{key}.json")
    if not stale:
        ok("catalogs are up to date")
    return finish()


# --------------------------------------------------------------------------- constitution
def resolve_governance(arg: str | None) -> Path:
    gov = Path(arg) if arg else PLATFORM_ROOT / "governance"
    if not (gov / "org-baseline.md").exists():
        print(f"governance directory not found: {gov}", file=sys.stderr)
        sys.exit(2)
    return gov


def cmd_constitution_check(args: argparse.Namespace) -> int:
    path = Path(args.constitution)
    gov = resolve_governance(args.governance)
    if not path.exists():
        fail(f"constitution not found at {path} (ORG-1)", str(path))
        return finish()
    text = path.read_text(encoding="utf-8")
    current = current_fragments(gov)
    blocks = list(BLOCK_RE.finditer(text))
    names = [b["name"] for b in blocks]

    if names.count("ORG-BASELINE") != 1:
        fail("constitution must contain exactly one RELM:ORG-BASELINE block (Part A)", str(path))
    teams = [n for n in names if n.startswith("TEAM-")]
    if len(teams) != 1:
        fail(f"constitution must contain exactly one RELM:TEAM-* block (Part B); found {teams or 'none'}",
             str(path))
    if "## Part C" not in text:
        fail("constitution has no '## Part C — Repository Amendments' section", str(path))
    if re.search(r"\[(PROJECT_NAME|REPO_CODE|RULE_NAME|CONSTITUTION_VERSION)\]", text):
        fail("constitution still contains template placeholders — run /speckit.constitution", str(path))

    for b in blocks:
        name, ver = b["name"], b["version"]
        if name not in current:
            fail(f"unknown governance block RELM:{name}", str(path))
            continue
        cur_ver = current[name]["version"]
        snap = history_path(gov, name, ver)
        if not snap.exists():
            fail(f"RELM:{name} v{ver} is not a released governance version", str(path))
            continue
        if b.group(0).strip() != snap.read_text(encoding="utf-8").strip():
            fail(f"RELM:{name} v{ver} was edited locally — Parts A/B are read-only. "
                 f"Run `relm_sdd.py constitution-sync --write` to restore it", str(path))
            continue
        cmaj, cmin, _ = semver(cur_ver)
        rmaj, rmin, _ = semver(ver)
        if (rmaj, rmin) == (cmaj, cmin):
            if ver != cur_ver:
                warn(f"RELM:{name} v{ver} — patch {cur_ver} available (merge the sync PR)", str(path))
            else:
                ok(f"RELM:{name} v{ver} is current")
        elif rmaj != cmaj:
            fail(f"RELM:{name} v{ver} is a different MAJOR than current v{cur_ver}", str(path))
        elif cmin - rmin > args.max_minor_lag:
            fail(f"RELM:{name} v{ver} is {cmin - rmin} MINOR versions behind v{cur_ver} "
                 f"(policy allows {args.max_minor_lag})", str(path))
        else:
            warn(f"RELM:{name} v{ver} is behind v{cur_ver} — merge the governance sync PR", str(path))
    return finish()


def cmd_constitution_sync(args: argparse.Namespace) -> int:
    path = Path(args.constitution)
    gov = resolve_governance(args.governance)
    text = path.read_text(encoding="utf-8")
    current = current_fragments(gov)
    changed = []

    def repl(m: re.Match) -> str:
        cur = current.get(m["name"])
        if cur is None:
            return m.group(0)
        if m.group(0) != cur.group(0):
            changed.append(f"RELM:{m['name']} v{m['version']} -> v{cur['version']}")
        return cur.group(0)

    new = BLOCK_RE.sub(repl, text)
    if not changed:
        ok(f"{path}: governance blocks already current")
        return 0
    for c in changed:
        print(f"sync  {c}")
    if args.write:
        path.write_text(new, encoding="utf-8")
        ok(f"updated {path}")
    else:
        print("(dry run — pass --write to apply)")
    return 0


# --------------------------------------------------------------------------- spec lint
def spec_dirs(root: Path) -> list[Path]:
    specs = root / "specs"
    return sorted(p for p in specs.glob("[0-9][0-9][0-9]-*") if p.is_dir()) if specs.exists() else []


def status_of(text: str) -> str:
    m = re.search(r"^\*\*Status\*\*:\s*([A-Za-z -]+)", text, re.M)
    return (m.group(1).strip() if m else "Draft")


def cmd_spec_lint(args: argparse.Namespace) -> int:
    root = Path(args.root)
    dirs = spec_dirs(root)
    if not dirs:
        ok("no feature specs in this repository")
        return finish()
    for d in dirs:
        spec = d / "spec.md"
        rel = spec.relative_to(root).as_posix()
        if not spec.exists():
            fail(f"{d.name}: missing spec.md", rel)
            continue
        before = len(failures)
        text = spec.read_text(encoding="utf-8")
        num = int(d.name.split("-", 1)[0])
        fid = re.search(r"\*\*Feature ID\*\*:\s*RELM-(\d+)", text)
        if not fid:
            fail(f"{d.name}: spec.md has no '**Feature ID**: RELM-<n>' traceability line (ORG-1)", rel)
        elif int(fid.group(1)) != num:
            fail(f"{d.name}: Feature ID RELM-{fid.group(1)} does not match directory number {num:03d} (PRD-1)",
                 rel)
        stories = re.split(r"^### User Story", text, flags=re.M)[1:]
        if not stories:
            fail(f"{d.name}: spec.md has no '### User Story' sections (ORG-2)", rel)
        for i, s in enumerate(stories, 1):
            story = re.split(r"^## |^### Edge Cases", s, flags=re.M)[0]
            if "**Given**" not in story or "**Then**" not in story:
                fail(f"{d.name}: user story {i} has no Given/When/Then acceptance scenario (ORG-2)", rel)
        status = status_of(text)
        if status.lower() != "draft" and "[NEEDS CLARIFICATION" in text:
            fail(f"{d.name}: status is '{status}' but [NEEDS CLARIFICATION] markers remain (ORG-2)", rel)
        if "## Success Criteria" not in text:
            fail(f"{d.name}: spec.md has no Success Criteria section (ORG-2)", rel)
        if args.kind == "product":
            for required in ("impact.md", "contracts.lock.md", "checklists/requirements.md"):
                if not (d / required).exists():
                    fail(f"{d.name}: product feature is missing {required} (PRD-3/PRD-4)", rel)
        else:
            if "**Central spec**" not in text:
                warn(f"{d.name}: no '**Central spec**' link — fine for repo-local features only", rel)
        if len(failures) == before:
            ok(f"{d.name}: {status}")
    return finish()


# --------------------------------------------------------------------------- PR check
LANES = {"lane:feature", "lane:bugfix", "lane:chore", "lane:governance"}


def cmd_pr_check(args: argparse.Namespace) -> int:
    # HTML comments are template guidance, not evidence
    body = re.sub(r"<!--.*?-->", "", os.environ.get("PR_BODY", ""), flags=re.S)
    try:
        labels = set(json.loads(os.environ.get("PR_LABELS", "[]")))
    except json.JSONDecodeError:
        labels = set()
    root = Path(args.root)
    lanes = labels & LANES
    m = re.search(r"^\s*\**Feature\**:\s*RELM-(\d+)", body, re.M | re.I)

    if not lanes and not m:
        fail("PR declares neither 'Feature: RELM-<n>' in the body nor a lane label "
             f"({', '.join(sorted(LANES))}) — ORG-1")
        return finish()
    if len(lanes) > 1:
        fail(f"PR has more than one lane label: {sorted(lanes)}")

    if m or "lane:feature" in lanes:
        if not m:
            fail("lane:feature PRs must contain 'Feature: RELM-<n>' in the description")
            return finish()
        n = int(m.group(1))
        ok(f"PR traces to RELM-{n}")
        matches = sorted((root / "specs").glob(f"{n:03d}-*")) if (root / "specs").exists() else []
        if args.require_spec and not matches:
            fail(f"no specs/{n:03d}-*/ directory in this repository for RELM-{n} — run "
                 f"/speckit.specify with --number {n} (PRD-1)")
        for d in matches:
            ok(f"found local spec {d.relative_to(root)}")
        # ORG-9: evidence of analyze + converge (not applicable in product-specs, PS-1)
        if args.kind == "product":
            ok("product repository: analyze/converge evidence not required (PS-1)")
            return finish()
        if not re.search(r"speckit[.-]analyze[^\n]*0\s*CRITICAL", body, re.I):
            fail("PR description must record '/speckit.analyze: 0 CRITICAL' (ORG-9)")
        if not re.search(r"speckit[.-]converge[^\n]*converged", body, re.I):
            fail("PR description must record '/speckit.converge: Converged' (ORG-9)")
    else:
        lane = next(iter(lanes))
        ok(f"PR uses the {lane} lane")
        if lane == "lane:bugfix" and not re.search(r"(regression test|test)", body, re.I):
            warn("bugfix lane: describe the regression test that reproduces the bug")
    return finish()


# --------------------------------------------------------------------------- agent files
def cmd_agent_files_check(args: argparse.Namespace) -> int:
    root = Path(args.root)
    agents = root / "AGENTS.md"
    if not agents.exists():
        fail("AGENTS.md is missing (agent operating instructions)")
    else:
        t = agents.read_text(encoding="utf-8")
        for heading in ("## Commands", "## Spec Kit in this repository"):
            if heading not in t:
                fail(f"AGENTS.md is missing the '{heading}' section", "AGENTS.md")
        ok("AGENTS.md present")
    claude = root / "CLAUDE.md"
    if not claude.exists() or "@AGENTS.md" not in claude.read_text(encoding="utf-8"):
        fail("CLAUDE.md must exist and import @AGENTS.md", "CLAUDE.md")
    else:
        ok("CLAUDE.md imports AGENTS.md")
    if not (root / ".github/copilot-instructions.md").exists():
        fail(".github/copilot-instructions.md is missing", ".github/copilot-instructions.md")
    else:
        ok("copilot instructions present")
    if not (root / ".specify/memory/constitution.md").exists():
        fail(".specify/memory/constitution.md is missing — run specify init + /speckit.constitution")
    else:
        ok("constitution present")
    return finish()


# --------------------------------------------------------------------------- contracts
def git(*a: str) -> str:
    return subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout


def contract_version(text: str) -> str | None:
    m = re.search(r"^info:\s*\n(?:[ \t]+.*\n)*?[ \t]+version:\s*['\"]?([^'\"\s]+)", text, re.M)
    return m.group(1) if m else None


def cmd_contract_check(args: argparse.Namespace) -> int:
    base = args.base
    try:
        changed = [l for l in git("diff", "--name-only", f"{base}...HEAD").splitlines() if l]
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        return 2
    contracts = [c for c in changed if c.startswith("contracts/") and c.endswith((".yaml", ".yml"))]
    vendored = [c for c in contracts if c.startswith("contracts/vendor/")]
    owned = [c for c in contracts if c not in vendored]
    if not contracts:
        ok("no contract changes")
    for c in owned:
        if not Path(c).exists():
            fail(f"{c} was deleted — retiring a contract needs a MAJOR deprecation plan (ORG-3)", c)
            continue
        new_v = contract_version(Path(c).read_text(encoding="utf-8"))
        try:
            old_v = contract_version(git("show", f"{base}:{c}"))
        except subprocess.CalledProcessError:
            ok(f"{c}: new contract v{new_v}")
            continue
        if new_v == old_v:
            fail(f"{c} changed but info.version is still {new_v} — bump it (ORG-3)", c)
        else:
            ok(f"{c}: v{old_v} -> v{new_v}")
    if vendored and "contracts/vendor/README.md" not in changed:
        fail("vendored contracts changed without updating contracts/vendor/README.md "
             "(source repo, version, commit) — vendored copies are read-only (ORG-3)")
    elif vendored:
        for c in vendored:
            ok(f"{c}: vendored copy updated with provenance")
    return finish()


# --------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="relm_sdd", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build"); s.add_argument("--check", action="store_true"); s.set_defaults(fn=cmd_build)
    s = sub.add_parser("package"); s.add_argument("--out", default="dist"); s.set_defaults(fn=cmd_package)
    s = sub.add_parser("catalog"); s.add_argument("--tag", default="v1.0.0")
    s.add_argument("--check", action="store_true"); s.set_defaults(fn=cmd_catalog)

    for name, fn in (("constitution-check", cmd_constitution_check),
                     ("constitution-sync", cmd_constitution_sync)):
        s = sub.add_parser(name)
        s.add_argument("--constitution", default=".specify/memory/constitution.md")
        s.add_argument("--governance", help="path to speckit-platform/governance (default: alongside this script)")
        if name == "constitution-check":
            s.add_argument("--max-minor-lag", type=int, default=1)
        else:
            s.add_argument("--write", action="store_true")
        s.set_defaults(fn=fn)

    s = sub.add_parser("spec-lint"); s.add_argument("--root", default=".")
    s.add_argument("--kind", choices=["product", "service"], default="service"); s.set_defaults(fn=cmd_spec_lint)
    s = sub.add_parser("pr-check"); s.add_argument("--root", default=".")
    s.add_argument("--require-spec", action="store_true", help="feature PRs must have a local specs/NNN-* dir")
    s.add_argument("--kind", choices=["product", "service"], default="service")
    s.set_defaults(fn=cmd_pr_check)
    s = sub.add_parser("agent-files-check"); s.add_argument("--root", default="."); s.set_defaults(fn=cmd_agent_files_check)
    s = sub.add_parser("contract-check"); s.add_argument("--base", required=True); s.set_defaults(fn=cmd_contract_check)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
