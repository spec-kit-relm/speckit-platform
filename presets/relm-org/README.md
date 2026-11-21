# Preset `relm-org` — Relm Organization Baseline

Relm org-wide SDD standard: constitution Part A, traceability in specs, delivery sections in plans, mandatory verification phase in tasks.

| Provides | Strategy | File |
|---|---|---|
| template `constitution-template` | replace | [`templates/constitution-template.md`](templates/constitution-template.md) |
| template `spec-template` | append | [`templates/spec-traceability.md`](templates/spec-traceability.md) |
| template `plan-template` | append | [`templates/plan-delivery.md`](templates/plan-delivery.md) |
| template `tasks-template` | append | [`templates/tasks-verification.md`](templates/tasks-verification.md) |
| command `speckit.specify` | wrap | [`commands/speckit.specify.md`](commands/speckit.specify.md) |
| command `speckit.plan` | wrap | [`commands/speckit.plan.md`](commands/speckit.plan.md) |
| command `speckit.tasks` | wrap | [`commands/speckit.tasks.md`](commands/speckit.tasks.md) |
| command `speckit.implement` | wrap | [`commands/speckit.implement.md`](commands/speckit.implement.md) |

**`templates/constitution-template.md` is the canonical rule text** for this layer. To change a
rule, edit the block there and bump the version in its `BEGIN RELM:` marker — see
[`governance/README.md`](../../governance/README.md).

Install: normally via `bootstrap/init-repo.sh`; by hand from a checkout:
`specify preset add --dev ../speckit-platform/presets/relm-org --priority 20`.
