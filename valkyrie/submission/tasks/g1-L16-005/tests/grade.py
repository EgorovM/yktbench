"""Verifier injected only after a task's model has finished."""

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


SCHEMA = {
    "type": "object",
    "properties": {
        "parts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "reference": {"type": "string"},
                    "candidate": {"type": "string"},
                    "correct": {"type": "boolean"},
                },
                "required": ["reference", "candidate", "correct"],
                "additionalProperties": False,
            },
        },
        "reason": {"type": "string"},
    },
    "required": ["parts", "reason"],
    "additionalProperties": False,
}


def judge_prompt(item, candidate):
    guidance = (f"## Exercise-specific grading instructions (eval_instruction)\n"
                f"{item['eval_instruction']}\n\n") if item.get("eval_instruction") else ""
    return (
        f"## Exercise instruction\n{item['instruction']}\n\n"
        f"## Material\n{item['content'] or '(none)'}\n\n"
        + guidance +
        f"## Reference answer (textbook answer key)\n{item['answer']}\n\n"
        f"## Candidate answer\n{candidate}"
    )


def scores(result):
    parts = result["parts"]
    if not isinstance(parts, list) or any(type(p.get("correct")) is not bool for p in parts):
        raise ValueError("Judge returned invalid part scores")
    correct = sum(p["correct"] for p in parts)
    return {
        "reward": float(bool(parts) and correct == len(parts)),
        "partial_credit": correct / len(parts) if parts else 0.0,
    }


def grade(item, candidate, system, cfg):
    if not candidate.strip():
        return {"parts": [], "reason": "empty answer (not sent to judge)"}
    body = {
        "model": cfg["model"],
        "instructions": system,
        "input": judge_prompt(item, candidate),
        "max_output_tokens": cfg["max_tokens"],
        "reasoning": {"effort": cfg["effort"]},
        "text": {"format": {"type": "json_schema", "name": "grade", "schema": SCHEMA, "strict": True}},
    }
    url = cfg.get("base_url", "https://api.openai.com/v1").rstrip("/") + "/responses"
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode(),
        headers={"Authorization": "Bearer " + os.environ[cfg["api_key_env"]], "Content-Type": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.load(response)
            break
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(2 ** attempt)
    if data.get("status") != "completed":
        raise RuntimeError(f"Judge response status: {data.get('status')}")
    text = "".join(
        part.get("text", "")
        for output in data.get("output", [])
        for part in output.get("content", [])
        if part.get("type") == "output_text"
    )
    result = json.loads(text)
    result["judge_output_tokens"] = data.get("usage", {}).get("output_tokens")
    result["judge_response_id"] = data.get("id")
    scores(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests-dir", type=Path, default=Path("/tests"))
    parser.add_argument("--answer", type=Path, default=Path("/workspace/answer.txt"))
    parser.add_argument("--output-dir", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()
    item = json.loads((args.tests_dir / "reference.json").read_text(encoding="utf-8"))
    cfg = json.loads((args.tests_dir / "judge_config.json").read_text())
    candidate = args.answer.read_text(encoding="utf-8") if args.answer.exists() else ""
    system = (args.tests_dir / "judge_system.md").read_text(encoding="utf-8").strip()
    result = grade(item, candidate, system, cfg)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "judgment.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (args.output_dir / "reward.json").write_text(json.dumps(scores(result)) + "\n")


if __name__ == "__main__":
    main()
