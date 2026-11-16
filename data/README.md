# Benchmark data

`vals_90.jsonl` contains the 90 questions used by the [leaderboard](../LEADERBOARD.md).
The source workbook is [`vals_90.xlsx`](vals_90.xlsx), worksheet
`vals sub`. The [manifest](vals_90.manifest.json) records source, dataset, and
solver instruction hashes, generated IDs, and question counts.

| Grade | Questions |
|---|---:|
| 1 | 11 |
| 2 | 25 |
| 3 | 28 |
| 4 | 24 |
| Unspecified | 2 |
| Total | 90 |

All supplied rows are retained. Twelve source rows carry picture flags; evaluation
uses their text only. The two questions without grade metadata count in All.
Six missing IDs were generated deterministically. Five questions contain an
`eval_instruction`; only the judge receives that guidance and the answer key.
Sakha text, answer content, and Unicode symbols are preserved in UTF-8.

To rebuild into a temporary directory and compare against the frozen dataset:

```bash
mkdir -p /tmp/ykt-data
.venv/bin/python build_vals90.py \
  --input data/vals_90.xlsx --sheet 'vals sub' \
  --solver-instructions prompts/solver_system.md \
  --allow-visual-text --out /tmp/ykt-data/vals_90.jsonl
cmp data/vals_90.jsonl /tmp/ykt-data/vals_90.jsonl
```

`leaderboard_metrics.json` stores the current leaderboard's cost, latency, usage,
and token pricing snapshot. Completed outputs and hosted run IDs are described
in [the run records](../valkyrie/RUNS.md).
