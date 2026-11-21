"""Unit tests for scripts/relm_sdd.py (run: python -m unittest discover -s tests -v)."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import relm_sdd  # noqa: E402

GOV = ROOT / "governance"


def run(*argv, env=None):
    relm_sdd.failures.clear()
    relm_sdd.warnings.clear()
    old = dict(os.environ)
    os.environ.pop("GITHUB_ACTIONS", None)
    os.environ.update(env or {})
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = relm_sdd.main(list(argv))
    finally:
        os.environ.clear()
        os.environ.update(old)
    return code, out.getvalue()


def constitution(team="BACKEND", org_body=None):
    org = (GOV / "org-baseline.md").read_text()
    if org_body:
        org = org.replace("### ORG-1 Spec before code", org_body)
    overlay = (GOV / "overlays" / f"{team.lower()}.md").read_text()
    return (f"# demo Constitution\n\n{org}\n{overlay}\n## Part C — Repository Amendments (MUST)\n"
            "### DEMO-1 Thing\nDo it.\n*Check: CI*\n\n**Version**: 1.0.0\n")


SPEC = """# Feature Specification: Demo

**Feature Branch**: `001-demo`
**Status**: {status}

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Do the thing (Priority: P1)

1. **Given** a user, **When** they act, **Then** it works.

### Edge Cases
- none {marker}

## Requirements *(mandatory)*
- FR-001

## Success Criteria *(mandatory)*
- SC-001

## Relm Traceability *(mandatory — ORG-1, PRD-1, QA-2)*

**Feature ID**: RELM-{fid}
**Central spec**: n/a — repository-local feature
"""


class ConstitutionTests(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "constitution.md"
            p.write_text(text)
            return run("constitution-check", "--constitution", str(p), "--governance", str(GOV))

    def test_current_constitution_passes(self):
        code, out = self.check(constitution())
        self.assertEqual(code, 0, out)

    def test_local_edit_of_part_a_fails(self):
        code, out = self.check(constitution(org_body="### ORG-1 Spec before code (relaxed)"))
        self.assertEqual(code, 1)
        self.assertIn("edited locally", out)

    def test_missing_team_block_fails(self):
        org = (GOV / "org-baseline.md").read_text()
        code, out = self.check(f"# x\n{org}\n## Part C\n")
        self.assertEqual(code, 1)
        self.assertIn("TEAM-*", out)

    def test_sync_restores_edited_block(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "constitution.md"
            p.write_text(constitution(org_body="### ORG-1 tampered"))
            run("constitution-sync", "--constitution", str(p), "--governance", str(GOV), "--write")
            code, out = run("constitution-check", "--constitution", str(p), "--governance", str(GOV))
            self.assertEqual(code, 0, out)


class SpecLintTests(unittest.TestCase):
    def lint(self, status="Draft", marker="", fid="1", dirname="001-demo"):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "specs" / dirname
            f.mkdir(parents=True)
            (f / "spec.md").write_text(SPEC.format(status=status, marker=marker, fid=fid))
            return run("spec-lint", "--root", d)

    def test_valid_spec_passes(self):
        self.assertEqual(self.lint()[0], 0)

    def test_feature_id_must_match_directory(self):
        code, out = self.lint(fid="2")
        self.assertEqual(code, 1)
        self.assertIn("does not match", out)

    def test_clarification_markers_block_approval(self):
        self.assertEqual(self.lint(marker="[NEEDS CLARIFICATION: x]")[0], 0)  # draft is fine
        code, out = self.lint(status="Approved", marker="[NEEDS CLARIFICATION: x]")
        self.assertEqual(code, 1)


class PrCheckTests(unittest.TestCase):
    def pr(self, body, labels=()):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "specs" / "001-demo").mkdir(parents=True)
            return run("pr-check", "--root", d, "--require-spec",
                       env={"PR_BODY": body, "PR_LABELS": json.dumps(list(labels))})

    def test_no_feature_no_lane_fails(self):
        self.assertEqual(self.pr("just some change")[0], 1)

    def test_feature_with_evidence_passes(self):
        body = "Feature: RELM-1\n- /speckit.analyze: 0 CRITICAL\n- /speckit.converge: Converged\n"
        code, out = self.pr(body, ["lane:feature"])
        self.assertEqual(code, 0, out)

    def test_template_comments_are_not_evidence(self):
        body = ("Feature: RELM-1\n- /speckit.analyze: <!-- e.g. \"0 CRITICAL\" -->\n"
                "- /speckit.converge: <!-- \"Converged\" -->\n")
        self.assertEqual(self.pr(body)[0], 1)

    def test_missing_local_spec_fails(self):
        body = "Feature: RELM-7\n/speckit.analyze: 0 CRITICAL\n/speckit.converge: Converged"
        code, out = self.pr(body)
        self.assertIn("specs/007-*", out)
        self.assertEqual(code, 1)

    def test_chore_lane_passes(self):
        self.assertEqual(self.pr("bump deps", ["lane:chore"])[0], 0)


class BuildTests(unittest.TestCase):
    def test_generated_files_are_current(self):
        code, out = run("build", "--check")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
