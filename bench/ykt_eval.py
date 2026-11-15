#!/usr/bin/env python3
"""Sakha textbook QA eval: ask models the questions, grade answers with an LLM judge, report accuracy.

  python bench/ykt_eval.py all     --models fable-5.2,glm-5.3,astra --judges sol-6.1
  python bench/ykt_eval.py solve   --models fable-5.2,glm-5.3,astra   # ask the models
  python bench/ykt_eval.py judge   --judges sol-6.1                   # grade the answers
  python bench/ykt_eval.py report                                     # tables -> report.md, scores.csv
  python bench/ykt_eval.py preview --id g1-L02-004                    # print the prompts for one item

Everything is appended to <run-dir>/*.jsonl, so an interrupted run picks up where it
stopped: re-run the same command and only missing or failed calls are made again.
"""

import argparse
import csv
import fcntl
import hashlib
import json
import os
import random
import re
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    import tomli as tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers import make_provider  # noqa: E402

BENCH = Path(__file__).resolve().parent
DEFAULT_DATA = BENCH / "data" / "ykt_primary_v1.jsonl"
DEFAULT_RUN_DIR = BENCH / "results" / "v1"
SOLVER_SYSTEM = (BENCH / "prompts" / "solver_system.md").read_text(encoding="utf-8").strip()
JUDGE_SYSTEM = (BENCH / "prompts" / "judge_system.md").read_text(encoding="utf-8").strip()

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "parts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "reference": {"type": "string"},
                    "candidate": {"type": "string"},
                    "correct": {"type": "boolean"},
                },
                "required": ["reference", "candidate", "correct"],
                "additionalProperties": False,
            },
        },
        "reason": {"type": "string"},
    },
    "required": ["parts", "reason"],
    "additionalProperties": False,
}

FINAL_MARKER = re.compile(r"\**\s*хоруй\s*\**\s*[:：]\s*\**", re.IGNORECASE)


# ---------------------------------------------------------------- prompts

def solver_prompt(item):
    msg = f"Сорудах:\n{item['instruction']}"
    if item["content"]:
        msg += f"\n\nМатырыйаал:\n{item['content']}"
    return msg


def judge_prompt(item, candidate):
    guidance = (f"## Exercise-specific grading instructions (eval_instruction)\n"
                f"{item['eval_instruction']}\n\n") if item.get("eval_instruction") else ""
    return (
        f"## Exercise instruction\n{item['instruction']}\n\n"
        f"## Material\n{item['content'] or '(none)'}\n\n"
        + guidance +
        f"## Reference answer (textbook answer key)\n{item['answer']}\n\n"
        f"## Candidate answer\n{candidate}"
    )


def extract_final(text):
    """Text after the last 'ХОРУЙ:' line; the whole reply (tail) if the marker is missing."""
    matches = list(FINAL_MARKER.finditer(text or ""))
    if not matches:
        return (text or "").strip()[-3000:], False
    return text[matches[-1].end():].strip().strip("*").strip(), True


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------- storage

