"""Publish a prepared bundle and optionally start all configured model runs."""

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run_parallel import MODELS


KEYS = {
    "OPENAI_API_KEY": "ykt-openai-api-key",
    "ANTHROPIC_API_KEY": "ykt-anthropic-api-key",
    "OPENROUTER_API_KEY": "ykt-openrouter-api-key",
    "YANDEX_GIGACHAT_API_KEY": "ykt-gigachat-api-key",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--start-runs", action="store_true")
    parser.add_argument("--provider", help="use the organization's default when omitted")
    parser.add_argument("--concurrency", type=int, default=90)
    parser.add_argument("--skip-secrets", action="store_true", help="use the organization's existing configured secrets")
    parser.add_argument("--run-record", type=Path, default=Path("bench/results/vals_90/valkyrie_runs.json"))
    args = parser.parse_args()
    manifest = json.loads((args.bundle / "manifest.json").read_text())
    subprocess.run(["valkyrie", "whoami"], check=True)
    env = dict(dotenv_values(Path(__file__).resolve().parent.parent / ".env"))
    env.update(os.environ)
    missing = [key for key in KEYS if not env.get(key)]
    if missing:
        raise SystemExit("Missing credential variable names: " + ", ".join(missing))
    if not args.skip_secrets:
        for key, name in KEYS.items():
            subprocess.run(["valkyrie", "secret", "set", name], input=env[key], text=True, check=True)
    subprocess.run(["valkyrie", "agent", "push", str(args.bundle / "agent")], check=True)
    subprocess.run(["valkyrie", "dataset", "push", manifest["dataset_name"], str(args.bundle / "tasks"),
                    "--tag", "vals-90", "--concurrency", "16"], check=True)
    if args.start_runs:
        def start(model):
            cmd = ["valkyrie", "run", "start", "--agent", "yakut-text-model",
                   "--dataset", manifest["dataset_name"] + "@" + manifest["version"], "--model", model,
                   "--concurrency", str(args.concurrency), "--label", "yakut-vals-90"]
            if args.provider:
                cmd += ["--provider", args.provider]
            result = subprocess.run(cmd, text=True, capture_output=True)
            match = re.search(r"Run ID:\s*([0-9a-f-]{36})", result.stdout)
            row = {"model": model, "returncode": result.returncode,
                   "run_id": match.group(1) if match else None,
                   "error": result.stderr if result.returncode else None}
            print(model, row["run_id"] or row["error"], flush=True)
            return row
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as pool:
            runs = list(pool.map(start, MODELS))
        args.run_record.parent.mkdir(parents=True, exist_ok=True)
        args.run_record.write_text(json.dumps(runs, indent=2) + "\n")
        return int(any(run["returncode"] for run in runs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
