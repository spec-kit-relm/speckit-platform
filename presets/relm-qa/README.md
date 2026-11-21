# Preset `relm-qa` — Relm Quality Engineering

Relm QA overlay: constitution Part B (QA-1..QA-6), test-strategy plan section and QA checklist conventions.

| Provides | Strategy | File |
|---|---|---|
| template `constitution-template` | append | [`templates/constitution-template.md`](templates/constitution-template.md) |
| template `plan-template` | append | [`templates/plan-qa.md`](templates/plan-qa.md) |
| template `checklist-template` | append | [`templates/checklist-qa.md`](templates/checklist-qa.md) |

Generated files: `templates/constitution-template.md` is generated from `governance/` by
`python scripts/relm_sdd.py build` — never edit it by hand.

Install: `specify preset add relm-qa --priority 10` (Relm catalog) or `bootstrap/init-repo.sh`.
