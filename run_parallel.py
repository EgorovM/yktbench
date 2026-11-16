"""Run model queues concurrently and grade completed responses immediately."""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import ykt_eval


MODELS = [
    'fable-5.2',
    'gemini-4-carbon',
    'astra',
    'opus-5.5-eval',
    'sol-6.1-eval',
    'deepseek-v4.1-flash',
    'qwen-3.8-2.4t-a95b',
    'inkling-nvfp4',
    'grok-4.7',
    'inkling-2-small',
    'inkling-flagship',
    'muse-spark-open',
    'glm-5.3',
    'qwen-3.8-flash',
    'kimi-k3.1-pro',
    'qwen-3.8-27b',
    'gigachat-3.5',
    'gemma-4-31b',
    'mistral-large-4',
    'minimax-m3.1-flash',
]


def read_log(run_dir, name, fields):
    path = run_dir / name
    return ykt_eval.Log(path, fields).latest if path.exists() else {}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--solver-system", type=Path, required=True)
    ap.add_argument("--judge-system", type=Path)
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--judge", default="sol-6.1")
    ap.add_argument("--config", type=Path, default=Path(__file__).with_name("models_vals_modal.toml"))
    ap.add_argument("--workers-per-model", type=int, default=16)
    ap.add_argument("--grok-workers", type=int, default=90)
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args()
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    models = args.models.split(",")
    items = [json.loads(s) for s in args.data.read_text().splitlines() if s.strip()]
    expected = {(model, item["id"], 0) for model in models for item in items}
    base = [sys.executable, str(Path(__file__).with_name("ykt_eval.py")),
            "--data", str(args.data.resolve()), "--solver-system", str(args.solver_system.resolve()),
            "--run-dir", str(run_dir), "--judges", args.judge]
    base += ["--config", str(args.config.resolve())]
    if args.judge_system:
        base += ["--judge-system", str(args.judge_system.resolve())]
    subprocess.run([base[0], base[1], "check", *base[2:], "--models", args.models], check=True)
    jobs, tries, handles = {}, {}, []
    grade_job = None
    last_report = 0
    grade_retries = 0

    def start(kind, selected, workers, suffix):
        log = (run_dir / f"{kind}-{suffix}.log").open("a")
        handles.append(log)
        return subprocess.Popen([base[0], base[1], kind, *base[2:], "--models", selected,
                                 "--workers", str(workers)], stdout=log, stderr=subprocess.STDOUT)

    try:
        while True:
            responses = read_log(run_dir, "responses.jsonl", ["model", "item_id", "sample"])
            grades = read_log(run_dir, "judgments.jsonl", ["judge", "model", "item_id", "sample"])
            good = {k for k in expected if k in responses and not responses[k].get("error")}
            judged = {k for k in good if (j := grades.get((args.judge,) + k)) and not j.get("error")
                      and j.get("response_ts") == responses[k]["ts"]}
            for model in models:
                if model in jobs and jobs[model].poll() is None:
                    continue
                missing = [k for k in expected - good if k[0] == model]
                if missing and tries.get(model, 0) <= args.retries:
                    tries[model] = tries.get(model, 0) + 1
                    workers = args.grok_workers if model == "grok-4.7" else args.workers_per_model
                    jobs[model] = start("solve", model, workers, f"{model}-{tries[model]}")
                    print(f"Started {model}: {len(missing)} remaining, {workers} workers", flush=True)
            if grade_job is not None and grade_job.poll() is not None:
                if grade_job.returncode:
                    grade_retries += 1
                grade_job = None
            if good - judged and grade_job is None and grade_retries <= 3:
                grade_job = start("judge", args.models, 32, "live")
            active = any(job.poll() is None for job in jobs.values())
            snapshot = {
                "updated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "expected": len(expected), "responses": len(good), "graded": len(judged),
                "complete": len(judged) == len(expected), "rows": [],
            }
            for model in models:
                keys = [k for k in judged if k[0] == model]
                rs = [responses[k] for k in good if k[0] == model]
                js = [grades[(args.judge,) + k] for k in keys]
                limit = ykt_eval.load_config(args.config)[model].get("max_tokens", 33000)
                snapshot["rows"].append({
                    "model": model, "answers": len(rs), "graded": len(js), "total": len(items),
                    "correct": sum(j["strict"] for j in js),
                    "accuracy": 100 * sum(j["strict"] for j in js) / len(js) if js else None,
                    "partial": 100 * sum(j["score"] for j in js) / len(js) if js else None,
                    "max_output_tokens": max((r.get("output_tokens") or 0 for r in rs), default=0),
                    "over_limit": sum((r.get("output_tokens") or 0) > limit for r in rs),
                })
            (run_dir / "progress.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
            if time.monotonic() - last_report > 30:
                print(f"Progress: {len(good)}/{len(expected)} answers, {len(judged)} graded", flush=True)
                if judged:
                    subprocess.run([base[0], base[1], "report", *base[2:]], stdout=subprocess.DEVNULL)
                last_report = time.monotonic()
            if len(judged) == len(expected):
                subprocess.run([base[0], base[1], "report", *base[2:]], stdout=subprocess.DEVNULL, check=True)
                print("COMPLETE", flush=True)
                return 0
            if not active and grade_job is None and all(tries.get(m, 0) > args.retries or
                    all(k in good for k in expected if k[0] == m) for m in models):
                print("INCOMPLETE: API errors remain; saved results are resumable.", flush=True)
                return 1
            time.sleep(3)
    finally:
        for handle in handles:
            handle.close()


if __name__ == "__main__":
    sys.exit(main())
