# AGENTS.md — <repository name>

<!--
  Template for Relm repositories. AGENTS.md = HOW to work here (commands, layout, conventions).
  The constitution = WHAT MUST be true. Never duplicate constitution rules here; reference them.
  `sdd-gates / agent-files-check` requires the "Commands" and "Spec Kit in this repository" sections.
-->

<One paragraph: what this repository is, which team owns it, which interfaces it provides/consumes.>

## Commands
| Purpose | Command |
|---------|---------|
| Install deps | `<cmd>` |
| Build | `<cmd>` |
| Unit tests | `<cmd>` |
| Integration tests | `<cmd>` |
| Contract tests | `<cmd>` |
| Lint / format | `<cmd>` |
| Run locally | `<cmd>` |

Run the unit tests and the linter before marking any task `[X]`.

## Layout
```text
<tree of the important directories, with one-line purpose each>
```

## Spec Kit in this repository
- Kind: `<product | backend | frontend | qa>` — presets `relm-org` + `relm-<kind>` are installed.
- Feature numbers are product feature issue numbers: `/speckit.specify RELM-<n> ...` →
  `specs/<NNN>-<short-name>/`, branch `<NNN>-<short-name>`.
- Start a cross-repo slice with `/speckit.relm.handoff RELM-<n>` (needs `../product-specs`).
- Implement one phase per `/speckit.implement` run; finish with `/speckit.converge` and `/speckit.relm.pr`.

## Conventions
- <naming, error handling, logging, testing conventions that are specific to this repo>

## Do not
- Edit `contracts/vendor/**`, generated code, or Parts A/B of the constitution.
- Add dependencies without checking the constitution (ORG-8).
- <repo-specific don'ts>

## Gotchas
- <things that regularly trip up humans and agents in this repository>
