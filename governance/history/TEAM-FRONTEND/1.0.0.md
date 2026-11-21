<!-- BEGIN RELM:TEAM-FRONTEND v1.0.0 | source: spec-kit-relm/speckit-platform/governance/overlays/frontend.md | owner: @spec-kit-relm/frontend | DO NOT EDIT OUTSIDE speckit-platform -->
## Part B — Frontend Team Overlay (MUST)

Applies to every user-facing application owned by `@spec-kit-relm/frontend`. Framework and
tooling specifics belong in Part C of each repository.

### FE-1 Accessible by default
UI meets WCAG 2.2 AA. Every interactive element is keyboard-operable and labelled; automated
axe checks report zero serious or critical violations on changed screens.
*Check: axe in component and E2E tests, design review.*

### FE-2 Every state is specified
For every screen or component a feature touches, the plan defines loading, empty, error,
partial, and success states, plus the copy for each. Error states map to the provider's
documented problem types.
*Check: plan review (`UI States` table), QA checklist `ux`.*

### FE-3 Contracts, not guesses
Frontend code talks to backend services only through API clients generated from the pinned
contract version. Hand-written requests to service endpoints are not allowed. Mock servers are
generated from the same pinned contract.
*Check: lint rule `no-restricted-imports` / `no-raw-fetch`, consumer contract tests.*

### FE-4 Performance budgets
Changed routes stay within budget: LCP < 2.5 s and INP < 200 ms at p75, and no route's JS bundle
grows by more than 10 % without a justified Complexity Tracking entry.
*Check: Lighthouse CI and bundle-size check on the PR.*

### FE-5 Design system and i18n
Use components from the design system; new primitives need a design-system PR first. No
user-facing string is hard-coded; all copy goes through the i18n catalog.
*Check: lint rules, design review.*

### FE-6 Privacy in the browser
No personal data in `localStorage`, URLs, or analytics payloads. Analytics events are declared in
the spec's tracking plan before they are implemented.
*Check: PR review, analytics schema validation.*
<!-- END RELM:TEAM-FRONTEND -->
