import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "harness.py"
EXAMPLE = ROOT / ".harness" / "task.example.json"


class HarnessCliTest(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_init_copies_example_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "task.json"

            first = self.run_cli("init", str(target))
            second = self.run_cli("init", str(target))

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["phase"], "intake")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("已存在", second.stderr)

    def test_check_rejects_done_without_evidence(self) -> None:
        state = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        state["phase"] = "done"
        state["requirements"]["success_criteria"] = ["可以驗證完成狀態"]
        state["design"]["approach"] = "使用狀態檔"
        state["plan"] = ["執行驗證"]

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "task.json"
            target.write_text(json.dumps(state), encoding="utf-8")

            result = self.run_cli("check", str(target))

        self.assertEqual(result.returncode, 1)
        self.assertIn("changes.files", result.stderr)
        self.assertIn("verification", result.stderr)
        self.assertIn("review.status", result.stderr)

    def test_check_rejects_unknown_phase(self) -> None:
        state = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        state["phase"] = "ship"

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "task.json"
            target.write_text(json.dumps(state), encoding="utf-8")

            result = self.run_cli("check", str(target))

        self.assertEqual(result.returncode, 1)
        self.assertIn("phase", result.stderr)

    def test_check_enforces_schema_for_done_state(self) -> None:
        state = self.complete_state()
        state["requirements"]["success_criteria"] = "not-an-array"
        state["changes"]["files"] = "scripts/harness.py"
        state["verification"] = [{"status": "pass"}]
        state["unexpected"] = True

        result = self.check_state(state)

        self.assertEqual(result.returncode, 1)
        self.assertIn("requirements.success_criteria", result.stderr)
        self.assertIn("changes.files", result.stderr)
        self.assertIn("verification[0].command", result.stderr)
        self.assertIn("unexpected", result.stderr)

    def test_check_rejects_skipped_phase_history(self) -> None:
        state = self.complete_state()
        state["phase_history"] = ["intake", "done"]

        result = self.check_state(state)

        self.assertEqual(result.returncode, 1)
        self.assertIn("phase_history", result.stderr)

    def test_check_rejects_latest_failed_verification(self) -> None:
        state = self.complete_state()
        state["verification"].append(
            {"command": "python final_check.py", "result": "1 failure", "status": "fail"}
        )

        result = self.check_state(state)

        self.assertEqual(result.returncode, 1)
        self.assertIn("最後一筆 verification", result.stderr)

    def test_blocked_keeps_previous_phase_requirements(self) -> None:
        state = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        state["phase"] = "blocked"
        state["phase_history"] = ["intake", "design", "blocked"]

        result = self.check_state(state)

        self.assertEqual(result.returncode, 1)
        self.assertIn("requirements.success_criteria", result.stderr)

    def test_check_aggregates_schema_and_semantic_errors(self) -> None:
        state = self.complete_state()
        state["unexpected"] = True
        state["changes"] = {"files": [], "summary": ""}
        state["verification"] = []
        state["review"] = {"status": "pending", "notes": ""}

        result = self.check_state(state)

        self.assertEqual(result.returncode, 1)
        self.assertIn("unexpected", result.stderr)
        self.assertIn("changes.files", result.stderr)
        self.assertIn("verification", result.stderr)
        self.assertIn("review.status", result.stderr)

    def test_check_accepts_complete_done_state(self) -> None:
        result = self.check_state(self.complete_state())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("通過", result.stdout)

    def complete_state(self) -> dict:
        state = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        state.update(
            phase="done",
            phase_history=["intake", "design", "plan", "implement", "verify", "review", "done"],
            plan=["新增測試", "實作功能", "執行驗證"],
            verification=[
                {"command": "python -m unittest", "result": "7 tests passed", "status": "pass"}
            ],
        )
        state["requirements"]["success_criteria"] = ["完成狀態通過驗證"]
        state["design"]["approach"] = "使用工具中立狀態檔"
        state["changes"] = {"files": ["scripts/harness.py"], "summary": "新增驗證器"}
        state["review"] = {"status": "pass", "notes": "需求與驗證證據一致"}
        return state

    def check_state(self, state: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "task.json"
            target.write_text(json.dumps(state), encoding="utf-8")
            return self.run_cli("check", str(target))


if __name__ == "__main__":
    unittest.main()
