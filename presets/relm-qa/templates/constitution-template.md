
<!-- BEGIN RELM:TEAM-QA v1.0.0 | source: spec-kit-relm/speckit-platform/presets/relm-qa/templates/constitution-template.md | owner: @spec-kit-relm/qa | DO NOT EDIT OUTSIDE speckit-platform -->
## Part B — Quality Engineering Overlay (MUST)

Applies to quality-engineering repositories (E2E, performance, contract-verification suites)
owned by `@spec-kit-relm/qa`.

### QA-1 Shift-left ownership
QA co-owns acceptance criteria with the product owner from `/speckit.specify` onwards and
generates the product feature's checklists (`/speckit.checklist`) before any service plan is
approved. Checklist items are ticked only by humans during review, never by an agent.
*Check: Gate 1 review, checklist diff in PR.*

### QA-2 Scenario traceability
Every Given/When/Then scenario has a stable ID `RELM-<n>/US<k>/AS<m>`. Every automated test title
starts with the scenario ID it verifies, so coverage can be computed from test reports.
*Check: `scenario-coverage` job in e2e-tests.*

### QA-3 Version-pinned environments
E2E suites pin the contract versions they exercise (`contracts.lock.json`) and select expectations
by contract version or capability flag, never by branch name.
*Check: E2E config validation.*

### QA-4 Deterministic suites
No fixed sleeps, no order dependence, no shared mutable test data. A flaky test is quarantined
within 24 hours and fixed or deleted within one sprint; quarantined tests never gate a release.
*Check: flake tracker, nightly rerun report.*

### QA-5 Synthetic data only
Tests use generated or synthetic data. Production data and real personal data are never used in
any test environment.
*Check: data-seeding review, secret/PII scanning.*

### QA-6 Release sign-off is evidence-based
Release readiness requires: all participating repositories converged, contract tests green,
`@smoke` E2E green in staging, and all P1 scenarios passing. QA records the sign-off on the
product feature issue.
*Check: Gate 4 checklist on the feature issue.*
<!-- END RELM:TEAM-QA -->

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
