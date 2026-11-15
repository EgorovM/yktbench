"""Offline checks for dataset provenance, version isolation, and XLSX ingestion.

Run with: .venv/bin/python -m unittest discover -s . -p 'test_*.py'
"""

import copy
import json
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET
import zipfile
from types import SimpleNamespace
from unittest.mock import patch
from collections import Counter
from pathlib import Path

import build_dataset as dataset
import ykt_eval as evaluator
from providers import make_provider


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "sources" / "clean_60_primary_school.xlsx"


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = dataset.read_xlsx(SOURCE, "clean")
        cls.items = dataset.build(cls.rows)

    def test_curated_sheet_has_60_unique_primary_items(self):
        self.assertEqual(len(self.items), 60)
        self.assertEqual(len({it["id"] for it in self.items}), 60)
        self.assertEqual(Counter(it["grade"] for it in self.items), {"1": 10, "2": 20, "3": 25, "4": 5})
        self.assertFalse(any(it["needs_visual"] for it in self.items))

    def test_blank_ids_are_stable_and_rows_are_traceable(self):
        by_row = {it["sheet_row"]: it["id"] for it in self.items}
        for row, rid in {12: "g2p1-L14-006b", 13: "g2p1-L14-006c", 14: "g2p1-L14-006d", 50: "g3p1-L33-011b"}.items():
            self.assertEqual(by_row[row], rid)
        original = copy.deepcopy(self.rows)
        dataset.build(self.rows)
        self.assertEqual(self.rows, original)

    def test_question_and_answer_text_comes_from_curated_sheet(self):
        by_row = {r["_sheet_row"]: r for r in self.rows}
        for it in self.items:
            for field in ("instruction", "content", "answer"):
                self.assertEqual(it[field], dataset.clean(by_row[it["sheet_row"]].get(field)))
        fixed = next(it for it in self.items if it["id"] == "g3p1-L34-001")
        self.assertIn("🟢🟥", fixed["content"])
        passage = next(it for it in self.items if it["id"] == "g2p2-L33-005")
        self.assertIn("Икки уол", passage["answer"])

    def test_exercise_grading_instructions_survive_normalization(self):
        row = dict(self.rows[0], eval_instruction="  Accept equivalent Sakha words.  ")
        item = dataset.build([row], version="vals_90")[0]
        self.assertEqual(item["eval_instruction"], "Accept equivalent Sakha words.")
        self.assertIn(item["eval_instruction"], evaluator.judge_prompt(item, "answer"))
        self.assertNotIn(item["eval_instruction"], evaluator.solver_prompt(item))

    def test_legacy_build_reproduces_frozen_v0(self):
        rebuilt = dataset.build(dataset.read_xlsx(ROOT / "data" / "sources" / "sample.xlsx"), version="v0")
        frozen = [json.loads(line) for line in (ROOT / "data" / "ykt_sample.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rebuilt, frozen)

    def test_reject_duplicate_ids_and_missing_required_text(self):
        with self.assertRaisesRegex(SystemExit, "duplicate ids"):
            dataset.build([self.rows[0], self.rows[0]])
        with self.assertRaisesRegex(SystemExit, "empty instruction or answer"):
            dataset.build([dict(self.rows[0], answer="")])
        with self.assertRaisesRegex(SystemExit, "no id and no item above"):
            dataset.build([dict(self.rows[0], id="")])

    def test_reject_nonprimary_and_external_visual_items(self):
        with self.assertRaisesRegex(SystemExit, "grades 1–4"):
            dataset.build([dict(self.rows[0], id="g10-11-T3-009")])
        with self.assertRaisesRegex(SystemExit, "external picture"):
            dataset.build([dict(self.rows[0], needs_visual="true")])
        with self.assertRaisesRegex(SystemExit, "invalid needs_visual"):
            dataset.build([dict(self.rows[0], needs_visual="unknown")])

    def test_named_sheet_resolution_and_real_row_numbers(self):
        # clean deliberately is not sheet1 and has a gap in Excel row numbers.
        m, r, p = dataset.NS["m"], dataset.NS["r"], dataset.NS["p"]
        workbook = f'<workbook xmlns="{m}" xmlns:r="{r}"><sheets><sheet name="wip" sheetId="1" r:id="r1"/><sheet name="clean" sheetId="7" r:id="r7"/></sheets></workbook>'
        rels = f'<Relationships xmlns="{p}"><Relationship Id="r1" Target="worksheets/sheet1.xml"/><Relationship Id="r7" Target="/xl/worksheets/sheet7.xml"/></Relationships>'
        sheet = ET.Element(f"{{{m}}}worksheet")
        body = ET.SubElement(sheet, f"{{{m}}}sheetData")
        for n, values in [(1, ["id", "grade", "instruction", "content", "answer", ""]), (4, ["g1-L01-001", "1.0", "Таай.", "🟢🟥", "Үүт.", ""])]:
            row = ET.SubElement(body, f"{{{m}}}row", r=str(n))
            for i, value in enumerate(values):
                cell = ET.SubElement(row, f"{{{m}}}c", r=f"{chr(65+i)}{n}", t="inlineStr")
                text = ET.SubElement(ET.SubElement(cell, f"{{{m}}}is"), f"{{{m}}}t")
                text.text = value
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.xlsx"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("xl/workbook.xml", workbook)
                z.writestr("xl/_rels/workbook.xml.rels", rels)
                z.writestr("xl/worksheets/sheet1.xml", "invalid XML, must not read wip")
                z.writestr("xl/worksheets/sheet7.xml", ET.tostring(sheet))
            rows = dataset.read_xlsx(path, "clean")
            self.assertEqual(rows[0]["_sheet_row"], 4)
            self.assertNotIn(None, rows[0])
            self.assertEqual(dataset.build(rows)[0]["content"], "🟢🟥")
            with self.assertRaisesRegex(ValueError, "not found"):
                dataset.read_xlsx(path, "missing")


class RunIsolationTests(unittest.TestCase):
    def test_answer_deadline_returns_a_terminal_empty_result(self):
        provider = make_provider("mock", {"provider": "mock", "model": "mock", "deadline_seconds": 0.001})
        start = time.monotonic()
        result = provider.complete("system", "question")
        self.assertLess(time.monotonic() - start, 3)
        self.assertEqual(result.stop_reason, "timeout")
        self.assertTrue(result.extra["timed_out"])
        self.assertEqual(result.text, "")

    def test_answer_before_deadline_is_preserved(self):
        provider = make_provider("mock", {"provider": "mock", "model": "mock", "deadline_seconds": 5})
        result = provider.complete("system", "question")
        self.assertIn("ХОРУЙ:", result.text)
        self.assertNotEqual(result.stop_reason, "timeout")

    def test_changed_model_instructions_reject_cached_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            data = run / "data.jsonl"
            data.write_text('{"answer":"Үүт"}\n', encoding="utf-8")
            args = SimpleNamespace(data=str(data))
            evaluator.write_meta(run, "solve", args, {"mock": {"model": "mock"}}, ["mock"])
            saved = (run / "meta.jsonl").read_bytes()
            with patch.object(evaluator, "SOLVER_SYSTEM", "Different instructions"):
                with self.assertRaisesRegex(SystemExit, "solver_prompt_sha differs"):
                    evaluator.write_meta(run, "solve", args, {"mock": {"model": "mock"}}, ["mock"])
            self.assertEqual(saved, (run / "meta.jsonl").read_bytes())

    def test_dataset_change_rejected_before_meta_append(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            data = run / "data.jsonl"
            data.write_text('{"answer": "Үүт"}\n', encoding="utf-8")
            meta = run / "meta.jsonl"
            meta.write_text(json.dumps({"dataset_sha": evaluator.sha(data.read_text(encoding="utf-8"))}) + "\n", encoding="utf-8")
            evaluator.validate_run_dataset(run, data)
            data.write_text('{"answer": "Тыа"}\n', encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "new --run-dir"):
                evaluator.validate_run_dataset(run, data)

    def test_defaults_use_v1_separately_from_v0(self):
        self.assertEqual(evaluator.DEFAULT_DATA.name, "ykt_primary_v1.jsonl")
        self.assertEqual(evaluator.DEFAULT_RUN_DIR.name, "v1")


if __name__ == "__main__":
    unittest.main()
