"""Aggregate strict accuracy and partial credit, with missing tasks worth zero."""

import argparse
import json
from pathlib import Path


def aggregate(rows):
    count = len(rows)
    return {
        "reward": sum((row or {}).get("reward", 0.0) for row in rows) / count if count else 0.0,
        "partial_credit": sum((row or {}).get("partial_credit", 0.0) for row in rows) / count if count else 0.0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    args.output.write_text(json.dumps(aggregate(rows)) + "\n")
