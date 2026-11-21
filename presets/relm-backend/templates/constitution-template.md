
<!-- BEGIN RELM:TEAM-BACKEND v1.0.0 | source: spec-kit-relm/speckit-platform/presets/relm-backend/templates/constitution-template.md | owner: @spec-kit-relm/backend | DO NOT EDIT OUTSIDE speckit-platform -->
## Part B — Backend Team Overlay (MUST)

Applies to every backend service owned by `@spec-kit-relm/backend`. Stack-specific rules
(language, framework, layout) belong in Part C of each repository.

### BE-1 Consistent HTTP APIs
Resources are plural nouns, errors use RFC 9457 `application/problem+json`, list endpoints use
cursor pagination, and every response carries `X-Request-Id`. The provider's OpenAPI file is the
source of truth; handlers are validated against it in tests.
*Check: contract lint (Redocly ruleset `relm-api`), provider verification tests.*

### BE-2 Idempotent writes
Every non-safe operation (`POST`, `PATCH`, `DELETE`, event handlers) is idempotent: HTTP writes
accept an `Idempotency-Key` header, event consumers de-duplicate by event ID. Retries are only
allowed on idempotent operations, with bounded exponential backoff and jitter.
*Check: contract tests replay every write twice; plan review.*

### BE-3 Backward-compatible data changes
Schema migrations are forward-only and backward-compatible with the previous release
(expand → migrate → contract). Destructive steps ship in a later release than the code that
stops using the column/table.
*Check: migration lint job, plan `Rollback` section.*

### BE-4 Reliable events
Events are published through a transactional outbox, carry `eventId`, `occurredAt`,
`schemaVersion`, and `traceId`, and are documented in the provider's AsyncAPI contract.
Consumers tolerate duplicates and out-of-order delivery.
*Check: AsyncAPI lint, consumer tests with duplicate/out-of-order fixtures.*

### BE-5 Resilience budgets
Every outbound call has an explicit timeout; plans state p99 latency and error-rate budgets per
endpoint; dependencies degrade gracefully (fallback or fast failure, never unbounded waits).
*Check: plan review (`Performance & Resilience` section), load test for P1 stories.*

### BE-6 Test pyramid
Domain logic has unit tests (≥ 80 % line coverage on the domain layer), adapters have
integration tests against real dependencies in containers, and every provided interface has
provider verification. Mocks of our own services are generated from pinned contracts only.
*Check: CI coverage gate, `/speckit.converge`.*
<!-- END RELM:TEAM-BACKEND -->

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
