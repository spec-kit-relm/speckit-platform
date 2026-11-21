# Changelog — speckit-platform

All notable changes to Relm's SDD toolchain. Governance block versions are listed separately
because repositories pin them individually (see `governance/versions.json`).

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
