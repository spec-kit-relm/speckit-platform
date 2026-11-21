<!-- BEGIN RELM:TEAM-PRODUCT v1.0.0 | source: spec-kit-relm/speckit-platform/governance/overlays/product.md | owner: @spec-kit-relm/architecture | DO NOT EDIT OUTSIDE speckit-platform -->
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
