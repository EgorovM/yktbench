"""Wait for prepared Modal servers, retry API-error tasks, and release idle GPUs."""

import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from uuid import UUID

from dotenv import dotenv_values


def request_json(url, key, payload=None):
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    }, data=json.dumps(payload).encode() if payload is not None else None)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def ready(spec, config, key):
    try:
        request_json(config["base_url"] + "/models", key)
        payload = {"model": config["model"], "messages": [{"role": "user", "content": "Reply only OK."}],
                   "max_tokens": config["max_tokens"], **config.get("extra_body", {})}
        result = request_json(config["base_url"] + "/chat/completions", key, payload)
        if not result.get("choices") or not result["choices"][0].get("message", {}).get("content"):
            raise ValueError("Readiness response contained no final answer")
        return True
    except urllib.error.HTTPError as error:
        if error.code in (429, 502, 503, 504):
            return False
        # Status codes are sufficient for diagnostics; don't log keys or response headers.
        raise RuntimeError(f"Readiness HTTP {error.code}") from None
    except (urllib.error.URLError, TimeoutError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--runs", type=Path, default=Path("results/vals_90/valkyrie_runs.json"))
    parser.add_argument("--state", type=Path, default=Path("results/vals_90/modal_deferred_state.json"))
    parser.add_argument("--max-wait", type=int, default=1800)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    env = {**dotenv_values(root / ".env"), **os.environ}
    key = env["MODAL_INFERENCE_API_KEY"]
    configs = tomllib.loads((args.bundle / "agent/models.toml").read_text())["models"]
    manifest = json.loads((args.bundle / "manifest.json").read_text())
    plan = json.loads(args.plan.read_text())
    from valkyrie.cli.client import call
    from valkyrie.sdk.models import FetchTasksRequest

    async def failed(client, run_id):
        page = await client.benchmarks.tasks(UUID(run_id), FetchTasksRequest(status=["ERROR"], limit=100))
        return [task["task_id"] for task in page.model_dump(mode="json")["tasks"]]

    async def status(client, run_id):
        return (await client.benchmarks.fetch(UUID(run_id))).status.value

    if args.dry_run:
        for spec in plan:
            config = configs[spec["model"]]
            assert config["api_key_env"] == "MODAL_INFERENCE_API_KEY"
            ids = call(lambda client: failed(client, spec["original_run_id"]))
            print(spec["model"], len(ids), "failed questions", config["model"], config["max_tokens"])
        return

    states = json.loads(args.state.read_text()) if args.state.exists() else {}
    for spec in plan:
        states.setdefault(spec["model"], {"phase": "warming", "since": time.time()})

    def save():
        args.state.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.state.with_suffix(".tmp")
        tmp.write_text(json.dumps(states, indent=2) + "\n")
        tmp.replace(args.state)

    def release(spec):
        subprocess.run(["modal", "server", "autoscaler", "update", spec["server"],
                        "--min-containers", "0", "--max-containers", "1"], check=True,
                       stdout=subprocess.DEVNULL)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(plan)) as pool:
        while True:
            warming = [spec for spec in plan if states[spec["model"]]["phase"] == "warming"]
            checks = {spec["model"]: pool.submit(ready, spec, configs[spec["model"]], key) for spec in warming}
            for spec in plan:
                state = states[spec["model"]]
                try:
                    if state["phase"] == "warming":
                        if time.time() - state["since"] > args.max_wait:
                            raise TimeoutError("Model startup deadline exceeded")
                        if not checks[spec["model"]].result():
                            continue
                        records = json.loads(args.runs.read_text())
                        previous = next((r for r in records if r["model"] == spec["model"]
                                         and r.get("inference_provider") == "modal"), None)
                        if previous:
                            state.update(phase="running", run_id=previous["run_id"])
                            continue
                        ids = call(lambda client: failed(client, spec["original_run_id"]))
                        if not ids:
                            state["phase"] = "no_errors"
                            release(spec)
                            continue
                        command = ["valkyrie", "run", "start", "--agent", str((args.bundle / "agent").resolve()),
                                   "--dataset", manifest["dataset_name"] + "@" + manifest["version"],
                                   "--model", spec["model"], "--provider", "modal", "--concurrency", "16",
                                   "--task-ids", ",".join(ids), "--label", "yakut-vals-90-modal-recovery"]
                        result = subprocess.run(command, text=True, capture_output=True, check=True)
                        match = re.search(r"Run ID:\s*([0-9a-f-]{36})", result.stdout)
                        if not match:
                            raise RuntimeError("Launch response contained no run ID")
                        row = {"model": spec["model"], "run_id": match.group(1), "returncode": 0,
                               "error": None, "retry_of": spec["original_run_id"], "task_ids": ids,
                               "inference_provider": "modal", "server": spec["server"]}
                        records.append(row)
                        tmp = args.runs.with_suffix(".tmp")
                        tmp.write_text(json.dumps(records, indent=2) + "\n")
                        tmp.replace(args.runs)
                        state.update(phase="running", run_id=row["run_id"], questions=len(ids))
                        print(spec["model"], "started", row["run_id"], len(ids), flush=True)
                    elif state["phase"] == "running":
                        current = call(lambda client: status(client, state["run_id"]))
                        if current in ("FINISHED", "ERROR", "STOPPED"):
                            release(spec)
                            state.update(phase="finished", status=current)
                            print(spec["model"], current, "GPU minimum restored to zero", flush=True)
                except Exception as error:
                    state.update(phase="error", error=type(error).__name__ + ": " + str(error))
                    release(spec)
                    print(spec["model"], state["error"], flush=True)
                save()
            save()
            try:
                subprocess.run([sys.executable, str(root / "valkyrie/collect.py"),
                                "--runs", str(args.runs), "--out", str(args.runs.parent / "hosted"),
                                "--artifacts"], check=True, stdout=subprocess.DEVNULL)
                subprocess.run([sys.executable, str(root / "valkyrie/leaderboard.py")], check=True)
            except subprocess.CalledProcessError:
                print("Result refresh failed; will try again next cycle", flush=True)
            if all(state["phase"] in ("finished", "error", "no_errors") for state in states.values()):
                break
            time.sleep(30)


if __name__ == "__main__":
    main()
