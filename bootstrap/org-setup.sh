#!/usr/bin/env bash
# One-time GitHub setup for the spec-kit-relm organization (run by an org owner with `gh`).
# Creates the teams referenced by CODEOWNERS, the lane/phase labels in every repo, and the
# "Product Delivery" project used to track features across repositories. Idempotent.
set -euo pipefail
ORG="${ORG:-spec-kit-relm}"
REPOS=(product-specs orders-service inventory-service web-storefront e2e-tests speckit-platform sdd-handbook .github)

echo "==> teams"
for t in architecture backend frontend qa sdd-guild; do
  gh api "orgs/$ORG/teams" -f name="$t" -f privacy=closed >/dev/null 2>&1 && echo "  created $t" || echo "  $t exists"
done
grant() { gh api -X PUT "orgs/$ORG/teams/$1/repos/$ORG/$2" -f permission="$3" >/dev/null && echo "  $1 -> $2 ($3)"; }
grant architecture product-specs maintain; grant qa product-specs push
grant backend orders-service maintain;     grant backend inventory-service maintain
grant frontend web-storefront maintain;    grant qa e2e-tests maintain
for r in "${REPOS[@]}"; do grant sdd-guild "$r" maintain; done
for r in product-specs orders-service inventory-service web-storefront e2e-tests; do
  for t in architecture backend frontend qa; do gh api -X PUT "orgs/$ORG/teams/$t/repos/$ORG/$r" -f permission=push >/dev/null 2>&1 || true; done
done

echo "==> labels"
label() { gh label create "$2" --repo "$ORG/$1" --color "$3" --description "$4" --force >/dev/null; }
for r in "${REPOS[@]}"; do
  label "$r" lane:feature    0E8A16 "Spec Kit feature work (Feature: RELM-<n>)"
  label "$r" lane:bugfix     D93F0B "Bugfix lane: reproduce with a test, no full SDD flow"
  label "$r" lane:chore      C5DEF5 "No behavior change (deps, refactor, docs)"
  label "$r" lane:governance 5319E7 "Constitution / governance sync"
  label "$r" feature         1D76DB "Product feature (parent issue)"
  label "$r" task            BFDADC "Task generated from tasks.md"
  label "$r" contract-change FBCA04 "Changes an owned contract"
  echo "  labels in $r"
done

echo "==> project"
# Idempotent: creates the project if missing, then any missing field. Note that "Repository",
# "Title", "Status", "Assignees", "Labels", "Milestone" … are built-in (reserved) field names.
num=$(gh project list --owner "$ORG" --format json --jq '.projects[] | select(.title=="Product Delivery") | .number' | head -1)
if [ -z "$num" ]; then
  num=$(gh project create --owner "$ORG" --title "Product Delivery" --format json --jq '.number')
  echo "  created project #$num"
else
  echo "  project #$num exists"
fi
fields=$(gh project field-list "$num" --owner "$ORG" --format json --jq '.fields[].name')
field() { # name type [options]
  if grep -qx "$1" <<<"$fields"; then echo "  field '$1' exists"; return; fi
  if [ -n "${3:-}" ]; then
    gh project field-create "$num" --owner "$ORG" --name "$1" --data-type "$2" --single-select-options "$3" >/dev/null
  else
    gh project field-create "$num" --owner "$ORG" --name "$1" --data-type "$2" >/dev/null
  fi
  echo "  created field '$1'"
}
field "Feature ID" TEXT
field "Target repo" SINGLE_SELECT "product-specs,orders-service,inventory-service,web-storefront,e2e-tests"
field "Phase" SINGLE_SELECT "Spec,Contract,Plan,Build,Verify,Released"
field "Contract version" TEXT
echo "Done. Next: bash speckit-platform/bootstrap/protect-branches.sh  (after finish-setup.sh)"
