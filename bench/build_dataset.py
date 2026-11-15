"""Freeze the curated primary-school workbook as the v1 benchmark.

    python3 bench/build_dataset.py
    python3 bench/build_dataset.py --version v0  # reproduce the original sample

Uses only the standard library. The v1 source is the `clean` sheet, never `wip`.
Blank IDs receive b/c/d... suffixes under the preceding explicit ID. Grades are
derived from IDs, avoiding Excel date/float conversions. Sakha text and Unicode
sound tokens are preserved. Legacy content overrides apply only to v0.
"""

import argparse
import hashlib
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
}

# `content` here is the theory text of the next chapter (the parser ran past the test's
# end); the instruction already holds the whole question with its options.
OVERRIDES = {
    "g10-11-T3-009": {"content": ""},
}

INHERIT = ["grade", "part", "chain", "lesson", "section", "block", "pdf_page_start", "pdf_page_end"]


def read_xlsx(path, sheet_name=None):
    """Read a named (or first) worksheet, retaining actual Excel row numbers."""
    with zipfile.ZipFile(path) as z:
        workbook = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = workbook.findall("m:sheets/m:sheet", NS)
        selected = next((s for s in sheets if sheet_name is None or s.get("name") == sheet_name), None)
        if selected is None:
            raise ValueError(f"worksheet {sheet_name!r} not found; available: {[s.get('name') for s in sheets]}")
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        target = targets[selected.get(f"{{{NS['r']}}}id")]
        sheet_path = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        sheet = ET.fromstring(z.read(sheet_path))
        rows = []
        for r in sheet.findall("m:sheetData/m:row", NS):
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
            rows.append((int(r.get("r")), row))
    if not rows:
        raise ValueError("worksheet is empty")
    header = {k: clean(v) for k, v in rows[0][1].items() if clean(v)}
    required = {"id", "instruction", "content", "answer"}
    if not required.issubset(header.values()):
        raise ValueError(f"missing columns: {sorted(required - set(header.values()))}")
    if len(set(header.values())) != len(header):
        raise ValueError("duplicate column names")
    return [
        dict({header[k]: v for k, v in r.items() if k in header}, _sheet_row=n)
        for n, r in rows[1:]
    ]


def clean(s):
    if s is None:
        return ""
    s = str(s).replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in s.strip().split("\n"))


def build(rows, version="v1"):
    items, last, suffix = [], None, 0
    for i, original in enumerate(rows, start=2):
        r = dict(original)
        i = r.pop("_sheet_row", i)
        if not any(clean(v) for v in r.values()):
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
        if m is None:
            sys.exit(f"row {i}: invalid exercise id {rid!r}")
        visual = clean(r.get("needs_visual")).lower()
        if visual not in ("", "0", "0.0", "false", "no", "1", "1.0", "true", "yes"):
            sys.exit(f"row {i} ({rid}): invalid needs_visual value {visual!r}")
        item = {
            "id": rid,
            "grade": m.group(1),
            "part": clean(r.get("part")),
            "lesson": clean(r.get("lesson")),
            "section": clean(r.get("section")),
            "block": clean(r.get("block")),
            "icon": clean(r.get("icon")),
            "needs_visual": visual in ("1", "1.0", "true", "yes"),
            "mapping": clean(r.get("mapping")),
            "instruction": clean(r.get("instruction")),
            "content": clean(r.get("content")),
            "answer": clean(r.get("answer")),
            "answer_key": clean(r.get("answer_key")),
            "pdf_page_start": clean(r.get("pdf_page_start")),
            "sheet_row": i,
        }
        if version == "v0":
            item.update(OVERRIDES.get(rid, {}))
        elif item["grade"] not in {"1", "2", "3", "4"} or item["needs_visual"]:
            sys.exit(f"row {i} ({rid}): v1 requires grades 1–4 and no external picture dependency")
        if not item["instruction"] or not item["answer"]:
            sys.exit(f"row {i} ({rid}): empty instruction or answer")
        items.append(item)
    dupes = [k for k, n in Counter(it["id"] for it in items).items() if n > 1]
    if dupes:
        sys.exit(f"duplicate ids: {dupes}")
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", choices=["v0", "v1"], default="v1")
    ap.add_argument("--xlsx", type=Path)
    ap.add_argument("--sheet", help="worksheet name (v1 default: clean; v0 default: first sheet)")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    legacy = args.version == "v0"
    args.xlsx = args.xlsx or ROOT / "data" / ("sample.xlsx" if legacy else "clean_60_primary_school.xlsx")
    args.out = args.out or ROOT / "bench" / "data" / ("ykt_sample.jsonl" if legacy else "ykt_primary_v1.jsonl")
    sheet_name = args.sheet or (None if legacy else "clean")

    try:
        rows = read_xlsx(args.xlsx, sheet_name)
    except (ValueError, KeyError, zipfile.BadZipFile) as e:
        sys.exit(str(e))
    items = build(rows, version=args.version)
    if not legacy and len(items) != 60:
        sys.exit(f"v1 requires exactly 60 items, found {len(items)}")
    source = str(args.xlsx.resolve().relative_to(ROOT)) if args.xlsx.resolve().is_relative_to(ROOT) else args.xlsx.name
    if not legacy:
        for item in items:
            item.update(dataset_version="v1", source_file=source, source_sheet=sheet_name)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    if not legacy:
        generated_rows = {r["_sheet_row"] for r in rows if not clean(r.get("id"))}
        manifest = {
            "dataset_version": "v1",
            "source_file": source,
            "source_sheet": sheet_name,
            "source_sha256": hashlib.sha256(args.xlsx.read_bytes()).hexdigest(),
            "dataset_sha256": hashlib.sha256(args.out.read_bytes()).hexdigest(),
            "item_count": len(items),
            "by_grade": dict(sorted(Counter(it["grade"] for it in items).items())),
            "needs_visual": sum(it["needs_visual"] for it in items),
            "generated_ids": [
                {"sheet_row": it["sheet_row"], "id": it["id"]}
                for it in items if it["sheet_row"] in generated_rows
            ],
        }
        args.out.with_suffix(".manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(items)} items -> {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}")
    print("by grade:", dict(sorted(Counter(it["grade"] for it in items).items(), key=lambda kv: [int(x) for x in kv[0].split("-")])))
    print("needs_visual:", sum(it["needs_visual"] for it in items))


if __name__ == "__main__":
    main()
