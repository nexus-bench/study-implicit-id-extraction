# Implicit ID extraction across OpenRouter providers

This is a small, reproducible **information extraction diagnostic**. It asks
whether provider tags serving the same OpenRouter model slug return the exact
expected JSON for a record whose ID appears in a form label rather than an
explicit `id` field. The prompt also distinguishes an explicitly empty
nickname (`""`) from a missing middle name (`null`). It tests one narrow
prompt family, not general model quality or approximate string matching.

For example, a record beginning `Form K111:` should produce:

```json
{"id":"K111","nickname":"","middle_name":null}
```

The [DeepSeek V4.1 Flash temperature-zero run](results/RESULTS-DS-TOP10-20-TEMPERATURE0.md)
scored 20 requests per provider across ten pinned provider tags. Exact-match
rates ranged from 10% to 100%. The report includes the full provider table and
raw request/response evidence. These ten IDs are instances of one template,
so the percentages describe this diagnostic, not a broad provider ranking.

## Method

The script sends `Form K111:` through `Form K120:` twice to each provider by
default. Each request uses the same system instruction, a three-field JSON
schema, and one OpenRouter model slug. It pins one provider tag with fallback
disabled. **% correct = exact expected JSON responses / scheduled requests**
for that provider. Wrong answers, invalid or incomplete outputs, and request
errors all count as not correct and are shown separately. This study keeps
only the implicit-ID condition from the original `llm-provider-bench`
experiment; its explicit `Record ID:` control is omitted.

`python bench.py` selects the ten eligible provider tags with the highest
recent median throughput for `deepseek/deepseek-v4.1-flash`. This selects for
speed, not correctness, and the set can change between runs. The defaults are
20 requests per provider, temperature 0, high reasoning effort, strict JSON
schema, 8192 output tokens, five concurrent requests, a 60-second socket
timeout per attempt, and three retries after 429 or 5xx responses. A 429 starts
a cooldown shared across workers; in-flight requests may still complete.

## Run

Python 3.10+ is sufficient; there are no runtime dependencies. Supply an
OpenRouter key through `OPENROUTER_API_KEY`, a local gitignored `.env` file
containing `OPENROUTER_API_KEY=...`, or `--env-file path/to/credentials.env`.
An explicit env file takes precedence over the environment, which takes
precedence over the local `.env`. The key is never written to results.

```sh
python bench.py
```

The run makes paid completion requests. To inspect eligible provider tags
without completions:

```sh
python bench.py --list-providers
python bench.py --model z-ai/glm-5.3-flash --list-providers
```

Common overrides:

```sh
python bench.py --model z-ai/glm-5.3-flash --top 5
python bench.py --provider together --provider fireworks/us
python bench.py --all-providers
python bench.py --temperature 1 --num-requests 10
python bench.py --max-tokens 4096 --concurrency 3 --timeout 90 --retries 5
```

