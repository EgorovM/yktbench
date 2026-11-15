# Yakut Benchmark Leaderboards

- **[Valkyrie — 90 questions](LEADERBOARD_90.md):** current vals_90 evaluation, per-grade scores, token usage, and run status.
- **[v1 — 60 questions](LEADERBOARD_60.md):** completed baseline and token usage.

## v0 — proof of concept


Results from the original 61-question sample (grades 1–4 and 10–11), with one
answer per model and question. Judge: GPT 6.1 Sol (`gpt-6.1-sol`), high reasoning
effort. Accuracy requires every reference part to be correct; partial credit is
the mean share of parts correct.  Missing, refused, and truncated answers count as wrong.

| Model Name | Company | Accuracy % | Partial % | Avg output tokens | Avg latency (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| Claude Fable 5.2 | Anthropic | **49.2** | 63.0 | 772 | 9 |
| Gemini 4 Argon | Google | 45.9 | 61.5 | 3769 | 67 |
| GPT-6 Astra | OpenAI | 34.4 | 49.8 | 1516 | 43 |
| Grok 4.7 | SpaceX (xAI) | 26.2 | 40.7 | 27180 | 535 |
| Inkling | Thinking Machines Lab | 26.2 | 40.5 | 8154 | 92 |
| DeepSeek V4 Pro | DeepSeek | 23.0 | 35.4 | 7061 | 93 |
| DeepSeek V4.1 Flash | DeepSeek | 23.0 | 39.0 | 10322 | 53 |
| Inkling 2 Small | Thinking Machines Lab | 19.7 | 33.0 | 11282 | 60 |
| GLM 5.3 | Z.ai | 16.4 | 20.9 | 17072 | 129 |
| Gemma 4 31B | Google | 8.2 | 10.1 | 1756 | 14 |

This initial sample includes 13 picture-flagged questions, although solvers
received text only, and some prompt/answer-key alignment issues. These scores
are a proof of concept; later dataset versions should be evaluated separately.
Reasoning settings and effective token budgets differ across providers; Grok
reported output usage above its requested limit. See [benchmark documentation](USAGE.md)
for model settings and grading rules.
