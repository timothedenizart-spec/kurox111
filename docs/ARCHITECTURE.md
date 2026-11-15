# UCA architecture

## Audit boundary

The initial repository had exactly one tracked `README.md`; it did **not**
contain the component inventory described in the project brief. UCA keeps an
adapter and status slot for every named component rather than pretending the
missing implementation/checkpoints exist. This is a codebase transformation,
not a claim that models have been trained or evaluated here.

## Central exchange contract

`CognitiveContext` is the request-owned ledger. It contains the request ID,
initial and normalized text, available context, documents, symbolic facts,
proposals, confidence values, uncertainties, execution history and module
states. All substantive records are immutable `Artifact` objects with:

- an ID and one kind;
- producer, timestamp, input artifact IDs and references;
- optional confidence and explicit uncertainty;
- JSON-only content.

The engine is the only mutator. Modules receive a JSON snapshot and return a
`ModuleResult`; they cannot overwrite earlier output. `DOCUMENT`,
`SYMBOLIC_FACT`, and `PROPOSAL` are distinct types. In particular, NCM and
nanoDiff output cannot enter the fact bin.

## Default execution order

1. `input_processing` normalizes and classifies a request.
2. `user_memory` searches only JSON entries marked `explicit: true`.
3. `knowledge_retrieval` uses parameterized SQLite FTS5 retrieval and retains
   document ID, content, provenance, metadata and ranking.
4. `symbolic_processing` calls an operator-provided MeTTa bridge, or (only when
   actual operator facts are supplied) a clearly labeled explicit fact-index lookup;
   the fallback performs no MeTTa inference.
5. `ncm_concept_generation` calls a validated NCM runner and marks every item
   `NON_VERIFIE`.
6. `smollm2_135_analysis` creates a first independently attributed analysis.
7. `smollm2_360_review` critically reviews it.
8. `nanodiff_specialist` sends masked token IDs to a denoiser-specific runner;
   it never calls causal `generate` and candidates are review-only.
9. `global_workspace` emits a dossier that separates evidence, analyses and
   proposals; different text is a divergence, not an asserted contradiction.
10. `final_verification` applies bounded, local lexical corroboration, re-queries
    a configured MeTTa bridge for statement verification, and preserves inconclusive outcomes.
11. `final_response` makes one evidence-preserving response.

The engine may make **one** targeted review pass only if a future validated
verifier writes `correction_required: true`; it preserves prior outputs and
never loops indefinitely. Current conservative verification does not infer
such a correction from text mismatch alone.

## States and resilience

Every module exposes `functional`, `unavailable`, `non_validated`,
`disabled_voluntarily`, or `failed_execution` with a reason. A missing model,
corpus, or runner records its state and the rest of the pipeline continues.
Time limits are soft thread limits: a late isolated result cannot alter the
central context, but arbitrary Python code cannot safely be force-killed.

`sequential_unload` releases model objects and optional CUDA cache after a
module. Text artifacts remain, so RAM/VRAM pressure does not erase reasoning
trace. `resident` is available only by explicit configuration. When
`engine.cache_enabled=true`, only FTS retrieval records are held in a bounded
in-memory LRU cache keyed by local DB signature and query terms; user memory
and model responses are never cached by this mechanism.

## Cognitive-control extension

The default 11-stage order is preserved. Stage 1 now adds a deterministic
perception/control plan and a safe exact-arithmetic route; stage 9 adds bounded
working memory, an evidence graph, a structured conflict register and
metacognitive coverage. These are transparent control artifacts, not hidden
reasoning or model-weight fusion. See [`COGNITIVE_CONTROL.md`](COGNITIVE_CONTROL.md).

## Brain- and mathematics-inspired extension (session arena/57dad57f-kurox111)

The pipeline now carries a hyperdimensional vector-symbolic memory with
analogical transfer (`analogical_memory`), an offline Hebbian consolidation
store (`associative_consolidation`), a Shannon-surprisal novelty monitor
(`surprisal_monitor`), and — at the coordination layer — a contiguous
topological-level **parallel engine** whose scheduling is bit-identical in
outputs to the sequential one. A Hopfield attractor network with explicit
capacity bounds is available in `uca/associative.py`. Full rationale, maths and
honesty boundaries: [`EXTENSIONS_COGNITIVES.md`](EXTENSIONS_COGNITIVES.md).