`--top N` ranks eligible tags by the p50 throughput in OpenRouter's live
[endpoint catalog](https://openrouter.ai/docs/api/api-reference/endpoints/list-all-endpoints-for-a-model).
Tags without a measurement are excluded, so fewer than N may be selected.
Eligibility requires the parameters used by this test; it does not guarantee
account access or a successful response. `--all-providers` uses every eligible
tag. `--num-requests N` sets the requests per provider, cycling through the
ten cases; `--repeats N` instead runs N full ten-case passes. Temperature can
be set from 0 to 2.

The CLI prints a progress count and a `% correct` table, and writes every
request and response to a new timestamped `results-*.jsonl` file as it
finishes. These local files are gitignored; use `--output` to choose a path.
Existing output is never overwritten. A nonzero exit code means at least one
request failed or returned an invalid or incomplete output. Retrying may
incur another charge if the server processed the earlier attempt.

## Recorded runs

### Paired provider experiment

The existing `bench.py` runner has a `--paired` mode for a matched implicit/explicit-ID study. It freezes the eligible provider tags and 100 distinct cases in a JSON manifest. Every provider receives both wordings of each case at temperatures 0 and 1. Only the ID heading changes between each implied/explicit pair. The same system instruction, strict JSON schema, high reasoning effort, `top_p=1`, output-token cap, and fallback-disabled provider routing apply throughout. Jobs are shuffled in paired blocks to reduce time-order effects. The JSONL output is append-only and `--run` resumes jobs already recorded there.

The manifest for the October 4 run is [`results/PAIRED-MANIFEST-20261004.json`](results/PAIRED-MANIFEST-20261004.json). The endpoint catalog had 21 eligible tags at preparation time; `open-inference/fp4` from the earlier 22-provider run was absent. To repeat this exact panel, use the committed manifest. To prepare a fresh panel from the live catalog, use `--prepare` with a new manifest path.

```sh
python bench.py --paired --run \
  --manifest results/PAIRED-MANIFEST-20261004.json \
  --output paired-results-20261004.jsonl \
  --concurrency 24
```

Preparation used `--max-tokens 32768 --timeout 240 --retries 3`. These values are stored in the manifest and used by every resumed run. Completion requests are paid. The `--limit N` option runs at most N remaining jobs for a preflight.

The paired report scores correct IDs among valid, completed JSON answers as its primary measure. It shows errors in the other two fields separately and also reports the exact three-field JSON total. Every score uses all 100 scheduled cases as its denominator.

If any requests end in HTTP 429 after the initial retry budget, rerun with `--retry-rate-limits`. The runner also recognizes 429 errors embedded in HTTP 200 response bodies. This mode retries only those jobs, allows up to ten retries, and appends a new raw attempt. For scoring, use the latest row for each `job_key`; an unresolved 429 is a request error, not a wrong extraction answer.

```sh
python bench.py --paired --run --retry-rate-limits \
  --manifest results/PAIRED-MANIFEST-20261004.json \
  --output paired-results-20261004.jsonl \
  --concurrency 1
python bench.py --paired --report \
  --manifest results/PAIRED-MANIFEST-20261004.json \
  --output results/PAIRED-RAW-20261004.jsonl.gz
```

The archived raw JSONL is gzip compressed. The runner can report directly from it; to resume a run, use an uncompressed JSONL output path. The October 4 run used concurrency 24 for the main pass and concurrency 1 for rate-limit retries. It recorded 8,485 raw attempts for 8,400 unique jobs.

Each report links its own raw evidence and documents its settings. Runs used
different provider sets or settings; compare their percentages with those
differences in mind.

| Model and scope | Report |
| --- | --- |
| DeepSeek V4.1 Flash, 21 provider tags, 100 paired cases, temperatures 0 and 1 | [Paired study](results/PAIRED-STUDY-20261004.md) |
| DeepSeek V4.1 Flash, top 10, 20 requests each, temperature 0 | [Temperature-zero comparison](results/RESULTS-DS-TOP10-20-TEMPERATURE0.md) |
| DeepSeek V4.1 Flash, top 10, 20 requests each, temperature 1 | [Temperature-one run](results/RESULTS-DS-TOP10-20.md) |
| DeepSeek V4.1 Flash, top 5, 20 requests each, temperature 1 | [Top-five twenty-request run](results/RESULTS-DS-TOP5-20.md) |
| DeepSeek V4.1 Flash, top 5, 10 requests each, temperature 1 | [Top-five ten-request run](results/RESULTS-DS-TOP5.md) |
| DeepSeek V4.1 Flash, 22 providers, 10 requests each, temperature 1 | [All-provider run](results/RESULTS.md) |
| GLM-5.3-Flash, top 5, 10 requests each, temperature 1 | [GLM run](results/RESULTS-GLM.md) |

The original prompts, expected answers, and scoring rule are in `bench.py`.
The paired mode's case generation and ID-specific report are in
`paired_experiment.py`. The GLM option extends the original DeepSeek diagnostic.

## License

Apache License 2.0. See [LICENSE](LICENSE).
