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
if ! gh project list --owner "$ORG" --format json | grep -q '"Product Delivery"'; then
  num=$(gh project create --owner "$ORG" --title "Product Delivery" --format json | python3 -c 'import json,sys;print(json.load(sys.stdin)["number"])')
  gh project field-create "$num" --owner "$ORG" --name "Feature ID" --data-type TEXT
  gh project field-create "$num" --owner "$ORG" --name "Repository" --data-type SINGLE_SELECT \
    --single-select-options "product-specs,orders-service,inventory-service,web-storefront,e2e-tests"
  gh project field-create "$num" --owner "$ORG" --name "Phase" --data-type SINGLE_SELECT \
    --single-select-options "Spec,Contract,Plan,Build,Verify,Released"
  gh project field-create "$num" --owner "$ORG" --name "Contract version" --data-type TEXT
  echo "  created project #$num"
else
  echo "  project exists"
fi
echo "Done. Next: protect main in each repo and require 'sdd / sdd-gates' (+ 'contracts / contract-check')."
