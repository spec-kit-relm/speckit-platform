
### QA: scenario-to-test strategy (QA-2, QA-3)

| Scenario ID | Level (unit / contract / integration / E2E) | Repository & suite | Tag | Data setup (synthetic) |
|-------------|---------------------------------------------|--------------------|-----|------------------------|
| [RELM-N/US1/AS1] | [E2E] | [e2e-tests / checkout] | [@smoke] | [seed: 1 SKU, stock 5] |

### QA: environments & pinned versions (QA-3)

| Environment | Contract versions exercised | Capability flags | Data reset strategy |
|-------------|-----------------------------|------------------|---------------------|
| [staging] | [orders-api@1.3.0, inventory-api@1.1.0] | [checkout.reservations=on] | [per-test namespace] |

### QA: release sign-off evidence (QA-6)

- [ ] All participating repositories report `/speckit.converge`: Converged
- [ ] Provider + consumer contract tests green for every locked version
- [ ] `@smoke` suite green in staging; all P1 scenarios pass
- [ ] Sign-off recorded on the product feature issue
