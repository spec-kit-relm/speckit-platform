# speckit-platform

**The Relm SDD toolchain: one place that packages, versions and enforces how every Relm repository
does spec-driven development with [GitHub Spec Kit](https://github.com/github/spec-kit).**

Owner: `@spec-kit-relm/sdd-guild` · Pinned Spec Kit CLI: **v1.4.3** (`SPECKIT_VERSION`) ·
Platform version: **v1.0.0** (`VERSION`)

> New here? Read [`sdd-handbook`](https://github.com/spec-kit-relm/sdd-handbook) first: it explains
> the process. This repository holds the **machinery** that makes the process the default.

---

## What lives here and why

Spec Kit projects are **directory-scoped**: every repository has its own `.specify/`,
constitution and feature numbering, with no constitution inheritance and no cross-repo linking.
Relm runs ~10 people across several repositories, so we build the missing org layer ourselves
from Spec Kit's official primitives: **presets** (template/command overrides that compose at
runtime), **extensions** (new commands), **bundles** and **catalogs** (versioned distribution).

| Path | What | Used by |
|------|------|---------|
| [`governance/`](governance/) | **Canonical constitution text.** `org-baseline.md` = Part A (ORG-1…ORG-9). `overlays/*.md` = Part B per team (BE, FE, QA, PRD). `history/` = immutable snapshots per released version. | Everyone reads it; only the SDD Guild changes it |
| [`presets/`](presets/) | `relm-org` (priority 20) + one team preset each (`relm-backend`, `relm-frontend`, `relm-qa`, `relm-product`, priority 10). They add the constitution skeleton, the **Relm Traceability** section in specs, **delivery sections** in plans, the mandatory **Phase R** in tasks, and wrap `/speckit.specify`, `/speckit.plan`, `/speckit.tasks` and `/speckit.implement` with Relm rules. | Installed in every repo |
| [`extensions/relm/`](extensions/relm/) | New commands for multi-repo work: `/speckit.relm.impact`, `/speckit.relm.handoff`, `/speckit.relm.pr`. | Installed in every repo |
| [`bundles/`](bundles/) | One bundle per repository kind (org preset + team preset + git, github and relm extensions, all pinned). | Target distribution format |
| [`catalogs/`](catalogs/) | Relm **private catalog** (`presets.json`, `extensions.json`) with deterministic sha256 digests. Configured as the only install-allowed non-core source in every repo. | `specify preset add …` |
| [`.github/workflows/`](.github/workflows/) | **Reusable gates**: `sdd-gates.yml` (agent files, constitution drift, spec lint, PR traceability) and `contract-check.yml` (lint, version bump, breaking changes, vendored provenance). Plus platform CI, release and governance propagation. | Every repo's CI |
| [`scripts/relm_sdd.py`](scripts/relm_sdd.py) | The stdlib-only guardrail CLI behind all the gates. Run it locally too. | CI, engineers, SDD Guild |
| [`bootstrap/init-repo.sh`](bootstrap/init-repo.sh) | Turns a repo into a Relm Spec Kit project in one command. | Onboarding a repo, propagation bot |
| [`templates/repo/`](templates/repo/) | `AGENTS.md`, `CLAUDE.md`, Copilot instructions, PR template, `sdd.yml`, `CODEOWNERS` to copy into a new repo. | New repos |
| [`contracts/redocly.yaml`](contracts/redocly.yaml) | The `relm-api` lint ruleset (BE-1, BE-2). | `contract-check` |

## How the layers compose

```text
                 speckit-platform/governance           (canonical, versioned)
   org-baseline.md ──► presets/relm-org         ── constitution-template (Part A)      priority 20
   overlays/<team>.md ► presets/relm-<team>     ── constitution-template (+Part B, Part C skeleton) priority 10, append
                                    │
                  specify preset add / init-repo.sh
                                    ▼
   <repo>/.specify/memory/constitution.md  =  Part A (synced, read-only)
                                            + Part B (synced, read-only)
                                            + Part C (owned by the repo: ORD-1, INV-2, …)
```

The same layering applies to templates: `relm-org` appends the traceability section to Spec Kit's
core `spec-template`, and the team preset appends its own plan sections on top. See it in any
repo with:

```bash
specify preset resolve plan-template     # shows the composition chain
specify artifact info speckit.plan --json
```

`/speckit.constitution` does **not** rewrite templates any more (Spec Kit ≥ 0.14.4); that is
exactly why we govern shared assets as presets rather than per-repo copies.

## Usage, in order

### 1. Onboard a repository (once per repo)

```bash
# prerequisites: git, python3, and the pinned Spec Kit CLI
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.4.3

git clone https://github.com/spec-kit-relm/speckit-platform ../speckit-platform
bash ../speckit-platform/bootstrap/init-repo.sh backend      # product | backend | frontend | qa
```

Then:

1. Run `/speckit.constitution` in your agent and fill **Part C** (3–6 rules with a repo prefix,
   each naming its check). Part A/B stay untouched.
2. Copy `templates/repo/*` (AGENTS.md, CLAUDE.md, `.github/…`) and adapt `AGENTS.md`.
3. Add `.github/workflows/sdd.yml` (also offered as the org workflow template **Relm SDD gates**).
4. Make `sdd / sdd-gates` and `contracts / contract-check` required checks on `main`.
5. Add the repository to [`governance/consumers.json`](governance/consumers.json) so it gets sync PRs.
6. Verify locally:
   ```bash
   python ../speckit-platform/scripts/relm_sdd.py agent-files-check
   python ../speckit-platform/scripts/relm_sdd.py constitution-check --governance ../speckit-platform/governance
   python ../speckit-platform/scripts/relm_sdd.py spec-lint
   ```

### 2. Day-to-day (engineers)

Nothing to do here — the presets and extension are already in your repo. Use the gates locally
before pushing (`spec-lint`, `constitution-check`). The process itself is in
[`sdd-handbook/playbooks`](https://github.com/spec-kit-relm/sdd-handbook/tree/main/playbooks).

### 3. Change a rule (SDD Guild)

1. Branch `governance/<topic>`; edit `governance/org-baseline.md` or `governance/overlays/<team>.md`
   **and bump the version in its BEGIN marker** (MAJOR/MINOR/PATCH, see the handbook).
2. `python scripts/relm_sdd.py build` regenerates the preset templates and writes the new
   `governance/history/<BLOCK>/<version>.md` snapshot. Old snapshots are never edited.
3. Bump preset versions if their content changed, update `VERSION` and `CHANGELOG.md`, then
   `python scripts/relm_sdd.py catalog --tag v<VERSION>`.
4. PR → review by the SDD Guild + one approver per discipline (CODEOWNERS) → merge.
5. Tag `v<VERSION>`. `release.yml` publishes the zips referenced by the catalog and moves the
   floating `v1` tag; `propagate-governance.yml` opens a sync PR in every consumer repository.
6. Repos must merge within one sprint: `constitution-check` fails once a repo is a different
   MAJOR or more than one MINOR behind.

### 4. Upgrade Spec Kit itself

Change `SPECKIT_VERSION`, read the [Spec Kit upgrade guide](https://github.github.io/spec-kit/upgrade.html),
let `platform-ci / install-smoke-test` prove the presets still compose, release a new platform
version. Spec Kit moves fast (dozens of releases per quarter) — never float it.

## Guardrail CLI reference

```text
python scripts/relm_sdd.py <command>
  build [--check]                 regenerate preset constitution templates + history snapshots
  package --out dist              deterministic zips of presets/* and extensions/*
  catalog --tag vX.Y.Z [--check]  regenerate catalogs/*.json with sha256 digests
  constitution-check              drift check of Parts A/B (+ placeholders, Part C present)
  constitution-sync [--write]     replace Parts A/B with the current governance blocks
  spec-lint [--kind product]      Feature ID ↔ directory, Given/When/Then, clarifications, required files
  pr-check [--require-spec]       PR_BODY/PR_LABELS: feature or lane, local spec, analyze/converge evidence
  agent-files-check               AGENTS.md sections, CLAUDE.md → @AGENTS.md, Copilot file, constitution
  contract-check --base <ref>     owned contract version bumps, read-only vendored contracts
```

## Official vs. Relm convention

| Official Spec Kit | Relm convention built on it |
|-------------------|-----------------------------|
| Directory-scoped projects, presets (replace/append/prepend/wrap), extensions, bundles, private catalogs, `git` + `github` extensions, `/speckit.analyze`, `/speckit.converge`, `/speckit.checklist`, the Contract-Driven Development guide | Three-part constitution with synced read-only blocks, drift check, feature number = product issue number, `product-specs` hub repo, `impact.md` / `contracts.lock.md`, Phase R, PR evidence gate, propagation bot |
