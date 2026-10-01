"""Identity and path regression tests using isolated temporary workspaces."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import product_scope as scope
from route_engineer_task import route_task


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.other = self.root / "other"
        self.other.mkdir()
        self.context = scope.resolve_context("Build importer", product_line="project-7", workspace=str(self.workspace))

    def test_route_separates_role_and_identity(self):
        route = route_task("Review dataset", product_line="arbitrary.project", workspace=str(self.workspace))
        self.assertEqual(route["product_context"]["product_line"], "arbitrary.project")
        self.assertEqual(route["primary_role"], "data-engineer")
        self.assertEqual(route["runtime_action"], "none")
        self.assertEqual(route["role_semantics"], "advisory_label_only")

    def test_missing_context_fields_fail_closed(self):
        for key in ("schema_version", "product_line", "workspace", "status", "conflicts", "allowed_scopes", "state_namespace", "archive_root"):
            with self.subTest(key=key):
                context = copy.deepcopy(self.context)
                del context[key]
                with self.assertRaises(ValueError):
                    scope.validate_context(context)

    def test_malformed_contexts_fail_closed(self):
        for context in (None, [], {}, {**self.context, "schema_version": True}, {**self.context, "status": "blocked"}):
            with self.subTest(context=context), self.assertRaises(ValueError):
                scope.validate_context(context)

    def test_workspace_binding_and_canonical_form(self):
        for workspace in ("relative", str(self.workspace / ".." / "workspace"), str(self.other), str(self.root / "missing")):
            with self.subTest(workspace=workspace), self.assertRaises(ValueError):
                scope.validate_context({**self.context, "workspace": workspace})
        with self.assertRaises(ValueError):
            scope.resolve_context("Task")
        with self.assertRaises(ValueError):
            scope.resolve_context("Task", product_line="../outside", workspace=str(self.workspace))

    def test_recovery_rejects_project_workspace_module_mismatch(self):
        valid = {"product_context": self.context, "active_module_key": "importer"}
        scope.validate_recovery(self.context, valid, "importer")
        wrong_project = scope.resolve_context("Task", product_line="different", workspace=str(self.workspace))
        wrong_workspace = scope.resolve_context("Task", product_line="project-7", workspace=str(self.other))
        for record in ({}, {**valid, "active_module_key": "other"}, {**valid, "product_context": wrong_project}, {**valid, "product_context": wrong_workspace}, {**valid, "product_context": {"product_line": "project-7", "workspace": str(self.workspace)}}):
            with self.subTest(record=record), self.assertRaises(ValueError):
                scope.validate_recovery(self.context, record, "importer")
        with self.assertRaises(ValueError):
            scope.validate_recovery(self.context, valid, "")

    def test_path_scope(self):
        scope.validate_execution_paths(self.context, [str(self.workspace / "new.py")])
        for path in ("relative.py", str(self.other / "foreign.py"), str(self.workspace), str(self.workspace / "missing" / "new.py"), str(self.workspace / ".." / "other" / "foreign.py")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                scope.validate_execution_paths(self.context, [path])
        with self.assertRaises(ValueError):
            scope.validate_execution_paths(self.context, "not a list")

    def test_symlink_escape(self):
        (self.workspace / "link").symlink_to(self.other, target_is_directory=True)
        with self.assertRaises(ValueError):
            scope.validate_execution_paths(self.context, [str(self.workspace / "link" / "outside.py")])
        outside_file = self.other / "existing.py"
        outside_file.write_text("", encoding="utf-8")
        (self.workspace / "file.py").symlink_to(outside_file)
        with self.assertRaises(ValueError):
            scope.validate_execution_paths(self.context, [str(self.workspace / "file.py")])
        (self.workspace / ".agent-state").symlink_to(self.other, target_is_directory=True)
        with self.assertRaises(ValueError):
            scope.validate_context(self.context)

    def test_load_context_and_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "route_engineer_task.py"), "--task", "Build a feature", "--product-line", "project-7", "--workspace", str(self.workspace)], capture_output=True, text=True, check=True)
        output = self.root / "route.json"
        output.write_text(result.stdout, encoding="utf-8")
        self.assertEqual(scope.load_context(output), self.context)
        output.write_text(json.dumps(self.context), encoding="utf-8")
        self.assertEqual(scope.load_context(output), self.context)
        output.write_text("[]", encoding="utf-8")
        with self.assertRaises(ValueError):
            scope.load_context(output)
        blocked = subprocess.run([sys.executable, str(SCRIPTS / "route_engineer_task.py"), "--task", "", "--workspace", str(self.workspace)], capture_output=True, text=True)
        self.assertEqual(blocked.returncode, 2)
        self.assertEqual(json.loads(blocked.stdout)["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
