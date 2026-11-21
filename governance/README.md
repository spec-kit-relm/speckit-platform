# Relm governance — where the rules live and how to change them

The canonical company and team rules are the **rule blocks inside the Relm presets**. There is no
separate copy and no build step: what you read in the preset is exactly what every repository's
constitution contains.

| Block | Constitution part | Canonical file | Owner |
|-------|-------------------|----------------|-------|
| `RELM:ORG-BASELINE` | A — company (ORG-1 … ORG-9) | [`presets/relm-org/templates/constitution-template.md`](../presets/relm-org/templates/constitution-template.md) | SDD Guild + one approver per discipline |
| `RELM:TEAM-BACKEND` | B — backend (BE-1 … BE-6) | [`presets/relm-backend/templates/constitution-template.md`](../presets/relm-backend/templates/constitution-template.md) | `@spec-kit-relm/backend` |
| `RELM:TEAM-FRONTEND` | B — frontend (FE-1 … FE-6) | [`presets/relm-frontend/templates/constitution-template.md`](../presets/relm-frontend/templates/constitution-template.md) | `@spec-kit-relm/frontend` |
| `RELM:TEAM-QA` | B — quality engineering (QA-1 … QA-6) | [`presets/relm-qa/templates/constitution-template.md`](../presets/relm-qa/templates/constitution-template.md) | `@spec-kit-relm/qa` |
| `RELM:TEAM-PRODUCT` | B — product & architecture (PRD-1 … PRD-6) | [`presets/relm-product/templates/constitution-template.md`](../presets/relm-product/templates/constitution-template.md) | `@spec-kit-relm/architecture` |

Repositories that receive sync pull requests are listed in [`../consumers.json`](../consumers.json).

## How it reaches a repository

1. **New repository:** `bootstrap/init-repo.sh <kind>` installs `relm-org` (priority 20) and
   `relm-<kind>` (priority 10, `append`). Spec Kit composes the two templates and the script seeds
   `.specify/memory/constitution.md` from the result. The team then writes Part C.
2. **Existing repository:** Spec Kit seeds the constitution only once, and later preset changes do
   not rewrite it (by design — Part C is the repository's own text). So when a new platform version
   is tagged, `propagate-governance.yml` opens a sync PR that replaces only the Part A/B blocks
   (`relm_sdd.py constitution-sync`).
3. **Every PR:** `sdd-gates / constitution-check` compares the repository's Part A/B blocks with the
   blocks in speckit-platform at the pinned tag (`@v1`). Same version → the rules must be identical.
   Older version → warning if at most one MINOR behind, failure otherwise.

## Changing a rule

1. Branch `governance/<topic>`. Edit the block in the preset's `templates/constitution-template.md`.
2. Bump the version in its `BEGIN RELM:<NAME> vX.Y.Z` marker:
   MAJOR = principle removed or redefined · MINOR = principle added or materially expanded ·
   PATCH = wording only. Also bump `version:` in that preset's `preset.yml`.
3. Writing rules: 5–10 rules per block, every rule ends with `*Check: …*` naming the CI job,
   analyzer or review step that enforces it. Lower layers only add or tighten. No technology in
   Part A. `python scripts/relm_sdd.py governance-lint` checks the shape.
4. PR → approval from the owners above (CODEOWNERS) → merge.
5. Release: bump `VERSION`, add a `CHANGELOG.md` entry, then tag and move the floating major tag:
   ```bash
   git tag -a v1.2.0 -m "speckit-platform v1.2.0" && git tag -f v1
   git push origin v1.2.0 && git push -f origin v1
   ```
   Pushing `v1.2.0` triggers the sync PRs. Repositories merge them within one sprint.
