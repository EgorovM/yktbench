"""Publish a reproducible Markdown leaderboard from collected Valkyrie results."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from model_names import model_company, model_name
from leaderboard_metrics import render as render_metrics


EXCLUDED_FROM_VALS_90 = {"deepseek-v4"}


def included_rows(snapshot):
    return [row for row in snapshot["rows"] if row["model"] not in EXCLUDED_FROM_VALS_90]


def render(snapshot):
    source_rows = included_rows(snapshot)
    active = any(row["status"] not in ("FINISHED", "ERROR", "STOPPED", "launch_error") for row in source_rows)
    complete = sum(bool(row.get("complete")) for row in source_rows)
    status = ("**Evaluation is in progress.**" if active else
              f"**Evaluation incomplete: {complete}/{len(source_rows)} models fully graded.**"
              if complete < len(source_rows) else "**Evaluation complete.**")
    lines = ["# Yakut Benchmark Leaderboard", "", "## vals_90", "",
             f"Snapshot: {snapshot['updated_utc']}. Scores are percentages.", "",
             status + " Partial scores use graded questions only;",
             "their denominators differ and they are not final rankings. Failed tasks",
             "remain ungraded. Grade columns show accuracy percentages.",
             "Bold accuracy marks the best completed run; bold token usage marks the largest observed report.", "",
             "| Model Name | Company | All | Partial credit | Grade 1 | Grade 2 | Grade 3 | Grade 4 | Graded | Max reported output tokens | Over limit | Status |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    def score(value):
        return f"{value:.1f}" if value is not None else "—"
    rows = sorted(source_rows, key=lambda row: (not row.get("complete"), row.get("accuracy") is None, -(row.get("accuracy") or 0)))
    best_accuracy = max((row["accuracy"] for row in rows if row.get("complete") and row.get("accuracy") is not None), default=None)
    max_tokens = max((row["max_output_tokens"] for row in rows if row.get("max_output_tokens") is not None), default=None)
    for row in rows:
        name = model_name(row["model"]) + (" **(judge model)**" if row.get("judge_model") else "")
        grades = []
        for grade in ("1", "2", "3", "4"):
            cell = row["grades"][grade]
            grades.append(score(cell["accuracy"]))
        status = ("Complete" if row.get("complete") else
                  "Needs credits" if row.get("blocked_reason") == "insufficient_credits" else
                  "Run errors" if row["status"] in ("ERROR", "STOPPED") else "Running")
        accuracy = score(row.get("accuracy"))
        if row.get("complete") and row.get("accuracy") == best_accuracy:
            accuracy = f"**{accuracy}**"
        tokens = str(row["max_output_tokens"]) if row.get("max_output_tokens") is not None else "—"
        if row.get("max_output_tokens") is not None and row["max_output_tokens"] == max_tokens:
            tokens = f"**{tokens}**"
        lines.append(f"| {name} | {model_company(row['model'])} | {accuracy} | {score(row.get('partial'))} | "
                     + " | ".join(grades) + f" | {row.get('graded', 0)}/90 | "
                     + f"{tokens} | "
                     + f"{row['over_limit'] if row.get('over_limit') is not None else '—'} | {status} |")
    extended = render_metrics("vals_90", [row["model"] for row in rows])
    if extended:
        lines += ["", extended]
    if any(row["model"] in ("qwen-3.8-2.4t-a95b", "inkling-nvfp4", "muse-spark-open", "kimi-k3.1-pro") for row in rows):
        lines += ["", "The expanded Modal runs use Muse Spark Open, Kimi K3.1 Pro, Qwen3.8 2.4T A95B, and Inkling NVFP4.",
                  "Qwen3.8 2.4T A95B replaces the Max-0902 row. Inkling NVFP4 and the fresh Inkling flagship evaluation have separate rows.",
                  "Gemini 4 Carbon replaces the empty Argon row. Earlier variant scores remain archived in the run records and are not merged.",
                  "[Modal run settings and IDs](valkyrie/modal_round4.json) · [Modal model configuration](models_vals_modal.toml)"]
    lines += ["", "Two questions have unspecified grades; they count in All, but not in grade columns.",
              "Twelve source rows carry picture flags; solvers receive text only. All 90 supplied rows are retained.", "",
              "Solvers have no browsing or tools, a 900-second answer deadline, and a requested",
              "33,000-token output limit (Gemma: 16,384). GPT-6.1 Sol grades with a 16,000-token",
              "budget and receives each question's `eval_instruction`; solvers do not.",
              "Max reported output tokens is the largest downloaded usage report, including reasoning tokens where reported.",
              "Usage for unfinished runs may cover only a subset of graded answers.",
              "A dash means usage has not yet been collected. Over-limit answers are retained and flagged.", "",
              "[Run IDs](valkyrie/RUNS.md) · [Dataset](data/vals_90.jsonl) · [Settings](models_vals.toml)", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collected", type=Path, default=Path("results/vals_90/hosted"))
    parser.add_argument("--dataset", type=Path, default=Path("data/vals_90.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("LEADERBOARD_90.md"))
    parser.add_argument("--snapshot", type=Path, default=Path("valkyrie/leaderboard_snapshot.json"))
    args = parser.parse_args()
    items = [json.loads(line) for line in args.dataset.read_text().splitlines() if line.strip()]
    snapshot = json.loads((args.collected / "leaderboard.json").read_text())
    snapshot["rows"] = included_rows(snapshot)
    for row in snapshot["rows"]:
        task_rewards = row.get("task_rewards")
        if task_rewards is None:
            path = args.collected / (row["model"] + ".json")
            results = json.loads(path.read_text()).get("evaluation_results", {}) if path.exists() else {}
            task_rewards = {key: value["rewards"] for key, value in results.items()
                            if isinstance(value.get("rewards"), dict)}
        row["grades"] = {}
        for grade in ("1", "2", "3", "4"):
            subset = [item for item in items if str(item["grade"]) == grade]
            rewards = [task_rewards[item["id"]] for item in subset if item["id"] in task_rewards]
            row["grades"][grade] = {"total": len(subset), "graded": len(rewards),
                                    "accuracy": 100 * sum(r.get("reward", 0) for r in rewards) / len(rewards) if rewards else None}
    args.snapshot.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    args.output.write_text(render(snapshot), encoding="utf-8")


if __name__ == "__main__":
    main()
