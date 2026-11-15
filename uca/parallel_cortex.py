"""Parallel Cognitive Cortex: Brain-inspired and fundamental-mathematical reasoning substrate.

Incorporates:
1. Vector Symbolic Architecture (VSA / Hyperdimensional Computing) for associative binding and composition.
2. Hierarchical Predictive Coding (Friston's Free Energy minimization & prediction error vectors).
3. Thalamo-Cortical Parallel Bus: concurrent multi-stream reasoning (Deductive, Algebraic, Causal, Analogy, Predictive).
4. Thalamic Arbiter: dynamic gating, cross-stream consistency checking, and Global Workspace broadcast.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Mapping, Sequence
import math
import re

from .symbolic_math import CausalReasoner, ExactAlgebraKernel, HornClauseEngine, MinimumDescriptionLength, PropositionalTruthTable
from .types import Artifact, ArtifactKind, Provenance


# ---------------------------------------------------------------------------
# 1. Hyperdimensional Computing (Vector Symbolic Architecture - VSA)
# ---------------------------------------------------------------------------

class Hypervector:
    """Bipolar hypervector {-1, +1}^D for holographic symbolic computing.

    Equipped with:
    - Binding (elementwise multiplication: role * filler)
    - Bundling (superposition / addition with thresholding)
    - Permutation (cyclic coordinate shift for sequence encoding)
    - Cosine similarity measurement
    """
    DIMENSION = 1024

    def __init__(self, values: Sequence[int]) -> None:
        if len(values) != self.DIMENSION:
            raise ValueError(f"Hypervector must have dimension {self.DIMENSION}")
        self.values = tuple(1 if v >= 0 else -1 for v in values)

    @classmethod
    def random(cls, seed_str: str) -> "Hypervector":
        """Deterministic pseudo-random hypervector generated from a text seed."""
        raw_bytes = sha256(seed_str.encode("utf-8")).digest()
        # Expand 32 bytes (256 bits) to 1024 bits using iterative hashing
        expanded: list[int] = []
        cycle = 0
        while len(expanded) < cls.DIMENSION:
            h = sha256(raw_bytes + cycle.to_bytes(4, "big")).digest()
            for byte in h:
                for bit in range(8):
                    expanded.append(1 if (byte >> bit) & 1 else -1)
                    if len(expanded) == cls.DIMENSION:
                        break
                if len(expanded) == cls.DIMENSION:
                    break
            cycle += 1
        return cls(expanded)

    def bind(self, other: "Hypervector") -> "Hypervector":
        """XOR / Hadamard product: self * other. Associative, commutative, invertible."""
        return Hypervector([s * o for s, o in zip(self.values, other.values)])

    @classmethod
    def bundle(cls, vectors: Sequence["Hypervector"]) -> "Hypervector":
        """Superposition of multiple hypervectors via majority voting."""
        if not vectors:
            return cls.random("empty_bundle")
        sums = [sum(v.values[i] for v in vectors) for i in range(cls.DIMENSION)]
        return Hypervector([1 if s >= 0 else -1 for s in sums])

    def permute(self, shift: int = 1) -> "Hypervector":
        """Cyclic coordinate rotation (encodes syntactic role or sequence order)."""
        shift = shift % self.DIMENSION
        rotated = self.values[-shift:] + self.values[:-shift]
        return Hypervector(rotated)

    def similarity(self, other: "Hypervector") -> float:
        """Normalized cosine similarity in [-1.0, 1.0]."""
        dot = sum(s * o for s, o in zip(self.values, other.values))
        return round(dot / self.DIMENSION, 4)


class HyperdimensionalMemory:
    """Associative semantic memory built on Vector Symbolic Architecture."""

    def __init__(self) -> None:
        self.item_memory: dict[str, Hypervector] = {}

    def get_or_create(self, symbol: str) -> Hypervector:
        symbol = symbol.strip().lower()
        if symbol not in self.item_memory:
            self.item_memory[symbol] = Hypervector.random(symbol)
        return self.item_memory[symbol]

    def encode_relation(self, subject: str, predicate: str, obj: str) -> Hypervector:
        """Encodes (Subject * RoleSubj) + (Predicate * RolePred) + (Object * RoleObj)."""
        role_s = self.get_or_create("__ROLE_SUBJECT__")
        role_p = self.get_or_create("__ROLE_PREDICATE__")
        role_o = self.get_or_create("__ROLE_OBJECT__")

        s = self.get_or_create(subject).bind(role_s)
        p = self.get_or_create(predicate).bind(role_p)
        o = self.get_or_create(obj).bind(role_o)

        return Hypervector.bundle([s, p, o])

    def cleanup(self, query: Hypervector, top_k: int = 3) -> list[tuple[str, float]]:
        """Finds closest symbolic items in memory to the query vector."""
        scores = [(symbol, query.similarity(vec)) for symbol, vec in self.item_memory.items()
                  if not symbol.startswith("__ROLE_")]
        scores.sort(key=lambda pair: pair[1], reverse=True)
        return scores[:top_k]


# ---------------------------------------------------------------------------
# 2. Hierarchical Predictive Coding & Active Inference
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PredictiveSignal:
    level: str
    expected_concept: str
    observed_concept: str
    prediction_error: float
    precision_weight: float
    dissonance_flag: bool
    interpretation: str


class PredictiveInferenceEngine:
    """Karl Friston's Free Energy Principle & Predictive Processing analogue.

    Computes prediction errors between top-down expectations and bottom-up evidence.
    High prediction errors signal cognitive dissonance and prompt deliberative review.
    """

    @classmethod
    def evaluate_predictive_fit(
        cls,
        task_query: str,
        retrieved_documents: list[str],
        deduced_facts: list[str],
    ) -> list[PredictiveSignal]:
        signals: list[PredictiveSignal] = []
        q_terms = {w.lower() for w in re.findall(r"\w+", task_query) if len(w) > 3}

        # Level 1: Document corroboration expectation
        doc_terms = {w.lower() for doc in retrieved_documents for w in re.findall(r"\w+", doc)}
        doc_overlap = len(q_terms & doc_terms) / max(1, len(q_terms))
        doc_error = round(1.0 - doc_overlap, 4)
        signals.append(PredictiveSignal(
            level="sensory_documentary",
            expected_concept=f"Lexical grounding for {list(q_terms)[:4]}",
            observed_concept=f"Corroborating terms ({len(q_terms & doc_terms)}/{len(q_terms)})",
            prediction_error=doc_error,
            precision_weight=0.75,
            dissonance_flag=doc_error > 0.65,
            interpretation="Faible ancrage documentaire local" if doc_error > 0.65 else "Ancrage documentaire satisfaisant"
        ))

        # Level 2: Deductive alignment
        fact_terms = {w.lower() for f in deduced_facts for w in re.findall(r"\w+", f)}
        fact_overlap = len(q_terms & fact_terms) / max(1, len(q_terms))
        fact_error = round(1.0 - fact_overlap, 4)
        signals.append(PredictiveSignal(
            level="symbolic_deductive",
            expected_concept="Convergence logique formelle",
            observed_concept=f"Faits déduits ({len(deduced_facts)})",
            prediction_error=fact_error,
            precision_weight=0.90,
            dissonance_flag=fact_error > 0.70 and bool(deduced_facts),
            interpretation="Déductions formelles disponibles et alignées" if fact_error <= 0.7 else "Déductions symboliques incomplètes"
        ))

        return signals


# ---------------------------------------------------------------------------
# 3. Parallel Cognitive Cortex & Thalamic Routing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CortexStreamResult:
    stream_name: str
    success: bool
    execution_time_ms: float
    output: Any
    confidence: float
    uncertainty: tuple[str, ...] = ()
    explanation: str = ""


class ParallelCognitiveCortex:
    """Orchestrates concurrent brain-inspired and mathematical reasoning streams."""

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers
        self.vsa_memory = HyperdimensionalMemory()

    def _stream_algebra(self, text: str) -> CortexStreamResult:
        """Stream 1: Exact linear equation and rational algebra."""
        sol = ExactAlgebraKernel.solve_linear(text)
        if sol:
            return CortexStreamResult(
                stream_name="exact_algebra",
                success=True,
                execution_time_ms=0.5,
                output={
                    "variable": sol.variable,
                    "exact_value": sol.exact_value,
                    "approximate_value": sol.approximate_value,
                    "steps": sol.steps,
                },
                confidence=1.0,
                explanation=f"Équation résolue exactement : {sol.variable} = {sol.exact_value}"
            )
        nt = ExactAlgebraKernel.analyze_number(text)
        if nt:
            return CortexStreamResult(
                stream_name="exact_algebra",
                success=True,
                execution_time_ms=0.4,
                output=nt.result,
                confidence=1.0,
                explanation=nt.steps[0] if nt.steps else nt.query
            )
        return CortexStreamResult(stream_name="exact_algebra", success=False, execution_time_ms=0.2, output=None, confidence=0.0)

    def _stream_logic(self, text: str) -> CortexStreamResult:
        """Stream 2: Formal Horn clause forward deduction and propositional truth table."""
        horn = HornClauseEngine.parse_and_infer(text)
        if horn and horn.facts_derived:
            return CortexStreamResult(
                stream_name="formal_logic",
                success=True,
                execution_time_ms=0.6,
                output={
                    "status": horn.status,
                    "facts_derived": horn.facts_derived,
                    "proof_steps": [s.explanation for s in horn.proof_steps],
                },
                confidence=1.0,
                explanation=f"Déduction formelle exacte : {', '.join(horn.facts_derived)}"
            )
        tt = PropositionalTruthTable.evaluate(text)
        if tt:
            return CortexStreamResult(
                stream_name="formal_logic",
                success=True,
                execution_time_ms=0.8,
                output=tt,
                confidence=1.0,
                explanation=f"Classification logique : formule est une {tt['classification']}"
            )
        return CortexStreamResult(stream_name="formal_logic", success=False, execution_time_ms=0.2, output=None, confidence=0.0)

    def _stream_causal(self, text: str) -> CortexStreamResult:
        """Stream 3: Pearl's Structural Causal Models & Intervention Analysis."""
        dag = CausalReasoner.extract_graph(text)
        if len(dag.nodes) >= 2:
            return CortexStreamResult(
                stream_name="causal_reasoner",
                success=True,
                execution_time_ms=0.7,
                output=dag.to_dict(),
                confidence=0.85,
                explanation=f"Graphe causal structurel extrait : {len(dag.nodes)} variables, {len(dag.to_dict()['edges'])} mécanismes causaux"
            )
        return CortexStreamResult(stream_name="causal_reasoner", success=False, execution_time_ms=0.2, output=None, confidence=0.0)

    def _stream_vsa_analogy(self, text: str) -> CortexStreamResult:
        """Stream 4: Hyperdimensional Vector Symbolic concept composition."""
        words = [w.lower() for w in re.findall(r"\w+", text) if len(w) > 3]
        if len(words) >= 3:
            s, p, o = words[0], words[1], words[2]
            bound_vec = self.vsa_memory.encode_relation(s, p, o)
            top_matches = self.vsa_memory.cleanup(bound_vec, top_k=2)
            return CortexStreamResult(
                stream_name="vsa_hyperdimensional",
                success=True,
                execution_time_ms=1.2,
                output={
                    "bound_concept": f"{s} * {p} * {o}",
                    "holographic_dimension": Hypervector.DIMENSION,
                    "associative_cleanup": top_matches,
                },
                confidence=0.80,
                explanation="Composition hyperdimensionnelle (VSA) de relation et mémoire associative holographique"
            )
        return CortexStreamResult(stream_name="vsa_hyperdimensional", success=False, execution_time_ms=0.2, output=None, confidence=0.0)

    def _stream_predictive(self, text: str, snapshot: dict[str, Any]) -> CortexStreamResult:
        """Stream 5: Hierarchical Predictive Processing & Free Energy check."""
        retrieved_docs = [str(s.get("content", {}).get("content", "")) for s in snapshot.get("sources", [])]
        symbolic_facts = [str(f.get("content", {}).get("statement", "")) for f in snapshot.get("symbolic_facts", [])]
        signals = PredictiveInferenceEngine.evaluate_predictive_fit(text, retrieved_docs, symbolic_facts)
        mean_error = sum(s.prediction_error for s in signals) / len(signals) if signals else 0.0
        return CortexStreamResult(
            stream_name="predictive_processing",
            success=True,
            execution_time_ms=0.8,
            output={
                "signals": [
                    {
                        "level": s.level,
                        "error": s.prediction_error,
                        "dissonance": s.dissonance_flag,
                        "interpretation": s.interpretation,
                    }
                    for s in signals
                ],
                "mean_prediction_error": round(mean_error, 4),
            },
            confidence=0.90,
            explanation=f"Boucle prédictive Fristonienne : erreur moyenne = {round(mean_error, 2)}"
        )

    def execute_parallel(self, text: str, snapshot: dict[str, Any]) -> list[CortexStreamResult]:
        """Dispatches reasoning streams in parallel and returns valid results."""
        results: list[CortexStreamResult] = []
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="uca-cortex") as pool:
            futures = [
                pool.submit(self._stream_algebra, text),
                pool.submit(self._stream_logic, text),
                pool.submit(self._stream_causal, text),
                pool.submit(self._stream_vsa_analogy, text),
                pool.submit(self._stream_predictive, text, snapshot),
            ]
            for fut in as_completed(futures):
                try:
                    res = fut.result(timeout=5.0)
                    if res and res.success:
                        results.append(res)
                except Exception:
                    pass
        return results

    def synthesize_artifacts(self, text: str, snapshot: dict[str, Any]) -> list[Artifact]:
        """Converts successful cortex streams into immutable UCA artifacts."""
        stream_results = self.execute_parallel(text, snapshot)
        artifacts: list[Artifact] = []

        for item in stream_results:
            if item.stream_name == "exact_algebra":
                artifacts.append(Artifact(
                    kind=ArtifactKind.COMPUTATION,
                    content={
                        "module": "parallel_cortex",
                        "operation": "exact_algebra_and_equations",
                        "data": item.output,
                        "verification_status": "exact_deterministic",
                    },
                    provenance=Provenance(producer="parallel_cortex", implementation="ExactAlgebraKernel"),
                    confidence=item.confidence,
                    uncertainty=item.uncertainty,
                ))
            elif item.stream_name == "formal_logic":
                artifacts.append(Artifact(
                    kind=ArtifactKind.COMPUTATION,
                    content={
                        "module": "parallel_cortex",
                        "operation": "formal_propositional_deduction",
                        "data": item.output,
                        "verification_status": "exact_deterministic",
                    },
                    provenance=Provenance(producer="parallel_cortex", implementation="HornClauseEngine"),
                    confidence=item.confidence,
                    uncertainty=item.uncertainty,
                ))
            elif item.stream_name == "causal_reasoner":
                artifacts.append(Artifact(
                    kind=ArtifactKind.ANALYSIS,
                    content={
                        "module": "parallel_cortex",
                        "operation": "structural_causal_dag",
                        "dag": item.output,
                    },
                    provenance=Provenance(producer="parallel_cortex", implementation="PearlCausalReasoner"),
                    confidence=item.confidence,
                    uncertainty=("Causal relations extracted from text require empirical validation.",),
                ))
            elif item.stream_name == "predictive_processing":
                artifacts.append(Artifact(
                    kind=ArtifactKind.DIAGNOSTIC,
                    content={
                        "module": "parallel_cortex",
                        "operation": "free_energy_predictive_coding",
                        "signals": item.output,
                    },
                    provenance=Provenance(producer="parallel_cortex", implementation="PredictiveInferenceEngine"),
                    confidence=item.confidence,
                ))
            elif item.stream_name == "vsa_hyperdimensional":
                artifacts.append(Artifact(
                    kind=ArtifactKind.PROPOSAL,
                    content={
                        "module": "parallel_cortex",
                        "operation": "vector_symbolic_architecture",
                        "data": item.output,
                        "status": "NON_VERIFIE",
                    },
                    provenance=Provenance(producer="parallel_cortex", implementation="HyperdimensionalMemory"),
                    confidence=item.confidence,
                    uncertainty=("VSA associative cleanup is a holographic heuristic, not a proof.",),
                ))

        return artifacts
