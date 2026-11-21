
### Backend: idempotency & retries (BE-2)

| Operation | Idempotency mechanism | Retry policy | Duplicate behavior |
|-----------|----------------------|--------------|--------------------|
| [POST /resource] | [Idempotency-Key, 24 h window] | [client may retry 3× with backoff] | [returns original 201 response] |

### Backend: data changes & migrations (BE-3)

| Change | Migration | Backward-compatible with previous release? | Contract step (later release) |
|--------|-----------|---------------------------------------------|-------------------------------|
| [add table / column] | [V12__add_x.sql] | [yes — nullable, unused by old code] | [drop old column in RELM-N+1] |

### Backend: events (BE-4)

| Event | Direction | AsyncAPI channel | Outbox? | Consumer de-dup key |
|-------|-----------|------------------|---------|---------------------|
| [inventory.reservation.expired] | [publishes / consumes] | [inventory.reservations.v1] | [yes] | [eventId] |

### Backend: performance & resilience budgets (BE-5)

| Endpoint / consumer | p99 latency budget | Error budget | Timeouts on outbound calls | Degradation behavior |
|---------------------|--------------------|--------------|----------------------------|----------------------|
| [POST /reservations] | [150 ms] | [0.1 %] | [inventory DB 50 ms] | [fail fast with 503 + Retry-After] |
