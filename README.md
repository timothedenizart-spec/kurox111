# Unified Cognitive Architecture (UCA)

UCA is a **local sequential orchestration application** for heterogeneous AI
components. It is not a merged checkpoint, a shared tokenizer, a distilled
student, or a claim that unavailable models have run. Each model adapter keeps
its own tokenizer and is invoked only through a model-specific boundary.

> **Repository audit (2026-11-15).** The starting commit contained only this
> README (then two lines long). It contained no checkpoints, model code,
> Hyperon installation, MeTTa program, FTS database, Wikipedia shard, JSON
> memory, 50 operator facts, or experimental-module implementations. UCA
> therefore implements the requested runnable architecture and adapters, but
> deliberately reports these assets as unavailable / non-validated until their
> actual local paths and runners are supplied. No third-party project was
> downloaded.

## What is implemented

- `UnifiedCognitiveEngine`: immutable-result sequential execution, dependencies,
  soft time limits, trace records, run IDs, bounded correction pass, error
  isolation, and per-module enablement.
- A typed common exchange format with sources, symbolic facts, exact computations,
  unverified propositions, analyses, confidence, uncertainty, provenance, and full
  execution history.
- A deterministic cognitive-control layer: bounded working memory, interpretable
  evidence-attention priorities, sparse provenance/lexical evidence graph, conflict
  register, metacognitive coverage, and a restricted exact rational-arithmetic kernel.
- The required 11-stage default pipeline: input, opt-in memory, FTS5 retrieval,
  MeTTa bridge, NCM, SmolLM2-135M, SmolLM2-360M, nanoDiff, global workspace,
  verification, and final response.
- Actual standard-library JSON memory and SQLite FTS5 integrations; local
  Transformers adapters when installed; safe external-runner contracts for NCM,
  MeTTa, and masked nanoDiff.
- Controlled adapters registry for LoRA/TIES/DARE, AoE, FLA, E2E/JAX, and the
  future Scallop integration. These never claim execution without a compatible,
  validated asset.
- A dependency-free local web conversation UI and reproducible benchmark runner.
- A content-addressed experiment registry that records code/configuration/asset provenance and refuses non-finite or unmeasured metric values instead of fabricating a claimed gain.
- A local-only training preflight that blocks a fine-tuning run until checkpoint, licensing, Data Card, disjoint data splits, file digests, budget, output policy and evaluation suite are declared.

## Quick start

```bash
python -m uca init --root .              # creates empty local stores, never downloads data
python -m uca status --root .
python -m uca chat --root . "Bonjour"
python -m uca serve --root . --host 0.0.0.0 --port 8080
python -m unittest discover -s tests -v
```

Then visit `http://localhost:8080`. The UI uses relative API URLs, so it also
works through a proxied development preview.

The initial answer is intentionally conservative: without local model weights
or an imported corpus it will report the absence rather than fabricate an
answer. Importing an FTS shard or pointing at a checkpoint is an explicit local
operator action; see [`docs/OPERATIONS.md`](docs/OPERATIONS.md). The bounded
attention/evidence graph and exact arithmetic substrate are documented in
[`docs/COGNITIVE_CONTROL.md`](docs/COGNITIVE_CONTROL.md).

## Design promises

1. **No automatic personal-memory learning.** Only JSON entries explicitly
   marked `explicit: true` can be retrieved. Chat requests never write memory.
2. **No tokenizer mixing.** Text crosses a model boundary as Unicode text;
   each model adapter independently encodes and decodes with its own tokenizer.
3. **Evidence is not generation.** NCM/nanoDiff/model content is retained with
   provenance and uncertainty, and cannot turn itself into a symbolic fact.
4. **Absence is not proof.** A missing MeTTa fact or FTS hit becomes an
   uncertainty, never a negative assertion.
5. **One user-facing response, many visible traces.** Normal mode returns only
   a response. Developer mode exposes the trace, module states, sources, and
   intermediate artifacts.

## Asset reality and activation

Expected local asset paths are configured in `config/uca.toml`. The values are
empty by default. UCA will not fetch models or data. A module's status is one
of `functional`, `unavailable`, `non_validated`, `disabled_voluntarily`, or
`failed_execution`; the reason is shown in the UI/CLI. Read
[`docs/INTEGRATION.md`](docs/INTEGRATION.md) before enabling a model.

## Project layout

- `uca/` — engine, typed exchange objects, module adapters, UI and benchmark
- `config/uca.toml` — local-only configuration and ordered default pipeline
- `docs/` — architecture, cognitive-control design, integration contracts, operations and validation plan
- `tests/` — standard-library tests that run without model packages or assets
- `benchmarks/` — reproducible task-set format (no fabricated results)
