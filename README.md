# Implicit record ID extraction, small mirror

This standalone Python project reproduces the implicit ID extraction condition from
[`llm-provider-bench`](https://github.com/nexus-bench/llm-provider-bench). The
historical task asks a model to extract `id`, an explicitly empty `nickname`, and
an absent `middle_name`. Each provider receives ten `Form K111:` through
`Form K120:` requests. The explicit `Record ID:` control is omitted.

The script uses OpenRouter's chat completions endpoint with the DeepSeek V4.1
Flash model, `reasoning.effort=high`, strict JSON schema, temperature 1, top_p 1,
and a 4096-token cap. `provider.only` pins each endpoint and disables fallbacks.
Provider slugs must be available for this model and support these parameters.

## Run

Python 3.10+ is enough; there are no runtime dependencies.

```sh
export OPENROUTER_API_KEY=...
python bench.py --provider PROVIDER_SLUG --provider ANOTHER_SLUG
```

Use endpoint slugs from the [OpenRouter model endpoint catalog](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash/endpoints), not display names. The default is three requests at once across the whole run. Adjust with `--concurrency`; `--retries` controls retries for HTTP 429 and 5xx responses. `Retry-After` is honored when supplied. Each logical request is scored once after its final attempt.

The table reports exact JSON correctness for the ten fuzzy ID cases, plus
wrong answers and transport/format failures. Full request and response records go to
`results.jsonl` (gitignored) as each request finishes; use `--output` to choose
another file. Existing output files are never overwritten. A nonzero
exit code means at least one request failed or produced an incomplete/invalid
response. This small, deliberately selected template panel is a diagnostic,
not an independent-task benchmark or a broad provider ranking. Retries can
repeat a request that the server already processed and may incur another charge.

Source: `packages/evaluation/src/id-diagnostic.ts` and
`docs/OPENROUTER_ID_STUDY.md` on the source repository's
`codex/openrouter-id-study` branch. This mirror uses ten implicit cases instead
of its larger paired, repeated panel.
