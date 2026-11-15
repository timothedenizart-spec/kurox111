# Cognitive-control layer: bounded, inspectable reasoning support

UCA now includes a deterministic **cognitive-control layer** in its mandatory
input and GlobalWorkspace stages. It is inspired by useful abstractions from
cognitive science and elementary mathematics, not by a claim that the program
is conscious, biologically equivalent to a brain, or executing a hidden
chain-of-thought.

## 1. Perception and task control

`input_processing` creates a non-factual control plan from the request:

- significant lexical attention terms;
- up to four textual request facets;
- a suggested control policy (`retrieve_and_verify`,
  `retrieve_then_synthesize_with_limits`, or
  `compute_exactly_then_verify_context`);
- epistemic invariants that travel with the context.

The plan has diagnostic provenance and never becomes a source or a fact. It is
provided as text to every model adapter, so model tokenizers still encode it
independently.

## 2. Exact symbolic arithmetic

The `ExactArithmeticKernel` is a restricted AST evaluator over rational
numbers (`fractions.Fraction`). It accepts literal constants, parentheses,
unary plus/minus, addition, subtraction, multiplication, division and bounded
integer powers. It rejects names, calls, attributes, indexing, assignments,
non-finite numbers, large exponents, oversized rationals and division by zero.

A successful result is stored as a separate `computation` artifact, with
`verification_status: exact_deterministic`. The confidence of `1.0` means only
that the parsed **literal arithmetic expression** was evaluated exactly; it
says nothing about factual assumptions around it. Computations are not
converted into documentary or MeTTa facts.

## 3. Bounded working memory and an evidence graph

The GlobalWorkspace runs `CognitiveControlLayer.workspace` over existing
artifacts. It builds:

- a capacity-bounded working set (default: 12 records);
- a sparse graph of declared artifact dependencies and lexical associations;
- a structured symbolic-conflict register for the same subject/predicate with
  multiple object values;
- a predictive-coding-style **grounding-gap register**: generated artifacts with
  low lexical overlap with available documentary/symbolic/computation anchors
  are prioritized for verification, never declared false;
- coverage and unresolved-evidence indicators.

Working-memory priority is deliberately interpretable:

```text
0.60 × lexical relevance
+ 0.30 × epistemic provenance weight
+ 0.10 × traceability
```

This score only allocates limited workspace capacity. It is **not** a Bayesian
posterior, a confidence in truth, a vote, or an authority ranking. The system
never selects a conflicting claim merely because more modules repeat it.

## 4. Metacognitive limits and correction

The workspace reports documentary, symbolic, computation and model-analysis
coverage, plus the fraction of nodes carrying uncertainty. Missing coverage is
an unresolved limit, not negative evidence. The verifier reuses the structured
conflict register and can request at most one SmolLM2-360M review/re-verification
pass. It cannot loop indefinitely.

## Configuration

`[cognitive]` in `config/uca.toml` controls only resource bounds:

```toml
working_memory_capacity = 12  # 3..32
max_evidence_nodes = 48       # capacity..96
max_evidence_edges = 160      # 20..400
```

These bounds make the controller usable locally and prevent a long corpus from
being treated as unlimited short-term memory. They do not alter model weights,
tokenizers, or evidence provenance.
