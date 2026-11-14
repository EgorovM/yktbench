# YKT textbook QA eval

Measures how well frontier models solve Sakha-language textbook exercises. Each model gets
an exercise (instruction + material, in Sakha) and answers it. A judge model then compares
the answer with the textbook's answer key.

- **Dataset:** `data/ykt_sample.jsonl`, 61 exercises from grades 1–4 and 10–11 (riddles,
  word puzzles, multiple choice), frozen from `data/sample.xlsx`.
- **Models under test:** Claude Fable 5.2, GLM-5.3, GPT-6 Astra.
- **Judge:** Claude Opus 5.5 by default. You can add more judges and compare them.

## 1. Set up on the VM

Needs Python 3.10 or newer.

```bash
git clone https://github.com/daanaea/ykt_bench.git
```

```bash
cd ykt_bench && git checkout bench-eval
```

```bash
python3 -m venv .venv && source .venv/bin/activate
```

```bash
pip install -r bench/requirements.txt
```

Set one API key per provider:

```bash
export ANTHROPIC_API_KEY=...   # Fable 5.2, and Opus 5.5 as judge
export ZAI_API_KEY=...         # GLM-5.3 (Z.ai)
export OPENAI_API_KEY=...      # GPT-6 Astra
```

## 2. Smoke test (2 items, a few cents)

```bash
python bench/ykt_eval.py all --models fable-5.2,glm-5.3,astra --judges opus-5.5 --limit 2 --run-dir bench/results/smoke
```

Look at `bench/results/smoke/responses.jsonl`. Every line should have a `response` and a
`final_answer`, and no `error`.

## 3. Full run

```bash
python bench/ykt_eval.py all --models fable-5.2,glm-5.3,astra --judges opus-5.5
```

This writes to `bench/results/main/`:

| file | contents |
|---|---|
| `responses.jsonl` | every model answer: full text, extracted final answer, tokens, latency, stop reason |
| `judgments.jsonl` | every grade: per-part verdicts, score, the judge's reason |
| `report.md` | accuracy table, 95% CI, breakdown by grade and by picture dependence, warnings |
| `scores.csv` | one row per model × item, for checking grades by hand (opens in Excel) |
| `meta.jsonl` | command, model settings and prompt/dataset hashes for each invocation |

**Interrupted or some calls failed?** Run the same command again. Only missing or failed
calls are repeated, and finished ones are kept. You can also run the steps separately:

```bash
python bench/ykt_eval.py solve --models fable-5.2,glm-5.3,astra
```

```bash
python bench/ykt_eval.py judge --judges opus-5.5
```

```bash
python bench/ykt_eval.py report
```

Useful options:

| option | what it does |
|---|---|
| `--run-dir DIR` | a separate folder per experiment (default `bench/results/main`) |
| `--samples 3` | ask each model 3 times per item. With only 61 items, this shows how much scores move between runs |
| `--workers 8` | parallel API calls; lower it if a provider rate-limits you |
| `--limit N`, `--ids a,b` | run a subset |
| `--judges opus-5.5,astra` | grade with several judges; the report adds an agreement table |
| `--judge astra` | (report) headline another judge's grades |

To see exactly what a model and the judge receive for one item:

```bash
python bench/ykt_eval.py preview --id g2p2-L30-011
```

## How grading works

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
run `judge --judges astra`, then `report`. Keep in mind that a judge from the same family as
a model under test may favour it. That's Opus for Fable, and Astra for itself.

## Model settings (`models.toml`)

All three models run at reasoning effort `high`.

- **fable-5.2** (`claude-fable-5-2`): thinking is always on. Server-side refusal fallback is
  enabled: if Fable declines a request, the API answers it with another Claude model. Such
  answers are counted in the "fallback-served" column. Set `fallbacks = false` to record a
  refusal instead. Fable 5.2 needs the org's data retention to be 30 days or more. Orgs on
  zero data retention get a 400.
- **glm-5.3** (`glm-5.3` at `https://api.z.ai/api/paas/v4/`): if your key is a GLM Coding
  Plan key, change `base_url` to `https://api.z.ai/api/coding/paas/v4/`. GLM-5.3 can't turn
  reasoning off.
- **astra** (`gpt-6-astra`, OpenAI Responses API). If OpenAI ships a newer Astra, change
  `model` here.

Add another model by copying a block. The table name is what you pass to `--models`.

## Dataset

`data/ykt_sample.jsonl` is built from `data/sample.xlsx`. The spreadsheet isn't in git, but
the frozen `.jsonl` is, and that's all the eval needs. To rebuild after editing the
spreadsheet:

```bash
python3 bench/build_dataset.py
```

The build script fixes three problems in the spreadsheet:

- The three unnamed multiple-choice rows under `g2p1-L14-006` become `…006b/c/d`.
- Grade `10-11`, which Excel had turned into a date, is restored.
- In `g10-11-T3-009`, the `content` column held text from the next chapter, so it's dropped.
  The question and its options are all in the instruction.

13 items are flagged `needs_visual`, and about 6 of them can't really be answered without
the textbook picture. The report shows text-only and picture items separately.

The `data/` files are in this public repo, so the answers are public. That's fine for
measuring models today, but future models may have trained on them.

## Cost

One full pass is 61 items × 3 models, plus 183 judge calls. Reasoning tokens make up most of
the cost. Run the smoke test first and multiply: `responses.jsonl` records input and output
tokens for every call.
