# Impact Map: [FEATURE NAME]

**Feature ID**: RELM-[N] | **Product spec**: [spec.md](./spec.md) | **Owner**: [tech lead]

## Participating repositories

| Repository | Team | Role in this feature | Stories / scenarios | Slice size (dev-days) | Owner (human) |
|------------|------|----------------------|---------------------|-----------------------|---------------|
| [inventory-service] | [backend] | [provider: Inventory API] | [US1, US3] | [≤ 5] | [@name] |

## Interfaces

| Interface | Provider (owner) | Consumers | Change | Contract file | Target version |
|-----------|------------------|-----------|--------|---------------|----------------|
| [Inventory API — reservations] | [inventory-service] | [orders-service, web-storefront] | [additive] | [contracts/inventory-api.yaml] | [1.1.0] |

## Rollout order (ORG-7)

1. [provider first, flag off]
2. [...]
N. [enable flag for 5 % → 50 % → 100 %]

## Rollback order

1. [disable flag]
2. [roll back consumers before providers]

## Risks & open questions

- [risk — owner — mitigation]
