# Changelog — speckit-platform

All notable changes to Relm's SDD toolchain. Governance block versions are listed separately
because repositories pin them individually (see `governance/versions.json`).

## [Unreleased]

### Changed
- Repository PR template: generic scenario-ID example (`RELM-<n>/…`).
- Docs: link to the handbook's organization-setup playbook; sync-token note in `governance/README.md`.

## [1.1.0] - 2026-11-22

Lean layout: rely on Spec Kit presets as the single source of the rules.

### Changed
- The rule blocks in `presets/relm-*/templates/constitution-template.md` are now the canonical
  text (BEGIN markers point there). Block versions are unchanged (v1.0.0).
- `constitution-check` compares rule content only (marker metadata may differ) and takes
  `--platform <checkout>`; `--governance <checkout>/governance` still works.
- `propagate-governance.yml` runs on version tags instead of GitHub releases.
- `governance/consumers.json` moved to `consumers.json`.

### Removed
- `governance/` rule copies and history snapshots, `relm_sdd.py build|package|catalog`,
  bundles, private catalogs and the release workflow. Install from a checkout with
  `bootstrap/init-repo.sh`.

### Added
- `relm_sdd.py governance-lint`; `bootstrap/protect-branches.sh`.

## [1.0.0] - 2026-11-21

### Governance
- `RELM:ORG-BASELINE` v1.0.0 — ORG-1 … ORG-9 ratified.
- `RELM:TEAM-BACKEND` v1.0.0 (BE-1 … BE-6), `RELM:TEAM-FRONTEND` v1.0.0 (FE-1 … FE-6),
  `RELM:TEAM-QA` v1.0.0 (QA-1 … QA-6), `RELM:TEAM-PRODUCT` v1.0.0 (PRD-1 … PRD-6).

### Added
- Presets `relm-org`, `relm-backend`, `relm-frontend`, `relm-qa`, `relm-product` (1.0.0).
- Extension `relm` 1.0.0: `/speckit.relm.impact`, `/speckit.relm.handoff`, `/speckit.relm.pr`.
- Bundles `relm-<kind>` 1.0.0, private catalogs, reusable workflows `sdd-gates` and `contract-check`.
- `scripts/relm_sdd.py` guardrail CLI, `bootstrap/init-repo.sh`, repository templates.
- Pinned Spec Kit CLI v1.4.3.
