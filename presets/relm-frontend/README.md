# Preset `relm-frontend` — Relm Frontend Team

Relm frontend overlay: constitution Part B (FE-1..FE-6) and frontend plan sections (UI states, accessibility, performance, tracking).

| Provides | Strategy | File |
|---|---|---|
| template `constitution-template` | append | [`templates/constitution-template.md`](templates/constitution-template.md) |
| template `plan-template` | append | [`templates/plan-frontend.md`](templates/plan-frontend.md) |

**`templates/constitution-template.md` is the canonical rule text** for this layer. To change a
rule, edit the block there and bump the version in its `BEGIN RELM:` marker — see
[`governance/README.md`](../../governance/README.md).

Install: normally via `bootstrap/init-repo.sh`; by hand from a checkout:
`specify preset add --dev ../speckit-platform/presets/relm-frontend --priority 10`.
