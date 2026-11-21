# Preset `relm-backend` — Relm Backend Team

Relm backend overlay: constitution Part B (BE-1..BE-6) and backend plan sections (idempotency, data changes, resilience).

| Provides | Strategy | File |
|---|---|---|
| template `constitution-template` | append | [`templates/constitution-template.md`](templates/constitution-template.md) |
| template `plan-template` | append | [`templates/plan-backend.md`](templates/plan-backend.md) |

Generated files: `templates/constitution-template.md` is generated from `governance/` by
`python scripts/relm_sdd.py build` — never edit it by hand.

Install: `specify preset add relm-backend --priority 10` (Relm catalog) or `bootstrap/init-repo.sh`.
