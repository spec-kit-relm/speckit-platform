# Preset `relm-product` — Relm Product Specs

Relm product-level overlay for product-specs: constitution Part B (PRD-1..PRD-6) plus impact-map and contract-lock templates.

| Provides | Strategy | File |
|---|---|---|
| template `constitution-template` | append | [`templates/constitution-template.md`](templates/constitution-template.md) |
| template `impact-template` | replace | [`templates/impact-template.md`](templates/impact-template.md) |
| template `contracts-lock-template` | replace | [`templates/contracts-lock-template.md`](templates/contracts-lock-template.md) |

Generated files: `templates/constitution-template.md` is generated from `governance/` by
`python scripts/relm_sdd.py build` — never edit it by hand.

Install: `specify preset add relm-product --priority 10` (Relm catalog) or `bootstrap/init-repo.sh`.
