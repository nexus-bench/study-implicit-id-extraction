"""Paired experiment mode for the repository's bench.py runner."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import random
import sys

import bench


BODY_TEMPLATES = (
    'nickname was explicitly set to the empty string "". No middle_name was provided. Extract id, nickname, middle_name.',
    'The nickname field is present with value "". The middle_name field is absent. Extract id, nickname, middle_name.',
    'nickname="" was entered. No middle_name was entered. Extract id, nickname, middle_name.',
    'nickname: ""\nThere is no middle_name entry. Extract id, nickname, middle_name.',
    'The nickname is explicitly an empty string (""). The record does not provide middle_name. Extract id, nickname, middle_name.',
)
TEMPERATURES = (0, 1)
CONDITIONS = ("implied", "explicit")


def cases():
    return [
        {"id": f"K{201 + index}", "template": index % len(BODY_TEMPLATES),
         "body": BODY_TEMPLATES[index % len(BODY_TEMPLATES)]}
        for index in range(100)
    ]


def user_message(case, condition):
    if condition == "implied":
        prefix = f"Form {case['id']}: "
    elif condition == "explicit":
        prefix = f"Record ID: {case['id']}. "
    else:
        raise ValueError(f"unknown condition: {condition}")
    return prefix + case["body"]


def jobs(manifest):
    blocks = [(provider, case, temperature)
              for provider in manifest["providers"]
              for case in manifest["cases"]
              for temperature in TEMPERATURES]
    random.Random(manifest["shuffle_seed"]).shuffle(blocks)
    for provider, case, temperature in blocks:
        conditions = list(CONDITIONS)
        random.Random(f"{manifest['shuffle_seed']}:{provider}:{case['id']}:{temperature}").shuffle(conditions)
        for condition in conditions:
            yield provider, case, temperature, condition


def job_key(provider, case_id, temperature, condition):
    return f"{provider}|{case_id}|{temperature}|{condition}"


def latest_rows(path):
    latest = {}
    raw_count = 0
    if path.exists():
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row["job_key"] in latest and not is_rate_limit(latest[row["job_key"]]):
                    raise ValueError(f"duplicate non-rate-limited job: {row['job_key']}")
                latest[row["job_key"]] = row
                raw_count += 1
    return latest, raw_count


def is_rate_limit(row):
    if row.get("error") == "HTTP 429":
        return True
    response = row.get("response")
    return (isinstance(response, dict) and isinstance(response.get("error"), dict)
            and response["error"].get("code") == 429)


def id_is_correct(row):
    if row["status"] not in ("correct", "wrong"):
        return False
    try:
        answer = json.loads(row["response"]["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError, ValueError):
        return False
    return isinstance(answer, dict) and answer.get("id") == row["id"]


def report(manifest, latest, raw_count):
    expected = len(manifest["providers"]) * len(manifest["cases"]) * 4
    if len(latest) != expected:
        raise ValueError(f"report requires all {expected} jobs; only {len(latest)} are recorded")
    expected_keys = {job_key(provider, case["id"], temperature, condition)
                     for provider, case, temperature, condition in jobs(manifest)}
    if set(latest) != expected_keys:
        raise ValueError("recorded jobs do not match the frozen manifest")
    cases_by_id = {case["id"]: case for case in manifest["cases"]}
    for row in latest.values():
        case = cases_by_id[row["id"]]
        expected_request = bench.payload(manifest["model"], row["provider"], row["id"],
                                         manifest["max_tokens"], row["temperature"])
        expected_request["messages"][1]["content"] = user_message(case, row["condition"])
        if row["request"] != expected_request or row["template"] != case["template"]:
            raise ValueError(f"request differs from frozen manifest: {row['job_key']}")
    print(f"# Paired implicit-ID extraction: {manifest['model']}")
    print()
    print(f"Final jobs: {len(latest)}/{expected}; raw attempts: {raw_count}. "
          "Each score is correct ID / 100 scheduled cases. "
          "HTTP 429 and other request errors are listed separately.")
    print()
    print("| Provider tag | T0 implied | T0 explicit | T1 implied | T1 explicit | "
          "Wrong ID | Other fields wrong | Incomplete/invalid | Request errors |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for provider in manifest["providers"]:
        cells = []
        provider_rows = [r for r in latest.values() if r["provider"] == provider]
        for temperature in TEMPERATURES:
            for condition in CONDITIONS:
                subset = [r for r in provider_rows if r["temperature"] == temperature
                          and r["condition"] == condition]
                correct = sum(id_is_correct(r) for r in subset)
                cells.append(f"{correct}/{len(manifest['cases'])}")
        wrong_id = sum(r["status"] == "wrong" and not id_is_correct(r) for r in provider_rows)
        other_wrong = sum(r["status"] == "wrong" and id_is_correct(r) for r in provider_rows)
        incomplete = sum(r["status"] in ("incomplete", "invalid") for r in provider_rows)
        errors = sum(r["status"] == "error" for r in provider_rows)
        print(f"| {provider} | {' | '.join(cells)} | {wrong_id} | {other_wrong} | "
              f"{incomplete} | {errors} |")
    print()
    exact = sum(r["status"] == "correct" for r in latest.values())
    print(f"Exact three-field JSON: {exact}/{expected} jobs.")
    print()
    print("## By case template")
    print()
    print("| Template | T0 implied | T0 explicit | T1 implied | T1 explicit |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for template in range(len(BODY_TEMPLATES)):
        cells = []
        for temperature in TEMPERATURES:
            for condition in CONDITIONS:
                subset = [r for r in latest.values() if r["template"] == template
                          and r["temperature"] == temperature and r["condition"] == condition]
                cells.append(f"{sum(id_is_correct(r) for r in subset)}/{len(subset)}")
        print(f"| {template + 1} | {' | '.join(cells)} |")
    print()
    print("The provider tag names OpenRouter's reported serving target. "
          "It does not prove identical weights, quantization, or engines across tags.")


def run_one(job, manifest, key, cooldown, retry_rate_limit=False):
    provider, case, temperature, condition = job
    body = bench.payload(manifest["model"], provider, case["id"],
                         manifest["max_tokens"], temperature)
    body["messages"][1]["content"] = user_message(case, condition)
    retries = max(manifest["retries"], 10) if retry_rate_limit else manifest["retries"]
    response, attempts, error = bench.request(body, key, manifest["timeout"],
                                               retries, cooldown)
    return {
        "job_key": job_key(provider, case["id"], temperature, condition),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": provider, "id": case["id"], "template": case["template"],
        "temperature": temperature, "condition": condition,
        "request": body, "response": response, "attempts": attempts,
        "retry_rate_limit": retry_rate_limit, "retry_budget": retries,
        "status": "error" if error else bench.score(response, case["id"]),
        "error": error,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true", help="freeze eligible providers and cases without completions")
    parser.add_argument("--run", action="store_true", help="make paid requests, resuming recorded jobs")
    parser.add_argument("--report", action="store_true", help="summarize the latest recorded outcome per job")
    parser.add_argument("--concurrency", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=240)
    parser.add_argument("--max-tokens", type=int, default=32768)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--limit", type=int, help="run at most this many remaining jobs for a preflight")
    parser.add_argument("--retry-rate-limits", action="store_true",
                        help="retry only jobs whose latest recorded result is HTTP 429")
    args = parser.parse_args(argv)
    if sum((args.prepare, args.run, args.report)) != 1:
        parser.error("choose exactly one of --prepare, --run, or --report")
    if args.run and args.output.suffix == ".gz":
        parser.error("--run requires an uncompressed JSONL output path")
    if (args.concurrency < 1 or args.timeout <= 0 or args.max_tokens < 1
            or not 0 <= args.retries <= 10 or (args.limit is not None and args.limit < 1)):
        parser.error("invalid request limits")
    key = bench.resolve_key(None) if not args.report else None
    if not key and not args.report:
        parser.error("set OPENROUTER_API_KEY or add it to .env")
    if args.prepare:
        if args.manifest.exists() or args.output.exists():
            parser.error("manifest or output already exists")
        providers = list(bench.discover_providers(bench.MODEL, key, args.timeout))
        if not providers:
            parser.error("no eligible providers found")
        manifest = {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "model": bench.MODEL, "providers": providers, "cases": cases(),
            "temperatures": TEMPERATURES, "conditions": CONDITIONS,
            "shuffle_seed": 20261004,
            "max_tokens": args.max_tokens, "timeout": args.timeout,
            "retries": args.retries, "top_p": 1, "reasoning_effort": "high",
            "schema": bench.SCHEMA, "system_message": bench.SYSTEM,
        }
        args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Prepared {len(providers)} providers, {len(manifest['cases'])} cases, "
              f"{len(providers) * len(manifest['cases']) * 4} scheduled requests")
        print(f"Manifest: {args.manifest}")
        return 0

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest["model"] != bench.MODEL or len(manifest["cases"]) != 100:
        parser.error("unexpected manifest")
    all_jobs = list(jobs(manifest))
    if len({job_key(p, c["id"], t, q) for p, c, t, q in all_jobs}) != len(all_jobs):
        parser.error("duplicate jobs in manifest")
    try:
        existing, history_count = latest_rows(args.output)
    except ValueError as exc:
        parser.error(str(exc))
    if args.report:
        try:
            report(manifest, existing, history_count)
        except ValueError as exc:
            parser.error(str(exc))
        return 0
    if args.retry_rate_limits:
        remaining = [job for job in all_jobs
                     if is_rate_limit(existing.get(job_key(job[0], job[1]["id"], job[2], job[3]), {}))]
    else:
        remaining = [job for job in all_jobs if job_key(job[0], job[1]["id"], job[2], job[3]) not in existing]
    if args.limit is not None:
        remaining = remaining[:args.limit]
    print(f"Recorded {len(existing)}/{len(all_jobs)} final jobs ({history_count} raw attempts); "
          f"running {len(remaining)}{' rate-limit retries' if args.retry_rate_limits else ''} with "
          f"concurrency {args.concurrency}, timeout {manifest['timeout']}s, "
          f"max_tokens {manifest['max_tokens']}", file=sys.stderr, flush=True)
    counts = Counter(row["status"] for row in existing.values())
    cooldown = bench.RateLimitCooldown()
    with args.output.open("a", encoding="utf-8") as stream:
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = [pool.submit(run_one, job, manifest, key, cooldown, args.retry_rate_limits)
                       for job in remaining]
            for index, future in enumerate(as_completed(futures), 1):
                row = future.result()
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                if args.retry_rate_limits:
                    counts[existing[row["job_key"]]["status"]] -= 1
                    existing[row["job_key"]] = row
                counts[row["status"]] += 1
                if index % 100 == 0 or index == len(remaining):
                    progress_label = (f"Retried {index}/{len(remaining)}" if args.retry_rate_limits
                                      else f"Completed {len(existing) + index}/{len(all_jobs)}")
                    print(f"{progress_label} | "
                          f"correct {counts['correct']} wrong {counts['wrong']} "
                          f"incomplete {counts['incomplete']} invalid {counts['invalid']} "
                          f"errors {counts['error']}", file=sys.stderr, flush=True)
    return 0
