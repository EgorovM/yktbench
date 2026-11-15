"""Freeze the supplied vals_90 questions and record the exact model instructions."""

import argparse
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

import build_dataset


def read_rows(path, sheet=None):
    if path.suffix.lower() == ".xlsx":
        if sheet is None:
            with zipfile.ZipFile(path) as archive:
                workbook = ET.fromstring(archive.read("xl/workbook.xml"))
                names = [s.get("name") for s in workbook.findall("m:sheets/m:sheet", build_dataset.NS)]
            sheet = next((n for n in names if n.lower() == "vals_90"), None)
            if sheet is None:
                if len(names) != 1:
                    raise ValueError(f"Specify --sheet; workbook has {names}")
                sheet = names[0]
        return build_dataset.read_xlsx(path, sheet), sheet
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as source:
            return [dict(row, _sheet_row=i) for i, row in enumerate(csv.DictReader(source), 2)], ""
    if path.suffix.lower() == ".jsonl":
        return [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()], ""
    raise ValueError("Input must be XLSX, CSV, or UTF-8 JSONL")


def freeze(source, instructions, output, sheet=None, expected_count=90, allow_visual_text=False):
    rows, selected = read_rows(source, sheet)
    items = build_dataset.build(rows, version="vals_90")
    if len(items) != expected_count:
        raise ValueError(f"Expected {expected_count} questions, found {len(items)}")
    if not allow_visual_text and any(item["needs_visual"] for item in items):
        raise ValueError("vals_90 must contain text-only questions")
    if not instructions.read_text(encoding="utf-8").strip():
        raise ValueError("Model instructions must not be empty")
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    for item in items:
        item.update(dataset_version="vals_90", source_file=source.name, source_sheet=selected)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in items), encoding="utf-8")
    manifest = {
        "dataset_version": "vals_90", "source_file": source.name, "source_sheet": selected,
        "source_sha256": source_hash, "dataset_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "solver_instructions_file": str(instructions),
        "solver_instructions_sha256": hashlib.sha256(instructions.read_bytes()).hexdigest(),
        "questions": len(items), "by_grade": dict(Counter(it["grade"] for it in items)),
        "needs_visual": sum(it["needs_visual"] for it in items),
        "evaluation_mode": "text-only; original picture flags retained",
        "eval_instruction_count": sum(bool(it.get("eval_instruction")) for it in items),
    }
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--sheet")
    parser.add_argument("--solver-instructions", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "data/vals_90.jsonl")
    parser.add_argument("--expected-count", type=int, default=90)
    parser.add_argument("--allow-visual-text", action="store_true", help="retain source picture flags while evaluating text only")
    args = parser.parse_args()
    print(json.dumps(freeze(args.input, args.solver_instructions, args.out, args.sheet,
                            args.expected_count, args.allow_visual_text), indent=2))


if __name__ == "__main__":
    main()
