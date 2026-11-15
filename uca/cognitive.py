"""Deterministic cognitive-control primitives for UCA.

The design borrows *control principles* rather than claiming to emulate a
brain: bounded working memory, attention allocation, predictive error signals,
and a separate exact symbolic substrate. Every score below is an attention
priority, never a probability that a proposition is true.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from typing import Any
import ast
import math
import re

from .types import ArtifactKind


_WORD = re.compile(r"[\wÀ-ÿ'-]+", re.UNICODE)
_EXPRESSION = re.compile(r"(?<![\w])\d[\d\s,\.\+\-\*/×÷\^()]{0,220}(?![\w])")
_STOP_WORDS = {
    "a", "à", "au", "aux", "avec", "ce", "ces", "cette", "comment", "dans", "de", "des", "du", "elle", "en",
    "est", "et", "il", "je", "la", "le", "les", "leur", "leurs", "mais", "mes", "mon", "ne", "nous", "ou", "par",
    "pas", "pour", "que", "quel", "quelle", "qui", "sa", "se", "ses", "son", "sur", "tes", "ton", "tu", "un", "une",
    "vos", "votre", "vous", "y", "the", "and", "or", "is", "of", "to", "in", "what", "why", "how",
}


def lexical_terms(text: str) -> set[str]:
    """A transparent lexical representation, not a cross-model embedding space."""
    return {word.lower() for word in _WORD.findall(text) if len(word) > 2 and word.lower() not in _STOP_WORDS}


def _text_from_artifact(item: dict[str, Any]) -> str:
    content = item.get("content", {})
    if not isinstance(content, dict):
        return ""
    pieces = [content.get(key, "") for key in ("content", "statement", "text", "answer", "expression", "exact_value")]
    relation = content.get("relation", {})
    if isinstance(relation, dict):
        pieces.extend(relation.get(key, "") for key in ("subject", "predicate", "object"))
    return " ".join(str(piece) for piece in pieces if piece)


@dataclass(frozen=True)
class ArithmeticOutcome:
    expression: str
    exact_value: str
    approximate_value: float | None
    operation_count: int


class ExactArithmeticKernel:
    """A small, auditable rational-arithmetic kernel.

    It intentionally supports only literal arithmetic, unary +/- and the five
    basic binary operators. No names, attributes, calls, indexing, assignment,
    complex numbers, or arbitrary Python evaluation is admitted.
    """
    MAX_OPERATIONS = 128
    MAX_EXPONENT = 20
    MAX_NUMERATOR_BITS = 4096

    @classmethod
    def extract(cls, text: str) -> str | None:
        lower = text.lower()
        math_signal = any(token in lower for token in (
            "calcule", "calcul", "combien fait", "équation", "equation", "résous", "resous", "math", "arithmétique",
        ))
        for candidate in _EXPRESSION.findall(text):
            candidate = candidate.strip(" .?!:;")
            normalized = candidate.replace("×", "*").replace("÷", "/").replace("−", "-")
            has_operator = any(symbol in normalized for symbol in ("+", "-", "*", "/", "^"))
            # Avoid turning ordinary years or IDs into calculations unless an explicit
            # calculation instruction surrounds them.
            if has_operator and (math_signal or re.fullmatch(r"[\d\s,\.\+\-\*/\^()]+", text.strip(" .?!"))):
                return normalized
        return None

    @classmethod
    def evaluate(cls, expression: str) -> ArithmeticOutcome:
        normalized = expression.replace("^", "**").replace(",", ".")
        if len(normalized) > 256:
            raise ValueError("Expression too long")
        try:
            root = ast.parse(normalized, mode="eval")
        except SyntaxError as error:
            raise ValueError("Invalid arithmetic syntax") from error
        operations = 0

        def guard(value: Fraction) -> Fraction:
            if value.numerator.bit_length() > cls.MAX_NUMERATOR_BITS or value.denominator.bit_length() > cls.MAX_NUMERATOR_BITS:
                raise ValueError("Exact result exceeds safe size")
            return value

        def visit(node: ast.AST) -> Fraction:
            nonlocal operations
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                if isinstance(node.value, float) and (math.isnan(node.value) or math.isinf(node.value)):
                    raise ValueError("Non-finite literal")
                return guard(Fraction(str(node.value)))
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                value = visit(node.operand)
                return value if isinstance(node.op, ast.UAdd) else guard(-value)
            if not isinstance(node, ast.BinOp) or not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                raise ValueError("Only basic literal arithmetic is allowed")
            operations += 1
            if operations > cls.MAX_OPERATIONS:
                raise ValueError("Too many arithmetic operations")
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return guard(left + right)
            if isinstance(node.op, ast.Sub):
                return guard(left - right)
            if isinstance(node.op, ast.Mult):
                return guard(left * right)
            if isinstance(node.op, ast.Div):
                if not right:
                    raise ValueError("Division by zero")
                return guard(left / right)
            if right.denominator != 1 or abs(right.numerator) > cls.MAX_EXPONENT:
                raise ValueError(f"Exponent must be an integer in [-{cls.MAX_EXPONENT}, {cls.MAX_EXPONENT}]")
            if not left and right.numerator < 0:
                raise ValueError("Zero cannot have a negative exponent")
            return guard(left ** right.numerator)

        result = visit(root.body)
        exact = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
        approximate = float(result) if result.numerator.bit_length() < 1024 and result.denominator.bit_length() < 1024 else None
        return ArithmeticOutcome(expression=expression, exact_value=exact, approximate_value=approximate,
                                 operation_count=operations)


class CognitiveControlLayer:
    """Bounded attention/workspace controller built from inspectable rules.

    The layer has three deliberately modest analogues to cognitive control:
    - **perception/planning**: lexical task facets and an exact math route;
    - **working memory**: a capacity-bounded, relevance-prioritized evidence set;
    - **metacognition**: coverage and unresolved-evidence signals.

    It makes no claim of sentience, hidden chain-of-thought, truth by consensus,
    or biological equivalence.
    """
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}
        self.capacity = max(3, min(int(config.get("working_memory_capacity", 12)), 32))
        self.max_nodes = max(self.capacity, min(int(config.get("max_evidence_nodes", 48)), 96))
        self.max_edges = max(20, min(int(config.get("max_evidence_edges", 160)), 400))
        self.diversity_bonus = max(0.0, min(float(config.get("diversity_bonus", 0.08)), 0.25))

    def perceive(self, text: str, query_type: str) -> tuple[dict[str, Any], ArithmeticOutcome | None, str | None]:
        terms = lexical_terms(text)
        counts = Counter(word.lower() for word in _WORD.findall(text) if word.lower() in terms)
        facets = [segment.strip() for segment in re.split(r"[?;]|\b(?:puis|ensuite)\b", text, flags=re.IGNORECASE) if segment.strip()]
        facets = facets[:4] or [text]
        operation = "retrieve_and_verify"
        if query_type == "math_or_logic":
            operation = "compute_exactly_then_verify_context"
        elif query_type == "explanation":
            operation = "retrieve_then_synthesize_with_limits"
        plan = {
            "attention_terms": [term for term, _ in counts.most_common(12)],
            "query_facets": facets,
            "suggested_control_policy": operation,
            "epistemic_invariants": [
                "Generated propositions remain distinct from verified facts.",
                "Missing local evidence is inconclusive.",
                "Attention priority is not truth probability.",
            ],
        }
        expression = ExactArithmeticKernel.extract(text)
        if expression is None:
            return plan, None, None
        try:
            return plan, ExactArithmeticKernel.evaluate(expression), None
        except ValueError as error:
            return plan, None, str(error)

    @staticmethod
    def _epistemic_weight(item: dict[str, Any]) -> float:
        kind = item.get("kind")
        implementation = str(item.get("provenance", {}).get("implementation", "")).lower()
        if kind == ArtifactKind.COMPUTATION.value:
            return 1.0 if item.get("content", {}).get("verification_status") == "exact_deterministic" else 0.5
        if kind == ArtifactKind.SYMBOLIC_FACT.value:
            return 0.85 if "metta" in implementation and "no metta" not in implementation else 0.65
        if kind == ArtifactKind.DOCUMENT.value:
            return 0.70
        if kind == ArtifactKind.MEMORY.value:
            return 0.25
        if kind == ArtifactKind.ANALYSIS.value:
            return 0.20
        if kind == ArtifactKind.PROPOSAL.value:
            return 0.08
        return 0.05

    def _attention(self, item: dict[str, Any], query_terms: set[str]) -> dict[str, Any]:
        body_terms = lexical_terms(_text_from_artifact(item))
        overlap = query_terms & body_terms
        relevance = len(overlap) / max(1, len(query_terms))
        traceability = 1.0 if item.get("provenance", {}).get("references") or item.get("provenance", {}).get("input_artifact_ids") else 0.55
        epistemic = self._epistemic_weight(item)
        # Scores prioritize scarce workspace capacity. They are explicitly not confidence.
        priority = round(0.60 * relevance + 0.30 * epistemic + 0.10 * traceability, 4)
        return {"artifact_id": item.get("id"), "kind": item.get("kind"), "attention_priority": priority,
                "relevance": round(relevance, 4), "epistemic_weight": epistemic,
                "traceability": traceability, "overlap_terms": sorted(overlap)[:12]}

    def _diverse_working_memory(self, scored: list[dict[str, Any]], nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Greedily preserve evidence-type/producer diversity under a hard budget.

        The novelty term prevents a large family of similar model outputs from
        crowding out every independent evidence modality. It is a scheduling
        heuristic, not evidence aggregation or confidence calibration.
        """
        metadata = {item.get("id"): item.get("provenance", {}).get("producer", "unknown") for item in nodes}
        remaining = list(scored)
        selected: list[dict[str, Any]] = []
        seen_kinds: set[str] = set()
        seen_producers: set[str] = set()
        while remaining and len(selected) < self.capacity:
            def rank(entry: dict[str, Any]) -> tuple[float, str]:
                producer = str(metadata.get(entry.get("artifact_id"), "unknown"))
                novelty = (self.diversity_bonus if entry.get("kind") not in seen_kinds else 0.0)
                novelty += (self.diversity_bonus / 2 if producer not in seen_producers else 0.0)
                return (entry["attention_priority"] + novelty, str(entry.get("artifact_id")))
            # Artifact ID gives deterministic tie-breaking. `max` keeps the higher
            # lexical/provenance priority before any novelty preference.
            winner = max(remaining, key=rank)
            remaining.remove(winner)
            producer = str(metadata.get(winner.get("artifact_id"), "unknown"))
            novelty = (self.diversity_bonus if winner.get("kind") not in seen_kinds else 0.0)
            novelty += (self.diversity_bonus / 2 if producer not in seen_producers else 0.0)
            selected.append({**winner, "workspace_selection_priority": round(winner["attention_priority"] + novelty, 4),
                             "diversity_bonus": round(novelty, 4), "producer": producer})
            seen_kinds.add(str(winner.get("kind")))
            seen_producers.add(producer)
        return selected

    @staticmethod
    def _symbolic_conflicts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        groups: dict[tuple[str, str], list[tuple[str, str]]] = {}
        for item in items:
            if item.get("kind") != ArtifactKind.SYMBOLIC_FACT.value:
                continue
            relation = item.get("content", {}).get("relation", {})
            values = [relation.get(key) for key in ("subject", "predicate", "object")] if isinstance(relation, dict) else []
            if not all(isinstance(value, str) and value.strip() for value in values):
                continue
            subject, predicate, obj = (value.strip() for value in values)
            groups.setdefault((subject.casefold(), predicate.casefold()), []).append((obj, str(item.get("id"))))
        conflicts = []
        for (subject, predicate), options in groups.items():
            objects = {obj for obj, _ in options}
            if len(objects) > 1:
                conflicts.append({"type": "structured_symbolic_conflict", "subject": subject, "predicate": predicate,
                                  "objects": sorted(objects), "artifact_ids": [artifact_id for _, artifact_id in options],
                                  "interpretation": "Review required; UCA does not select a winner by vote."})
        return conflicts

    def workspace(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        query_terms = lexical_terms(snapshot.get("normalized_text") or snapshot.get("user_text", ""))
        raw = [item for item in snapshot.get("artifacts", [])
               if item.get("kind") in {kind.value for kind in (ArtifactKind.DOCUMENT, ArtifactKind.SYMBOLIC_FACT,
                                                                  ArtifactKind.MEMORY, ArtifactKind.PROPOSAL,
                                                                  ArtifactKind.ANALYSIS, ArtifactKind.COMPUTATION)}]
        nodes = raw[:self.max_nodes]
        scored = [self._attention(item, query_terms) for item in nodes]
        scored.sort(key=lambda entry: (-entry["attention_priority"], str(entry["artifact_id"])))
        working_memory = self._diverse_working_memory(scored, nodes)
        index = {item.get("id"): item for item in nodes}
        edges: list[dict[str, Any]] = []
        for item in nodes:
            provenance = item.get("provenance", {})
            for parent in provenance.get("input_artifact_ids", []) if isinstance(provenance, dict) else []:
                if parent in index:
                    edges.append({"from": parent, "to": item.get("id"), "relation": "declared_input_dependency"})
        # Sparse association only: require two shared significant lexical terms.
        for left_index, left in enumerate(nodes):
            left_terms = lexical_terms(_text_from_artifact(left))
            for right in nodes[left_index + 1:]:
                shared = left_terms & lexical_terms(_text_from_artifact(right))
                if len(shared) >= 2:
                    edges.append({"from": left.get("id"), "to": right.get("id"), "relation": "lexical_association",
                                  "shared_terms": sorted(shared)[:8]})
                if len(edges) >= self.max_edges:
                    break
            if len(edges) >= self.max_edges:
                break
        conflicts = self._symbolic_conflicts(nodes)
        # A predictive-coding-style *grounding gap*: generated text whose lexical
        # content has little overlap with currently available non-generated
        # evidence is queued for verification. This is not a falsity verdict.
        anchors = [item for item in nodes if item.get("kind") in {
            ArtifactKind.DOCUMENT.value, ArtifactKind.SYMBOLIC_FACT.value, ArtifactKind.COMPUTATION.value
        }]
        grounding_gaps = []
        for generated in [item for item in nodes if item.get("kind") in {ArtifactKind.ANALYSIS.value, ArtifactKind.PROPOSAL.value}]:
            generated_terms = lexical_terms(_text_from_artifact(generated))
            overlaps = []
            for anchor in anchors:
                anchor_terms = lexical_terms(_text_from_artifact(anchor))
                overlaps.append(len(generated_terms & anchor_terms) / max(1, len(generated_terms | anchor_terms)))
            best_overlap = max(overlaps, default=0.0)
            if best_overlap < 0.15:
                grounding_gaps.append({"artifact_id": generated.get("id"), "kind": generated.get("kind"),
                                       "lexical_anchor_overlap": round(best_overlap, 4),
                                       "status": "verification_priority",
                                       "interpretation": "Low lexical grounding is a review signal, not evidence of falsehood."})
        kinds = Counter(item.get("kind") for item in nodes)
        producers = Counter(str(item.get("provenance", {}).get("producer", "unknown")) for item in nodes)
        total_nodes = len(nodes)
        modality_entropy = -sum((count / total_nodes) * math.log2(count / total_nodes) for count in kinds.values()) if total_nodes else 0.0
        producer_entropy = -sum((count / total_nodes) * math.log2(count / total_nodes) for count in producers.values()) if total_nodes else 0.0
        coverage = {
            "documentary": kinds[ArtifactKind.DOCUMENT.value] > 0,
            "symbolic": kinds[ArtifactKind.SYMBOLIC_FACT.value] > 0,
            "exact_computation": kinds[ArtifactKind.COMPUTATION.value] > 0,
            "model_analysis": kinds[ArtifactKind.ANALYSIS.value] > 0,
            "generated_proposals": kinds[ArtifactKind.PROPOSAL.value] > 0,
        }
        unresolved = []
        if not coverage["documentary"]:
            unresolved.append("No local documentary passage was available for corroboration.")
        if not coverage["symbolic"]:
            unresolved.append("No applicable symbolic fact was available.")
        if coverage["generated_proposals"] and not (coverage["documentary"] or coverage["symbolic"]):
            unresolved.append("Generated proposals have no independent local corroboration.")
        if grounding_gaps:
            unresolved.append(f"{len(grounding_gaps)} generated artifact(s) have a low lexical grounding signal and need verification.")
        uncertain = sum(1 for item in nodes if item.get("uncertainty"))
        return {
            "controller": "bounded_attention_workspace_v1",
            "working_memory_capacity": self.capacity,
            "working_memory": working_memory,
            "evidence_graph": {"nodes": [{"artifact_id": item.get("id"), "kind": item.get("kind"),
                                               "producer": item.get("provenance", {}).get("producer")}
                                              for item in nodes], "edges": edges},
            "information_geometry": {
                "modality_counts": dict(sorted(kinds.items())), "producer_counts": dict(sorted(producers.items())),
                "modality_entropy_bits": round(modality_entropy, 4),
                "producer_entropy_bits": round(producer_entropy, 4),
                "effective_modalities": round(2 ** modality_entropy, 4),
                "effective_producers": round(2 ** producer_entropy, 4),
                "interpretation": "Diversity descriptors for workspace allocation, not information truth or quality.",
            },
            "conflict_register": conflicts,
            "prediction_error_register": grounding_gaps,
            "coverage": coverage,
            "metacognitive_state": {
                "evidence_node_count": len(nodes), "uncertain_node_count": uncertain,
                "uncertainty_ratio": round(uncertain / max(1, len(nodes)), 4),
                "unresolved": unresolved,
                "invariant": "Neither majority agreement nor attention priority is treated as truth.",
            },
            "attention_formula": "0.60 lexical relevance + 0.30 epistemic provenance weight + 0.10 traceability",
            "attention_disclaimer": "Attention priority allocates bounded working memory; it is not a truth confidence.",
        }
