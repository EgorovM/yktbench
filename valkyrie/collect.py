"""Collect hosted run scores and optional response artifacts into a leaderboard."""

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from model_names import model_company, model_name


def summarize(results, total):
    rewards = [v["rewards"] for v in results.values() if isinstance(v, dict) and isinstance(v.get("rewards"), dict)]
    graded = len(rewards)
    return {
        "graded": graded, "questions": total,
        "correct": sum(r.get("reward", 0) for r in rewards),
        "accuracy": 100 * sum(r.get("reward", 0) for r in rewards) / graded if graded else None,
        "partial": 100 * sum(r.get("partial_credit", 0) for r in rewards) / graded if graded else None,
    }


def merge_graded(results, latest):
    """Retain successful answers when a recovery run has no result for a task."""
    for key, value in latest.items():
        if isinstance(value, dict) and isinstance(value.get("rewards"), dict):
            results[key] = value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--artifacts", action="store_true")
    args = parser.parse_args()
    from valkyrie.cli.client import call
    from valkyrie.sdk.errors import ValkyrieAPIError

    runs = json.loads(args.runs.read_text())
    groups = {}
    for run in runs:
        groups.setdefault(run["model"], []).append(run)
    args.out.mkdir(parents=True, exist_ok=True)

    async def collect(client):
        gate = asyncio.Semaphore(8)
        async def one(group):
            async with gate:
                run = group[0]
                if not run.get("run_id"):
                    return {"model": run["model"], "status": "launch_error", "error": run.get("error")}
                merged, states = {}, []
                total = 0
                for attempt in group:
                    if not attempt.get("run_id"):
                        continue
                    rid = UUID(attempt["run_id"])
                    state = await client.benchmarks.fetch(rid)
                    states.append(state.status.value)
                    total = max(total, state.total_tasks)
                    try:
                        result = await client.runs.results(rid)
                        data = result.model_dump(mode="json")
                        merge_graded(merged, data.get("evaluation_results") or {})
                    except ValkyrieAPIError as error:
                        if error.status_code not in (404, 409):
                            raise
                data = {"evaluation_results": merged, "run_ids": [r["run_id"] for r in group if r.get("run_id")]}
                (args.out / f"{run['model']}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
                row = summarize(merged, total)
                status = "FINISHED" if row["graded"] == total else ("IN_PROGRESS" if any(s not in ("FINISHED", "ERROR", "STOPPED") for s in states) else "ERROR")
                row.update(model=run["model"], run_id=run["run_id"], run_ids=data["run_ids"], status=status,
                           task_rewards={key: value["rewards"] for key, value in merged.items()},
                           model_name=model_name(run["model"]), company=model_company(run["model"]),
                           complete=row["graded"] == total,
                           max_output_tokens=None, over_limit=None,
                           judge_model=run["model"] == "sol-6.1-eval")
                return row
        return await asyncio.gather(*(one(group) for group in groups.values()))

    rows = call(collect)
    if args.artifacts:
        for row in rows:
            if not row.get("complete"):
                partial_output = args.out.parent / "partial_usage" / row["model"]
                observed = {}
                for path in sorted(partial_output.rglob("response.json")):
                    observed[path.relative_to(partial_output).parts[0]] = json.loads(path.read_text())
                if observed:
                    row["max_output_tokens"] = max(r.get("output_tokens") or 0 for r in observed.values())
                    row["over_limit"] = sum(bool(r.get("over_limit")) for r in observed.values())
                    row["timed_out"] = sum(bool(r.get("timed_out")) for r in observed.values())
                    row["responses_with_usage"] = len(observed)
                continue
            output = args.out / "artifacts" / row["model"]
            responses = {}
            for run_id in row["run_ids"]:
                run_output = output if len(row["run_ids"]) == 1 else output / run_id
                marker = run_output / ".downloaded"
                if not marker.exists():
                    subprocess.run(["valkyrie", "run", "outputs", run_id, "--output-dir", str(run_output)], check=True)
                    marker.touch()
                for path in sorted(run_output.rglob("response.json")):
                    key = path.relative_to(run_output).parts[0]
                    responses[key] = json.loads(path.read_text())
            row["max_output_tokens"] = max((r.get("output_tokens") or 0 for r in responses.values()), default=0)
            row["over_limit"] = sum(bool(r.get("over_limit")) for r in responses.values())
            row["timed_out"] = sum(bool(r.get("timed_out")) for r in responses.values())
            row["responses_with_usage"] = len(responses)
    rows.sort(key=lambda r: (r.get("accuracy") is None, -(r.get("accuracy") or 0)))
    report = {"updated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "platform": "Valkyrie", "rows": rows}
    (args.out / "leaderboard.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    lines = ["# Valkyrie leaderboard", "", "Unfinished rows use graded questions only and are provisional.", "",
             "| Model Name | Company | Graded | Accuracy % | Partial % | Max output tokens | Over limit | Status |",
             "|---|---|---:|---:|---:|---:|---:|---|"]
    for row in rows:
        model = model_name(row["model"]) + (" (judge model)" if row.get("judge_model") else "")
        acc = f"{row['accuracy']:.1f}" if row.get("accuracy") is not None else "—"
        part = f"{row['partial']:.1f}" if row.get("partial") is not None else "—"
        lines.append(f"| {model} | {model_company(row['model'])} | {row.get('graded', 0)}/{row.get('questions', 90)} | {acc} | {part} | "
                     f"{row.get('max_output_tokens') if row.get('max_output_tokens') is not None else '—'} | "
                     f"{row.get('over_limit') if row.get('over_limit') is not None else '—'} | {row['status']} |")
    text = "\n".join(lines) + "\n"
    (args.out / "leaderboard.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
