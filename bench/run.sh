#!/usr/bin/env bash
# Resumable v1 fifteen-model run. Pass benchmark options, e.g. --workers 4.
set -euo pipefail
cd "$(dirname "$0")/.."
models=fable-5.2,astra,deepseek-v4,gemini-4-argon,glm-5.3,grok-4.7,gemma-4-31b,deepseek-v4.1-flash,inkling-flagship,inkling-2-small,qwen-3.8-max,qwen-3.8-flash,qwen-3.8-27b,sol-6.1-eval,gigachat-3.5
.venv/bin/python bench/ykt_eval.py check --models "$models" --judges sol-6.1
.venv/bin/python bench/ykt_eval.py all --models "$models" --judges sol-6.1 \
  --run-dir bench/results/v1-smoke --limit 2 "$@"
# API failures stop the launcher above. Model refusals and exhausted token
# budgets are benchmark outcomes: flag them and retain their zero scores.
.venv/bin/python - <<'PY'
import json
import sys
from pathlib import Path
rows = {}
for line in Path('bench/results/v1-smoke/responses.jsonl').read_text().splitlines():
    r = json.loads(line)
    rows[(r['model'], r['item_id'], r['sample'])] = r
bad = [k for k, r in rows.items() if r.get('error') or not r.get('final_answer', '').strip()
       or r.get('stop_reason') in ('length', 'max_tokens', 'refusal')
       or str(r.get('stop_reason', '')).startswith('incomplete')]
if bad:
    print(f'Warning: empty/refused/truncated smoke answers (counted wrong): {bad}', file=sys.stderr)
PY
.venv/bin/python bench/ykt_eval.py all --models "$models" --judges sol-6.1 \
  --run-dir bench/results/v1 "$@"
