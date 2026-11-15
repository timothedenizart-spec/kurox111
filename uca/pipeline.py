"""Concrete modules in the required UCA sequential pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import re
import unicodedata

from .cognitive import CognitiveControlLayer
from .consolidation import load_associations
from .model_adapters import ExternalNcmAdapter, LocalCausalGenerator, MaskedNanoDiffAdapter, invoke_json_runner
from .modules import Capability, CognitiveModule
from .predictive import LocalSurprisalModel, corpus_background, novelty_report
from .storage import ExplicitMemoryStore, FTSKnowledgeStore, OperatorFactStore
from .types import Artifact, ArtifactKind, ModuleResult, ModuleStatus, Provenance
from .vsa import HyperMemory


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
        # knowledge_retrieval is declared because the bridge query embeds document IDs:
        # parallel scheduling must preserve that information flow.
        super().__init__("symbolic_processing", enabled=enabled,
                         dependencies=("input_processing", "knowledge_retrieval"))
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


class ConsolidatedAssociationModule(CognitiveModule):
    """Surfaces offline Hebbian consolidations as review-only proposals.

    The associations come from `python -m uca consolidate` (deterministic
    co-occurrence replay over local stores). Absence of the store is reported
    as unavailable; it is never fabricated or treated as negative evidence.
    """
    def __init__(self, path: Path, enabled: bool = True) -> None:
        super().__init__("associative_consolidation", enabled=enabled, dependencies=("input_processing",))
        self.path = Path(path)

    def capability(self) -> Capability:
        disabled = super().capability()
        if disabled.status is not ModuleStatus.FUNCTIONAL:
            return disabled
        edges = load_associations(self.path)
        if edges:
            return Capability(ModuleStatus.FUNCTIONAL,
                              f"Consolidated association store available ({len(edges)} edges)",
                              {"edge_count": len(edges)})
        return Capability(ModuleStatus.UNAVAILABLE,
                          "No consolidated associations; run `python -m uca consolidate` on local stores")

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        edges = load_associations(self.path)[:16]
        records = tuple(
            artifact(ArtifactKind.PROPOSAL, self.module_id,
                     {"text": (f"Association consolidée hors-ligne : {edge['a']} ⇔ {edge['b']} "
                               f"(force {edge['strength']}, {edge['co_occurrences']} co-occurrences)"),
                      "association": {"a": edge["a"], "b": edge["b"], "strength": edge["strength"]},
                      "status": "NON_VERIFIE", "eligible_for_review_only": True},
                     uncertainty=("Hebbian offline co-occurrence with documentary provenance; "
                                  "an association is not an asserted fact.",),
                     references=tuple(edge.get("supporting_document_ids", [])[:3]),
                     implementation="deterministic Hebbian consolidation replay")
            for edge in edges
        )
        return ModuleResult(artifacts=records,
                            message=f"Surfaced {len(records)} consolidated association(s) for review")


class AnalogicalMemoryModule(CognitiveModule):
    """Hyperdimensional holographic memory over structured symbolic facts.

    Encodes each (subject, predicate, object) triple by VSA binding/bundling,
    publishes an internal reconstruction-fidelity diagnostic, then emits a few
    *analogical transfer* proposals for predicate gaps of structurally similar
    entities. Cosine scores are similarity, never confidence in truth.
    """
    def __init__(self, enabled: bool = True) -> None:
        super().__init__("analogical_memory", enabled=enabled, dependencies=("symbolic_processing",))

    @staticmethod
    def _structured_facts(snapshot: dict[str, Any]) -> list[dict[str, str]]:
        facts: list[dict[str, str]] = []
        for item in snapshot.get("symbolic_facts", []):
            content = item.get("content", {})
            relation = content.get("relation", {})
            values = [relation.get(key) for key in ("subject", "predicate", "object")] if isinstance(relation, dict) else []
            if all(isinstance(value, str) and value.strip() for value in values):
                facts.append({"subject": values[0].strip(), "predicate": values[1].strip(),
                              "object": values[2].strip(), "fact_id": str(content.get("fact_id", ""))})
        return facts

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        facts = self._structured_facts(snapshot)
        memory = HyperMemory()
        for fact in facts:
            memory.encode_fact(fact["subject"], fact["predicate"], fact["object"], fact_id=fact["fact_id"])
        artifacts: list[Artifact] = []
        fidelity = memory.reconstruct_check()
        fidelity.pop("details", None)
        artifacts.append(artifact(
            ArtifactKind.DIAGNOSTIC, self.module_id,
            {"holographic_encoding": {"fact_count": len(facts), **fidelity},
             "interpretation": "Internal encoding-fidelity probe of the hyperdimensional memory only."},
            uncertainty=("Reconstruction fidelity measures the memory channel, not the truth of facts.",),
            implementation="deterministic VSA binding/bundling over SHA-256 seeded atoms"))
        subjects = sorted({fact["subject"] for fact in facts})
        predicates = sorted({fact["predicate"] for fact in facts})
        proposals: list[Artifact] = []
        for target in subjects:
            held = {fact["predicate"] for fact in facts if fact["subject"] == target}
            for predicate in predicates:
                if predicate in held:
                    continue
                candidates = memory.analogical_transfer(target, predicate, sources=subjects, facts=facts, limit=2)
                for candidate in candidates:
                    if candidate["analogy_weight"] < 0.01:
                        continue
                    proposals.append(artifact(
                        ArtifactKind.PROPOSAL, self.module_id,
                        {"text": (f"Hypothèse analogique : {target} · {predicate} ≈ "
                                  f"{candidate['object']} (poids {candidate['analogy_weight']})"),
                         "analogy": {"target": target, "predicate": predicate,
                                     "candidate_object": candidate["object"],
                                     "weight": candidate["analogy_weight"]},
                         "status": "NON_VERIFIE", "eligible_for_review_only": True},
                        uncertainty=("Analogical transfer by structural neighbourhood; "
                                     "an untested hypothesis, not a fact.",),
                        references=tuple(fact["fact_id"] for fact in facts if fact["fact_id"])[:4],
                        implementation="holographic role-profile analogy"))
                    if len(proposals) >= 8:
                        break
                if len(proposals) >= 8:
                    break
            if len(proposals) >= 8:
                break
        artifacts.extend(proposals)
        return ModuleResult(artifacts=tuple(artifacts),
                            message=(f"Hyperdimensional memory encoded {len(facts)} structured fact(s); "
                                     f"{len(proposals)} analogical proposal(s) emitted"))


class SurprisalMonitorModule(CognitiveModule):
    """Predictive-coding styled novelty signal over generated analyses.

    A local bigram model trained on available evidence assigns each generated
    sentence a Shannon surprisal. Sentences far above the corpus background are
    flagged for verification. With no local corpus, the module reports the
    absence honestly instead of inventing expectations.
    """
    def __init__(self, enabled: bool = True) -> None:
        super().__init__("surprisal_monitor", enabled=enabled,
                         dependencies=("smollm2_360_review", "knowledge_retrieval", "symbolic_processing"))

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        corpus = [str(item.get("content", {}).get("content", "")) for item in snapshot.get("sources", [])]
        corpus += [str(item.get("content", {}).get("statement", "")) for item in snapshot.get("symbolic_facts", [])]
        corpus = [text for text in corpus if text.strip()][:80]
        model = LocalSurprisalModel()
        model.train(corpus)
        analyses = [str(item.get("content", {}).get("text", ""))
                    for item in snapshot.get("artifacts", [])
                    if item.get("kind") == ArtifactKind.ANALYSIS.value][-2:]
        if not model.is_trained:
            artifacts = (artifact(ArtifactKind.DIAGNOSTIC, self.module_id,
                                  {"status": "no_local_corpus",
                                   "interpretation": "No local evidence text to set a surprisal background; monitoring is inconclusive."},
                                  uncertainty=("Without a local corpus, novelty relative to evidence cannot be estimated.",),
                                  implementation="adaptive bigram surprisal monitor"),)
            return ModuleResult(artifacts=artifacts, message="Surprisal monitor inactive: empty local corpus")
        background = corpus_background(model, corpus)
        reports = [novelty_report(model, text, background_mean=background["background_mean"])
                   for text in analyses if text.strip()]
        flagged = sum(1 for report in reports if report.get("flagged"))
        artifacts = (artifact(ArtifactKind.DIAGNOSTIC, self.module_id,
                              {"background": background, "surprisal_reports": reports,
                               "flagged_count": flagged,
                               "interpretation": ("Mean token surprisal relative to the local corpus; a flag "
                                                  "queues verification, it never asserts falsehood.")},
                              uncertainty=("High surprisal marks novelty against local evidence, not error.",),
                              implementation="Shannon bigram surprisal over local evidence"),)
        return ModuleResult(artifacts=artifacts,
                            message=f"Surprisal monitor reviewed {len(reports)} analysis text(s); {flagged} flagged")


class GlobalWorkspaceModule(CognitiveModule):
    def __init__(self, cognitive_config: dict[str, Any] | None = None) -> None:
        # The dossier aggregates *all* upstream artifacts: surprisal and
        # nanoDiff outputs are declared dependencies so parallel scheduling
        # preserves the sequential information flow.
        super().__init__("global_workspace",
                         dependencies=("smollm2_135_analysis", "smollm2_360_review",
                                       "surprisal_monitor", "nanodiff_specialist"))
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
    def __init__(self) -> None:
        super().__init__("final_response", dependencies=("final_verification",))

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        documents = [item.get("content", {}) for item in snapshot.get("sources", [])]
        facts = [item.get("content", {}) for item in snapshot.get("symbolic_facts", [])]
        analyses = [item.get("content", {}) for item in snapshot.get("artifacts", [])
                    if item.get("kind") == ArtifactKind.ANALYSIS.value]
        computations = [item.get("content", {}) for item in snapshot.get("artifacts", [])
                        if item.get("kind") == ArtifactKind.COMPUTATION.value]
        verification = [item.get("content", {}) for item in snapshot.get("artifacts", [])
                        if item.get("kind") == ArtifactKind.VERIFICATION.value]
        lines = ["Réponse UCA — synthèse locale traçable."]
        if documents:
            lines.append("Passages documentaires locaux pertinents :")
            for doc in documents[:4]:
                excerpt = " ".join(str(doc.get("content", "")).split())[:420]
                lines.append(f"- [{doc.get('document_id', '?')} | {doc.get('provenance', 'provenance inconnue')}] {excerpt}")
        if facts:
            lines.append("Faits symboliques retournés par MeTTa :")
            for fact in facts[:6]:
                lines.append(f"- [{fact.get('fact_id', '?')}] {fact.get('statement', '')}")
        if computations:
            lines.append("Calculs exacts vérifiés par le noyau symbolique :")
            for calculation in computations[:4]:
                lines.append(f"- {calculation.get('expression', '')} = {calculation.get('exact_value', '')} (arithmétique rationnelle déterministe)")
        if analyses:
            preferred = analyses[-1]
            text = " ".join(str(preferred.get("text", "")).split())[:1100]
            if text:
                lines.append(f"Analyse intermédiaire de {preferred.get('model', 'modèle local')} (à vérifier, non promue au rang de fait) : {text}")
        if not documents and not facts and not analyses and not computations:
            lines.append("Aucune source documentaire, fait MeTTa, calcul exact ou sortie de modèle local n'était disponible pour répondre de façon étayée à cette demande.")
        if verification:
            checks = verification[-1].get("checks", [])
            unresolved = sum(1 for check in checks if check.get("status") != "supported_by_available_excerpt")
            if unresolved:
                lines.append(f"Vérification : {unresolved} affirmation(s) générée(s) ne sont pas vérifiables avec les ressources locales actuellement disponibles.")
            grounding_gaps = verification[-1].get("grounding_gaps_for_review", [])
            if grounding_gaps:
                lines.append(f"Contrôle de cohérence : {len(grounding_gaps)} sortie(s) générée(s) ont une faible liaison lexicale aux preuves locales et restent à vérifier.")
        lines.append("Limites : les extraits proviennent uniquement du corpus local installé ; ils ne constituent pas une encyclopédie exhaustive. Les propositions générées restent distinctes des faits vérifiés.")
        answer = "\n\n".join(lines)
        return ModuleResult(artifacts=(artifact(ArtifactKind.FINAL, self.module_id,
                                                {"answer": answer, "format": "single_user_response",
                                                 "source_count": len(documents), "symbolic_fact_count": len(facts),
                                                 "exact_computation_count": len(computations)},
                                                uncertainty=("The final response is limited to the locally available resources listed above.",),
                                                implementation="evidence-preserving deterministic response composer"),),
                            message="Produced one final response without overwriting intermediate artifacts")
