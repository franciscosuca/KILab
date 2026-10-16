"""Structural/validator tests, not an evaluation of LLM skill behavior."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PACK = Path(__file__).resolve().parents[1]
COLLECTION = PACK / "catalog/core/skills/feature-planning"
SCRIPT = COLLECTION / "plan-spec/scripts/validate_plan.py"
SPEC = importlib.util.spec_from_file_location("validate_plan", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
SLUG = "plan-XXXX-config-validation"
COMMIT = "https://github.com/example/service/commit/" + "a" * 40


def make_tldr(scope="Validate configuration.", delivered="None yet.", command=None, diagram=""):
    command = command or "/plan-create " + SLUG
    text = ("**Scope:** " + scope + "\n\n**Status:** Draft; approval pending.\n\n"
            "**Delivered:** " + delivered + "\n\n**Next:** `" + command + "` — after the named gate.\n")
    if diagram:
        text += "\n**Diagram:**\n\n" + diagram + "\n"
    return text


def make_plan(tldr=None, metadata=None, command=None):
    command = command or "/plan-create " + SLUG
    values = dict(schema_version=2, id=None, title="Validate configuration", status="draft", owner="Owner",
                  created="2026-01-01", updated="2026-01-01", sources=[], repositories=[], branches=[],
                  pull_requests=[], depends_on=[], blocked_by=[], scope_revision=1, approved_revision=None,
                  approved_by=None, approved_at=None)
    values.update(metadata or {})
    header = "---\n" + "".join(key + ": " + json.dumps(value) + "\n" for key, value in values.items()) + "---\n"
    return (header + "# Validate configuration\n\n## tldr-version\n\n" + (tldr or make_tldr(command=command))
            + "\n## agent-version\n\n### Resume\n- Active writer: none.\n- Next: " + command
            + " — after the named gate.\n\n### Scope\nApproved boundary and non-goals.\n"
            "\n### Implementation\n1. Inspect the owning code and test before changes.\n"
            "\n### Verification\nWorking directory and checks still require investigation.\n"
            "\n### History\n- 2026-01-01 /plan-create " + SLUG + ": captured.\n")


def approved(status="next", **overrides):
    values = dict(status=status, approved_revision=1, approved_by="Owner", approved_at="2026-01-01")
    values.update(overrides)
    return values


def create_root(root, text=None, folder="drafts"):
    for name in validator.LIFECYCLES:
        (root / name).mkdir(parents=True, exist_ok=True)
    bundle = root / folder / SLUG
    (bundle / "artifacts").mkdir(parents=True)
    (bundle / "artifacts/request.md").write_text("Sanitized test input.\n", encoding="utf-8")
    (bundle / "plan.md").write_text(text or make_plan(), encoding="utf-8")
    entries = {name: "" for name in validator.INDEX_SECTIONS.values()}
    entries[validator.INDEX_SECTIONS[folder]] = "[Test](" + folder + "/" + SLUG + "/plan.md)\n"
    (root / "README.md").write_text("# Task Plans\n\nPlan prefix: plan\n\n" + "".join(
        "## " + name + "\n" + value + "\n" for name, value in entries.items()), encoding="utf-8")
    return bundle


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class PlanFormatTests(unittest.TestCase):
    def errors(self, text=None, **kwargs):
        return validator.validate_text(text or make_plan(), SLUG, **kwargs)[1]

    def test_valid_draft_and_actual_documented_example(self):
        self.assertEqual(self.errors(lifecycle="drafts"), [])
        example = re.search(r"```markdown\n(---\n.*?)\n```", (COLLECTION / "EXAMPLES.md").read_text(), re.S)
        self.assertIsNotNone(example)
        self.assertEqual(self.errors(example.group(1), lifecycle="drafts"), [])

    def test_template_becomes_valid_after_user_values_are_substituted(self):
        text = (COLLECTION / "plan-spec/templates/plan.md").read_text()
        text = text.replace("<YYYY-MM-DD>", "2026-01-01").replace("<plan-slug>", SLUG)
        self.assertEqual(self.errors(text, lifecycle="drafts"), [])
        self.assertTrue(self.errors(text, ready=True))

    def test_299_words_pass_300_fail(self):
        base = make_tldr()
        padding = 299 - validator.tldr_word_count(base)
        text = make_tldr(scope="Validate configuration." + " word" * padding)
        self.assertEqual(validator.tldr_word_count(text), 299)
        self.assertEqual(self.errors(make_plan(tldr=text)), [])
        self.assertTrue(any("300 words" in e for e in self.errors(make_plan(tldr=text + " word"))))

    def test_only_mermaid_blocks_are_excluded_from_count(self):
        diagram = "```mermaid\nflowchart LR\n" + "A --> B\n" * 400 + "```"
        text = make_tldr(diagram=diagram)
        self.assertLess(validator.tldr_word_count(text), 100)
        self.assertEqual(self.errors(make_plan(tldr=text)), [])
        self.assertGreater(validator.tldr_word_count("```text\n" + "word " * 400 + "\n```"), 300)
        self.assertEqual(validator.tldr_word_count("[two words](https://example.com/long-url)"), 2)

    def test_tilde_and_long_fences_and_hidden_heading(self):
        for fence in ("~~~", "````"):
            text = make_tldr(diagram=fence + "mermaid\n## agent-version\n" + fence)
            self.assertEqual(self.errors(make_plan(tldr=text)), [])

    def test_agent_details_have_no_word_cap(self):
        text = make_plan().replace("Approved boundary and non-goals.", "detail " * 2000)
        self.assertEqual(self.errors(text), [])

    def test_exact_fields_order_no_extra_sections_and_optional_diagram(self):
        for text in (make_tldr().replace("**Scope:**", "**Summary:**"),
                     make_tldr() + "\n**Evidence:** not a TL;DR field.\n",
                     make_tldr() + "\n### Steps\nDo something.\n",
                     "Unexpected introduction.\n" + make_tldr(),
                     make_tldr(diagram="```text\nnot a diagram\n```")):
            with self.subTest(text=text[:60]):
                self.assertTrue(self.errors(make_plan(tldr=text)))

    def test_each_delivered_claim_needs_commit_link_or_explicit_fallback(self):
        valid = "\n- API validation — [aaaaaaa](" + COMMIT + ").\n- Tests — [aaaaaaa](" + COMMIT + ")."
        self.assertEqual(self.errors(make_plan(tldr=make_tldr(delivered=valid))), [])
        for value in (valid + "\n- Documentation without a link.",
                      "\n- API — [PR](https://github.com/example/service/pull/1).",
                      "Delivered something without a bullet."):
            self.assertTrue(any("claim" in e or "bullet" in e for e in self.errors(make_plan(tldr=make_tldr(delivered=value)))))
        for marker in ("uncommitted", "commit unavailable"):
            self.assertEqual(self.errors(make_plan(tldr=make_tldr(delivered="\n- Verified local work — " + marker))), [])

    def test_delivered_paragraph_cannot_hide_an_unlinked_statement(self):
        delivered = "\n- First delivery — [aaaaaaa](" + COMMIT + ").\nAnother delivery without its own link."
        self.assertTrue(any("own bullet" in e for e in self.errors(make_plan(tldr=make_tldr(delivered=delivered)))))

    def test_commit_url_cannot_be_a_credential_url_or_malformed(self):
        self.assertFalse(validator.is_commit_url("https://user:secret@example.com/commit/" + "a" * 40))
        self.assertFalse(validator.is_commit_url("https://[broken/commit/" + "a" * 40))
        self.assertTrue(validator.is_commit_url(COMMIT))

    def test_missing_bad_frontmatter_unknown_schema_and_duplicate_keys(self):
        for text in ("# Missing frontmatter", make_plan().replace("schema_version: 2", "schema_version: 1"),
                     make_plan().replace('owner: "Owner"', "owner: Owner"),
                     make_plan().replace("id: null", "id: null\nid: null"),
                     make_plan().replace("repositories: []", "repositories: null"),
                     make_plan().replace('updated: "2026-01-01"', 'updated: "yesterday"')):
            self.assertTrue(self.errors(text))

    def test_exact_date_format_and_title_are_required(self):
        for text in (make_plan(metadata={"created": "20260101"}),
                     make_plan().replace("# Validate configuration\n", ""),
                     make_plan().replace("# Validate configuration\n", "# One title\n# Another title\n")):
            self.assertTrue(self.errors(text))

    def test_wrong_status_types_are_errors_not_exceptions(self):
        for status in ([], {}, False, "drafts"):
            self.assertTrue(self.errors(make_plan(metadata={"status": status})))
        self.assertTrue(self.errors(make_plan(), lifecycle="open"))

    def test_readiness_requires_current_approval_no_blockers_and_nonterminal_state(self):
        self.assertEqual(self.errors(make_plan(metadata=approved()), lifecycle="next", ready=True), [])
        for metadata in (approved(approved_revision=None), approved(scope_revision=2),
                         approved(blocked_by=["Owner approval pending"]), approved(approved_by=None),
                         approved(status="done"), approved(scope_revision=True)):
            self.assertTrue(self.errors(make_plan(metadata=metadata), ready=True))

    def test_revised_open_plan_valid_but_not_execution_ready(self):
        text = make_plan(metadata=approved(status="open", scope_revision=2, blocked_by=["Owner: revision 2 approval"]))
        self.assertEqual(self.errors(text, lifecycle="open"), [])
        self.assertTrue(self.errors(text, ready=True))
        self.assertTrue(self.errors(make_plan(metadata=approved(status="open", scope_revision=2))))

    def test_next_command_required_resolved_and_aligned(self):
        for text in (make_plan(tldr=make_tldr().replace("`/plan-create " + SLUG + "`", "Await approval")),
                     make_plan(tldr=make_tldr(command="/plan-status " + SLUG)),
                     make_plan(tldr=make_tldr(command="/plan-execute unknown-plan")),
                     make_plan(command="/plan-sync " + SLUG, tldr=make_tldr())):
            self.assertTrue(any("Next" in e for e in self.errors(text)))

    def test_completed_retro_new_request_placeholder_is_explicit(self):
        command = "/plan-create <new-request>"
        tldr = make_tldr(command=command).replace("after the named gate.", "only for another task; new-request is a placeholder.")
        self.assertEqual(self.errors(make_plan(tldr=tldr, command=command)), [])
        self.assertTrue(self.errors(make_plan(command=command)))

    def test_unclosed_fence_is_rejected(self):
        self.assertTrue(self.errors(make_plan() + "\n```mermaid\nflowchart LR"))


class PlanRootTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = create_root(self.root)

    def test_root_gate_before_inventory(self):
        for value in (None, "", "relative/PLANNING"):
            with mock.patch.object(Path, "iterdir", side_effect=AssertionError("must not scan")):
                with self.assertRaises(validator.PlanError):
                    validator.validate_root(value)

    def test_root_layout_and_path_selection_fail_closed(self):
        for selector in ("../other", "/tmp/other", SLUG + " wp-1"):
            with self.assertRaises(validator.PlanError):
                validator.validate_root(str(self.root), selector)
        (self.root / "next").rmdir()
        with self.assertRaises(validator.PlanError):
            validator.validate_root(str(self.root))

    def test_valid_root_and_cli_are_read_only(self):
        before = snapshot(self.root)
        errors, count, legacy = validator.validate_root(str(self.root), SLUG)
        self.assertEqual((errors, count, legacy), ([], 1, 0))
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "--plan", SLUG],
                                capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_empty_explicit_root_never_falls_back_to_environment(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", ""], capture_output=True, text=True,
                                env={**os.environ, "PLAN_ROOT": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 2)

    def test_extra_bundle_files_and_missing_request_are_rejected(self):
        (self.bundle / "work-packages").mkdir()
        self.assertTrue(any("top level" in e for e in validator.validate_root(str(self.root))[0]))
        (self.bundle / "work-packages").rmdir()
        (self.bundle / "artifacts/request.md").unlink()
        self.assertTrue(any("request.md" in e for e in validator.validate_root(str(self.root))[0]))

    def test_duplicate_slug_index_and_wrong_index_section(self):
        other = self.root / "open" / SLUG
        (other / "artifacts").mkdir(parents=True)
        (other / "artifacts/request.md").write_text("Input")
        (other / "plan.md").write_text(make_plan(metadata=approved(status="open")))
        self.assertTrue(any("duplicate" in e for e in validator.validate_root(str(self.root))[0]))
        index = self.root / "README.md"
        index.write_text(index.read_text().replace("## Drafts", "## Unclassified Legacy Plans"))
        self.assertTrue(any("lifecycle section" in e for e in validator.validate_root(str(self.root))[0]))
        index.write_text(index.read_text() + "\n[Duplicate](drafts/" + SLUG + "/plan.md)\n")
        self.assertTrue(any("exactly once" in e for e in validator.validate_root(str(self.root))[0]))

    def test_broken_markdown_reference_and_wiki_links(self):
        request = self.bundle / "artifacts/request.md"
        for link in ("[missing](missing.md)", "[reference]: missing.md", "[[missing|label]]"):
            request.write_text(link)
            self.assertTrue(any("broken local link" in e for e in validator.validate_root(str(self.root))[0]))
        request.write_text("[[../plan|plan]]\n[original](../plan.md)\n[ref]: ../plan.md\n")
        self.assertEqual(validator.validate_root(str(self.root))[0], [])

    def test_live_incoming_links_are_checked_but_historical_code_is_preserved(self):
        legacy = self.root / "drafts/legacy.md"
        path = "../done/" + SLUG + "/plan.md"
        legacy.write_text("Historical `[old](" + path + ")`\n```text\n[old](" + path + ")\n```\n")
        self.assertEqual(validator.validate_root(str(self.root))[0], [])
        legacy.write_text("[Live stale reference](" + path + ")\n")
        self.assertTrue(any("stale live lifecycle" in e for e in validator.validate_root(str(self.root))[0]))

    def test_existing_legacy_collision_does_not_hide_stale_links(self):
        legacy = self.root / "done" / SLUG
        legacy.mkdir()
        (legacy / "plan.md").write_text("Historical legacy content, not migrated.")
        (self.root / "drafts/reference.md").write_text("[Old](../done/" + SLUG + "/plan.md)")
        errors = validator.validate_root(str(self.root), SLUG)[0]
        self.assertTrue(any("legacy collisions" in e for e in errors))
        self.assertTrue(any("stale live lifecycle" in e for e in errors))

    def test_complete_bundle_move_is_valid_only_after_index_and_live_link_repairs(self):
        request_before = (self.bundle / "artifacts/request.md").read_bytes()
        incoming = self.root / "drafts/reference.md"
        old = "drafts/" + SLUG + "/plan.md"
        incoming.write_text("[Live](../" + old + ")\nHistorical `" + old + "`\n")
        moved = self.root / "done" / SLUG
        self.bundle.rename(moved)
        (moved / "plan.md").write_text(make_plan(metadata=approved(status="done")))
        self.assertTrue(validator.validate_root(str(self.root))[0])
        index = self.root / "README.md"
        text = index.read_text().replace("[Test](" + old + ")", "")
        text = text.replace("## Recently Done\n", "## Recently Done\n[Test](done/" + SLUG + "/plan.md)\n")
        index.write_text(text)
        incoming.write_text(incoming.read_text().replace("(../" + old + ")", "(../done/" + SLUG + "/plan.md)"))
        self.assertEqual(validator.validate_root(str(self.root))[0], [])
        self.assertIn("Historical `" + old + "`", incoming.read_text())
        self.assertEqual((moved / "artifacts/request.md").read_bytes(), request_before)

    def test_legacy_is_read_only_and_not_executable(self):
        (self.bundle / "plan.md").write_text(make_plan().replace("schema_version: 2", "schema_version: 1"))
        before = snapshot(self.root)
        errors, count, legacy = validator.validate_root(str(self.root), SLUG, ready=True)
        self.assertEqual((count, legacy), (0, 1))
        self.assertTrue(any("explicit migration" in e for e in errors))
        self.assertEqual(snapshot(self.root), before)

    def test_symlink_bundle_is_not_followed(self):
        (self.root / "open" / "linked").symlink_to(self.bundle, target_is_directory=True)
        self.assertTrue(any("symlink" in e for e in validator.validate_root(str(self.root))[0]))


class CollectionInstructionTests(unittest.TestCase):
    def test_exact_active_skill_set_and_internal_controls(self):
        names = {p.parent.name for p in COLLECTION.glob("*/SKILL.md")}
        self.assertEqual(names, {"plan-create", "plan-execute", "plan-sync", "plan-retro", "plan-spec", "plan-status"})
        self.assertFalse((COLLECTION / "SKILL.md").exists())
        for name in names:
            source = (COLLECTION / name / "SKILL.md").read_text()
            self.assertIn("name: " + name + "\n", source)
            self.assertIn("description:", source)
            if name != "plan-spec":
                self.assertIn("../plan-spec/SKILL.md", source)
                self.assertIn("Next:", source)
                for result in ("failed", "blocked", "unchanged", "checkpoint", "handoff"):
                    self.assertIn(result, source)
        contract = (COLLECTION / "plan-spec/SKILL.md").read_text()
        self.assertIn("user-invocable: false", contract)
        self.assertIn("disable-model-invocation: true", contract)

    def test_main_quick_start_and_diagrams_only_primary_commands(self):
        readme = (COLLECTION / "README.md").read_text()
        quick = readme.split("## Quick Start", 1)[1].split("## Lifecycle", 1)[0]
        self.assertEqual(set(re.findall(r"/plan-[a-z-]+", quick)), validator.PRIMARY)
        for diagram in re.findall(r"```mermaid\n(.*?)\n```", readme, re.S):
            self.assertEqual(set(re.findall(r"/plan-[a-z-]+", diagram)), validator.PRIMARY)
        self.assertNotIn("/plan-status", quick)
        self.assertNotIn("/plan-spec", quick)

    def test_behavioral_checks_are_explicitly_not_automated_claims(self):
        checklist = (COLLECTION / "ACCEPTANCE.md").read_text()
        self.assertIn("operator-run agent scenarios", checklist)
        self.assertIn("Unrun scenarios remain unverified", checklist)
        for safeguard in ("Owner-reported", "raw `git remote -v`", "Local closure", "exact Owner exceptions"):
            self.assertIn(safeguard, (COLLECTION / "plan-spec/SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
