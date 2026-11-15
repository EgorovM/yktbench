"""Collect hosted run scores and optional response artifacts into a leaderboard."""

import argparse
import asyncio
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID


def summarize(results, total):
    rewards = [v["rewards"] for v in results.values() if isinstance(v, dict) and isinstance(v.get("rewards"), dict)]
    graded = len(rewards)
    return {
        "graded": graded, "questions": total,
        "correct": sum(r.get("reward", 0) for r in rewards),
        "accuracy": 100 * sum(r.get("reward", 0) for r in rewards) / graded if graded else None,
        "partial": 100 * sum(r.get("partial_credit", 0) for r in rewards) / graded if graded else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--artifacts", action="store_true")
    args = parser.parse_args()
    from valkyrie.cli.client import call
    from valkyrie.sdk.errors import ValkyrieAPIError

    runs = json.loads(args.runs.read_text())
    args.out.mkdir(parents=True, exist_ok=True)

    async def collect(client):
        gate = asyncio.Semaphore(8)
        async def one(run):
            async with gate:
                if not run.get("run_id"):
                    return {"model": run["model"], "status": "launch_error", "error": run.get("error")}
                rid = UUID(run["run_id"])
                state = await client.benchmarks.fetch(rid)
                try:
                    result = await client.runs.results(rid)
                    data = result.model_dump(mode="json")
                    (args.out / f"{run['model']}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
                    row = summarize(data.get("evaluation_results") or {}, state.total_tasks)
                except ValkyrieAPIError as error:
                    if error.status_code not in (404, 409):
                        raise
                    row = summarize({}, state.total_tasks)
                row.update(model=run["model"], run_id=str(rid), status=state.status.value,
                           complete=row["graded"] == state.total_tasks,
                           max_output_tokens=None, over_limit=None,
                           judge_model=run["model"] == "sol-6.1-eval")
                return row
        return await asyncio.gather(*(one(run) for run in runs))

    rows = call(collect)
    if args.artifacts:
        for row in rows:
            if not row.get("complete"):
                continue
            output = args.out / "artifacts" / row["model"]
            marker = output / ".downloaded"
            if not marker.exists():
                subprocess.run(["valkyrie", "run", "outputs", row["run_id"], "--output-dir", str(output)], check=True)
                marker.touch()
            responses = {}
            for path in output.rglob("response.json"):
                key = path.relative_to(output).parts[0]
                responses[key] = json.loads(path.read_text())
            row["max_output_tokens"] = max((r.get("output_tokens") or 0 for r in responses.values()), default=0)
            row["over_limit"] = sum(bool(r.get("over_limit")) for r in responses.values())
            row["responses_with_usage"] = len(responses)
    rows.sort(key=lambda r: (r.get("accuracy") is None, -(r.get("accuracy") or 0)))
    report = {"updated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "platform": "Valkyrie", "rows": rows}
    (args.out / "leaderboard.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    lines = ["# Valkyrie leaderboard", "", "Unfinished rows use graded questions only and are provisional.", "",
             "| Model | Graded | Accuracy % | Partial % | Max output tokens | Over limit | Status |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for row in rows:
        model = row["model"] + (" (judge model)" if row.get("judge_model") else "")
        acc = f"{row['accuracy']:.1f}" if row.get("accuracy") is not None else "—"
        part = f"{row['partial']:.1f}" if row.get("partial") is not None else "—"
        lines.append(f"| {model} | {row.get('graded', 0)}/{row.get('questions', 90)} | {acc} | {part} | "
                     f"{row.get('max_output_tokens') if row.get('max_output_tokens') is not None else '—'} | "
                     f"{row.get('over_limit') if row.get('over_limit') is not None else '—'} | {row['status']} |")
    text = "\n".join(lines) + "\n"
    (args.out / "leaderboard.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
