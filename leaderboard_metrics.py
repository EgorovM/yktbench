"""Collect final-response latency and recorded API charges for published boards."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

from model_names import MODEL_NAMES, model_company, model_name


ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / "data/leaderboard_metrics.json"
START = "<!-- COST_LATENCY_START -->"
END = "<!-- COST_LATENCY_END -->"
BOARDS = {
    "v0": ("LEADERBOARD.md", "data/ykt_sample.jsonl", "results/main"),
    "v1": ("LEADERBOARD_60.md", "data/ykt_primary_v1.jsonl", "results/v1"),
    "vals_90": ("LEADERBOARD_90.md", "data/vals_90.jsonl", "results/vals_90"),
}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def published_models(path):
    names = {}
    for alias, (name, _) in MODEL_NAMES.items():
        names.setdefault(name, alias)
    found, table = [], False
    for line in path.read_text().splitlines():
        if line.startswith("| Model Name"):
            table = True
            continue
        if not table:
            continue
        if not line.startswith("|"):
            break
        label = line.split("|")[1].strip().replace("**", "").replace(" (judge model)", "")
        if label in names:
            found.append(names[label])
    return found


def select_local(path, models, item_ids):
    latest = {}
    for row in read_jsonl(path):
        if row.get("model") in models and row.get("item_id") in item_ids and row.get("sample", 0) == 0:
            latest[row["model"], row["item_id"]] = row
    return {model: {item: row for (name, item), row in latest.items()
                    if name == model and not row.get("error")} for model in models}


def response_files(folder, item_ids):
    records = {}
    for path in sorted(folder.rglob("response.json")):
        item = next((part for part in path.relative_to(folder).parts if part in item_ids), None)
        if item:
            records[item] = json.loads(path.read_text())
    return records


def hosted_records(base, models, item_ids, download=False):
    runs = json.loads((base / "valkyrie_runs.json").read_text())
    published = json.loads((ROOT / "valkyrie/leaderboard_snapshot.json").read_text())
    graded = {row["model"]: set(row.get("task_rewards", {})) for row in published["rows"]}
    records = {model: {} for model in models}
    cache = ROOT / "results/leaderboard_metrics/outputs"
    for run in runs:
        model, run_id = run["model"], run.get("run_id")
        if model not in records or not run_id or not graded.get(model):
            continue
        archive = None
        for folder in (base / "hosted/artifacts" / model / run_id,
                       base / "hosted/artifacts" / model, cache / run_id):
            # Filtered task archives omit yakut.json. This cache directory is
            # already keyed by run ID and is published atomically by the CLI.
            if folder == cache / run_id and folder.is_dir():
                archive = folder
                break
            metadata = folder / "yakut.json"
            if metadata.exists() and str(json.loads(metadata.read_text()).get("benchmark_id")) == run_id:
                archive = folder
                break
        if archive is None and download:
            archive = cache / run_id
            selected = sorted(graded[model] & item_ids)
            print(model, "downloading available response artifacts", flush=True)
            result = subprocess.run(["valkyrie", "run", "outputs", run_id, "--task-ids", ",".join(selected),
                                     "--output-dir", str(archive)], text=True, capture_output=True)
            if result.returncode:
                print(model, "artifact download unavailable", flush=True)
                archive = None
        if archive:
            records[model].update({item: row for item, row in response_files(archive, item_ids).items()
                                   if item in graded[model]})
    return records


def summarize(records, expected, costs):
    rows = list(records.values())
    latency = [row["latency_s"] for row in rows
               if isinstance(row.get("latency_s"), (int, float)) and math.isfinite(row["latency_s"])]
    latency.sort()
    usage = [row for row in rows if isinstance(row.get("input_tokens"), int)
             and isinstance(row.get("output_tokens"), int)]
    costed = [row for row in rows if costs.get(row.get("response_id"), {}).get("total_cost") is not None]
    ids = {row["response_id"] for row in costed}
    return {
        "questions": expected, "response_records": len(rows), "latency_records": len(latency),
        "mean_s": statistics.mean(latency) if latency else None,
        "median_s": statistics.median(latency) if latency else None,
        "p95_s": latency[math.ceil(0.95 * len(latency)) - 1] if latency else None,
        "max_s": max(latency) if latency else None,
        "timeouts": sum(bool(row.get("timed_out")) for row in rows),
        "usage_records": len(usage),
        "input_tokens": sum(row["input_tokens"] for row in usage) if usage else None,
        "output_tokens": sum(row["output_tokens"] for row in usage) if usage else None,
        "costed_answers": len(costed), "costed_requests": len(ids),
        "known_api_cost_usd": sum(costs[rid]["total_cost"] for rid in ids) if ids else None,
    }


def fetch_cost(generation_id, key):
    url = "https://openrouter.ai/api/v1/generation?" + urllib.parse.urlencode({"id": generation_id})
    for attempt in range(5):
        try:
            request = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.load(response)["data"]
            return {"response_id": generation_id, "total_cost": data.get("total_cost"),
                    "model": data.get("model"), "provider": data.get("provider_name"),
                    "source": "OpenRouter generation API"}
        except urllib.error.HTTPError as error:
            if error.code in (401, 403):
                raise RuntimeError(f"Cost metadata authorization failed: HTTP {error.code}") from None
            if error.code in (429, 500, 502, 503, 504) and attempt < 4:
                try:
                    retry_after = float(error.headers.get("Retry-After", "0"))
                except ValueError:
                    retry_after = 0
                time.sleep(min(30, max(2 ** attempt, retry_after)))
                continue
            return {"response_id": generation_id, "total_cost": None, "http_status": error.code}
        except (urllib.error.URLError, TimeoutError):
            if attempt < 4:
                time.sleep(2 ** attempt)
                continue
            return {"response_id": generation_id, "total_cost": None, "error": "network unavailable"}


def render(dataset, models, snapshot=None):
    if snapshot is None:
        snapshot = json.loads(SNAPSHOT.read_text()) if SNAPSHOT.exists() else {"datasets": {}}
    saved = snapshot.get("datasets", {}).get(dataset, {})
    rows = saved.get("models", {})
    if not rows:
        return ""
    lines = [START, "", "### Cost and latency", "",
             f"Metrics snapshot: {snapshot['updated_utc']}. Latencies are seconds per final selected response; p95 uses nearest rank.",
             "Timeouts are included. Latency excludes grading and sandbox setup; it can include client startup and transport.",
             "Token totals contain reported usage only; † marks incomplete usage. Coverage is out of the full question set.", "",
             "| Model Name | Company | Latency records | Avg (s) | Median (s) | p95 (s) | Max (s) | Timeouts | Input tokens | Output tokens | Known API cost (USD) | Cost coverage |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for model in models:
        row = rows.get(model, {})
        n = row.get("questions", saved.get("questions", 0))
        number = lambda key: f"{row[key]:.1f}" if row.get(key) is not None else "—"
        incomplete = row.get("usage_records", 0) < row.get("response_records", 0)
        tokens = lambda key: (f"{row[key]:,}" + ("†" if incomplete else "")) if row.get(key) is not None else "—"
        cost = f"{row['known_api_cost_usd']:.4f}" if row.get("known_api_cost_usd") is not None else "—"
        name = model_name(model) + (" **(judge model)**" if model == "sol-6.1-eval" else "")
        lines.append(f"| {name} | {model_company(model)} | {row.get('latency_records', 0)}/{n} | "
                     + " | ".join(number(key) for key in ("mean_s", "median_s", "p95_s", "max_s"))
                     + f" | {row.get('timeouts', 0)} | {tokens('input_tokens')} | {tokens('output_tokens')} | {cost} | {row.get('costed_answers', 0)}/{n} |")
    lines += ["", "Known API cost is the sum of retrieved OpenRouter charges for the selected answers, not total benchmark spend.",
              "A dash means unavailable, not free. Cost coverage counts answers with a retrieved charge; duplicate request IDs are charged once.",
              "Judging, discarded/failed attempts, Modal token or GPU hosting charges (including warmup), storage, and net credit adjustments are excluded.",
              "Provider changes and native reasoning translations remain documented in the run notes; latency figures are not measurements of thinking time.",
              "[Metric snapshot and definitions](data/leaderboard_metrics.json) · [OpenRouter cost metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation)",
              "", END]
    return "\n".join(lines)


def insert_table(text, table):
    if START in text:
        start, rest = text.split(START, 1)
        _, end = rest.split(END, 1)
        return start + table + end
    lines = text.splitlines()
    in_table = False
    for index, line in enumerate(lines):
        if line.startswith("| Model Name"):
            in_table = True
        elif in_table and not line.startswith("|"):
            lines[index:index] = ["", table, ""]
            return "\n".join(lines) + "\n"
    raise ValueError("No published leaderboard table found")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-costs", action="store_true")
    parser.add_argument("--download-outputs", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    selected, model_orders = {}, {}
    for dataset, (board, data, base) in BOARDS.items():
        models = published_models(ROOT / board)
        ids = {row["id"] for row in read_jsonl(ROOT / data)}
        records = (hosted_records(ROOT / base, models, ids, args.download_outputs) if dataset == "vals_90"
                   else select_local(ROOT / base / "responses.jsonl", models, ids))
        selected[dataset] = (len(ids), records)
        model_orders[dataset] = models
    cache = ROOT / "results/leaderboard_metrics/openrouter_costs.jsonl"
    cache.parent.mkdir(parents=True, exist_ok=True)
    costs = {row["response_id"]: row for row in read_jsonl(cache)} if cache.exists() else {}
    ids = {row["response_id"] for _, models in selected.values() for rows in models.values()
           for row in rows.values() if str(row.get("response_id", "")).startswith("gen-")}
    missing = sorted(ids - costs.keys())
    print("Cost metadata:", len(ids), "request IDs,", len(missing), "uncached", flush=True)
    if args.fetch_costs and missing:
        from dotenv import dotenv_values
        key = {**dotenv_values(ROOT / ".env"), **os.environ}["OPENROUTER_API_KEY"]
        with ThreadPoolExecutor(max_workers=8) as pool, cache.open("a") as output:
            futures = [pool.submit(fetch_cost, rid, key) for rid in missing]
            for index, future in enumerate(as_completed(futures), 1):
                row = future.result()
                costs[row["response_id"]] = row
                output.write(json.dumps(row) + "\n")
                output.flush()
                if index % 100 == 0 or index == len(missing):
                    print("Retrieved", index, "/", len(missing), "cost records", flush=True)
    snapshot = {"updated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "cost_currency": "USD", "latency_unit": "seconds", "percentile_method": "nearest rank",
                "scope": "Final selected solver responses; no judge, discarded attempts, Modal hosting, or credits",
                "datasets": {}}
    for dataset, (expected, models) in selected.items():
        snapshot["datasets"][dataset] = {"questions": expected, "models": {
            model: summarize(records, expected, costs) for model, records in models.items()}}
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    if args.publish:
        for dataset, (board, _, _) in BOARDS.items():
            path = ROOT / board
            path.write_text(insert_table(path.read_text(), render(dataset, model_orders[dataset], snapshot)), encoding="utf-8")
    print("Saved metric snapshot:", SNAPSHOT, flush=True)


if __name__ == "__main__":
    main()
