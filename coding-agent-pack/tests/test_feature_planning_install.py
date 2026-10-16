"""Real installer smoke tests in isolated temporary projects/HOME, no host changes."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_feature_planning import PACK, SLUG, create_root, snapshot, validator


INSTALLER = PACK / "scripts/install-pack.sh"
STAGES = ("plan-create", "plan-execute", "plan-sync", "plan-retro", "plan-status")
RETIRED = ("plan-init", "plan-add", "plan-write", "plan-dispatch", "task-planning")
GUIDES = ("README.md", "EXAMPLES.md", "MIGRATION.md", "ACCEPTANCE.md")


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="planning install ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project with spaces"
        self.home = self.base / "isolated home"
        self.project.mkdir()
        self.home.mkdir()
        self.env = {**os.environ, "HOME": str(self.home), "PI_CODING_AGENT_DIR": str(self.home / "pi-config"),
                    "PYTHONDONTWRITEBYTECODE": "1"}
        self.env.pop("PLAN_ROOT", None)

    def install(self, harness, scope="project", dry_run=False, skills="feature-planning"):
        command = ["bash", str(INSTALLER), "--harness", harness, "--scope", scope,
                   "--target", str(self.project), "--agents", "none", "--skills", skills]
        if harness == "pi":
            command += ["--extensions", "none", "--models", "none"]
        if dry_run:
            command.append("--dry-run")
        result = subprocess.run(command, capture_output=True, text=True, env=self.env, timeout=40)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result

    def destination(self, harness, scope="project"):
        if scope == "global":
            return self.home / (".claude" if harness == "claude" else "pi-config")
        return self.project / {"copilot": ".github", "claude": ".claude", "pi": ".pi"}[harness]

    def check_installation(self, harness, scope="project"):
        dest = self.destination(harness, scope)
        guides = dest / "skills/feature-planning"
        contract = guides / "plan-spec" if harness == "copilot" else dest / "skills/plan-spec"
        for guide in GUIDES:
            self.assertTrue((guides / guide).is_file(), str(guides / guide))
        self.assertTrue((contract / "SKILL.md").is_file())
        self.assertTrue((contract / "templates/plan.md").is_file())
        installed_validator = contract / "scripts/validate_plan.py"
        self.assertTrue(installed_validator.is_file())
        self.assertIn("disable-model-invocation: true", (contract / "SKILL.md").read_text())
        if harness == "claude":
            self.assertIn("user-invocable: false", (contract / "SKILL.md").read_text())
            self.assertFalse((dest / "commands/plan-spec.md").exists())
        for name in STAGES:
            source = ((guides / name / "SKILL.md") if harness == "copilot" else
                      (dest / "commands" / (name + ".md")) if harness == "claude" else
                      (dest / "skills" / name / "SKILL.md"))
            self.assertTrue(source.is_file(), str(source))
            links = list(validator.local_links(source.read_text(), source))
            self.assertIn((contract / "SKILL.md").resolve(), links)
            self.assertTrue(all(target.exists() for target in links))
            if harness != "claude":
                self.assertIn("name: " + name + "\n", source.read_text())
            if harness == "pi":
                alias = dest / "prompts" / (name + ".md")
                self.assertTrue(alias.is_file())
                self.assertIn(str(source), alias.read_text())
                self.assertIn("$ARGUMENTS", alias.read_text())
                self.assertIn("argument-hint:", alias.read_text())
        if harness == "pi":
            self.assertFalse((dest / "prompts/plan-spec.md").exists())
        for document in [*(guides / guide for guide in GUIDES), contract / "SKILL.md"]:
            for target in validator.local_links(document.read_text(), document):
                self.assertTrue(target.exists(), str(document) + " -> " + str(target))
        for name in RETIRED:
            self.assertFalse((guides / name / "SKILL.md").exists())
            self.assertFalse((dest / "skills" / name / "SKILL.md").exists())
            self.assertFalse((dest / "commands" / (name + ".md")).exists())
        plan_root = self.base / (harness + "-plans-" + scope)
        create_root(plan_root)
        result = subprocess.run([sys.executable, str(installed_validator), "--root", str(plan_root), "--plan", SLUG],
                                capture_output=True, text=True, env=self.env, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((dest / "auth.json").exists())
        return dest

    def test_fresh_project_installs_resolve_contract_guides_and_assets(self):
        for harness in ("copilot", "claude", "pi"):
            with self.subTest(harness=harness):
                self.install(harness)
                self.check_installation(harness)

    def test_global_installs_use_only_isolated_home(self):
        for harness in ("claude", "pi"):
            with self.subTest(harness=harness):
                self.install(harness, scope="global")
                self.check_installation(harness, scope="global")
                self.assertFalse((self.project / (".claude" if harness == "claude" else ".pi")).exists())

    def test_dry_run_writes_nothing(self):
        before = snapshot(self.base)
        before_tree = sorted(str(p.relative_to(self.base)) for p in self.base.rglob("*"))
        for harness in ("copilot", "claude", "pi"):
            result = self.install(harness, dry_run=True)
            self.assertIn("feature-planning", result.stdout)
            if harness != "copilot":
                self.assertIn("plan-create", result.stdout)
                self.assertIn("plan-spec", result.stdout)
        self.assertEqual(snapshot(self.base), before)
        self.assertEqual(sorted(str(p.relative_to(self.base)) for p in self.base.rglob("*")), before_tree)

    def seed_upgrade(self, harness):
        dest = self.destination(harness)
        preserved = []
        for name in RETIRED:
            path = ((dest / "skills/feature-planning" / name / "SKILL.md") if harness == "copilot" else
                    (dest / "commands" / (name + ".md")) if harness == "claude" else
                    (dest / "skills" / name / "SKILL.md"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("User-customized legacy content: " + name + "\n")
            preserved.append(path)
        for path in (dest / "skills/unselected/SKILL.md", dest / "skills/plan-create/user-notes.md"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Unrelated user content; preserve.\n")
            preserved.append(path)
        if harness == "claude":
            path = dest / "commands/plan-spec.md"
            path.write_text("Old generated internal command, possibly customized.\n")
            preserved.append(path)
        elif harness == "pi":
            for name in RETIRED:
                path = dest / "prompts" / (name + ".md")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Legacy/custom prompt; preserve.\n")
                preserved.append(path)
        return preserved

    def test_upgrade_warns_exact_paths_without_deleting_custom_or_unselected_files(self):
        for harness in ("copilot", "claude", "pi"):
            with self.subTest(harness=harness):
                preserved = self.seed_upgrade(harness)
                before = {path: path.read_bytes() for path in preserved}
                for preview in (True, False):
                    result = self.install(harness, dry_run=preview)
                    self.assertIn("WARNING: stale", result.stderr)
                    self.assertIn("Nothing is deleted", result.stderr)
                    for path in preserved:
                        self.assertEqual(path.read_bytes(), before[path])
                    for path in preserved[:len(RETIRED)]:
                        self.assertIn(str(path), result.stderr)
                    if harness == "claude":
                        self.assertIn("stale internal helper command", result.stderr)
                    elif harness == "pi":
                        for name in RETIRED:
                            self.assertIn(str(self.destination(harness) / "prompts" / (name + ".md")), result.stderr)
                self.assertTrue((self.destination(harness) / "skills/feature-planning/MIGRATION.md").exists())

    def test_unselected_collection_does_not_warn_or_modify_legacy_content(self):
        for harness in ("copilot", "claude", "pi"):
            preserved = self.seed_upgrade(harness)
            before = {path: path.read_bytes() for path in preserved}
            result = self.install(harness, skills="none")
            self.assertNotIn("WARNING: stale", result.stderr)
            self.assertEqual({path: path.read_bytes() for path in preserved}, before)
            self.assertFalse((self.destination(harness) / "skills/feature-planning/README.md").exists())

    def test_reinstallation_preserves_extras_and_is_content_idempotent(self):
        for harness in ("copilot", "claude", "pi"):
            self.install(harness)
            dest = self.destination(harness)
            extra = dest / "skills/feature-planning/user-notes.md"
            extra.write_text("Keep my notes.\n")
            before = snapshot(dest)
            self.install(harness)
            self.assertEqual(snapshot(dest), before)


if __name__ == "__main__":
    unittest.main()
