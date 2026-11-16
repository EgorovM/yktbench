import json
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import leaderboard_metrics as metrics


class MetricsTests(unittest.TestCase):
    def test_catalog_prices_are_per_million_and_gigachat_uses_supplied_rates(self):
        catalog = {"data": [{"id": model_id, "pricing": {"prompt": "0.000002", "completion": "0.00001"}}
                            for model_id in metrics.PRICING_MODELS.values()]}
        snapshot = metrics.pricing_snapshot(catalog, "test")
        self.assertEqual(snapshot["models"]["astra"]["input_usd_per_million"], 2)
        self.assertEqual(snapshot["models"]["astra"]["output_usd_per_million"], 10)
        giga = snapshot["models"]["gigachat-3.5"]
        self.assertEqual(giga["input_usd_per_million"], 1.07)
        self.assertEqual(giga["output_usd_per_million"], 3.21)
        self.assertEqual(metrics.estimated_cost({"input_tokens": 33650, "output_tokens": 8263}, giga),
                         Decimal("0.06252973"))

    def test_estimates_require_usage_and_rates_but_zero_usage_is_valid(self):
        price = {"input_usd_per_million": 8, "output_usd_per_million": 40}
        self.assertEqual(metrics.estimated_cost({"input_tokens": 100, "output_tokens": 200}, price), Decimal("0.0088"))
        self.assertEqual(metrics.estimated_cost({"input_tokens": 0, "output_tokens": 0}, price), 0)
        self.assertIsNone(metrics.estimated_cost({"input_tokens": None, "output_tokens": 1}, price))
        self.assertIsNone(metrics.estimated_cost({"input_tokens": 1, "output_tokens": 1}, {}))

    def test_render_keeps_prices_next_to_estimate_and_actual_charges_separate(self):
        row = metrics.summarize({"q1": {"input_tokens": 1000, "output_tokens": 2000,
                                               "response_id": "gen-1"}}, 90, {"gen-1": {"total_cost": 0.01}})
        snapshot = {"updated_utc": "test", "pricing": {"retrieved_utc": "test", "models": {
            "astra": {"input_usd_per_million": 10, "output_usd_per_million": 50}}},
            "datasets": {"vals_90": {"questions": 90, "models": {"astra": row}}}}
        text = metrics.render("vals_90", ["astra"], snapshot)
        self.assertIn("| Input $/1M | Output $/1M | Estimated cost (USD) | Known API cost (USD) |", text)
        self.assertIn("| 1,000† | 2,000† | 1/90 | 10 | 50 | 0.1100*† | 0.0100 | 1/90 |", text)

    def test_zero_latency_timeout_and_partial_usage_are_counted(self):
        records = {
            "a": {"latency_s": 0.0, "input_tokens": 0, "output_tokens": 0},
            "b": {"latency_s": 10.0, "input_tokens": 5, "output_tokens": 10},
            "c": {"latency_s": 900.0, "timed_out": True, "input_tokens": None, "output_tokens": None},
        }
        row = metrics.summarize(records, 90, {})
        self.assertEqual(row["latency_records"], 3)
        self.assertEqual(row["median_s"], 10)
        self.assertEqual(row["p95_s"], 900)
        self.assertEqual(row["timeouts"], 1)
        self.assertEqual(row["usage_records"], 2)
        self.assertEqual(row["output_tokens"], 10)
        self.assertIsNone(row["known_api_cost_usd"])

    def test_known_cost_falls_back_to_starred_estimate_without_replacing_zero_charge(self):
        for expected, known, cost, suffix in [(1, None, "0.1100*", "0/1"),
                                               (90, None, "0.1100*†", "0/90"),
                                               (1, 0.0, "0.0000", "1/1")]:
            with self.subTest(expected=expected, known=known):
                charges = {} if known is None else {"gen-1": {"total_cost": known}}
                row = metrics.summarize({"q1": {"input_tokens": 1000, "output_tokens": 2000,
                                                       "response_id": "gen-1"}}, expected, charges)
                snapshot = {"updated_utc": "test", "pricing": {"models": {
                    "astra": {"input_usd_per_million": 10, "output_usd_per_million": 50}}},
                    "datasets": {"test": {"questions": expected, "models": {"astra": row}}}}
                text = metrics.render("test", ["astra"], snapshot)
                entry = next(line for line in text.splitlines() if line.startswith("| GPT-6 Astra"))
                self.assertTrue(entry.endswith(f"| {cost} | {suffix} |"))
                self.assertEqual(row["known_api_cost_usd"], known)

    def test_reused_request_is_not_billed_twice_and_zero_charge_is_known(self):
        records = {"a": {"response_id": "gen-1"}, "b": {"response_id": "gen-1"},
                   "c": {"response_id": "gen-2"}, "d": {"response_id": "missing"}}
        row = metrics.summarize(records, 60, {"gen-1": {"total_cost": 0.1}, "gen-2": {"total_cost": 0.0}})
        self.assertAlmostEqual(row["known_api_cost_usd"], 0.1)
        self.assertEqual(row["costed_answers"], 3)
        self.assertEqual(row["costed_requests"], 2)

    def test_percentile_uses_nearest_rank(self):
        row = metrics.summarize({str(i): {"latency_s": i} for i in range(1, 21)}, 20, {})
        self.assertEqual(row["p95_s"], 19)

    def test_last_attempt_selection_excludes_other_datasets_and_samples(self):
        rows = [{"model": "astra", "item_id": "q1", "sample": 0, "latency_s": 1},
                {"model": "astra", "item_id": "q1", "sample": 0, "latency_s": 3},
                {"model": "astra", "item_id": "q1", "sample": 1, "latency_s": 100},
                {"model": "astra", "item_id": "other", "sample": 0, "latency_s": 100},
                {"model": "astra", "item_id": "q2", "sample": 0, "error": "failed"}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "responses.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            result = metrics.select_local(path, ["astra"], {"q1", "q2"})
        self.assertEqual(list(result["astra"]), ["q1"])
        self.assertEqual(result["astra"]["q1"]["latency_s"], 3)

    def test_extended_table_is_idempotent_and_preserves_main_table(self):
        original = "# Results\n\n| Model Name | Accuracy |\n|---|---:|\n| Astra | 41.1 |\n\nNotes.\n"
        table = metrics.START + "\n\nMetrics\n\n" + metrics.END
        first = metrics.insert_table(original, table)
        self.assertIn("| Astra | 41.1 |", first)
        self.assertEqual(first.count(metrics.START), 1)
        self.assertEqual(metrics.insert_table(first, table), first)
        self.assertTrue(first.endswith("Notes.\n"))

    def test_filtered_hosted_archive_is_reused_without_run_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "results/vals_90"
            base.mkdir(parents=True)
            (root / "valkyrie").mkdir()
            (base / "valkyrie_runs.json").write_text(json.dumps([{"model": "astra", "run_id": "run1"}]))
            (root / "valkyrie/leaderboard_snapshot.json").write_text(json.dumps({
                "rows": [{"model": "astra", "task_rewards": {"q1": {"reward": 1}}}]}))
            archive = root / "results/leaderboard_metrics/outputs/run1/q1/artifacts"
            archive.mkdir(parents=True)
            (archive / "response.json").write_text(json.dumps({"latency_s": 12}))
            with patch.object(metrics, "ROOT", root):
                first = metrics.hosted_records(base, ["astra"], {"q1"})
                second = metrics.hosted_records(base, ["astra"], {"q1"})
            self.assertEqual(first, second)
            self.assertEqual(first["astra"]["q1"]["latency_s"], 12)

    def test_missing_cost_is_a_dash_with_explicit_coverage(self):
        row = metrics.summarize({"a": {"latency_s": 1}}, 90, {})
        snapshot = {"updated_utc": "test", "datasets": {"vals_90": {"questions": 90, "models": {"astra": row}}}}
        text = metrics.render("vals_90", ["astra"], snapshot)
        entry = next(line for line in text.splitlines() if line.startswith("| GPT-6 Astra"))
        self.assertTrue(entry.endswith("| — | 0/90 |"))
        self.assertIn("not total benchmark spend", text)


if __name__ == "__main__":
    unittest.main()
