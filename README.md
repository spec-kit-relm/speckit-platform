# speckit-platform

**The Relm SDD toolchain: Spec Kit presets that carry the company and team rules, one extension
for multi-repo work, and the CI gates every Relm repository runs.**

Owner: `@spec-kit-relm/sdd-guild` · Pinned Spec Kit CLI: **v1.4.3** (`SPECKIT_VERSION`) ·
Platform version: **v1.1.0** (`VERSION`; repositories use the floating tag `v1`)

> New here? Read [`sdd-handbook`](https://github.com/spec-kit-relm/sdd-handbook) first: it explains
> the process. This repository holds the **machinery** that makes the process the default.

---

## Design: use Spec Kit's features, script only the gaps

Spec Kit projects are **directory-scoped**: each repository has its own `.specify/`, constitution
and numbering. Spec Kit has **no constitution inheritance** and **no cross-repo linking** — its
official multi-repo guidance is contract-driven development plus a shared feature reference.

| Need | How Relm does it | Official Spec Kit? |
|------|------------------|--------------------|
| Same rules and artifact shape everywhere | **Presets** composed by priority: `relm-org` (Part A) + `relm-<team>` appended (Part B) | ✅ |
| Same feature number in every repo | `/speckit.specify RELM-<n>` → `--number <n>` (documented flag) | ✅ |
| Read the central spec from a service repo | `relm` **extension** commands (`handoff`, `impact`, `pr`) — prompts that read `../product-specs` | ✅ |
| Keep existing constitutions in sync after a rule change | `constitution-sync` + propagation PRs | ❌ gap — Spec Kit seeds the constitution once |
| Stop drift and unchecked PRs | `sdd-gates` and `contract-check` reusable workflows | ❌ gap — analyze/converge run only inside the agent |

## What lives here

| Path | What |
|------|------|
| [`presets/`](presets/) | `relm-org` (priority 20) and `relm-backend` / `relm-frontend` / `relm-qa` / `relm-product` (priority 10). Each `templates/constitution-template.md` **is the canonical rule text** for its layer. They also add the Relm Traceability section to specs, delivery sections to plans, Phase R to tasks, and wrap `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`. |
| [`extensions/relm/`](extensions/relm/) | `/speckit.relm.impact`, `/speckit.relm.handoff`, `/speckit.relm.pr` |
| [`governance/README.md`](governance/README.md) | Where each rule block lives, how it reaches repositories, how to change a rule |
| [`consumers.json`](consumers.json) | Repositories that receive governance sync PRs, with their kind |
| [`.github/workflows/`](.github/workflows/) | Reusable `sdd-gates.yml` and `contract-check.yml`; `ci.yml` (platform tests + install smoke test); `propagate-governance.yml` |
| [`scripts/relm_sdd.py`](scripts/relm_sdd.py) | Stdlib-only guardrail CLI behind all gates — run it locally too |
| [`bootstrap/`](bootstrap/) | `init-repo.sh` (make a repo a Relm Spec Kit project), `org-setup.sh` (teams, labels, project), `protect-branches.sh` (rulesets) |
| [`templates/repo/`](templates/repo/) | `AGENTS.md`, `CLAUDE.md`, Copilot instructions, PR template, `sdd.yml`, `CODEOWNERS` for new repos |
| [`contracts/redocly.yaml`](contracts/redocly.yaml) | The `relm-api` lint ruleset (BE-1, BE-2) |

See the composition in any repo:

```bash
specify preset resolve constitution-template   # base relm-org → append relm-<team>
specify preset resolve plan-template
```

## Usage, in order

### 1. Onboard a repository (once per repo)

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.4.3
git clone --branch v1 https://github.com/spec-kit-relm/speckit-platform ../speckit-platform
bash ../speckit-platform/bootstrap/init-repo.sh backend      # product | backend | frontend | qa
```

Then: run `/speckit.constitution` to write **Part C**; copy and adapt `templates/repo/*`; add
`.github/workflows/sdd.yml`; add the repo to `consumers.json`; verify:

```bash
python ../speckit-platform/scripts/relm_sdd.py agent-files-check
python ../speckit-platform/scripts/relm_sdd.py constitution-check --platform ../speckit-platform
python ../speckit-platform/scripts/relm_sdd.py spec-lint
```

Setting up the whole organization (tags, teams, labels, project, branch protection, sync token)
is a separate one-time task for an org owner: see the handbook's
[Set up the organization](https://github.com/spec-kit-relm/sdd-handbook/blob/main/playbooks/set-up-the-organization.md).

### 2. Day-to-day (engineers)

Nothing to do here — presets and the extension are installed in your repo. The process is in the
[handbook playbooks](https://github.com/spec-kit-relm/sdd-handbook/tree/main/playbooks).

### 3. Change a rule (SDD Guild)

Edit the block in the preset, bump its version, PR, tag — step by step in
[`governance/README.md`](governance/README.md#changing-a-rule).

### 4. Upgrade Spec Kit

Change `SPECKIT_VERSION`, read the [upgrade guide](https://github.github.io/spec-kit/upgrade.html),
let `ci / install-smoke-test` prove the presets still compose, then tag a new platform version.

## Guardrail CLI reference

```text
python scripts/relm_sdd.py <command>
  governance-lint                 preset rule blocks well-formed (platform CI)
  constitution-check [--platform] drift check of Parts A/B (+ placeholders, Part C present)
  constitution-sync [--write]     replace Parts A/B with the current preset blocks
  spec-lint [--kind product]      Feature ID ↔ directory, Given/When/Then, clarifications, required files
  pr-check [--require-spec]       PR_BODY/PR_LABELS: feature or lane, local spec, analyze/converge evidence
  agent-files-check               AGENTS.md sections, CLAUDE.md → @AGENTS.md, Copilot file, constitution
  contract-check --base <ref>     owned contract version bumps, read-only vendored contracts
```

## Versions

Repositories call the reusable workflows at `@v1` and `constitution-check` compares against the
rule blocks at that tag. Move `v1` only when you release (`governance/README.md` step 5).
