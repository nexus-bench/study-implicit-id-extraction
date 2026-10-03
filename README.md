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

The [DeepSeek V4.1 Flash temperature-zero run](RESULTS-DS-TOP10-20-TEMPERATURE0.md)
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
errors all count as not correct and are shown separately. This mirror keeps
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

Each report links its own raw evidence and documents its settings. Runs used
different provider sets or settings; compare their percentages with those
differences in mind.

| Model and scope | Report |
| --- | --- |
| DeepSeek V4.1 Flash, top 10, 20 requests each, temperature 0 | [Temperature-zero comparison](RESULTS-DS-TOP10-20-TEMPERATURE0.md) |
| DeepSeek V4.1 Flash, top 10, 20 requests each, temperature 1 | [Temperature-one run](RESULTS-DS-TOP10-20.md) |
| DeepSeek V4.1 Flash, top 5, 20 requests each | [Top-five twenty-request run](RESULTS-DS-TOP5-20.md) |
| DeepSeek V4.1 Flash, top 5, 10 requests each | [Top-five ten-request run](RESULTS-DS-TOP5.md) |
| DeepSeek V4.1 Flash, 22 providers, 10 requests each | [All-provider run](RESULTS.md) |
| GLM-5.3-Flash, top 5, 10 requests each | [GLM run](RESULTS-GLM.md) |

The prompts, expected answers, and scoring rule are self-contained in
`bench.py`. The GLM option extends the original DeepSeek diagnostic.
