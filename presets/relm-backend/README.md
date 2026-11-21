# Preset `relm-backend` — Relm Backend Team

Relm backend overlay: constitution Part B (BE-1..BE-6) and backend plan sections (idempotency, data changes, resilience).

| Provides | Strategy | File |
|---|---|---|
| template `constitution-template` | append | [`templates/constitution-template.md`](templates/constitution-template.md) |
| template `plan-template` | append | [`templates/plan-backend.md`](templates/plan-backend.md) |

**`templates/constitution-template.md` is the canonical rule text** for this layer. To change a
rule, edit the block there and bump the version in its `BEGIN RELM:` marker — see
[`governance/README.md`](../../governance/README.md).

Install: normally via `bootstrap/init-repo.sh`; by hand from a checkout:
`specify preset add --dev ../speckit-platform/presets/relm-backend --priority 10`.
