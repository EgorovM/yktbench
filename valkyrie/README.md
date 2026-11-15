# Yakut benchmark on Valkyrie

This adapter publishes a frozen text-only dataset as individually graded Valkyrie
tasks. It packages the existing API model configurations as a single-call agent.

The supplied solver instructions are preserved separately from each exercise.
The agent reads them from the task's instruction prefix, so a published agent
can evaluate new dataset versions without silently keeping an older prompt.
The agent receives no reference answers, browser, search tools, or shell tool.
Only model API endpoints are allowed during the agent phase. Grading uses the
existing GPT 6.1 Sol rubric and 16,000-token request budget, with full-question
accuracy and partial credit recorded separately. Sol's own row is self-judged.

New runs use `models_vals.toml`: each answer has a 900-second wall-clock
deadline and requests at most 33,000 output tokens. Gemma 4 31B is limited by
its API to 16,384 tokens and is marked as an exception. Timed-out answers are
saved as empty, flagged, and scored zero without retrying them. The sandbox
allows another ten seconds to save the timeout result before it is stopped.

## Build

Freeze the supplied workbook, CSV, or JSONL and bind it to the actual model
instructions. XLSX files with several sheets require `--sheet` unless one is
named `vals_90`.

```bash
.venv/bin/python build_vals90.py \
  --input data/sources/vals_90.xlsx --sheet vals_90 \
  --solver-instructions prompts/solver_system.md
```

Then export the normalized questions:

```bash
.venv/bin/python valkyrie/build.py \
  --data data/vals_90.jsonl \
  --solver-instructions prompts/solver_system.md \
  --judge-instructions prompts/vals_90_judge.md \
  --models-config models_vals.toml \
  --out valkyrie/submission
```

The builder refuses to overwrite an existing output folder. Its output includes
`tasks/dataset.toml` with exact task digests, 90 task folders
when the input has 90 questions, an agent contract, and a provenance manifest.
Answer keys reside only under each task's `tests/`, which Valkyrie injects during
grading after the agent has finished. API credentials are never bundled.
The `eval_instruction` field is supplied only to the judge. Valkyrie's built-in
mean aggregation computes the strict reward and partial credit without requiring
custom scoring support in the hosted deployment.

## Re-evaluate locally

```bash
.venv/bin/python run_parallel.py \
  --data data/vals_90.jsonl \
  --solver-system prompts/solver_system.md \
  --judge-system prompts/vals_90_judge.md \
  --config models_vals.toml \
  --run-dir results/vals_90 \
  --workers-per-model 16 --grok-workers 90
```

Each model has its own queue, and grading overlaps generation. `progress.json`
records completed answers, graded counts, token maxima, and over-limit answers.
The runner retains over-limit responses and never reruns successful answers
because they are wrong. Re-running the command resumes missing/API-failed items.
Dataset and prompt hashes prevent accidental reuse of results from another run.

## Publish and run on Valkyrie

Install `valkyrie-cli` with `uv tool install valkyrie-cli`, then sign in using
`valkyrie login`. Hosted execution also requires a configured sandbox provider
for the organization, such as Modal or Daytona.

```bash
.venv/bin/python valkyrie/publish.py valkyrie/submission
# Also launch all 15 models after the provider is configured:
.venv/bin/python valkyrie/publish.py valkyrie/submission \
  --start-runs --provider modal --concurrency 90
```

The publisher reads the existing credential environment with `.env` as a
fallback and sends values to Valkyrie's secret store over its authenticated CLI.
It keeps tokens off the command line and out of the published files. Native and
hosted evaluation share the model configurations and grading rules; results must
still be labeled with the platform on which they were collected.

## Collect results

The publisher writes model aliases and run IDs to
`results/vals_90/valkyrie_runs.json`. Collect scores and token usage with:

```bash
uv run --python 3.12 --with valkyrie-cli python valkyrie/collect.py \
  --runs results/vals_90/valkyrie_runs.json \
  --out results/vals_90/hosted --artifacts
```

Unfinished rows are provisional and show the number of graded questions. Full
outputs, token usage, and over-limit flags are retained separately from grading.

## Hosted pipeline validation

Run `91fc4b38-ceff-4765-b23e-e9dc3f0b7225` completed on Modal with the
`yakut-text-model` agent and one existing test question, using Fable 5.2.
It received full credit, reported 627 output tokens, and included an
`eval_instruction` in the judge's input. This is a pipeline smoke test, not a
90-question result. See [the validation record](smoke_validation.json).

```bash
valkyrie run fetch 91fc4b38-ceff-4765-b23e-e9dc3f0b7225
```

## Validation

```bash
.venv/bin/python -m unittest discover -s valkyrie -p 'test_*.py'
.venv/bin/python -m unittest discover -s . -p 'test_*.py'
```

The adapter is validated against Valkyrie's task and agent schemas and dataset
digest implementation. The exporter is generic: validation fixtures and the
previous 60-question set are not a substitute for the supplied `vals_90` data.

Official references: [dataset publishing](https://docs.valkyrie.vals.ai/benchmarks/datasets)
and [agent contracts](https://docs.valkyrie.vals.ai/agents/agent-contract).

## Direct Modal model inference

`--provider modal` selects the sandbox provider. Direct model calls use a separate
Modal inference endpoint and proxy token. The current recovery profile is
[`models_vals_modal.toml`](../models_vals_modal.toml), covering GLM 5.3,
DeepSeek V4.1 Flash, and Inkling 2 Small. Other model entries retain their original
providers. These endpoints were verified with live model calls.

Create a proxy token with `modal workspace proxy-tokens create`; combine its ID
and secret as described in the [Modal endpoint documentation](https://modal.com/docs/guide/endpoints).
Store it as `MODAL_INFERENCE_API_KEY` in the ignored `.env`, and as the Valkyrie
secret `ykt-modal-inference-api-key`. Never commit either credential.

```bash
python valkyrie/build.py --data data/vals_90.jsonl \
  --solver-instructions prompts/solver_system.md \
  --judge-instructions prompts/vals_90_judge.md \
  --models-config models_vals_modal.toml \
  --out results/modal-submission --allow-visual-text
python valkyrie/publish.py results/modal-submission --provider modal
```

The endpoint URLs are workspace-specific. Create or select your own endpoints
and update the recovery profile before using it in another workspace.
Recovery runs are listed in [RUNS.md](RUNS.md). The collector accepts multiple
run records for the same model and merges graded tasks by question ID.
To refresh the public leaderboard after collecting results:

```bash
python valkyrie/leaderboard.py
```
