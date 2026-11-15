"""Render a shareable leaderboard chart from a saved run summary."""

import argparse
import json
from pathlib import Path
from model_names import model_name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="output basename for SVG and PNG")
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = json.loads(args.summary.read_text(encoding="utf-8"))
    rows = sorted((r for r in data["rows"] if r.get("accuracy") is not None),
                  key=lambda r: (r["accuracy"], r["partial"]))
    fig, ax = plt.subplots(figsize=(10, max(5, len(rows) * 0.48 + 1.6)))
    y = list(range(len(rows)))
    accuracy = [r["accuracy"] for r in rows]
    partial = [r["partial"] for r in rows]
    ax.barh([v + 0.17 for v in y], partial, height=0.3, color="#c6d4e1", label="Partial credit")
    ax.barh([v - 0.17 for v in y], accuracy, height=0.3, color="#2864a0", label="Full-question accuracy")
    for pos, row in enumerate(rows):
        ax.text(row["accuracy"] + 1, pos - 0.17, f"{row['accuracy']:.1f}%", va="center", fontsize=9)
    labels = [model_name(r["model"]) + (" (judge)" if r.get("judge_model") or r["model"] == "sol-6.1-eval" else "") for r in rows]
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score (%)")
    ax.set_title(args.title, loc="left", weight="bold", pad=16)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color="#e8e8e8", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower right", frameon=False)
    fig.text(0.02, 0.015, "No browsing or external tools. Sol also grades the benchmark; its row is self-judged.", fontsize=9, color="#555555")
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out.with_suffix(".svg"), metadata={"Date": None})
    svg = args.out.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    fig.savefig(args.out.with_suffix(".png"), dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
