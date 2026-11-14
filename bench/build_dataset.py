"""Freeze data/sample.xlsx into bench/data/ykt_sample.jsonl (one benchmark item per line).

    python3 bench/build_dataset.py [--xlsx data/sample.xlsx] [--out bench/data/ykt_sample.jsonl]

Reads the .xlsx with the standard library only. Fixes applied to the sheet:
  * rows without an `id` continue the item above them (the extra multiple-choice
    questions under g2p1-L14-006); they get ids with a b/c/d... suffix and inherit
    grade/part/lesson from it;
  * `grade` is re-derived from the id, because Excel turned "10-11" into a date serial;
  * per-item overrides in OVERRIDES below.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

# `content` here is the theory text of the next chapter (the parser ran past the test's
# end); the instruction already holds the whole question with its options.
OVERRIDES = {
    "g10-11-T3-009": {"content": ""},
}

INHERIT = ["grade", "part", "chain", "lesson", "section", "block", "pdf_page_start", "pdf_page_end"]


def read_xlsx(path):
    """Return the first sheet as a list of dicts keyed by the header row."""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for r in sheet.iter(f"{{{NS['m']}}}row"):
        row = {}
        for c in r.findall("m:c", NS):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            v, t = c.find("m:v", NS), c.get("t")
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
            else:
                val = v.text if v is not None else None
            row[col] = val
        rows.append(row)
    header = rows[0]
    return [{header[k]: v for k, v in r.items() if k in header} for r in rows[1:]]


def clean(s):
    if s is None:
        return ""
    s = str(s).replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in s.strip().split("\n"))


def build(rows):
    items, last, suffix = [], None, 0
    for i, r in enumerate(rows, start=2):  # sheet row number, for traceability
        if not any((v or "").strip() for v in r.values() if isinstance(v, str)):
            continue
        rid = clean(r.get("id"))
        if rid:
            last, suffix = r, 0
        else:
            if last is None:
                sys.exit(f"row {i}: no id and no item above it to attach to")
            suffix += 1
            rid = f"{clean(last['id'])}{chr(ord('a') + suffix)}"  # 2nd row -> b
            for k in INHERIT:
                if not clean(r.get(k)):
                    r[k] = last.get(k)
        m = re.match(r"g(\d+(?:-\d+)?)", rid)
        item = {
            "id": rid,
            "grade": m.group(1) if m else clean(r.get("grade")),
            "part": clean(r.get("part")),
            "lesson": clean(r.get("lesson")),
            "section": clean(r.get("section")),
            "block": clean(r.get("block")),
            "icon": clean(r.get("icon")),
            "needs_visual": clean(r.get("needs_visual")) == "1",
            "mapping": clean(r.get("mapping")),
            "instruction": clean(r.get("instruction")),
            "content": clean(r.get("content")),
            "answer": clean(r.get("answer")),
            "answer_key": clean(r.get("answer_key")),
            "pdf_page_start": clean(r.get("pdf_page_start")),
            "sheet_row": i,
        }
        item.update(OVERRIDES.get(rid, {}))
        if not item["instruction"] or not item["answer"]:
            sys.exit(f"row {i} ({rid}): empty instruction or answer")
        items.append(item)
    dupes = [k for k, n in Counter(it["id"] for it in items).items() if n > 1]
    if dupes:
        sys.exit(f"duplicate ids: {dupes}")
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", default=ROOT / "data" / "sample.xlsx", type=Path)
    ap.add_argument("--out", default=ROOT / "bench" / "data" / "ykt_sample.jsonl", type=Path)
    args = ap.parse_args()

    items = build(read_xlsx(args.xlsx))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"{len(items)} items -> {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}")
    print("by grade:", dict(sorted(Counter(it["grade"] for it in items).items(), key=lambda kv: [int(x) for x in kv[0].split("-")])))
    print("needs_visual:", sum(it["needs_visual"] for it in items))


if __name__ == "__main__":
    main()
