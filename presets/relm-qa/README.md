# Preset `relm-qa` — Relm Quality Engineering

Relm QA overlay: constitution Part B (QA-1..QA-6), test-strategy plan section and QA checklist conventions.

| Provides | Strategy | File |
|---|---|---|
| template `constitution-template` | append | [`templates/constitution-template.md`](templates/constitution-template.md) |
| template `plan-template` | append | [`templates/plan-qa.md`](templates/plan-qa.md) |
| template `checklist-template` | append | [`templates/checklist-qa.md`](templates/checklist-qa.md) |

**`templates/constitution-template.md` is the canonical rule text** for this layer. To change a
rule, edit the block there and bump the version in its `BEGIN RELM:` marker — see
[`governance/README.md`](../../governance/README.md).

Install: normally via `bootstrap/init-repo.sh`; by hand from a checkout:
`specify preset add --dev ../speckit-platform/presets/relm-qa --priority 10`.
