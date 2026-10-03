import json
from io import BytesIO
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import bench


class ExperimentTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
