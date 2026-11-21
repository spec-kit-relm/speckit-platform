# governance/ — the canonical Relm constitution text

| File | Block | Part | Owner |
|------|-------|------|-------|
| `org-baseline.md` | `RELM:ORG-BASELINE` | A — organization baseline (ORG-1 … ORG-9) | SDD Guild |
| `overlays/backend.md` | `RELM:TEAM-BACKEND` | B — backend overlay (BE-1 … BE-6) | `@spec-kit-relm/backend` |
| `overlays/frontend.md` | `RELM:TEAM-FRONTEND` | B — frontend overlay (FE-1 … FE-6) | `@spec-kit-relm/frontend` |
| `overlays/qa.md` | `RELM:TEAM-QA` | B — quality engineering overlay (QA-1 … QA-6) | `@spec-kit-relm/qa` |
| `overlays/product.md` | `RELM:TEAM-PRODUCT` | B — product & architecture overlay (PRD-1 … PRD-6) | `@spec-kit-relm/architecture` |
| `history/<BLOCK>/<version>.md` | — | immutable snapshot of every released version (generated) | — |
| `versions.json` | — | current version of every block (generated) | — |
| `consumers.json` | — | repositories that receive sync PRs and their kind | SDD Guild |

## Block format

```markdown
<!-- BEGIN RELM:<NAME> v<MAJOR.MINOR.PATCH> | source: … | DO NOT EDIT OUTSIDE speckit-platform -->
…rules…
<!-- END RELM:<NAME> -->
```

The markers are what the drift check (`relm_sdd.py constitution-check`) and the sync
(`relm_sdd.py constitution-sync`) look for. A repository's copy must be byte-identical to the
snapshot of the version it declares.

## Writing rules (read before you propose an amendment)

1. **Few and testable.** 5–10 MUST rules per layer. Every rule ends with `*Check: …*` naming the CI
   job, analyzer, or review step that enforces it. A rule without a check belongs in a handbook
   standard or `AGENTS.md`, not here.
2. **Lower layers only add or tighten.** Team overlays never relax Part A; repository amendments
   never relax Parts A/B. Exceptions go in Part C → *Exceptions* with an ADR and expiry date.
3. **No technology in Part A.** Stack choices live in Part C of the repo that makes them.
4. **Versioning.** MAJOR: a principle removed or redefined. MINOR: a principle added or materially
   expanded. PATCH: wording/clarification. Bump the version inside the BEGIN marker.
5. **Run `python scripts/relm_sdd.py build`** after every change and commit the generated files.
