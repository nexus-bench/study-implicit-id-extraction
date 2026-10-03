import json
from io import BytesIO, StringIO
from contextlib import redirect_stdout
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import bench


class ExperimentTests(unittest.TestCase):
    def test_catalog_filters_and_deduplicates_compatible_targets(self):
        required = sorted(bench.REQUIRED_PARAMETERS)
        catalog = {"data": {"id": "z-ai/glm-5.3-flash", "endpoints": [
            {"tag": "ready/fp8", "provider_name": "Ready", "status": 0,
             "supported_parameters": required},
            {"tag": "ready/fp8", "provider_name": "Ready", "status": 0,
             "supported_parameters": required},
            {"tag": "down", "status": -2, "supported_parameters": required},
            {"tag": "no-schema", "status": 0,
             "supported_parameters": [p for p in required if p != "structured_outputs"]},
        ]}}
        self.assertEqual(bench.select_providers(catalog, "z-ai/glm-5.3-flash"), {"ready/fp8": "Ready"})
        with self.assertRaises(ValueError):
            bench.select_providers(catalog, "deepseek/deepseek-v4.1-flash")

    def test_top_selects_fastest_eligible_provider_tags(self):
        required = sorted(bench.REQUIRED_PARAMETERS)
        def endpoint(tag, rate, status=0):
            return {"tag": tag, "provider_name": tag, "status": status,
                    "supported_parameters": required,
                    "throughput_last_30m": {"p50": rate}}
        catalog = {"data": {"id": bench.MODEL, "endpoints": [
            endpoint("slow", 10), endpoint("fast", 30), endpoint("fast", 35),
            endpoint("middle", 20), endpoint("down", 100, -1),
            {"tag": "unmeasured", "status": 0, "supported_parameters": required},
        ]}}
        self.assertEqual(list(bench.select_providers(catalog, bench.MODEL, 2)), ["fast", "middle"])

    def test_list_mode_makes_no_completion_requests(self):
        with patch.object(bench, "discover_providers", return_value={"ready/fp8": "Ready"}), patch.object(bench, "run_one") as run:
            with redirect_stdout(StringIO()) as output:
                code = bench.main(["--model", "z-ai/glm-5.3-flash", "--list-providers"])
        self.assertEqual(code, 0)
        self.assertIn("ready/fp8", output.getvalue())
        run.assert_not_called()

    def test_all_providers_runs_ten_each(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "results.jsonl"
            def fake_run(provider, record_id, model, key, timeout, retries, cooldown):
                return {"provider": provider, "id": record_id, "status": "correct"}
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}), \
                 patch.object(bench, "discover_providers", return_value={"ready/fp8": "Ready"}), \
                 patch.object(bench, "run_one", side_effect=fake_run) as run, \
                 redirect_stdout(StringIO()) as printed:
                code = bench.main(["--model", "z-ai/glm-5.3-flash", "--all-providers", "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertEqual(run.call_count, 10)
            self.assertEqual(len(output.read_text().splitlines()), 10)
            self.assertIn("z-ai/glm-5.3-flash", printed.getvalue())
            self.assertIn("100%", printed.getvalue())

    def test_percent_correct_uses_all_ten_cases(self):
        rows = ([{"provider": "ready/fp8", "status": "correct"}] * 7
                + [{"provider": "ready/fp8", "status": status}
                   for status in ("wrong", "invalid", "error")])
        with redirect_stdout(StringIO()) as output:
            bench.table(rows, ["ready/fp8"], "example/model")
        self.assertIn("70%", output.getvalue())
        self.assertIn("7/10", output.getvalue())

    def test_ten_implicit_requests(self):
        self.assertEqual(len(bench.IDS), 10)
        for record_id in bench.IDS:
            body = bench.payload(bench.MODEL, "example", record_id)
            self.assertIn(f"Form {record_id}:", body["messages"][1]["content"])
            self.assertEqual(body["provider"]["only"], ["example"])

    def test_exact_gold_and_incomplete_are_distinct(self):
        response = {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({
            "id": "K111", "nickname": "", "middle_name": None})}}]}
        self.assertEqual(bench.score(response, "K111"), "correct")
        response["choices"][0]["message"]["content"] = '{"id":"K111","nickname":null,"middle_name":null}'
        self.assertEqual(bench.score(response, "K111"), "wrong")
        response["choices"][0]["finish_reason"] = "length"
        self.assertEqual(bench.score(response, "K111"), "incomplete")

    def test_retry_after(self):
        self.assertEqual(bench.retry_delay("2", 0), 2)
        with patch.object(bench.random, "random", return_value=0):
            self.assertEqual(bench.retry_delay(None, 2), 4)

    def test_retry_429_then_success(self):
        for code in (429, 503):
            with self.subTest(code=code):
                first = HTTPError(bench.URL, code, "temporary", {"Retry-After": "0"}, BytesIO(b""))
                second = BytesIO(b'{"choices": []}')
                with patch.object(bench, "urlopen", side_effect=[first, second]) as send, patch.object(bench.time, "sleep"):
                    response, attempts, error = bench.request({}, "test-key", 5, 2)
                self.assertEqual((response, attempts, error), ({"choices": []}, 2, None))
                self.assertEqual(send.call_count, 2)

    def test_no_retry_for_bad_request(self):
        first = HTTPError(bench.URL, 400, "bad request", {}, BytesIO(b""))
        with patch.object(bench, "urlopen", side_effect=first) as send:
            response, attempts, error = bench.request({}, "test-key", 5, 3)
        self.assertEqual((response, attempts, error), (None, 1, "HTTP 400"))
        self.assertEqual(send.call_count, 1)

    def test_429_delays_other_requests_even_without_retries(self):
        clock = [100.0]
        sleeps = []

        def sleep(seconds):
            sleeps.append(seconds)
            clock[0] += seconds

        first = HTTPError(bench.URL, 429, "rate limited", {"Retry-After": "2"}, BytesIO(b""))
        second = BytesIO(b'{"choices": []}')
        cooldown = bench.RateLimitCooldown()
        with patch.object(bench, "urlopen", side_effect=[first, second]) as send, \
             patch.object(bench.time, "monotonic", side_effect=lambda: clock[0]), \
             patch.object(bench.time, "sleep", side_effect=sleep):
            self.assertEqual(bench.request({}, "test-key", 5, 0, cooldown)[2], "HTTP 429")
            self.assertEqual(bench.request({}, "test-key", 5, 0, cooldown)[2], None)
        self.assertEqual(send.call_count, 2)
        self.assertEqual(sleeps, [2])


if __name__ == "__main__":
    unittest.main()
