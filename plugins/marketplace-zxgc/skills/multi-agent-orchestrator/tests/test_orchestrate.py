"""Contract tests for the candidate scheduler; no agents are started."""
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "orchestrate.py"
spec = importlib.util.spec_from_file_location("candidate_orchestrate", SCRIPT)
orchestrate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orchestrate)


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.context = orchestrate.product_scope.resolve_context(
            "shared workflow", product_line="shared", workspace=str(self.root))
        self.a = str(self.root / "a.py")
        self.b = str(self.root / "b.py")
        self.workflow = {
            "product_context": self.context, "active_module_key": "module-a",
            "confirmed": True, "available_models": ["your-worker-model", "your-scout-model"],
            "capacity": {"total_slots": 4, "root_slots": 1},
            "tasks": [], "state": {},
        }

    def task(self, name, kind="implementation", files=None, deps=None, refs=None,
             difficulty="low", risk="low"):
        return {"id": name, "kind": kind, "difficulty": difficulty, "risk": risk,
                "goal": "Complete " + name, "dependencies": deps or [],
                "allowed_files": files or [], "evidence_refs": refs or [],
                "acceptance": ["Evidence reviewed"], "constraints": ["Stay in scope"]}

    def add(self, task, status="pending", accepted=False, attempts=0,
            failure_reason="", usage=None):
        self.workflow["tasks"].append(task)
        self.workflow["state"][task["id"]] = {
            "status": status, "accepted": accepted, "attempts": attempts,
            "failure_reason": failure_reason, "usage": usage,
        }

    def run_plan(self):
        return orchestrate.plan_wave(self.workflow, self.context, "module-a")

    def test_parallel_wave_uses_native_compiler_spawn_args(self):
        self.add(self.task("write", files=[self.a]))
        self.add(self.task("read", kind="research", refs=[self.b]))
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["write", "read"])
        self.assertEqual([x["spawn_args"]["agent_type"] for x in out["wave"]],
                         ["default", "default"])
        self.assertIn('"active_module_key":"module-a"', out["wave"][0]["spawn_args"]["message"])

    def test_cycle_and_unknown_dependency_rejected(self):
        self.add(self.task("a", deps=["b"]))
        self.add(self.task("b", deps=["a"]))
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.run_plan()
        self.workflow["tasks"][1]["dependencies"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown dependency"):
            self.run_plan()

    def test_duplicate_id_unknown_state_and_bad_types_rejected(self):
        self.add(self.task("a"))
        self.workflow["tasks"].append(self.task("a"))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_plan()
        self.workflow["tasks"].pop()
        self.workflow["state"]["ghost"] = dict(self.workflow["state"]["a"])
        with self.assertRaisesRegex(ValueError, "state ids"):
            self.run_plan()
        del self.workflow["state"]["ghost"]
        self.workflow["tasks"][0]["difficulty"] = "extreme"
        with self.assertRaisesRegex(ValueError, "difficulty"):
            self.run_plan()

    def test_accepted_cannot_fake_passed(self):
        self.add(self.task("a"), accepted=True)
        with self.assertRaisesRegex(ValueError, "accepted"):
            self.run_plan()

    def test_dependency_requires_passed_and_accepted(self):
        self.add(self.task("a"), status="passed", attempts=1, accepted=False)
        self.add(self.task("b", deps=["a"], files=[self.b]))
        out = self.run_plan()
        self.assertEqual(out["wave"], [])
        self.assertEqual(out["deferred"]["b"], "dependency a is not passed and accepted")
        self.workflow["state"]["a"]["accepted"] = True
        self.assertEqual([x["id"] for x in self.run_plan()["wave"]], ["b"])

    def test_upstream_failure_does_not_skip_or_retry(self):
        self.add(self.task("a"), status="failed", attempts=1, failure_reason="test_failed")
        self.add(self.task("b", deps=["a"], files=[self.b]))
        out = self.run_plan()
        self.assertEqual(out["wave"], [])
        self.assertIn("dependency a", out["deferred"]["b"])
        self.assertIn("failed task requires primary review", out["deferred"]["a"])

    def test_realpath_write_conflict_and_read_of_unfinished_write(self):
        self.add(self.task("a", files=[self.a]))
        self.add(self.task("b", files=[str(self.root / "." / "a.py")]))
        self.add(self.task("c", kind="query", refs=[self.a]))
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["a"])
        self.assertIn("write conflict", out["deferred"]["b"])
        self.assertIn("selected wave write", out["deferred"]["c"])

    def test_running_uses_capacity_and_file_ownership(self):
        self.workflow["capacity"] = {"total_slots": 2, "root_slots": 1}
        self.add(self.task("running", files=[self.a]), status="running", attempts=1)
        self.add(self.task("next", files=[self.b]))
        self.assertEqual(self.run_plan()["wave"], [])
        self.workflow["capacity"]["total_slots"] = 3
        self.assertEqual([x["id"] for x in self.run_plan()["wave"]], ["next"])
        self.workflow["tasks"][1]["allowed_files"] = [self.a]
        self.assertEqual(self.run_plan()["wave"], [])

    def test_running_oversubscription_and_duplicate_owner_rejected(self):
        self.add(self.task("one", files=[self.a]), status="running", attempts=1)
        self.add(self.task("two", files=[self.a]), status="running", attempts=1)
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.run_plan()
        self.workflow["tasks"][1]["allowed_files"] = [self.b]
        self.workflow["capacity"]["total_slots"] = 2
        with self.assertRaisesRegex(ValueError, "exceed capacity"):
            self.run_plan()

    def test_model_unavailable_and_unconfirmed_cannot_spawn(self):
        self.add(self.task("a", files=[self.a]))
        self.workflow["available_models"] = ["your-scout-model"]
        out = self.run_plan()
        self.assertEqual(out["wave"], [])
        self.assertIn("unavailable", out["deferred"]["a"])
        self.workflow["confirmed"] = False
        self.assertEqual(self.run_plan()["wave"], [])

    def test_primary_routing_and_unknown_usage(self):
        self.add(self.task("plan", kind="planning"))
        self.add(self.task("eval", kind="evaluation"))
        self.add(self.task("hard", files=[self.a], difficulty="high"))
        self.add(self.task("risky", kind="research", risk="high"))
        out = self.run_plan()
        self.assertEqual(len(out["wave"]), 1)
        self.assertEqual(out["wave"][0]["id"], "plan")
        self.assertEqual(out["wave"][0]["route"], "primary_agent")
        self.assertNotIn("spawn_args", out["wave"][0])
        self.assertIsNone(out["usage"]["input_tokens"])
        self.workflow["tasks"] = [self.workflow["tasks"][2]]
        self.workflow["state"] = {"hard": self.workflow["state"]["hard"]}
        self.assertEqual(self.run_plan()["wave"][0]["route"], "primary_agent")

    def test_primary_write_reserves_file_and_retry_limit_stays_blocked(self):
        self.add(self.task("hard", files=[self.a], difficulty="high"))
        self.add(self.task("worker", files=[self.a]))
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["hard"])
        self.assertIn("write conflict", out["deferred"]["worker"])
        self.workflow["state"]["hard"]["attempts"] = 2
        out = self.run_plan()
        self.assertNotIn("hard", [x["id"] for x in out["wave"]])
        self.assertIn("retry limit", out["deferred"]["hard"])

    def test_policy_context_limit_and_unknown_field_rejected(self):
        self.add(self.task("large", files=[self.a]))
        self.workflow["tasks"][0]["goal"] = "x" * 13000
        out = self.run_plan()
        self.assertEqual(out["wave"], [])
        self.assertIn("context exceeds", out["deferred"]["large"])
        self.workflow["tasks"][0]["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "exactly"):
            self.run_plan()

    def test_symlink_and_product_scope_isolation(self):
        Path(self.a).touch()
        link = self.root / "link.py"
        link.symlink_to(self.a)
        self.add(self.task("first", files=[self.a]))
        self.add(self.task("second", files=[str(link)]))
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["first"])
        self.assertIn("write conflict", out["deferred"]["second"])
        foreign = orchestrate.product_scope.resolve_context(
            "name workflow", product_line="other-project", workspace=str(self.root))
        with self.assertRaisesRegex(ValueError, "product_line"):
            orchestrate.plan_wave(self.workflow, foreign, "module-a")

    def test_independent_scope_and_attempt_usage_validation(self):
        self.add(self.task("a", files=[self.a]))
        with self.assertRaisesRegex(ValueError, "module"):
            orchestrate.plan_wave(self.workflow, self.context, "other")
        self.workflow["state"]["a"]["attempts"] = 1
        self.workflow["state"]["a"]["usage"] = None
        self.assertIsNone(self.run_plan()["usage"]["input_tokens"])
        self.workflow["state"]["a"]["usage"] = {"input_tokens": 12, "output_tokens": 4}
        self.assertEqual(self.run_plan()["usage"]["input_tokens"], 12)
        self.assertEqual(self.run_plan()["usage"]["status"], "reported_task_subtotal")
        self.assertEqual(self.run_plan()["usage"]["overall_status"], "unknown")

    def test_pending_reader_before_dependent_writer_does_not_deadlock(self):
        self.add(self.task("inspect", kind="query", refs=[self.a]))
        self.add(self.task("fix", files=[self.a], deps=["inspect"]))
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["inspect"])
        self.assertIn("dependency inspect", out["deferred"]["fix"])

    def test_reader_and_writer_conflicts_both_directions(self):
        self.add(self.task("reader", kind="query", refs=[self.a]))
        self.add(self.task("writer", files=[self.a]))
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["reader"])
        self.assertIn("read conflict", out["deferred"]["writer"])
        self.workflow["state"]["reader"].update(status="running", attempts=1)
        self.assertEqual(self.run_plan()["wave"], [])
        self.assertIn("read conflict", self.run_plan()["deferred"]["writer"])

    def test_failed_or_unaccepted_writer_blocks_reader_without_dependency(self):
        self.add(self.task("writer", files=[self.a]), status="failed", attempts=1,
                 failure_reason="test_failed")
        self.add(self.task("reader", kind="query", refs=[self.a]))
        out = self.run_plan()
        self.assertEqual(out["wave"], [])
        self.assertIn("unaccepted write", out["deferred"]["reader"])
        self.workflow["state"]["writer"].update(status="passed", failure_reason="")
        out = self.run_plan()
        self.assertEqual(out["status"], "waiting")
        self.assertIn("awaits acceptance", out["deferred"]["writer"])
        self.assertIn("unaccepted write", out["deferred"]["reader"])

    def test_root_running_uses_root_slot_once(self):
        self.workflow["capacity"] = {"total_slots": 2, "root_slots": 1}
        self.add(self.task("plan", kind="planning"), status="running", attempts=1)
        self.add(self.task("worker", files=[self.a]))
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["worker"])
        self.add(self.task("eval", kind="evaluation"), status="running", attempts=1)
        with self.assertRaisesRegex(ValueError, "root"):
            self.run_plan()

    def test_high_risk_is_globally_exclusive(self):
        self.add(self.task("risk", kind="evaluation", risk="high"))
        self.add(self.task("worker", files=[self.a]))
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["risk"])
        self.assertIn("high-risk", out["deferred"]["worker"])
        self.workflow["tasks"].reverse()
        out = self.run_plan()
        self.assertEqual([x["id"] for x in out["wave"]], ["worker"])
        self.assertIn("high-risk", out["deferred"]["risk"])
        self.workflow["state"]["worker"].update(status="running", attempts=1)
        self.assertEqual(self.run_plan()["wave"], [])
        self.assertIn("high-risk", self.run_plan()["deferred"]["risk"])
        self.workflow["state"]["risk"].update(status="running", attempts=1)
        with self.assertRaisesRegex(ValueError, "high-risk"):
            self.run_plan()

    def test_complete_and_waiting_statuses(self):
        self.add(self.task("a", kind="query"), status="passed", attempts=1, accepted=True)
        out = self.run_plan()
        self.assertEqual(out["status"], "complete")
        self.workflow["state"]["a"]["accepted"] = False
        out = self.run_plan()
        self.assertEqual(out["status"], "waiting")
        self.assertIn("awaits acceptance", out["deferred"]["a"])

    def test_pending_retry_writer_blocks_other_reader_but_not_self(self):
        self.add(self.task("reader", kind="query", refs=[self.a]))
        self.add(self.task("retry", files=[self.a], refs=[self.a]))
        self.workflow["state"]["retry"].update(attempts=1, failure_reason="test_failed")
        out = self.run_plan()
        self.assertIn("unaccepted write", out["deferred"]["reader"])
        self.assertEqual([x["id"] for x in out["wave"]], ["retry"])

    def test_empty_tasks_rejected_and_unconfirmed_cannot_complete(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            self.run_plan()
        self.add(self.task("accepted", kind="query"), status="passed", attempts=1, accepted=True)
        self.workflow["confirmed"] = False
        out = self.run_plan()
        self.assertEqual(out["status"], "blocked")
        self.assertEqual(out["wave"], [])


if __name__ == "__main__":
    unittest.main()
