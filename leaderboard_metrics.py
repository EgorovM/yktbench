"""Publish final-response latency, recorded charges, and token-price estimates."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
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
PRICING_URL = "https://openrouter.ai/api/v1/models"
PRICING_MODELS = {
    "fable-5.2": "anthropic/claude-fable-5.2",
    "astra": "openai/gpt-6-astra",
    "sol-6.1-eval": "openai/gpt-6.1-sol",
    "gemini-4-argon": "google/gemini-4-argon",
    "grok-4.7": "x-ai/grok-4.7",
    "deepseek-v4": "deepseek/deepseek-v4-pro",
    "deepseek-v4.1-flash": "deepseek/deepseek-v4.1-flash",
    "glm-5.3": "z-ai/glm-5.3",
    "inkling-flagship": "thinkingmachines/inkling",
    "inkling-2-small": "thinkingmachines/inkling-2-small",
    "inkling-nvfp4": "thinkingmachines/inkling",
    "muse-spark-open": "meta/muse-spark-open",
    "kimi-k3.1-pro": "moonshotai/kimi-k3.1-pro",
    "qwen-3.8-2.4t-a95b": "qwen/qwen3.8-2.4t-a95b",
    "opus-5.5-eval": "anthropic/claude-opus-5.5",
    "mistral-large-4": "mistralai/mistral-large-4-0",
    "minimax-m3.1-flash": "minimax/minimax-m3.1-flash",
    "qwen-3.8-max": "qwen/qwen3.8-max-0902",
    "qwen-3.8-flash": "qwen/qwen3.8-flash",
    "qwen-3.8-27b": "qwen/qwen3.8-27b",
    "gemma-4-31b": "google/gemma-4-31b-it",
}


def pricing_snapshot(catalog, retrieved_utc):
    """Convert exact paid model IDs' base USD/token rates to USD/million."""
    by_id = {model["id"]: model for model in catalog["data"]}
    models = {}
    for alias, model_id in PRICING_MODELS.items():
        price = by_id[model_id]["pricing"]
        models[alias] = {
            "model_id": model_id,
            "input_usd_per_million": float(Decimal(price["prompt"]) * 1_000_000),
            "output_usd_per_million": float(Decimal(price["completion"]) * 1_000_000),
            "source": "https://openrouter.ai/" + model_id,
            "catalog_pricing": price,
        }
    models["gigachat-3.5"] = {
        "model_id": "ai-sage/GigaChat3.5-432B-A28B",
        "input_usd_per_million": 1.07, "output_usd_per_million": 3.21,
        "source": "User-supplied USD rates on 2026-11-16",
    }
    return {"retrieved_utc": retrieved_utc, "currency": "USD", "unit": "per 1,000,000 tokens",
            "source": PRICING_URL, "basis": "Standard base input/output rates; no caching, batch, time-of-day, or context-tier adjustments",
            "models": models}


