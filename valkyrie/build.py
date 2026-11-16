"""Export a frozen YKT dataset as Valkyrie tasks and a text-only model agent."""

import argparse
import hashlib
import json
import re
import shutil
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
sys.path.insert(0, str(BENCH))
import ykt_eval


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(data, system_path, destination, dataset_name="yakut/vals-90", expected_count=None, judge_path=None, models_path=None, allow_visual_text=False):
    judge_path = judge_path or BENCH / "prompts/judge_system.md"
    models_path = models_path or BENCH / "models_vals.toml"
    items = [json.loads(line) for line in data.read_text(encoding="utf-8").splitlines() if line.strip()]
    if expected_count is not None and len(items) != expected_count:
        raise ValueError(f"Expected {expected_count} questions, found {len(items)}")
    if len({item["id"] for item in items}) != len(items):
        raise ValueError("Dataset contains duplicate IDs")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", item["id"]) for item in items):
        raise ValueError("A task ID is not a safe folder name")
    system = system_path.read_text(encoding="utf-8").strip()
    if not system:
        raise ValueError("Model instructions are empty")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Output directory is not empty: {destination}")
    cfg = tomllib.loads(models_path.read_text())["models"]
    judge = cfg["sol-6.1"]
    hosts = sorted({"api.openai.com", "api.anthropic.com", "openrouter.ai", "foundation-models.api.cloud.ru"}
                   | {urlparse(model["base_url"]).hostname for model in cfg.values() if model.get("base_url")})
    tasks = destination / "tasks"
    for item in items:
        if item.get("needs_visual") and not allow_visual_text:
            raise ValueError(f"Task {item['id']} needs an external picture")
        folder = tasks / item["id"]
        write(folder / "instruction.md", system + "\n\n<!-- YKT_MODEL_INPUT -->\n"
              + ykt_eval.solver_prompt(item) + "\n<!-- YKT_MODEL_INPUT_END -->\n\n"
              + "Submission: save only your final answer in UTF-8 to /workspace/answer.txt.\n")
        write(folder / "task.toml", f'''schema_version = "1.3"

[task]
name = "daanaea/{item['id']}"
version = "1.0.0"
description = "Text-only Sakha school exercise"

[metadata]
dataset = "{dataset_name}"
grade = "{item.get('grade', '')}"
source_needs_visual = {str(bool(item.get('needs_visual'))).lower()}

[environment]
docker_image = "python:3.12-slim"
workdir = "/workspace"
cpus = 1
memory_mb = 1024

[agent]
timeout_sec = 910
network_mode = "allowlist"
allowed_hosts = {json.dumps(hosts)}

[verifier]
timeout_sec = 900
network_mode = "allowlist"
allowed_hosts = ["api.openai.com"]

[[artifacts]]
source = "/logs/verifier/judgment.json"
destination = "judgment.json"
''')
        tests = folder / "tests"
        write(tests / "test.sh", "#!/bin/sh\nset -eu\npython /tests/grade.py\n")
        (tests / "test.sh").chmod(0o755)
        write(tests / "reference.json", json.dumps(item, ensure_ascii=False, indent=2) + "\n")
        write(tests / "judge_config.json", json.dumps(judge, indent=2) + "\n")
        shutil.copyfile(HERE / "grade.py", tests / "grade.py")
        shutil.copyfile(judge_path, tests / "judge_system.md")
    lock = [
        "[dataset]", f"name = {json.dumps(dataset_name)}",
        'description = "Text-only Yakut language and reasoning exercises"',
        'authors = [{name = "Sardaana Eginova"}]',
        'keywords = ["yakut", "sakha", "language", "reasoning"]', "",
        "[metadata]", f"dataset_sha256 = {json.dumps(digest(data))}",
        f"solver_instructions_sha256 = {json.dumps(digest(system_path))}", "",
    ]
    for item in items:
        folder = tasks / item["id"]
        outer = hashlib.sha256()
        for path in sorted(folder.rglob("*"), key=lambda p: p.relative_to(folder).as_posix()):
            if path.is_file():
                outer.update(f"{path.relative_to(folder).as_posix()}\0{digest(path)}\n".encode())
        lock += ["[[tasks]]", f'name = "daanaea/{item["id"]}"',
                 f'digest = "sha256:{outer.hexdigest()}"', ""]
    version = "v-" + hashlib.sha256("\n".join(lock).encode()).hexdigest()[:12]
    lock.insert(2, f'version = "{version}"')
    write(tasks / "dataset.toml", "\n".join(lock))
    agent = destination / "agent"
    agent.mkdir(parents=True, exist_ok=True)
    for source, name in [(HERE / "agent.py", "agent.py"), (BENCH / "providers.py", "providers.py"),
                         (models_path, "models.toml"), (system_path, "solver_system.md")]:
        shutil.copyfile(source, agent / name)
    write(agent / "requirements.txt", (BENCH / "requirements.txt").read_text())
    modal_secret = "  MODAL_INFERENCE_API_KEY: ykt-modal-inference-api-key\n" if any(model.get("api_key_env") == "MODAL_INFERENCE_API_KEY" for model in cfg.values()) else ""
    sara_secret = "  SARA_OPENROUTER_API_KEY: ykt-sara-openrouter-api-key\n" if any(model.get("api_key_env") == "SARA_OPENROUTER_API_KEY" for model in cfg.values()) else ""
    write(agent / "contract.yaml", '''name: yakut-text-model
install_cmd: python -m pip install -r requirements.txt
run_cmd: >-
  python /bundle/yakut-text-model/agent.py "{problem_statement_path}"
  --model "{model}" --output-dir /workspace
final_output: /workspace/response.json
allow_provider_tools: false
install_egress:
  - pypi.org
  - files.pythonhosted.org
defaults:
  model:
    type: str
    required: true
    description: Model alias from models.toml
secrets:
  OPENAI_API_KEY: ykt-openai-api-key
  ANTHROPIC_API_KEY: ykt-anthropic-api-key
  OPENROUTER_API_KEY: ykt-openrouter-api-key
  YANDEX_GIGACHAT_API_KEY: ykt-gigachat-api-key
''' + modal_secret + sara_secret + '''output_artifacts:
  - path: artifacts/response.json
    source: /workspace/response.json
''')
    manifest = {
        "dataset_name": dataset_name,
        "version": version,
        "questions": len(items),
        "dataset_sha256": digest(data),
        "solver_instructions_sha256": digest(system_path),
        "judge_instructions_sha256": digest(judge_path),
        "models_sha256": digest(models_path),
        "task_ids": [item["id"] for item in items],
        "reference_visibility": "tests injected during grading, never included in agent bundle",
    }
    write(destination / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--solver-instructions", type=Path, required=True)
    parser.add_argument("--judge-instructions", type=Path)
    parser.add_argument("--models-config", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dataset-name", default="yakut/vals-90")
    parser.add_argument("--expected-count", type=int, default=90)
    parser.add_argument("--allow-visual-text", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(args.data, args.solver_instructions, args.out, args.dataset_name,
                           args.expected_count, args.judge_instructions, args.models_config,
                           args.allow_visual_text), indent=2))


if __name__ == "__main__":
    main()
