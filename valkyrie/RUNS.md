# vals_90 runs

Published dataset: `yakut/vals-90@1`, immutable tag `v-1bfbfdb0441b`.

All 15 runs cover the same 90 tasks and were launched concurrently on Modal.
Per-answer deadline: 900 seconds. Requested output: 33,000 tokens, except
Gemma 4 31B at its API maximum of 16,384. Judge: GPT-6.1 Sol, 16,000 tokens.

| Model Name | Company | Run ID |
|---|---|---|
| Claude Fable 5.2 | Anthropic | `fea1bf47-69ec-41d4-867d-60734be402aa` |
| GPT-6 Astra | OpenAI | `392e635e-43cb-4d96-91f5-b5f728bb4830` |
| DeepSeek V4 Pro | DeepSeek | `1428ce18-270f-4702-aa74-9e7d8eda37f0` |
| Gemini 4 Argon | Google | `67d02148-9c8a-48d3-b8ca-49320ee76828` |
| GLM 5.3 | Z.ai | `ac59a29b-ee79-4750-bac2-ec6caf01a34f` |
| Grok 4.7 | SpaceX (xAI) | `35066cb0-074c-43c1-8942-743618bea169` |
| Gemma 4 31B | Google | `fc476ce6-16cc-4fe7-aac4-5509213e553a` |
| DeepSeek V4.1 Flash | DeepSeek | `f7c85dc8-c344-4a9e-be91-7bf445c4a8da` |
| Inkling | Thinking Machines Lab | `747d869c-d2db-4809-9431-23728b19c25e` |
| Inkling 2 Small | Thinking Machines Lab | `0b505d8b-b6eb-47c5-b229-200e381b0115` |
| Qwen3.8 Max | Alibaba | `8768945e-709f-447b-a486-15a0dba17a51` |
| Qwen3.8 Flash | Alibaba | `cc31a145-a908-4c92-985c-381ede148b0c` |
| Qwen3.8 27B | Alibaba | `7ba85ffb-bfb4-4e27-b260-3e9f6b4dd62e` |
| GPT-6.1 Sol (judge model) | OpenAI | `42b7c992-7578-4dcc-84cf-bfc40a5d53d9` |
| GigaChat 3.5 Ultra | Sber | `ea9722af-0fc1-47e1-9c5e-aec72c891dd9` |

Inspect any run with:

```bash
valkyrie run fetch fea1bf47-69ec-41d4-867d-60734be402aa
valkyrie tui
```

The input preserves all 90 selected rows, including 12 original picture flags.
Models receive text only. Five exercise-specific `eval_instruction` values are
provided to the judge, and excluded from solver input.

## Direct Modal inference recovery

The following runs retry only API-error tasks from the original runs.
The frozen question data and prompts are unchanged; task network allowlists
add the direct Modal endpoints. Dataset: `yakut/vals-90@2`, immutable tag
`v-e5b42b1c83d9`. Settings: [`models_vals_modal.toml`](../models_vals_modal.toml).
Completed answers from the original runs are preserved.

| Model Name | Questions retried | Run ID |
|---|---:|---|
| Inkling 2 Small | 2 | `328f7e27-a17f-4282-aac8-833e01177130` |
| DeepSeek V4.1 Flash | 81 | `d056dfe2-98a5-41ec-baac-db1368e32ae7` |

## Grok failed-request retry

On 2026-11-15 at 22:18 UTC, retried only `g3p2-L10-012` within run
`35066cb0-074c-43c1-8942-743618bea169`. The 89 graded answers were preserved.
The frozen agent and original settings were retained: 33,000 requested output
tokens, high reasoning, no tools, and a 900-second deadline. Retry concurrency: 1.
