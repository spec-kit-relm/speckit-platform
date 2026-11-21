# `relm` Spec Kit extension

Adds three commands that fill the multi-repository gap in Spec Kit (Spec Kit projects are
directory-scoped and have no built-in cross-repo linking):

| Command | Where | What it does |
|---------|-------|--------------|
| `/speckit.relm.impact` | `product-specs` | Builds `impact.md` (repos, roles, interface owners, rollout/rollback order) and a draft `contracts.lock.md` for the active product feature. |
| `/speckit.relm.handoff RELM-<n>` | service / FE / QA repos | Reads this repo's slice from `../product-specs` and prints a handoff brief plus the exact `/speckit.specify` command to run. |
| `/speckit.relm.pr` | any repo | Collects gate evidence (analyze, converge, tests, scenario IDs, contract versions) into the PR template. Offered automatically after `/speckit.implement`. |

Install (normally via `bootstrap/init-repo.sh`), from a checkout of speckit-platform at the pinned tag:

```bash
specify extension add --dev ../speckit-platform/extensions/relm
```
