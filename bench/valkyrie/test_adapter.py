import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import agent
import build
import grade
import metric
import providers


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / "items.jsonl"
        self.system = self.root / "system.md"
        self.system.write_text("Answer in Sakha.\nХОРУЙ: <answer>\n", encoding="utf-8")
        self.items = [
            {"id": "g1-test-001", "grade": "1", "instruction": "Таай.", "content": "Ас.",
             "answer": "REFERENCE_ONLY_Үүт", "needs_visual": False,
             "eval_instruction": "JUDGE_ONLY: Accept equivalent meanings."},
            {"id": "g2-test-002", "grade": "2", "instruction": "Толор.", "content": "",
             "answer": "REFERENCE_ONLY_Тыа", "needs_visual": False},
        ]
        self.data.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in self.items))

    def test_export_keeps_references_out_of_model_inputs_and_bundle(self):
        out = self.root / "export"
        result = build.build(self.data, self.system, out)
        self.assertEqual(result["questions"], 2)
        for item in self.items:
            task = out / "tasks" / item["id"]
            prompt = (task / "instruction.md").read_text()
            self.assertNotIn(item["answer"], prompt)
            self.assertNotIn("JUDGE_ONLY", prompt)
            self.assertEqual(agent.model_input(prompt), build.ykt_eval.solver_prompt(item))
            self.assertEqual(json.loads((task / "tests/reference.json").read_text())["answer"], item["answer"])
            config = tomllib.loads((task / "task.toml").read_text())
            self.assertEqual(config["agent"]["network_mode"], "allowlist")
            self.assertNotIn("*", config["agent"]["allowed_hosts"])
        for path in (out / "agent").iterdir():
            content = path.read_text()
            self.assertNotIn("REFERENCE_ONLY_", content)
            self.assertNotEqual(path.name, ".env")
        self.assertEqual((out / "agent/solver_system.md").read_bytes(), self.system.read_bytes())
        self.assertEqual(len(tomllib.loads((out / "tasks/dataset.toml").read_text())["tasks"]), 2)
        self.assertFalse((out / "tasks/metric.py").exists())

    def test_item_guidance_goes_to_both_judges_but_not_solver(self):
        item = self.items[0]
        native = build.ykt_eval.judge_prompt(item, "candidate")
        self.assertEqual(native, grade.judge_prompt(item, "candidate"))
        self.assertIn(item["eval_instruction"], native)
        self.assertNotIn(item["eval_instruction"], build.ykt_eval.solver_prompt(item))

    def test_agent_imports_bundle_modules_with_python_safe_path(self):
        out = self.root / "isolated"
        build.build(self.data, self.system, out)
        result = subprocess.run([sys.executable, "-I", str(out / "agent/agent.py"), "--help"],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_visual_items_and_duplicate_ids_are_rejected(self):
        for rows in ([self.items[0], self.items[0]], [dict(self.items[0], needs_visual=True)]):
            self.data.write_text("".join(json.dumps(x) + "\n" for x in rows))
            with self.assertRaises(ValueError):
                build.build(self.data, self.system, self.root / "rejected")

    def test_metric_counts_missing_tasks_as_zero(self):
        actual = metric.aggregate([{"reward": 1, "partial_credit": 1}, None,
                                   {"reward": 0, "partial_credit": 0.5}])
        self.assertAlmostEqual(actual["reward"], 1 / 3)
        self.assertEqual(actual["partial_credit"], 0.5)

    def test_judgment_requires_all_parts_for_full_credit(self):
        result = {"parts": [{"correct": True}, {"correct": False}]}
        self.assertEqual(grade.scores(result), {"reward": 0.0, "partial_credit": 0.5})
        with self.assertRaises(ValueError):
            grade.scores({"parts": [{"correct": "false"}]})

    def test_empty_answer_needs_no_judge_key(self):
        self.assertEqual(grade.scores(grade.grade(self.items[0], "", "", {})),
                         {"reward": 0.0, "partial_credit": 0.0})

    def test_streaming_preserves_limits_and_keeps_reported_overages(self):
        response = SimpleNamespace(status="completed", model="gpt-6.1-sol", output_text="ХОРУЙ: Үүт.",
                                   usage=SimpleNamespace(input_tokens=12, output_tokens=33000), id="test")
        events = [SimpleNamespace(type="response.completed", response=response)]
        class Stream:
            def __enter__(self): return iter(events)
            def __exit__(self, *args): pass
        calls = []
        def create(**kwargs):
            calls.append(kwargs)
            return Stream()
        provider = object.__new__(providers.OpenAIResponsesProvider)
        provider.cfg = {"model": "gpt-6.1-sol", "max_tokens": 32000, "effort": "high"}
        provider.client = SimpleNamespace(responses=SimpleNamespace(create=create))
        result = provider.complete("system", "question")
        self.assertEqual(calls[0], {"model": "gpt-6.1-sol", "instructions": "system", "input": "question",
                                    "max_output_tokens": 32000, "reasoning": {"effort": "high"}, "stream": True})
        self.assertEqual(result.output_tokens, 33000)
        self.assertEqual(result.text, "ХОРУЙ: Үүт.")


if __name__ == "__main__":
    unittest.main()
