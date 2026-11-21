#!/usr/bin/env bash
# Relm: turn any repository into a Relm-governed Spec Kit project.
#
#   usage: init-repo.sh <kind> [--agent claude|copilot|...] [--platform <path-to-speckit-platform>]
#     kind = product | backend | frontend | qa
#
# What it does (idempotent; safe to re-run after a platform upgrade):
#   1. checks the pinned Spec Kit CLI version
#   2. specify init --here with the chosen agent integration and the git extension
#   3. installs presets relm-org (priority 20) + relm-<kind> (priority 10)
#   4. installs the github and relm extensions
#   5. seeds .specify/memory/constitution.md from the COMPOSED constitution template
#      (only if the constitution is still an unedited placeholder)
#   6. writes .specify/preset-catalogs.yml / extension-catalogs.yml pointing at the Relm catalog
#
# Afterwards: run /speckit.constitution to fill Part C, write AGENTS.md (see templates/),
# add .github/workflows/sdd.yml (org workflow template "Relm SDD gates").
set -euo pipefail

SPECKIT_VERSION="${SPECKIT_VERSION:-1.4.3}"
KIND="${1:-}"; shift || true
AGENT="claude"
PLATFORM="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --platform) PLATFORM="$(cd "$2" && pwd)"; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
case "$KIND" in product|backend|frontend|qa) ;; *)
  echo "usage: $0 <product|backend|frontend|qa> [--agent claude] [--platform ../speckit-platform]" >&2; exit 2 ;;
esac

command -v specify >/dev/null || {
  echo "Spec Kit CLI not found. Install the pinned version:" >&2
  echo "  uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v${SPECKIT_VERSION}" >&2
  exit 2; }
INSTALLED="$(specify version 2>/dev/null | sed -n 's/.*CLI Version *\([0-9][0-9.]*\).*/\1/p' | head -1)"
if [ "$INSTALLED" != "$SPECKIT_VERSION" ]; then
  echo "warning: specify CLI $INSTALLED installed, Relm pins $SPECKIT_VERSION (see speckit-platform/VERSIONS.md)" >&2
fi

git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "run inside a git repository" >&2; exit 2; }

echo "==> specify init ($AGENT, git extension)"
if [ ! -d .specify ]; then
  specify init --here --force --non-interactive --ignore-agent-tools --integration "$AGENT" --extension git
else
  echo "    .specify/ exists — skipping init"
fi

echo "==> presets: relm-org (20) + relm-$KIND (10)"
for spec in "relm-org:20" "relm-$KIND:10"; do
  id="${spec%%:*}"; prio="${spec##*:}"
  specify preset remove "$id" >/dev/null 2>&1 || true
  specify preset add --dev "$PLATFORM/presets/$id" --priority "$prio"
done

echo "==> extensions: github, relm"
specify extension add github >/dev/null 2>&1 || echo "    github extension already installed"
specify extension remove relm >/dev/null 2>&1 || true
specify extension add --dev "$PLATFORM/extensions/relm"

echo "==> git extension: Relm numbering (number = product feature issue)"
GIT_CFG=.specify/extensions/git/git-config.yml
if [ -f "$GIT_CFG" ]; then
  sed -i.bak 's/^commit_style: .*/commit_style: conventional/' "$GIT_CFG" && rm -f "$GIT_CFG.bak"
fi

echo "==> catalogs"
cat > .specify/preset-catalogs.yml <<'EOF'
# Relm private catalog first (install allowed), public catalogs discovery-only.
catalogs:
  - name: "relm"
    url: "https://raw.githubusercontent.com/spec-kit-relm/speckit-platform/main/catalogs/presets.json"
    priority: 1
    install_allowed: true
    description: "Relm SDD Guild presets (reviewed)"
  - name: "default"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/presets/catalog.json"
    priority: 10
    install_allowed: true
    description: "Spec Kit first-party presets"
  - name: "community"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/presets/catalog.community.json"
    priority: 20
    install_allowed: false
    description: "Community presets — discovery only, vet before use"
EOF
sed -e 's/presets\.json/extensions.json/; s/presets\/catalog/extensions\/catalog/g; s/presets (reviewed)/extensions (reviewed)/; s/first-party presets/first-party extensions/; s/Community presets/Community extensions/' \
  .specify/preset-catalogs.yml > .specify/extension-catalogs.yml

echo "==> constitution"
CONST=.specify/memory/constitution.md
if [ ! -f "$CONST" ] || grep -q '\[PRINCIPLE_1_NAME\]' "$CONST"; then
  bash -c 'source .specify/scripts/bash/common.sh && resolve_template_content constitution-template "$PWD"' > "$CONST"
  echo "    seeded $CONST from the composed Relm template — now run /speckit.constitution to fill Part C"
else
  echo "    $CONST already authored — sync Parts A/B with:"
  echo "    python $PLATFORM/scripts/relm_sdd.py constitution-sync --write"
fi

echo
echo "Done. Next steps:"
echo "  1. /speckit.constitution  — fill Part C (repository amendments) and the version line"
echo "  2. copy $PLATFORM/templates/repo/AGENTS.md (and CLAUDE.md, copilot-instructions.md) and adapt"
echo "  3. add the 'Relm SDD gates' workflow from the org workflow templates"
echo "  4. python $PLATFORM/scripts/relm_sdd.py agent-files-check && python $PLATFORM/scripts/relm_sdd.py constitution-check --governance $PLATFORM/governance"
