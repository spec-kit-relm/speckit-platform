#!/usr/bin/env bash
# Protect `main` in every spec-kit-relm repository with a ruleset (run by an org owner with `gh`).
#
#   - changes reach main only through pull requests, approved by a CODEOWNER
#   - the SDD gates (and contract / build checks) must be green before merging
#   - no force-pushes, no branch deletion
#   - org admins may bypass (needed while one person owns everything; remove later)
#
# Run AFTER finish-setup.sh: the `sdd / sdd-gates` check only passes once speckit-platform@v1 exists.
# Idempotent: an existing "relm-protect-main" ruleset is updated in place.
set -euo pipefail
ORG="${ORG:-spec-kit-relm}"
APPROVALS="${APPROVALS:-1}"

# repo -> required status checks (check names exactly as GitHub shows them on a PR)
declare -A CHECKS=(
  [product-specs]="sdd / sdd-gates"
  [inventory-service]="sdd / sdd-gates,contracts / contract-check,test"
  [orders-service]="sdd / sdd-gates,contracts / contract-check,test"
  [web-storefront]="sdd / sdd-gates,contracts / contract-check,test"
  [e2e-tests]="sdd / sdd-gates,contracts / contract-check,static"
  [speckit-platform]="generated-files"
  [sdd-handbook]=""
  [.github]=""
)

for repo in "${!CHECKS[@]}"; do
  checks_json=$(python3 -c 'import json,sys; c=[x for x in sys.argv[1].split(",") if x]; print(json.dumps([{"context": x} for x in c]))' "${CHECKS[$repo]}")
  body=$(python3 - "$checks_json" "$APPROVALS" <<'PY'
import json, sys
checks, approvals = json.loads(sys.argv[1]), int(sys.argv[2])
rules = [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
        "required_approving_review_count": approvals,
        "require_code_owner_review": True,
        "dismiss_stale_reviews_on_push": True,
        "require_last_push_approval": False,
        "required_review_thread_resolution": True}},
]
if checks:
    rules.append({"type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": False,
        "required_status_checks": checks}})
print(json.dumps({
    "name": "relm-protect-main",
    "target": "branch",
    "enforcement": "active",
    "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
    "bypass_actors": [{"actor_id": 1, "actor_type": "OrganizationAdmin", "bypass_mode": "always"}],
    "rules": rules,
}))
PY
)
  existing=$(gh api "repos/$ORG/$repo/rulesets" --jq '.[] | select(.name=="relm-protect-main") | .id' 2>/dev/null || true)
  if [ -n "$existing" ]; then
    gh api -X PUT "repos/$ORG/$repo/rulesets/$existing" --input - <<<"$body" >/dev/null
    echo "  updated  $repo  [${CHECKS[$repo]:-no required checks}]"
  else
    gh api -X POST "repos/$ORG/$repo/rulesets" --input - <<<"$body" >/dev/null
    echo "  created  $repo  [${CHECKS[$repo]:-no required checks}]"
  fi
done
echo "Done. See Settings → Rules → Rulesets in each repository."
