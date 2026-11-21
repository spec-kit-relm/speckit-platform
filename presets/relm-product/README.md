# Preset `relm-product` — Relm Product Specs

Relm product-level overlay for product-specs: constitution Part B (PRD-1..PRD-6) plus impact-map and contract-lock templates.

| Provides | Strategy | File |
|---|---|---|
| template `constitution-template` | append | [`templates/constitution-template.md`](templates/constitution-template.md) |
| template `impact-template` | replace | [`templates/impact-template.md`](templates/impact-template.md) |
| template `contracts-lock-template` | replace | [`templates/contracts-lock-template.md`](templates/contracts-lock-template.md) |

**`templates/constitution-template.md` is the canonical rule text** for this layer. To change a
rule, edit the block there and bump the version in its `BEGIN RELM:` marker — see
[`governance/README.md`](../../governance/README.md).

Install: normally via `bootstrap/init-repo.sh`; by hand from a checkout:
`specify preset add --dev ../speckit-platform/presets/relm-product --priority 10`.
