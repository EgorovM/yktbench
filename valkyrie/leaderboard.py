"""Publish a reproducible Markdown leaderboard from collected Valkyrie results."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from model_names import model_company, model_name


def render(snapshot):
    lines = ["# Yakut Benchmark Leaderboard", "", "## vals_90", "",
             f"Snapshot: {snapshot['updated_utc']}. Scores are percentages.", "",
             "**Evaluation is in progress.** Partial scores use graded questions only;",
             "their denominators differ and they are not final rankings. API failures",
             "remain ungraded. Grade cells show accuracy followed by graded/total questions.", "",
             "| Model Name | Company | All | Grade 1 | Grade 2 | Grade 3 | Grade 4 | Graded | Partial credit | Max reported output tokens | Over limit | Status |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    def score(value):
        return f"{value:.1f}" if value is not None else "—"
    rows = sorted(snapshot["rows"], key=lambda row: (not row.get("complete"), row.get("accuracy") is None, -(row.get("accuracy") or 0)))
    for row in rows:
        name = model_name(row["model"]) + (" **(judge model)**" if row.get("judge_model") else "")
        grades = []
        for grade in ("1", "2", "3", "4"):
            cell = row["grades"][grade]
            grades.append(f"{score(cell['accuracy'])} ({cell['graded']}/{cell['total']})")
        status = "Complete" if row.get("complete") else ("API errors" if row["status"] == "ERROR" else "Running")
        lines.append(f"| {name} | {model_company(row['model'])} | {score(row.get('accuracy'))} | "
                     + " | ".join(grades) + f" | {row.get('graded', 0)}/90 | {score(row.get('partial'))} | "
                     + f"{row['max_output_tokens'] if row.get('max_output_tokens') is not None else '—'} | "
                     + f"{row['over_limit'] if row.get('over_limit') is not None else '—'} | {status} |")
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
    parser.add_argument("--output", type=Path, default=Path("LEADERBOARD.md"))
    parser.add_argument("--snapshot", type=Path, default=Path("valkyrie/leaderboard_snapshot.json"))
    args = parser.parse_args()
    items = [json.loads(line) for line in args.dataset.read_text().splitlines() if line.strip()]
    snapshot = json.loads((args.collected / "leaderboard.json").read_text())
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
    # Preserve the historical tables while updating the live snapshot.
    history = ""
    if args.output.exists():
        old = args.output.read_text()
        if "<!-- HISTORICAL_RESULTS -->" in old:
            history = old[old.index("<!-- HISTORICAL_RESULTS -->"):]
    args.output.write_text(render(snapshot) + history, encoding="utf-8")


if __name__ == "__main__":
    main()
