# YKT textbook QA eval

Measures how well frontier models solve Sakha-language textbook exercises. Each model gets
an exercise (instruction + material, in Sakha) and answers it. A judge model then compares
the answer with the textbook's answer key.

- **Dataset v1:** `data/ykt_primary_v1.jsonl`, 60 exercises from grades 1–4 (riddles,
  word puzzles, vocabulary, multiple choice), frozen from the `clean` sheet of
  [`data/sources/clean_60_primary_school.xlsx`](data/sources/clean_60_primary_school.xlsx).
  All necessary clues are text, including Unicode sound tokens; no external pictures are needed.
- **Previous version:** the original 61-item `data/ykt_sample.jsonl` and its results in
  `results/main/` are retained. The [root README leaderboard](../README.md#v0--proof-of-concept)
  is the v0 proof of concept, not a v1 score.
- **Models under test:** Claude Fable 5.2, GPT-6 Astra, DeepSeek V4 Pro, Gemini 4 Argon,
  GLM-5.3, Grok 4.7, Gemma 4 31B, DeepSeek V4.1 Flash, Inkling Flagship, Inkling 2 Small,
  Qwen3.8 Max (0902), Qwen3.8 Flash, Qwen3.8 27B, GPT 6.1 Sol (judge model), and GigaChat 3.5.
- **Judge:** GPT 6.1 Sol (`gpt-6.1-sol`), reasoning effort `high`, by default. You can add more judges and compare them.

## 1. Set up on the VM

Needs Python 3.10 or newer. The system Python on this VM is 3.9, so use the installed
`uv` to select Python 3.11.

```bash
git clone https://github.com/daanaea/ykt_bench.git
```

```bash
cd ykt_bench
```

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
```

```bash
uv pip install --python .venv/bin/python -r bench/requirements.txt
```

Set one API key per provider:

```bash
export ANTHROPIC_API_KEY=...   # Fable 5.2
export OPENAI_API_KEY=...      # GPT-6 Astra, and GPT 6.1 Sol as judge
export OPENROUTER_API_KEY=...  # DeepSeek, Gemini, GLM, Grok, Gemma, Inkling, Qwen
export YANDEX_GIGACHAT_API_KEY=...  # GigaChat through Cloud.ru
```

Alternatively, copy `bench/.env.example` to `bench/.env` and fill in the values there.
The runner loads `bench/.env`, then the repo `.env`; existing environment variables take
precedence. Both files, the virtual environment, and `bench/results/` are ignored by git.
Never commit credentials.

Check which keys are present without making API calls or printing secrets:

```bash
python bench/ykt_eval.py check --models fable-5.2,astra,deepseek-v4,gemini-4-argon,glm-5.3,grok-4.7,gemma-4-31b,deepseek-v4.1-flash,inkling-flagship,inkling-2-small,qwen-3.8-max,qwen-3.8-flash,qwen-3.8-27b,sol-6.1-eval,gigachat-3.5
```

Run the smoke test and then the full fifteen-model benchmark with one command:

```bash
bash bench/run.sh
```

The launcher stops if credentials are missing or a smoke API call fails. Empty, refused,
or truncated answers produce a warning and count as wrong. Re-running resumes completed work. Optional arguments
such as `--workers 4` are forwarded to both runs.

## 2. Smoke test (2 items per model)

```bash
python bench/ykt_eval.py all --models fable-5.2,astra,deepseek-v4,gemini-4-argon,glm-5.3,grok-4.7,gemma-4-31b,deepseek-v4.1-flash,inkling-flagship,inkling-2-small,qwen-3.8-max,qwen-3.8-flash,qwen-3.8-27b,sol-6.1-eval,gigachat-3.5 --judges sol-6.1 --limit 2 --run-dir bench/results/v1-smoke
```

Look at `bench/results/v1-smoke/responses.jsonl`. Every line should have a `response` and a
`final_answer`, and no `error`.

## 3. Full run

```bash
python bench/ykt_eval.py all --models fable-5.2,astra,deepseek-v4,gemini-4-argon,glm-5.3,grok-4.7,gemma-4-31b,deepseek-v4.1-flash,inkling-flagship,inkling-2-small,qwen-3.8-max,qwen-3.8-flash,qwen-3.8-27b,sol-6.1-eval,gigachat-3.5 --judges sol-6.1
```

This writes to `bench/results/v1/`:

| file | contents |
|---|---|
| `responses.jsonl` | every model answer: full text, extracted final answer, tokens, latency, stop reason |
| `judgments.jsonl` | every grade: per-part verdicts, score, the judge's reason |
| `report.md` | accuracy table, 95% CI, requested token limits, maximum reported output usage, grade/picture breakdowns, warnings |
| `scores.csv` | one row per model × item, for checking grades by hand (opens in Excel) |
| `meta.jsonl` | command, model settings and prompt/dataset hashes for each invocation |

**Interrupted or some calls failed?** Run the same command again. Only missing or failed
calls are repeated, and finished ones are kept. You can also run the steps separately:

```bash
python bench/ykt_eval.py solve --models fable-5.2,glm-5.3,astra
```

```bash
python bench/ykt_eval.py judge --judges sol-6.1
```

```bash
python bench/ykt_eval.py report
```

Useful options:

| option | what it does |
|---|---|
| `--run-dir DIR` | a separate folder per experiment (default `bench/results/v1`) |
| `--data FILE` | a frozen dataset (default `bench/data/ykt_primary_v1.jsonl`) |
| `--samples 3` | ask each model 3 times per item. With only 60 items, this shows how much scores move between runs |
| `--workers 8` | parallel API calls; lower it if a provider rate-limits you |
| `--limit N`, `--ids a,b` | run a subset |
| `--judges sol-6.1,astra` | grade with several judges; the report adds an agreement table |
| `--judge astra` | (report) headline another judge's grades |

To see exactly what a model and the judge receive for one item:

```bash
python bench/ykt_eval.py preview --id g2p2-L30-011
```

## How grading works

- Web search and browsing tools are not enabled. Solvers receive only the exercise
  instructions and text material; judges also receive the reference answer key.
- The solver prompt (`prompts/solver_system.md`) asks for an answer in Sakha that ends with
  a `ХОРУЙ: …` line. Everything after the last `ХОРУЙ:` is the final answer. If the line is
  missing, the judge sees the end of the reply, and the report counts it under "no ХОРУЙ line".
- The judge (`prompts/judge_system.md`) splits the reference into parts (numbered items or
  list words) and marks each part right or wrong. **Accuracy** means every part is right.
  **Partial** is the share of parts right.
- Rules the judge applies (edit the prompt file to change them):
  - The answer key is authoritative.
  - Another grammatical form of the same word is fine.
  - Lookalike letters for ҕ ҥ ө ү һ are fine.
  - **Answers in Russian are wrong.**
  - "X or Y" answers are wrong.
- Missing answers, failed calls and empty answers count as wrong, never as skipped. The
  report lists them under Warnings.

**Check the judge before trusting the numbers.** Open `scores.csv`, read about 20 rows (the
`reason` column says why), and count how often you disagree. To compare with a second judge,
run `judge --judges opus-5.5`, then `report --judge sol-6.1`. Keep in mind that a judge
from the same family as a model under test may favour it. The default Sol judge shares
its provider with Astra; compare a second judge when auditing scores.

## Model settings (`models.toml`)

GPT 6.1 Sol is also evaluated as `sol-6.1-eval`, marked **(judge model)** in
the leaderboard. Its solver budget is 32,000 tokens; the separate `sol-6.1`
grading configuration remains at 16,000 tokens. Its score under Sol grading is
self-judged and should be interpreted with that in mind. The solver alias uses a
3,600-second HTTP read timeout because one word-reconstruction item repeatedly
exceeded the default network timeout; generation settings are unchanged.


Models request reasoning effort `high` where supported. These settings do not imply
equal reasoning compute across vendors. Gemma uses its default non-thinking mode.
The results table includes each requested token limit and the largest output token
usage reported by its API. Reported usage can include reasoning and can exceed the
requested limit, as observed for Grok.

- **sol-6.1** (`gpt-6.1-sol`, OpenAI Responses API): default judge, effort `high`,
  with up to 16,000 output tokens per judgment. Opus 5.5 remains an optional judge.
- **fable-5.2** (`claude-fable-5-2`): thinking is always on. Server-side refusal fallback is
  enabled: if Fable declines a request, the API answers it with another Claude model. Such
  answers are counted in the "fallback-served" column. Set `fallbacks = false` to record a
  refusal instead. Fable 5.2 needs the org's data retention to be 30 days or more. Orgs on
  zero data retention get a 400.
- **glm-5.3** (`z-ai/glm-5.3`): OpenRouter, with high reasoning effort.
- **astra** (`gpt-6-astra`, OpenAI Responses API). If OpenAI ships a newer Astra, change
  `model` here.
- **deepseek-v4** (`deepseek/deepseek-v4-pro`): V4 Pro 0423 through OpenRouter. This is
  the Pro variant of the requested V4 generation, rather than V4.1 or Flash.
- **deepseek-v4.1-flash** (`deepseek/deepseek-v4.1-flash`): OpenRouter, high reasoning effort.
- **inkling-flagship** (`thinkingmachines/inkling`): OpenRouter, high reasoning effort,
  requested output limit 32,000 tokens. This is the flagship Inkling, separate from Inkling Small.
- **inkling-2-small** (`thinkingmachines/inkling-2-small`): paid OpenRouter endpoint, high
  reasoning effort, requested output limit 32,000 tokens. Reasoning is mandatory.
  Both Inkling IDs and settings were checked against the OpenRouter catalog on 2026-11-15.
- **gemini-4-argon** (`google/gemini-4-argon`): OpenRouter.
- **grok-4.7** (`x-ai/grok-4.7`): OpenRouter.
  The API reported more than 70,000 output tokens on one item despite the requested
  `max_tokens = 32000`. The report flags usage above requested limits; these settings
  do not enforce equal effective total token budgets across providers.
- **gemma-4-31b** (`google/gemma-4-31b-it`): paid OpenRouter endpoint, reasoning disabled
  (its default mode). Thinking exhausted the entire output budget without an answer on
  a smoke item. Uses `max_tokens = 16384` to respect its advertised output limit. Other solvers use
  32,000. These IDs and limits were checked against the
  [OpenRouter model catalog](https://openrouter.ai/api/v1/models) on 2026-11-14.

- **qwen-3.8-max** (`qwen/qwen3.8-max-0902`): Qwen3.8 Max's current 0902 snapshot,
  high reasoning effort and 32,000 requested output tokens.
- **qwen-3.8-flash** (`qwen/qwen3.8-flash`): the official hosted model based on
  Qwen3.8-Flash-Next, high reasoning effort and 32,000 requested output tokens.
  The leaderboard uses the served name, Qwen3.8 Flash; this is not a claim to run
  the exact downloadable Flash-Next weights. See the [Qwen model card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next).
- **qwen-3.8-27b** (`qwen/qwen3.8-27b`): high reasoning effort and 32,000 requested
  output tokens. All three Qwen endpoints use OpenRouter and were checked against
  its [model catalog](https://openrouter.ai/api/v1/models) on 2026-11-15.

- **gigachat-3.5** (`ai-sage/GigaChat3.5-432B-A28B`): Cloud.ru Foundation Models,
  32,000 requested output tokens, using its served default mode. Credentials are
  read from `YANDEX_GIGACHAT_API_KEY`; the name is user-selected, while the endpoint
  is Cloud.ru. No external tools or browser access are enabled.

Add another model by copying a block. The table name is what you pass to `--models`.

Qwen 4 Flash was also requested. On 2026-11-15 it was absent from OpenRouter's catalog,
and the API rejected `qwen/qwen4-flash` with HTTP 400 (invalid model ID). It is not
included in the launcher or accuracy scores. The requested v1 replacements are
Qwen3.8 Max, the hosted Qwen3.8 Flash counterpart of Flash-Next, and Qwen3.8 27B.

## Dataset

The v1 source is `bench/data/sources/clean_60_primary_school.xlsx`. Only its
`clean` worksheet is imported; the separate `wip` worksheet is excluded. The workbook
and frozen JSONL are both included; evaluation only needs the JSONL.

To rebuild v1:

```bash
python3 bench/build_dataset.py
```

The resulting `bench/data/ykt_primary_v1.jsonl` contains 60 questions: grade 1 (10),
grade 2 (20), grade 3 (25), and grade 4 (5). A companion `.manifest.json` records the
source sheet, source and dataset SHA-256 hashes, counts, and generated IDs.

- Sakha letters, punctuation, and Unicode sound tokens such as `🟢🟥` are preserved in
  UTF-8. Only surrounding whitespace, line endings, and trailing spaces are normalized.
- Grades are derived from IDs instead of Excel's numeric/date representation.
- The three blank-ID multiple-choice rows become `g2p1-L14-006b/c/d`.
- The blank-ID question about interrogative pronouns on sheet row 50 becomes
  `g3p1-L33-011b`, following the preceding explicit ID. This generated suffix does
  not claim a printed textbook exercise number.
- Each question records `dataset_version`, source file, worksheet, and actual sheet row.
- The curated `clean` sheet has no external picture dependencies. Its text is used
  directly; old picture flags and legacy content overrides are not copied across IDs.

One review issue remains in the supplied workbook: `g2p2-L35-011` asks for consonant
analysis but supplies riddle solutions as its answer key. It is retained as supplied.
See the [dataset notes](data/README.md) for version changes and review details.

New runs default to `bench/results/v1/`; v0 files remain in `bench/results/main/`.
The runner rejects an existing run directory whose recorded dataset hash differs,
so changed question text or reference answers cannot silently reuse old results.

To inspect or report the original v0 run, select both its dataset and run directory:

```bash
python bench/ykt_eval.py report --data bench/data/ykt_sample.jsonl --run-dir bench/results/main
```

To reproduce the frozen v0 dataset, run `python3 bench/build_dataset.py --version v0`.
Only that mode applies the original `g10-11-T3-009` content override.

The `data/` files are in this public repo, so the answers are public. That's fine for
measuring models today, but future models may have trained on them.

## Cost

One full pass is 60 items × 15 models (900 solver calls), plus up to 900 judge calls. Reasoning tokens make up most of
the cost. Run the smoke test first and multiply: `responses.jsonl` records input and output
tokens for every call.
