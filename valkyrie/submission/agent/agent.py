"""A text-only model runner for the exported Valkyrie tasks."""

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers import make_provider


INPUT_START = "<!-- YKT_MODEL_INPUT -->\n"
INPUT_END = "\n<!-- YKT_MODEL_INPUT_END -->"
FINAL_MARKER = re.compile(r"\**\s*хоруй\s*\**\s*[:：]\s*\**", re.IGNORECASE)


def model_input(statement):
    if statement.count(INPUT_START) != 1 or statement.count(INPUT_END) != 1:
        raise ValueError("The task does not contain exactly one model input")
    return statement.split(INPUT_START, 1)[1].split(INPUT_END, 1)[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem_statement", type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("/workspace"))
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    config = tomllib.loads((bundle / "models.toml").read_text())["models"]
    provider = make_provider(args.model, config[args.model])
    statement = args.problem_statement.read_text(encoding="utf-8")
    user = model_input(statement)
    system = statement.split(INPUT_START, 1)[0].strip()
    if not system:
        raise ValueError("The task contains no model instructions")
    result = provider.complete(system, user)
    markers = list(FINAL_MARKER.finditer(result.text or ""))
    final = (result.text[markers[-1].end():].strip().strip("*").strip()
             if markers else (result.text or "").strip()[-3000:])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "answer.txt").write_text(final, encoding="utf-8")
    limit = config[args.model]["max_tokens"]
    record = {
        "model": args.model,
        "model_id": config[args.model]["model"],
        "response": result.text,
        "final_answer": final,
        "has_marker": bool(markers),
        "served_by": result.served_by,
        "stop_reason": result.stop_reason,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "requested_output_limit": limit,
        "over_limit": (result.output_tokens or 0) > limit,
        "latency_s": result.latency_s,
        **result.extra,
    }
    (args.output_dir / "response.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import os

        if path := os.environ.get("VALKYRIE_ERROR_PATH"):
            Path(path).write_text(f"ModelAPIError: {type(error).__name__}\n")
        print(f"Model runner failed: {type(error).__name__}", file=sys.stderr)
        sys.exit(1)
