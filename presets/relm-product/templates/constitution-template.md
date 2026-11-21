
<!-- BEGIN RELM:TEAM-PRODUCT v1.0.0 | source: spec-kit-relm/speckit-platform/presets/relm-product/templates/constitution-template.md | owner: @spec-kit-relm/architecture | DO NOT EDIT OUTSIDE speckit-platform -->
## Part B — Product & Architecture Overlay (MUST)

Applies to the product-level specification repository (`product-specs`) owned by
`@spec-kit-relm/architecture` together with product owners and QA.

### PRD-1 One product feature, one parent issue
Every cross-repository feature starts as a `Feature` issue in `product-specs`. Its issue number
`<n>` is the Feature ID `RELM-<n>` and the Spec Kit feature number used in **every** repository
(`specify --number <n>`), so all repos share the directory and branch `NNN-<short-name>`.
*Check: `sdd-gates / spec-lint` (Feature ID matches directory number).*

### PRD-2 Technology-agnostic product specs
Product specs describe users, outcomes, scenarios, and constraints. They never prescribe
services, frameworks, or schemas — that is decided in each repository's plan.
*Check: Gate 1 review, `/speckit.analyze`.*

### PRD-3 Explicit impact map
Every product feature has an `impact.md` that lists each participating repository, its role
(provider/consumer) for each interface, the contract owner, the rollout order, and the rollback
order.
*Check: `sdd-gates / spec-lint` (required files), Gate 1 review.*

### PRD-4 Locked contract versions
When contract PRs are approved, `contracts.lock.md` for the feature and the org-wide
`contracts/REGISTRY.md` are updated in the same pull request. Service plans reference only locked
versions.
*Check: Gate 2 review.*

### PRD-5 Right-sized features
Each repository's slice of a feature fits in roughly five developer-days. Larger features are
split into several product features linked from a parent epic.
*Check: Gate 1 review (`Slices` table in impact.md).*

### PRD-6 Living product specs
After release, the product spec is updated whenever shipped behavior changes, and follow-up work
opens a new feature that links back. Service-level specs are flow-forward (immutable history).
*Check: PR template item "central spec updated", quarterly spec audit.*
<!-- END RELM:TEAM-PRODUCT -->

## Part C — Repository Amendments (MUST)

<!--
  Owned by THIS repository. Replace the placeholders below with 3–6 rules that are specific
  to this repository (stack, layout, domain invariants, interfaces it owns).
  Rules: prefix IDs with the repo code (e.g. ORD-1), add or tighten only, name the check.
-->

### [REPO_CODE]-1 [RULE_NAME]
[RULE_DESCRIPTION]
*Check: [CHECK]*

### [REPO_CODE]-2 [RULE_NAME]
[RULE_DESCRIPTION]
*Check: [CHECK]*

### Exceptions
None. <!-- Format: | Rule | Exception | ADR | Owner | Expires | -->

## Repository governance
- Part C is amended by pull request in this repository, approved by the CODEOWNERS of
  `.specify/memory/`, on a dedicated `governance/*` branch (never inside a feature branch).
- Parts A and B change only through the automated governance sync pull request.

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
