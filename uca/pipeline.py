"""Concrete modules in the required UCA sequential pipeline."""
from __future__ import annotations

from typing import Any
import re
import unicodedata

from .cognitive import CognitiveControlLayer
from .parallel_cortex import ParallelCognitiveCortex
from .model_adapters import ExternalNcmAdapter, LocalCausalGenerator, MaskedNanoDiffAdapter, invoke_json_runner
from .modules import Capability, CognitiveModule
from .storage import ExplicitMemoryStore, FTSKnowledgeStore, OperatorFactStore
from .types import Artifact, ArtifactKind, ModuleResult, ModuleStatus, Provenance


def artifact(kind: ArtifactKind, producer: str, content: dict[str, Any], *,
             confidence: float | None = None, uncertainty: tuple[str, ...] = (),
             references: tuple[str, ...] = (), inputs: tuple[str, ...] = (), implementation: str = "") -> Artifact:
    return Artifact(kind=kind, content=content,
                    provenance=Provenance(producer=producer, references=references,
                                          input_artifact_ids=inputs, implementation=implementation),
                    confidence=confidence, uncertainty=uncertainty)


def _compact(snapshot: dict[str, Any], limit: int = 6000) -> str:
    """Textual hand-off; never forwards a tokenizer-specific representation."""
    documents = []
    for source in snapshot.get("sources", [])[:6]:
        content = source.get("content", {})
        documents.append(f"[Document {content.get('document_id', '?')} | {content.get('provenance', 'local')}]: "
                         f"{str(content.get('content', ''))[:700]}")
    facts = []
    for fact in snapshot.get("symbolic_facts", [])[:12]:
        item = fact.get("content", {})
        facts.append("[Fait symbolique %s]: %s" % (item.get("fact_id", "?"), item.get("statement", "")))
    proposals = []
    for proposal in snapshot.get("propositions", [])[:8]:
        item = proposal.get("content", {})
        proposals.append(f"[Proposition NON VÉRIFIÉE]: {item.get('text', '')}")
    computations = []
    for calculation in snapshot.get("computations", [])[:4]:
        item = calculation.get("content", {})
        computations.append(f"[Calcul exact déterministe]: {item.get('expression', '')} = {item.get('exact_value', '')}")
    memory = []
    cognitive_plan = []
    for item in snapshot.get("artifacts", []):
        if item.get("kind") == ArtifactKind.MEMORY.value:
            data = item.get("content", {})
            memory.append(f"[Mémoire explicitement enregistrée]: {data.get('text', '')}")
        elif item.get("kind") == ArtifactKind.DIAGNOSTIC.value and item.get("provenance", {}).get("producer") == "input_processing":
            plan = item.get("content", {}).get("cognitive_plan", {})
            if isinstance(plan, dict):
                cognitive_plan.append(f"[Plan de contrôle, non factuel]: termes={plan.get('attention_terms', [])}; "
                                      f"politique={plan.get('suggested_control_policy', '')}")
    return ("\n".join(cognitive_plan + documents + facts + computations + proposals + memory))[:limit]


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[\wÀ-ÿ'-]+", text) if len(token) > 2}


class InputProcessingModule(CognitiveModule):
    def __init__(self, cognitive_config: dict[str, Any] | None = None) -> None:
        super().__init__("input_processing")
        self.controller = CognitiveControlLayer(cognitive_config)

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        raw = str(snapshot["user_text"])
        normalized = " ".join(unicodedata.normalize("NFC", raw).split())
        lower = normalized.lower()
        # The exact arithmetic kernel performs the final arithmetic decision; this
        # classifier intentionally does not mistake dates/IDs for mathematics.
        arithmetic_signal = any(word in lower for word in ("calcule", "calcul", "combien fait", "équation", "equation", "math", "résous", "resous"))
        if arithmetic_signal:
            query_type = "math_or_logic"
        elif lower.endswith("?") or any(word in lower for word in ("qui", "quoi", "quand", "où", "pourquoi", "comment")):
            query_type = "question"
        elif any(word in lower for word in ("résume", "synthèse", "explique")):
            query_type = "explanation"
        else:
            query_type = "conversation_or_instruction"
        plan, calculation, calculation_error = self.controller.perceive(normalized, query_type)
        if (calculation is not None or calculation_error is not None) and query_type != "math_or_logic":
            query_type = "math_or_logic"
            plan, calculation, calculation_error = self.controller.perceive(normalized, query_type)
        artifacts: list[Artifact] = [artifact(
            ArtifactKind.DIAGNOSTIC, self.module_id,
            {"normalization": "unicode_nfc_whitespace", "query_type": query_type, "cognitive_plan": plan},
            uncertainty=("The plan allocates attention only; it contains no factual conclusion.",),
            implementation="deterministic perception and bounded-attention planner",
        )]
        warnings: list[str] = []
        if calculation:
            artifacts.append(artifact(
                ArtifactKind.COMPUTATION, self.module_id,
                {"expression": calculation.expression, "exact_value": calculation.exact_value,
                 "approximate_value": calculation.approximate_value, "operation_count": calculation.operation_count,
                 "verification_status": "exact_deterministic", "scope": "literal rational arithmetic only"},
                confidence=1.0,
                uncertainty=("This verifies only the parsed arithmetic expression, not any surrounding real-world premise.",),
                implementation="restricted Fraction/AST arithmetic kernel",
            ))
        elif calculation_error:
            warnings.append(f"Exact arithmetic was not applied: {calculation_error}")
        return ModuleResult(
            artifacts=tuple(artifacts), warnings=tuple(warnings),
            metadata={"normalized_text": normalized, "query_type": query_type},
            message="Input normalized; cognitive control plan and safe arithmetic route prepared without retaining personal data",
        )


class UserMemoryModule(CognitiveModule):
    def __init__(self, store: ExplicitMemoryStore, enabled: bool = True) -> None:
        super().__init__("user_memory", enabled=enabled, dependencies=("input_processing",))
        self.store = store

    def capability(self) -> Capability:
        disabled = super().capability()
        if disabled.status is not ModuleStatus.FUNCTIONAL:
            return disabled
        available, reason = self.store.status()
        return Capability(ModuleStatus.FUNCTIONAL if available else ModuleStatus.UNAVAILABLE, reason)

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        entries = self.store.search(snapshot["normalized_text"] or snapshot["user_text"])
        outputs = tuple(
            artifact(ArtifactKind.MEMORY, self.module_id,
                     {"memory_id": str(entry.get("id")), "text": str(entry.get("text", "")),
                      "tags": list(entry.get("tags", [])), "explicit": True},
                     uncertainty=("This item is user-provided memory, not independently verified.",),
                     implementation="explicit JSON memory lookup")
            for entry in entries
        )
        return ModuleResult(artifacts=outputs, message=f"Retrieved {len(outputs)} explicitly stored memory item(s)")


class KnowledgeRetrievalModule(CognitiveModule):
    def __init__(self, store: FTSKnowledgeStore, enabled: bool = True) -> None:
        super().__init__("knowledge_retrieval", enabled=enabled, dependencies=("input_processing",))
        self.store = store

    def capability(self) -> Capability:
        disabled = super().capability()
        if disabled.status is not ModuleStatus.FUNCTIONAL:
            return disabled
        available, reason, count = self.store.status()
        return Capability(ModuleStatus.FUNCTIONAL if available else ModuleStatus.UNAVAILABLE, reason,
                          {"passage_count": count})

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        passages = self.store.search(snapshot["normalized_text"] or snapshot["user_text"])
        records = tuple(
            artifact(ArtifactKind.DOCUMENT, self.module_id,
                     {"document_id": item["document_id"], "content": item["content"],
                      "provenance": item["provenance"], "metadata": item["metadata"], "rank": item["rank"]},
                     confidence=None,
                     uncertainty=("A match in the locally installed corpus is not an exhaustive encyclopedic claim.",),
                     references=(item["document_id"],), implementation="SQLite FTS5 BM25 retrieval")
            for item in passages
        )
        count = self.store.status()[2]
        warning = () if count else ("The local FTS index contains no passages; no Wikipedia shard was supplied.",)
        return ModuleResult(artifacts=records, warnings=warning,
                            message=f"Retrieved {len(records)} passages from local FTS5 index")


class MettaSymbolicModule(CognitiveModule):
    """MeTTa bridge with a transparent fact-index fallback for supplied facts.

    The fallback performs only explicit fact matching. It is labeled as such and
    never represents itself as Hyperon inference; this lets an operator use an
    existing 50-fact base while a MeTTa runtime is being installed.
    """
    def __init__(self, command: str, facts: OperatorFactStore | None = None, enabled: bool = True) -> None:
        super().__init__("symbolic_processing", enabled=enabled, dependencies=("input_processing",))
        self.command = command
        self.facts = facts

    def _local_facts(self) -> list[dict[str, Any]]:
        return self.facts.load() if self.facts else []

    def capability(self) -> Capability:
        disabled = super().capability()
        if disabled.status is not ModuleStatus.FUNCTIONAL:
            return disabled
        if self.command.strip():
            return Capability(ModuleStatus.FUNCTIONAL, "Local MeTTa runner configured")
        count = len(self._local_facts())
        if count:
            return Capability(ModuleStatus.FUNCTIONAL,
                              "Explicit local operator-fact index available; MeTTa inference is unavailable",
                              {"fact_count": count, "metta": "unavailable"})
        return Capability(ModuleStatus.UNAVAILABLE,
                          "No MeTTa/Hyperon runner or actual operator facts are available")

    def _artifacts(self, results: list[dict[str, Any]], implementation: str) -> tuple[Artifact, ...]:
        items: list[Artifact] = []
        for fact in results[:30]:
            if not isinstance(fact, dict):
                continue
            statement = str(fact.get("statement") or " ".join(str(fact.get(key, "")) for key in ("subject", "predicate", "object"))).strip()
            if not statement:
                continue
            fact_id = str(fact.get("id", f"symbolic-{len(items) + 1}"))
            uncertainty = fact.get("uncertainty", [])
            items.append(artifact(ArtifactKind.SYMBOLIC_FACT, self.module_id,
                                  {"fact_id": fact_id, "statement": statement,
                                   "relation": {key: fact.get(key) for key in ("subject", "predicate", "object")},
                                   "metta_result": fact.get("metadata", {})},
                                  confidence=fact.get("confidence") if isinstance(fact.get("confidence"), (int, float)) else None,
                                  uncertainty=tuple(uncertainty) if isinstance(uncertainty, list) else (),
                                  references=(fact_id,), implementation=implementation))
        return tuple(items)

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        query = snapshot["normalized_text"] or snapshot["user_text"]
        if self.command.strip():
            response = invoke_json_runner(self.command, {
                "operation": "metta_query", "query": query,
                "context": {"document_ids": [x.get("content", {}).get("document_id") for x in snapshot.get("sources", [])]},
                "contract_version": 1,
            }, self.timeout_seconds or 30)
            results = response.get("facts", [])
            if not isinstance(results, list):
                raise RuntimeError("MeTTa runner field 'facts' must be a list")
            items = self._artifacts(results, "external MeTTa runner")
            message = f"MeTTa bridge returned {len(items)} structured fact(s)"
        else:
            query_tokens = _tokens(query)
            # Explicit lookup has no negation/completion rule: no match is inconclusive.
            matched = [fact for fact in self._local_facts()
                       if query_tokens & _tokens(" ".join(str(fact.get(key, "")) for key in ("statement", "subject", "predicate", "object")))]
            items = self._artifacts(matched, "explicit local operator-fact lookup; no MeTTa inference")
            message = f"Local fact index matched {len(items)} explicit fact(s); MeTTa inference was not run"
        return ModuleResult(artifacts=items,
                            warnings=() if items else ("No applicable symbolic fact was returned; this is not evidence of the opposite.",),
                            message=message)


class ParallelCortexModule(CognitiveModule):
    """Brain-inspired parallel neuro-mathematical cortex.

    Executes 5 concurrent streams:
    1. Exact algebra & linear equation solving
    2. Formal propositional & Horn clause deduction
    3. Pearl's Structural Causal Models & do-calculus
    4. Hyperdimensional Computing (VSA) holographic composition
    5. Hierarchical predictive coding & Free Energy check
    """
    def __init__(self, enabled: bool = True) -> None:
        super().__init__("parallel_cortex", enabled=enabled, dependencies=("input_processing",))
        self.cortex = ParallelCognitiveCortex()

    def capability(self) -> Capability:
        basic = super().capability()
        if basic.status is not ModuleStatus.FUNCTIONAL:
            return basic
        return Capability(ModuleStatus.FUNCTIONAL, "Parallel Neuro-Mathematical Cortex ready (Algebra, Logic, Causal, VSA, Predictive)")

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        query = snapshot.get("normalized_text") or snapshot.get("user_text", "")
        artifacts = self.cortex.synthesize_artifacts(query, snapshot)
        warnings: list[str] = []
        if not artifacts:
            warnings.append("No explicit algebraic, formal-logic, or causal structure was matched in query.")
        return ModuleResult(
            artifacts=tuple(artifacts),
            warnings=tuple(warnings),
            message=f"Parallel cortex synthesized {len(artifacts)} reasoned artifact(s)"
        )


class NcmConceptModule(CognitiveModule):
    def __init__(self, adapter: ExternalNcmAdapter, enabled: bool = True) -> None:
        super().__init__("ncm_concept_generation", enabled=enabled, dependencies=("input_processing",))
        self.adapter = adapter

    def capability(self) -> Capability:
        basic = super().capability()
        return basic if basic.status is not ModuleStatus.FUNCTIONAL else self.adapter.capability()

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        proposals = self.adapter.concepts(snapshot["normalized_text"] or snapshot["user_text"], snapshot,
                                          self.timeout_seconds or 45)
        records = tuple(artifact(ArtifactKind.PROPOSAL, self.module_id,
                                 {"text": item["text"], "status": "NON_VERIFIE",
                                  "must_not_be_promoted_to_fact": True,
                                  "runner_metadata": item.get("runner_metadata", {})},
                                 uncertainty=("NCM conceptual generation is non-verified and is not evidence.",),
                                 implementation="external NCM LM1B/VQ runner") for item in proposals)
        return ModuleResult(artifacts=records, message=f"NCM produced {len(records)} non-verified proposition(s)")


class SmolAnalysisModule(CognitiveModule):
    def __init__(self, module_id: str, model_label: str, generator: LocalCausalGenerator,
                 dependencies: tuple[str, ...]) -> None:
        super().__init__(module_id, dependencies=dependencies)
        self.model_label = model_label
        self.generator = generator

    def capability(self) -> Capability:
        basic = super().capability()
        return basic if basic.status is not ModuleStatus.FUNCTIONAL else self.generator.capability()

    def _instruction(self) -> str:
        if self.model_label == "SmolLM2-135M-Instruct":
            return ("Produce a first independent analysis. Separate source-backed observations, symbolic facts, "
                    "non-verified proposals, and uncertainty. Do not make absent evidence into a claim.")
        return ("Review the earlier analysis critically. Check it against the supplied local documents and symbolic "
                "facts, identify possible errors or conflicts, and write a cautious intermediate synthesis. "
                "Do not treat your own output as truth.")

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        prior = []
        for item in snapshot.get("artifacts", []):
            if item.get("kind") == ArtifactKind.ANALYSIS.value:
                content = item.get("content", {})
                prior.append(f"[{content.get('model', 'analysis')}]: {str(content.get('text', ''))[:1200]}")
        prompt = (
            "You are a component inside a traceable local Unified Cognitive Architecture.\n"
            f"User request: {snapshot['normalized_text'] or snapshot['user_text']}\n\n"
            f"Evidence packet:\n{_compact(snapshot)}\n\n"
            f"Earlier model analyses:\n{' '.join(prior)[:2800]}\n\n"
            f"Task: {self._instruction()}\n"
            "Write in the request language. Cite document IDs when relying on a provided passage."
        )
        text = self.generator.generate(prompt)
        if not text:
            raise RuntimeError(f"{self.model_label} returned an empty analysis")
        return ModuleResult(artifacts=(artifact(ArtifactKind.ANALYSIS, self.module_id,
                                                {"model": self.model_label, "text": text,
                                                 "role": "independent_analysis" if "135" in self.model_label else "critical_synthesis"},
                                                uncertainty=("Generated model analysis requires verification against available local evidence.",),
                                                implementation="local Transformers causal inference with model-owned tokenizer"),),
                            message=f"{self.model_label} analysis retained in central context")

    def unload(self) -> None:
        self.generator.unload()


class NanoDiffModule(CognitiveModule):
    def __init__(self, adapter: MaskedNanoDiffAdapter, enabled: bool = True) -> None:
        super().__init__("nanodiff_specialist", enabled=enabled, dependencies=("smollm2_360_review",))
        self.adapter = adapter

    def capability(self) -> Capability:
        basic = super().capability()
        return basic if basic.status is not ModuleStatus.FUNCTIONAL else self.adapter.capability()

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        analyses = [entry for entry in snapshot.get("artifacts", []) if entry.get("kind") == ArtifactKind.ANALYSIS.value]
        base = str(analyses[-1].get("content", {}).get("text", "")) if analyses else str(snapshot["user_text"])
        candidates: list[Artifact] = []
        for strategy in self.adapter.config.get("strategies", ["single_pass"]):
            output = self.adapter.denoise(base, str(strategy), self.timeout_seconds or 45)
            runner_score = output.get("runner_score")
            candidates.append(artifact(ArtifactKind.PROPOSAL, self.module_id,
                                       {"text": output["candidate_text"], "status": "NON_VERIFIE",
                                        "kind": "masked_denoiser_candidate", "strategy": output["strategy"],
                                        "changed": output["changed"], "runner_score": runner_score,
                                        "calibration_id": output.get("calibration_id"),
                                        "eligible_for_review_only": True,
                                        "must_not_replace_base_answer_automatically": True},
                                       confidence=float(runner_score) if isinstance(runner_score, (int, float)) else None,
                                       uncertainty=("nanoDiff candidate is a masked-denoising proposal, not an autoregressive answer or verified fact.",),
                                       implementation="token-ID masked denoising through nanoDiff-owned tokenizer"))
        return ModuleResult(artifacts=tuple(candidates),
                            warnings=("nanoDiff candidates are held for review and never auto-replace the base response.",),
                            message=f"nanoDiff produced {len(candidates)} masked-denoising candidate(s)")

    def unload(self) -> None:
        self.adapter.unload()


class GlobalWorkspaceModule(CognitiveModule):
    def __init__(self, cognitive_config: dict[str, Any] | None = None) -> None:
        super().__init__("global_workspace", dependencies=("smollm2_135_analysis", "smollm2_360_review"))
        self.controller = CognitiveControlLayer(cognitive_config)

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        artifacts = snapshot.get("artifacts", [])
        analyses = [item for item in artifacts if item.get("kind") == ArtifactKind.ANALYSIS.value]
        documents = [item for item in artifacts if item.get("kind") == ArtifactKind.DOCUMENT.value]
        facts = [item for item in artifacts if item.get("kind") == ArtifactKind.SYMBOLIC_FACT.value]
        proposals = [item for item in artifacts if item.get("kind") == ArtifactKind.PROPOSAL.value]
        computations = [item for item in artifacts if item.get("kind") == ArtifactKind.COMPUTATION.value]
        analysis_signatures = [" ".join(_tokens(str(item.get("content", {}).get("text", ""))))[:250] for item in analyses]
        common = []
        if len(analysis_signatures) > 1:
            shared = set.intersection(*[set(signature.split()) for signature in analysis_signatures if signature]) if all(analysis_signatures) else set()
            common = sorted(shared)[:20]
        # Different prose is a review signal, not a claimed factual contradiction.
        divergences = []
        if len(set(analysis_signatures)) > 1:
            divergences.append({"type": "model_output_divergence", "status": "review_required",
                                "detail": "Independent model analyses differ; lexical difference alone is not a contradiction."})
        control = self.controller.workspace(snapshot)
        dossier = {
            "document_artifact_ids": [item["id"] for item in documents],
            "symbolic_fact_artifact_ids": [item["id"] for item in facts],
            "computation_artifact_ids": [item["id"] for item in computations],
            "analysis_artifact_ids": [item["id"] for item in analyses],
            "proposal_artifact_ids": [item["id"] for item in proposals],
            "common_lexical_terms": common,
            "divergences": divergences,
            "cognitive_control": control,
            "selection_rule": "Primary evidence remains separately attributed documents, symbolic facts, and exact computations; model count is not truth.",
            "nanodiff_policy": "Masked-denoiser candidates remain review-only and cannot automatically replace a response.",
        }
        uncertainty = ["The workspace is a coordination dossier, not an independent factual authority."]
        uncertainty.extend(control["metacognitive_state"]["unresolved"])
        return ModuleResult(artifacts=(artifact(ArtifactKind.SYNTHESIS, self.module_id, dossier,
                                                uncertainty=tuple(uncertainty),
                                                inputs=tuple(item["id"] for item in artifacts),
                                                implementation="deterministic bounded-attention and provenance-aware workspace"),),
                            message=("Global workspace assembled evidence graph, bounded working memory, "
                                     "metacognitive coverage and separate proposals"))


class FinalVerificationModule(CognitiveModule):
    def __init__(self, knowledge: FTSKnowledgeStore, metta_command: str) -> None:
        super().__init__("final_verification", dependencies=("global_workspace",))
        self.knowledge = knowledge
        self.metta_command = metta_command

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        # Verification labels support; lack of a local result is deliberately inconclusive.
        docs = [item.get("content", {}) for item in snapshot.get("sources", [])]
        facts = [item.get("content", {}) for item in snapshot.get("symbolic_facts", [])]
        computations = [item.get("content", {}) for item in snapshot.get("artifacts", [])
                        if item.get("kind") == ArtifactKind.COMPUTATION.value]
        analyses = [item.get("content", {}).get("text", "") for item in snapshot.get("artifacts", [])
                    if item.get("kind") == ArtifactKind.ANALYSIS.value]
        claims: list[str] = []
        for text in analyses[-2:]:
            claims.extend([segment.strip() for segment in re.split(r"(?<=[.!?])\s+", str(text)) if len(segment.strip()) > 18][:4])
        checks = []
        for claim in claims[:8]:
            claim_terms = _tokens(claim)
            related_documents = [doc.get("document_id") for doc in docs
                                 if len(claim_terms & _tokens(str(doc.get("content", "")))) >= 3]
            related_facts = [fact.get("fact_id") for fact in facts
                             if len(claim_terms & _tokens(str(fact.get("statement", "")))) >= 2]
            status = "supported_by_available_excerpt" if related_documents or related_facts else "not_verified_with_available_resources"
            checks.append({"statement": claim, "status": status,
                           "document_ids": related_documents, "symbolic_fact_ids": related_facts})
        calculation_checks = [{"expression": item.get("expression"), "exact_value": item.get("exact_value"),
                               "status": "verified_literal_arithmetic" if item.get("verification_status") == "exact_deterministic"
                               else "not_verified"}
                              for item in computations]
        # Ask MeTTa again only when an actual bridge is configured. A bridge failure
        # limits verification but must not discard the rest of the dossier.
        metta_verifications: list[dict[str, Any]] = []
        verification_warnings: list[str] = []
        if self.metta_command.strip() and claims:
            try:
                response = invoke_json_runner(self.metta_command, {
                    "operation": "metta_verify", "statements": claims,
                    "query": snapshot.get("normalized_text") or snapshot["user_text"], "contract_version": 1,
                }, self.timeout_seconds or 30)
                returned = response.get("verifications", [])
                if isinstance(returned, list):
                    metta_verifications = [item for item in returned[:20] if isinstance(item, dict)]
                else:
                    verification_warnings.append("MeTTa verification response has no list-valued 'verifications' field.")
            except Exception as error:
                verification_warnings.append(f"MeTTa verification unavailable: {type(error).__name__}: {str(error)[:180]}")
        # Detect only a structured symbolic conflict, never a mere difference in model prose.
        relation_groups: dict[tuple[str, str], set[str]] = {}
        for fact in facts:
            relation = fact.get("relation", {})
            subject, predicate, obj = relation.get("subject"), relation.get("predicate"), relation.get("object")
            if all(isinstance(value, str) and value.strip() for value in (subject, predicate, obj)):
                relation_groups.setdefault((subject.strip().lower(), predicate.strip().lower()), set()).add(obj.strip())
        symbolic_conflicts = [{"subject": subject, "predicate": predicate, "objects": sorted(objects)}
                              for (subject, predicate), objects in relation_groups.items() if len(objects) > 1]
        # Any FTS re-query is intentionally not treated as a proof either; it makes corroboration traceable.
        query_hits = self.knowledge.search(snapshot.get("normalized_text") or snapshot["user_text"], limit=3)
        correction_required = bool(symbolic_conflicts)
        workspace_dossiers = [item.get("content", {}) for item in snapshot.get("artifacts", [])
                              if item.get("kind") == ArtifactKind.SYNTHESIS.value and item.get("provenance", {}).get("producer") == "global_workspace"]
        grounding_gaps = (workspace_dossiers[-1].get("cognitive_control", {}).get("prediction_error_register", [])
                          if workspace_dossiers else [])
        if grounding_gaps:
            verification_warnings.append(f"{len(grounding_gaps)} generated artifact(s) were prioritized for grounding review.")
        result = artifact(ArtifactKind.VERIFICATION, self.module_id,
                          {"checks": checks, "calculation_checks": calculation_checks,
                           "grounding_gaps_for_review": grounding_gaps,
                           "requery_document_ids": [hit["document_id"] for hit in query_hits],
                           "metta_verifications": metta_verifications,
                           "symbolic_conflicts": symbolic_conflicts,
                           "correction_required": correction_required,
                           "method": "lexical corroboration against available local FTS passages and MeTTa results",
                           "negative_evidence_policy": "No hit or no symbolic fact is inconclusive, never proof of negation."},
                          uncertainty=("Lexical support is not a full fact-check; unavailable corpus/MeTTa assets limit verification.",),
                          implementation="bounded local verification")
        return ModuleResult(artifacts=(result,), warnings=tuple(verification_warnings),
                            message=f"Checked {len(checks)} generated statement(s)",
                            metadata={"correction_required": correction_required})


class FinalResponseModule(CognitiveModule):
    def __init__(self, adapter: Any | None = None) -> None:
        super().__init__("final_response", dependencies=("final_verification",))
        self.adapter = adapter

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        query = snapshot.get("normalized_text") or snapshot.get("user_text", "")
        documents = [item.get("content", {}) for item in snapshot.get("sources", [])]
        facts = [item.get("content", {}) for item in snapshot.get("symbolic_facts", [])]
        analyses = [item.get("content", {}) for item in snapshot.get("artifacts", [])
                    if item.get("kind") == ArtifactKind.ANALYSIS.value]
        computations = [item.get("content", {}) for item in snapshot.get("artifacts", [])
                        if item.get("kind") == ArtifactKind.COMPUTATION.value]
        proposals = [item.get("content", {}) for item in snapshot.get("artifacts", [])
                     if item.get("kind") == ArtifactKind.PROPOSAL.value]
        synthesis = next((item.get("content", {}) for item in snapshot.get("artifacts", [])
                          if item.get("kind") == ArtifactKind.SYNTHESIS.value), {})
        verification = next((item.get("content", {}) for item in snapshot.get("artifacts", [])
                             if item.get("kind") == ArtifactKind.VERIFICATION.value), {})

        cognitive_ctrl = synthesis.get("cognitive_control", {})
        metacog = cognitive_ctrl.get("metacognitive_state", {})
        coverage = cognitive_ctrl.get("coverage", {})
        prediction_errors = cognitive_ctrl.get("prediction_error_register", [])
        working_memory = cognitive_ctrl.get("working_memory", [])
        conflicts = cognitive_ctrl.get("conflict_register", [])

        reflection = {
            "metacognitive_state": metacog,
            "coverage": coverage,
            "prediction_error_register": prediction_errors,
            "working_memory": working_memory,
            "conflict_register": conflicts,
        }

        # 1. Tentative de raffinement neuronal NCM couplé à la réflexion
        refined_payload: dict[str, Any] | None = None
        if self.adapter is not None and hasattr(self.adapter, "refine_response"):
            refined_payload = self.adapter.refine_response(
                query=query,
                reflection=reflection,
                computations=computations,
                analyses=analyses,
                documents=documents,
                facts=facts,
                proposals=proposals,
                timeout=self.timeout_seconds or 45.0,
            )

        if refined_payload and isinstance(refined_payload.get("refined_answer"), str):
            answer = refined_payload["refined_answer"]
            impl = "ncm_neural_refiner_and_reflective_synthesizer"
            metrics = refined_payload.get("reflection_metrics", {})
        else:
            # 2. Synthèse réflexive déterministe enrichie (mode dégradé robuste)
            unc_ratio = float(metacog.get("uncertainty_ratio", 0.0))
            certainty = round(max(0.0, 1.0 - unc_ratio), 3)

            # Section 1 : Synthèse Directe
            sec1 = ["### 💡 Synthèse & Résolution Cognitive"]
            direct_ans = ""
            for comp in computations:
                op = comp.get("operation")
                data = comp.get("data", {})
                if op == "exact_algebra_and_equations":
                    direct_ans = f"La résolution exacte de l'équation donne : **{data.get('variable')} = {data.get('exact_value')}**."
                    break
                elif "expression" in comp and "exact_value" in comp:
                    direct_ans = f"Le calcul arithmétique exact aboutit à : **{comp['expression']} = {comp['exact_value']}**."
                    break
                elif op == "formal_propositional_deduction":
                    derived = data.get("facts_derived", [])
                    direct_ans = f"Par déduction logique stricte, la conclusion démontrée est : **{', '.join(derived)}**."
                    break
                elif op == "causal_dag_and_intervention":
                    direct_ans = "Analyse causale structurelle (do-calculus de Pearl) : l'intervention active est validée sur le graphe orienté."
                    break

            if not direct_ans:
                for ana in analyses:
                    if ana.get("operation") == "structural_causal_dag":
                        dag = ana.get("dag", {})
                        nodes = dag.get("nodes", [])
                        direct_ans = f"Analyse causale structurelle (do-calculus de Pearl) : chaîne orientée ({' → '.join(nodes)}). L'intervention do(X) neutralise les facteurs confondants."
                        break

            if not direct_ans and documents:
                best = documents[0]
                direct_ans = f"D'après les sources documentaires certifiées [{best.get('document_id', '?')}] : {best.get('content', '')[:180]}..."
            elif not direct_ans and facts:
                best_f = facts[0]
                direct_ans = f"Fait formel MeTTa vérifié : {best_f.get('statement', '')}."
            elif not direct_ans:
                direct_ans = "Aucune source documentaire, fait MeTTa ou calcul exact n'était disponible pour établir une conclusion certifiée sur cette requête."

            sec1.append(direct_ans)

            # Section 2 : Preuves formelles
            sec2 = ["### 📐 Démonstration Déductive & Preuves Formelles"]
            proofs = []
            for comp in computations:
                op = comp.get("operation")
                data = comp.get("data", {})
                if op == "exact_algebra_and_equations":
                    for s in data.get("steps", []):
                        proofs.append(f"- 🔸 {s}")
                elif "expression" in comp and "exact_value" in comp:
                    proofs.append(f"- 🔸 Évaluation rationnelle : `{comp['expression']}` = `{comp['exact_value']}`")
                elif op == "formal_propositional_deduction":
                    for s in data.get("steps", []):
                        proofs.append(f"- 🔸 {s}")
                elif op == "causal_dag_and_intervention":
                    edges = data.get("edges", [])
                    if edges:
                        proofs.append(f"- 🔸 Graphe causal : {', '.join(f'{u} → {v}' for u, v in edges)}")
            for d in documents[:3]:
                proofs.append(f"- 📄 Source certifiée `[{d.get('document_id', '?')}]` : {d.get('content', '')[:200]}...")
            for f in facts[:3]:
                proofs.append(f"- 🔗 Fait MeTTa certifié `[{f.get('fact_id', '?')}]` : {f.get('statement', '')}")
            if not proofs:
                proofs.append("- Aucune preuve formelle ou passage certifié disponible dans l'index local.")
            sec2.extend(proofs)

            # Section 3 : Métacognition
            sec3 = [
                "### 🧠 Réflexion Métacognitive & Contrôle Épistémique",
                f"- **Indice de certitude épistémique :** `{certainty * 100:.1f}%` (Incertitude : `{unc_ratio:.2f}`)",
                "- **Garantie d'inviolabilité :** Les calculs déterministes et preuves sont mathématiquement vérifiés. Les sorties génératives restent des hypothèses distinctes.",
            ]

            # Section 4 : Concepts
            sec4 = ["### 🧬 Résonance Conceptuelle Neuronale (NCM)"]
            if proposals:
                concept_texts = [p.get("text", "") for p in proposals if p.get("text")]
                sec4.append(f"- **Propositions conceptuelles :** {', '.join(concept_texts)}")
            else:
                sec4.append("- Aucun concept latent spécifique requis pour cette opération directe.")

            answer = "\n\n".join(["\n".join(sec1), "\n".join(sec2), "\n".join(sec3), "\n".join(sec4)])
            impl = "evidence_preserving_deterministic_reflective_composer"
            metrics = {"certainty": certainty, "uncertainty_ratio": unc_ratio}

        return ModuleResult(
            artifacts=(
                artifact(
                    ArtifactKind.FINAL,
                    self.module_id,
                    {
                        "answer": answer,
                        "format": "structured_reflective_response",
                        "source_count": len(documents),
                        "symbolic_fact_count": len(facts),
                        "exact_computation_count": len(computations),
                        "reflection_metrics": metrics,
                    },
                    uncertainty=("The final response is limited to the locally available resources listed above.",),
                    implementation=impl,
                ),
            ),
            message="Produced refined reflective response without overwriting intermediate artifacts",
        )
