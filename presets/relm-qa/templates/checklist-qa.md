
---

## Relm checklist conventions (QA-1)

- Items test the **requirements**, not the implementation ("Is the reservation expiry behavior
  defined for a closed browser tab?", not "Does the timer work?").
- Reference the spec section or scenario ID in each item, e.g. `[Spec §US2, RELM-N/US2/AS1]`.
- Items are ticked **only by a human reviewer** during the spec review PR. Agents never mark `[x]`.
- An unchecked item at Gate 1 is either resolved in the spec or explicitly accepted by the PO in
  the review thread.