class Log:
    """Append-only JSONL file; the last record for a key wins."""

    def __init__(self, path, key_fields):
        self.path, self.key_fields = path, key_fields
        self.lock = threading.Lock()
        self.latest = {}
        if path.exists():
            with path.open(encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        self.latest[self.key(rec)] = rec

    def key(self, rec):
        return tuple(rec[k] for k in self.key_fields)

    def done(self, key):
        rec = self.latest.get(key)
        return rec is not None and not rec.get("error")

    def append(self, rec):
        with self.lock:
            with self.path.open("a", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
            self.latest[self.key(rec)] = rec


def load_config(path):
    with open(path, "rb") as f:
        return tomllib.load(f)["models"]


def load_items(args):
    items = [json.loads(line) for line in Path(args.data).open(encoding="utf-8") if line.strip()]
    if args.ids:
        wanted = set(args.ids.split(","))
        missing = wanted - {it["id"] for it in items}
        if missing:
            sys.exit(f"unknown ids: {sorted(missing)}")
        items = [it for it in items if it["id"] in wanted]
    if args.limit:
        items = items[: args.limit]
    return items


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def validate_run_dataset(run_dir, data):
    """Reject stale cached answers/grades when a dataset changes under the same IDs."""
    path = Path(run_dir) / "meta.jsonl"
    if not path.exists():
        return
    expected = sha(Path(data).read_text(encoding="utf-8"))
    with path.open(encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        for line in f:
            if not line.strip():
                continue
            previous = json.loads(line).get("dataset_sha")
            if previous and previous != expected:
                sys.exit(
                    f"dataset differs from the one recorded in {path}; use a new --run-dir "
                    "for this dataset, or select the original dataset with --data"
                )


def write_meta(run_dir, command, args, config, names):
    validate_run_dataset(run_dir, args.data)
    meta_path = Path(run_dir) / "meta.jsonl"
    if meta_path.exists():
        with meta_path.open(encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            for line in f:
                if not line.strip():
                    continue
                previous = json.loads(line)
                for field, value in (("solver_prompt_sha", sha(SOLVER_SYSTEM)),
                                     ("judge_prompt_sha", sha(JUDGE_SYSTEM))):
                    if previous.get(field) and previous[field] != value:
                        sys.exit(f"{field} differs from the saved run; use a new --run-dir or the original instruction files")
    rec = {
        "ts": now(),
        "command": command,
        "argv": sys.argv[1:],
        "dataset_sha": sha(Path(args.data).read_text(encoding="utf-8")),
        "dataset_file": str(Path(args.data).resolve()),
        "solver_prompt_sha": sha(SOLVER_SYSTEM),
        "judge_prompt_sha": sha(JUDGE_SYSTEM),
        "models": {n: config[n] for n in names},
    }
    with (run_dir / "meta.jsonl").open("a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()


def pick(config, names, what):
    names = [n.strip() for n in names.split(",") if n.strip()]
    unknown = [n for n in names if n not in config]
    if unknown:
        sys.exit(f"unknown {what}: {unknown}. Defined in models.toml: {sorted(config)}")
    return names


def build_providers(config, names):
    try:
        return {n: make_provider(n, config[n]) for n in names}
    except (RuntimeError, ValueError, ImportError) as e:
        sys.exit(f"error: {e}")


def run_pool(jobs, fn, workers, label):
    total, failed = len(jobs), 0
    if not total:
        print(f"{label}: nothing to do (all done already)", file=sys.stderr)
        return 0
    print(f"{label}: {total} calls, {workers} at a time", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fn, job): job for job in jobs}
        for i, fut in enumerate(as_completed(futures), 1):
            status = fut.result()
            failed += status.startswith("ERROR")
            print(f"[{i}/{total}] {status}", file=sys.stderr)
    if failed:
        print(f"{label}: {failed} calls failed; re-run the same command to retry them", file=sys.stderr)
    return failed


# ---------------------------------------------------------------- solve

def cmd_solve(args, config):
    names = pick(config, args.models, "models")
    items = load_items(args)
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    write_meta(run_dir, "solve", args, config, names)
    log = Log(run_dir / "responses.jsonl", ["model", "item_id", "sample"])
    providers = build_providers(config, names)

    jobs = [
        (n, it, s)
        for n in names
        for it in items
        for s in range(args.samples)
        if not log.done((n, it["id"], s))
    ]

    def work(job):
        name, item, sample = job
        user = solver_prompt(item)
        rec = {
            "ts": now(),
            "model": name,
            "model_id": config[name]["model"],
            "item_id": item["id"],
            "sample": sample,
            "system_prompt_sha": sha(SOLVER_SYSTEM),
            "prompt_sha": sha(SOLVER_SYSTEM + "\n" + user),
        }
        try:
            c = providers[name].complete(SOLVER_SYSTEM, user)
            final, has_marker = extract_final(c.text)
            rec.update(
                response=c.text,
                final_answer=final,
                has_marker=has_marker,
                served_by=c.served_by,
                stop_reason=c.stop_reason,
                input_tokens=c.input_tokens,
                output_tokens=c.output_tokens,
                latency_s=round(c.latency_s, 2),
                **c.extra,
            )
            log.append(rec)
            return f"{name} {item['id']} s{sample}: {c.stop_reason} {c.latency_s:.0f}s  {final[:60]!r}"
        except Exception as e:  # recorded, retried on the next run
            rec["error"] = f"{type(e).__name__}: {e}"
            rec["traceback"] = traceback.format_exc(limit=3)
            log.append(rec)
            return f"ERROR {name} {item['id']} s{sample}: {rec['error'][:200]}"

    return run_pool(jobs, work, args.workers, "solve")


# ---------------------------------------------------------------- judge

def parse_json(text):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"no JSON object in judge reply: {text[:200]!r}")
    return json.loads(text[start : end + 1])


def cmd_judge(args, config):
    judges = pick(config, args.judges, "judges")
    items = {it["id"]: it for it in load_items(args)}
    run_dir = Path(args.run_dir)
    resp_path = run_dir / "responses.jsonl"
    if not resp_path.exists():
        sys.exit(f"{resp_path} not found; run `solve` first")
    write_meta(run_dir, "judge", args, config, judges)
    responses = Log(resp_path, ["model", "item_id", "sample"])
    log = Log(run_dir / "judgments.jsonl", ["judge", "model", "item_id", "sample"])
    providers = build_providers(config, judges)

    todo = [r for r in responses.latest.values() if not r.get("error") and r["item_id"] in items]
    if args.models:
        keep = set(pick(config, args.models, "models"))
        todo = [r for r in todo if r["model"] in keep]
    jobs = [
        (j, r)
        for j in judges
        for r in todo
        if not log.done((j, r["model"], r["item_id"], r["sample"]))
        or log.latest[(j, r["model"], r["item_id"], r["sample"])].get("response_ts") != r["ts"]
    ]

    def work(job):
        judge, resp = job
        item = items[resp["item_id"]]
        rec = {
            "ts": now(),
            "judge": judge,
            "judge_model_id": config[judge]["model"],
            "model": resp["model"],
            "item_id": resp["item_id"],
            "sample": resp["sample"],
            "response_ts": resp["ts"],
            "judge_prompt_sha": sha(JUDGE_SYSTEM),
        }
        final = resp.get("final_answer", "").strip()
        if not final:
            rec.update(parts=[], score=0.0, strict=False, reason="empty answer (not sent to judge)")
            log.append(rec)
            return f"{judge} <- {resp['model']} {resp['item_id']}: empty answer, 0"
        try:
            c = providers[judge].complete(JUDGE_SYSTEM, judge_prompt(item, final), schema=JUDGE_SCHEMA)
            data = parse_json(c.text)
            parts = data.get("parts") or []
            n_ok = sum(bool(p.get("correct")) for p in parts)
            score = n_ok / len(parts) if parts else 0.0
            rec.update(
                parts=parts,
                score=round(score, 4),
                strict=bool(parts) and n_ok == len(parts),
                reason=data.get("reason", ""),
                judge_served_by=c.served_by,
                judge_stop_reason=c.stop_reason,
                judge_output_tokens=c.output_tokens,
            )
            log.append(rec)
            return f"{judge} <- {resp['model']} {resp['item_id']} s{resp['sample']}: {n_ok}/{len(parts)}"
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
            log.append(rec)
            return f"ERROR {judge} <- {resp['model']} {resp['item_id']}: {rec['error'][:200]}"

    return run_pool(jobs, work, args.workers, "judge")


# ---------------------------------------------------------------- report

def bootstrap_ci(values, n=2000, seed=0):
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(values, k=len(values))) / len(values) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def pct(x):
    return f"{100 * x:.1f}"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def cohen_kappa(a, b):
    n = len(a)
    if not n:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def cmd_report(args, config):
    items = load_items(args)
    run_dir = Path(args.run_dir)
    validate_run_dataset(run_dir, args.data)
    responses = Log(run_dir / "responses.jsonl", ["model", "item_id", "sample"]).latest
    judgments = Log(run_dir / "judgments.jsonl", ["judge", "model", "item_id", "sample"]).latest
    judgments = {k: v for k, v in judgments.items() if not v.get("error")}
    if not responses:
        sys.exit("no responses yet; run `solve` first")

    judges = sorted({k[0] for k in judgments})
    if not judges:
        sys.exit("no judgments yet; run `judge` first")
    primary = args.judge or judges[0]
    if primary not in judges:
        sys.exit(f"no judgments by {primary!r}; available: {judges}")
    models = sorted({k[0] for k in responses})
    samples = sorted({k[2] for k in responses})
    versions = ", ".join(sorted({it.get("dataset_version", "v0") for it in items}))
    judge_model_ids = {config.get(j, {}).get("model") for j in judges}

    def model_label(model):
        if config.get(model, {}).get("model") in judge_model_ids:
            return f"{model} (judge model)"
        return model

    lines = [
        "# YKT textbook QA: results",
        "",
        f"Run: `{run_dir}`. Items: {len(items)}. Samples per item: {len(samples)}. "
        f"Judge: **{primary}** ({config.get(primary, {}).get('model', '?')}).",
        "",
        f"Dataset: **{versions}**, `{Path(args.data).name}` "
        f"(SHA-256 prefix `{sha(Path(args.data).read_text(encoding='utf-8'))}`).",
        "",
        "Solvers that also serve as a judge are marked **(judge model)**; their scores "
        "under that same model's grading are self-judged.",
        "",
        "**Accuracy** = all parts of the answer correct. **Partial** = share of parts correct "
        "(numbered sub-answers). Missing or failed answers count as wrong. "
        "95% CI is a bootstrap over items.",
        "",
        "Token columns show the configured request limit and API-reported output usage, "
        "which can include reasoning tokens.",
        "",
    ]

    def item_scores(model, judge, field):
        """Per item: mean over samples of score/strict; missing -> 0."""
        out = {}
        for it in items:
            vals = []
            for s in samples:
                j = judgments.get((judge, model, it["id"], s))
                vals.append(float(j[field]) if j else 0.0)
            out[it["id"]] = sum(vals) / len(vals)
        return out

    summary_rows, csv_rows, warnings = [], [], []
    for m in models:
        strict = item_scores(m, primary, "strict")
        partial = item_scores(m, primary, "score")
        resp = [responses.get((m, it["id"], s)) for it in items for s in samples]
        ok = [r for r in resp if r and not r.get("error")]
        n_missing = len(resp) - len(ok)
        n_unjudged = sum(
            1 for it in items for s in samples
            if (m, it["id"], s) in responses and not responses[(m, it["id"], s)].get("error")
            and (primary, m, it["id"], s) not in judgments
        )
        if n_missing:
            warnings.append(f"{m}: {n_missing} answers missing or failed (counted wrong). Re-run `solve`.")
        if n_unjudged:
            warnings.append(f"{m}: {n_unjudged} answers not judged by {primary} (counted wrong). Re-run `judge`.")
        prompts = {r.get("system_prompt_sha") for r in ok}
        vals = list(strict.values())
        lo, hi = bootstrap_ci(vals)
        out_tok = [r["output_tokens"] for r in ok if r.get("output_tokens")]
        requested_limit = config.get(m, {}).get("max_tokens")
        over_limit = [n for n in out_tok if requested_limit and n > requested_limit]
        if over_limit:
            warnings.append(
                f"{m}: API reported output token usage above requested max_tokens={requested_limit} "
                f"in {len(over_limit)} answers (maximum {max(over_limit)}). "
                "Effective total token budgets were not equal across providers."
            )
        lat = [r["latency_s"] for r in ok if r.get("latency_s")]
        summary_rows.append([
            model_label(m),
            config.get(m, {}).get("model", ""),
            pct(sum(vals) / len(vals)),
            f"{pct(lo)}–{pct(hi)}",
            pct(sum(partial.values()) / len(partial)),
            n_missing,
            sum(1 for r in ok if not r.get("has_marker")),
            sum(1 for r in ok if r.get("fallback_ran")),
            sum(1 for r in ok if r.get("stop_reason") in ("refusal", "max_tokens", "length") or str(r.get("stop_reason", "")).startswith("incomplete")),
            requested_limit if requested_limit is not None else "",
            max(out_tok) if out_tok else "",
            len(over_limit),
            round(sum(out_tok) / len(out_tok)) if out_tok else "",
            f"{sum(lat) / len(lat):.0f}" if lat else "",
        ])
        if len(prompts) > 1:
            warnings.append(f"{m}: answers come from {len(prompts)} different prompt versions.")
        for it in items:
            for s in samples:
                r = responses.get((m, it["id"], s)) or {}
                row = {
                    "model": m, "item_id": it["id"], "grade": it["grade"],
                    "needs_visual": int(it["needs_visual"]), "sample": s,
                    "reference": it["answer"], "final_answer": r.get("final_answer", ""),
                    "error": r.get("error", ""),
                    "requested_output_token_limit": requested_limit,
                    "reported_output_tokens": r.get("output_tokens"),
                    "output_over_requested_limit": int(bool(
                        requested_limit and (r.get("output_tokens") or 0) > requested_limit
                    )),
                }
                for j in judges:
                    jr = judgments.get((j, m, it["id"], s))
                    row[f"{j}:strict"] = int(jr["strict"]) if jr else ""
                    row[f"{j}:score"] = jr["score"] if jr else ""
                    row[f"{j}:reason"] = jr.get("reason", "") if jr else ""
                csv_rows.append(row)

    summary_rows.sort(key=lambda r: -float(r[2]))
    lines += ["## Summary", "", table(
        ["model", "model id", "accuracy %", "95% CI", "partial %", "missing", "no ХОРУЙ line",
         "fallback-served", "refused/truncated", "requested token limit", "max reported output tok",
         "over-limit answers", "avg output tok", "avg latency s"],
        summary_rows,
    ), ""]

    def breakdown(title, key_fn, keys):
        rows = []
        for m in models:
            strict = item_scores(m, primary, "strict")
            row = [model_label(m)]
            for k in keys:
                vals = [strict[it["id"]] for it in items if key_fn(it) == k]
                row.append(f"{pct(sum(vals) / len(vals))} (n={len(vals)})" if vals else "")
            rows.append(row)
        return ["## " + title, "", table(["model"] + [str(k) for k in keys], rows), ""]

    grades = sorted({it["grade"] for it in items}, key=lambda g: [int(x) for x in g.split("-")])
    lines += breakdown("Accuracy by grade", lambda it: it["grade"], grades)
    lines += breakdown(
        "Accuracy by picture dependence",
        lambda it: "needs picture" if it["needs_visual"] else "text only",
        ["text only", "needs picture"],
    )

    if len(judges) > 1:
        rows = []
        for i, a in enumerate(judges):
            for b in judges[i + 1:]:
                keys = [k[1:] for k in judgments if k[0] == a and (b,) + k[1:] in judgments]
                va = [bool(judgments[(a,) + k]["strict"]) for k in keys]
                vb = [bool(judgments[(b,) + k]["strict"]) for k in keys]
                agree = sum(x == y for x, y in zip(va, vb)) / len(keys) if keys else float("nan")
                rows.append([a, b, len(keys), pct(agree), f"{cohen_kappa(va, vb):.2f}"])
        lines += ["## Judge agreement (all parts correct vs not)", "",
                  table(["judge A", "judge B", "answers", "agree %", "Cohen's kappa"], rows), ""]
        for j in judges:
            if j == primary:
                continue
            rows = []
            for m in models:
                v = list(item_scores(m, j, "strict").values())
                rows.append([model_label(m), pct(sum(v) / len(v))])
            lines += [f"Accuracy as graded by {j}:", "", table(["model", "accuracy %"], rows), ""]

    if warnings:
        lines += ["## Warnings", ""] + [f"- {w}" for w in warnings] + [""]

    report = "\n".join(lines)
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    with (run_dir / "scores.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)
    print(report)
    print(f"\nwrote {run_dir / 'report.md'} and {run_dir / 'scores.csv'}", file=sys.stderr)
    return 0


# ---------------------------------------------------------------- preview

def cmd_preview(args, config):
    items = {it["id"]: it for it in load_items(args)}
    item = items.get(args.id) or sys.exit(f"unknown id {args.id!r}")
    print("=" * 30, "SOLVER SYSTEM", "=" * 30)
    print(SOLVER_SYSTEM)
    print("=" * 30, "SOLVER USER", "=" * 30)
    print(solver_prompt(item))
    print("=" * 30, "JUDGE USER (candidate = reference)", "=" * 30)
    print(judge_prompt(item, item["answer"]))
    return 0


def cmd_check(args, config):
    """Check credentials without sending prompts or displaying secrets."""
    names = list(dict.fromkeys(
        pick(config, args.models, "models") + pick(config, args.judges, "judges")
    ))
    failed = 0
    for name in names:
        cfg = config[name]
        env = cfg.get("api_key_env")
        present = not env or bool(os.environ.get(env))
        print(f"{name}: {cfg['model']} via {cfg['provider']} — "
              + (f"{env} {'set' if present else 'MISSING'}" if env else "no key required"))
        failed += not present
    return int(bool(failed))


# ---------------------------------------------------------------- main

def main():
    global SOLVER_SYSTEM, JUDGE_SYSTEM
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["solve", "judge", "report", "all", "preview", "check"])
    ap.add_argument("--models", default="", help="comma-separated models to evaluate (names from models.toml)")
    ap.add_argument("--judges", default="sol-6.1", help="comma-separated judge models (default: sol-6.1)")
    ap.add_argument("--judge", default="", help="report: which judge's grades to headline (default: first)")
    ap.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    ap.add_argument("--data", default=str(DEFAULT_DATA))
    ap.add_argument("--config", default=str(BENCH / "models.toml"))
    ap.add_argument("--solver-system", type=Path, help="model instructions for this run; recorded and checked on resume")
    ap.add_argument("--judge-system", type=Path, help="judge instructions for this run; recorded and checked on resume")
    ap.add_argument("--samples", type=int, default=1, help="answers per item per model (default 1)")
    ap.add_argument("--workers", type=int, default=8, help="parallel API calls (default 8)")
    ap.add_argument("--ids", default="", help="only these item ids (comma-separated)")
    ap.add_argument("--limit", type=int, default=0, help="only the first N items")
    ap.add_argument("--id", default="", help="preview: item id")
    args = ap.parse_args()
    if args.solver_system:
        SOLVER_SYSTEM = args.solver_system.read_text(encoding="utf-8").strip()
        if not SOLVER_SYSTEM:
            ap.error("--solver-system must not be empty")
    if args.judge_system:
        JUDGE_SYSTEM = args.judge_system.read_text(encoding="utf-8").strip()
        if not JUDGE_SYSTEM:
            ap.error("--judge-system must not be empty")

    from dotenv import load_dotenv

    # Existing environment wins; bench/.env takes priority over the repo .env.
    load_dotenv(BENCH / ".env")
    load_dotenv(BENCH.parent / ".env")
    config = load_config(args.config)
    if args.command in ("solve", "all") and not args.models:
        ap.error("--models is required, e.g. --models fable-5.2,glm-5.3,astra")

    if args.command == "preview":
        return cmd_preview(args, config)
    if args.command == "check":
        return cmd_check(args, config)
    if args.command == "solve":
        return 1 if cmd_solve(args, config) else 0
    if args.command == "judge":
        return 1 if cmd_judge(args, config) else 0
    if args.command == "report":
        return cmd_report(args, config)
    # all
    failed = cmd_solve(args, config)
    failed += cmd_judge(args, config)
    cmd_report(args, config)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
