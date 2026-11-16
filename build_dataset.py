"""Shared XLSX reader and Unicode normalization for the 90-question benchmark."""

import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
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


def build(rows):
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
                rid = f"vals90-row-{i:03d}"
            else:
                suffix += 1
                rid = f"{clean(last['id'])}{chr(ord('a') + suffix)}"  # 2nd row -> b
                for k in INHERIT:
                    if not clean(r.get(k)):
                        r[k] = last.get(k)
        m = re.match(r"g(\d+(?:-\d+)?)", rid)
        visual = clean(r.get("needs_visual")).lower()
        if visual not in ("", "0", "0.0", "false", "no", "1", "1.0", "true", "yes"):
            sys.exit(f"row {i} ({rid}): invalid needs_visual value {visual!r}")
        item = {
            "id": rid,
            "grade": m.group(1) if m else clean(r.get("grade")).removesuffix(".0") or "unspecified",
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
        if guidance := clean(r.get("eval_instruction")):
            item["eval_instruction"] = guidance
        if not item["instruction"] or not item["answer"]:
            sys.exit(f"row {i} ({rid}): empty instruction or answer")
        items.append(item)
    dupes = [k for k, n in Counter(it["id"] for it in items).items() if n > 1]
    if dupes:
        sys.exit(f"duplicate ids: {dupes}")
    return items