def estimated_cost(row, price):
    """Price reported tokens only; missing usage/rates remain unknown."""
    keys = ("input_tokens", "output_tokens")
    rates = ("input_usd_per_million", "output_usd_per_million")
    if any(row.get(key) is None for key in keys) or any(price.get(key) is None for key in rates):
        return None
    return sum(Decimal(str(row[key])) * Decimal(str(price[rate]))
               for key, rate in zip(keys, rates)) / 1_000_000


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
                       base / "hosted/artifacts" / model,
                       base / "partial_usage" / model / run_id, cache / run_id):
            # Filtered task archives omit yakut.json. This cache directory is
            # already keyed by run ID and is published atomically by the CLI.
            if folder in (cache / run_id, base / "partial_usage" / model / run_id) and folder.is_dir():
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
    pricing = snapshot.get("pricing", {})
    if not rows:
        return ""
    lines = [START, "", "### Cost and latency", "",
             f"Metrics snapshot: {snapshot['updated_utc']}. Latencies are seconds per final selected response; p95 uses nearest rank.",
             "Timeouts are included. Latency excludes grading and sandbox setup; it can include client startup and transport.",
             "Token totals contain reported usage only; † marks usage or estimates covering fewer than all questions. Coverage is out of the full question set.",
             f"Pricing snapshot: {pricing.get('retrieved_utc', 'unavailable')}. Input and output prices are USD per 1M tokens.", "",
             "| Model Name | Company | Latency records | Avg (s) | Median (s) | p95 (s) | Max (s) | Timeouts | Input tokens | Output tokens | Usage coverage | Input $/1M | Output $/1M | Estimated cost (USD) | Known API cost (USD) | Cost coverage |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for model in models:
        row = rows.get(model, {})
        n = row.get("questions", saved.get("questions", 0))
        number = lambda key: f"{row[key]:.1f}" if row.get(key) is not None else "—"
        incomplete = row.get("usage_records", 0) < n
        tokens = lambda key: (f"{row[key]:,}" + ("†" if incomplete else "")) if row.get(key) is not None else "—"
        price = pricing.get("models", {}).get(model, {})
        rate = lambda key: f"{price[key]:g}" if price.get(key) is not None else "—"
        estimate = estimated_cost(row, price)
        estimate_text = f"{estimate:.4f}*" + ("†" if incomplete else "") if estimate is not None else "—"
        cost = f"{row['known_api_cost_usd']:.4f}" if row.get("known_api_cost_usd") is not None else estimate_text
        name = model_name(model) + (" **(judge model)**" if model == "sol-6.1-eval" else "")
        lines.append(f"| {name} | {model_company(model)} | {row.get('latency_records', 0)}/{n} | "
                     + " | ".join(number(key) for key in ("mean_s", "median_s", "p95_s", "max_s"))
                     + f" | {row.get('timeouts', 0)} | {tokens('input_tokens')} | {tokens('output_tokens')} | {row.get('usage_records', 0)}/{n} | "
                     + f"{rate('input_usd_per_million')} | {rate('output_usd_per_million')} | {estimate_text} | {cost} | {row.get('costed_answers', 0)}/{n} |")
    lines += ["", "\\* Estimated cost = (reported input tokens × input price + reported output tokens × output price) / 1,000,000.",
              "Estimates use the current OpenRouter catalog's standard base rates; GigaChat uses user-supplied rates of $1.07 input and $3.21 output per 1M tokens.",
              "These are API-equivalent estimates for logged usage, not historical bills or Modal GPU costs. Missing usage is not extrapolated to the full dataset.",
              "Caching, batch discounts, time-of-day offers, and context-tier adjustments are not applied; recorded charges can differ.",
              *( ["Inkling NVFP4 uses standard Inkling API prices for its estimate; its Modal serving variant is recorded separately."]
                 if "inkling-nvfp4" in models else []),
              "Known API cost shows the sum of retrieved OpenRouter charges when available; otherwise it shows the token-based estimate marked with \\*. It is not total benchmark spend.",
              "A dash means no reported token usage or charge is available, not free. Cost coverage counts only answers with a retrieved charge, including when a starred estimate is displayed; duplicate request IDs are charged once.",
              "Judging, discarded/failed attempts, Modal token or GPU hosting charges (including warmup), storage, and net credit adjustments are excluded.",
              "Provider changes and native reasoning translations remain documented in the run notes; latency figures are not measurements of thinking time.",
              "[Metric and pricing snapshot](data/leaderboard_metrics.json) · [Current OpenRouter pricing catalog](https://openrouter.ai/api/v1/models) · [OpenRouter cost metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation)",
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
    parser.add_argument("--refresh-pricing", action="store_true", help="Refresh public OpenRouter base token rates; retain user-supplied GigaChat rates")
    args = parser.parse_args()
    pricing = json.loads(SNAPSHOT.read_text()).get("pricing", {}) if SNAPSHOT.exists() else {}
    if args.refresh_pricing:
        with urllib.request.urlopen(PRICING_URL, timeout=20) as response:
            pricing = pricing_snapshot(json.load(response), datetime.now(timezone.utc).isoformat(timespec="seconds"))
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
                "pricing": pricing,
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
