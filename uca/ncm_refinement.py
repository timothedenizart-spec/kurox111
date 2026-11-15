"""Conservative reflection gate for a future local NCM response refiner.

An NCM may propose a response refinement, but this module never turns the
proposal into a fact and never auto-replaces the baseline answer. It builds a
bounded reflection packet from attributed evidence, validates the runner's JSON
contract, and allows only a *shadow-review* status when every declared claim
points to available evidence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping
import json
import re


CONTRACT_VERSION = 1
MAX_CANDIDATE_CHARS = 8_000
MAX_CLAIMS = 12
MAX_CLAIM_CHARS = 1_200
_ALLOWED_INTENTS = {"clarity", "add_limit", "cite_evidence", "correct_supported_claim", "abstain"}
_WORD = re.compile(r"[\wÀ-ÿ'-]+", re.UNICODE)
_STOP_TERMS = {"a", "à", "au", "aux", "de", "des", "du", "en", "est", "et", "il", "la", "le", "les", "un", "une", "the", "and", "of", "to", "in"}


@dataclass(frozen=True)
class NcmRefinementDecision:
    """Outcome of schema/provenance gating; acceptance is shadow-only in v1."""
    status: str
    candidate_answer: str | None
    claims: tuple[dict[str, Any], ...]
    change_intents: tuple[str, ...]
    uncertainties: tuple[str, ...]
    errors: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    auto_apply: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FinalAnswerSelection:
    """Selection result which preserves the baseline until a later gated version."""
    answer: str
    applied_ncm: bool
    reason: str
    decision_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _json_object(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    try:
        copied = json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError):
        return None
    return copied if isinstance(copied, dict) else None


def _terms(text: str) -> set[str]:
    return {word.casefold() for word in _WORD.findall(text)
            if len(word) > 2 and word.casefold() not in _STOP_TERMS}


def _evidence_text(artifact: Mapping[str, Any]) -> str:
    content = artifact.get("content", {})
    if not isinstance(content, Mapping):
        return ""
    values = [content.get("content", ""), content.get("statement", ""), content.get("expression", ""),
              content.get("exact_value", "")]
    relation = content.get("relation", {})
    if isinstance(relation, Mapping):
        values.extend(relation.get(key, "") for key in ("subject", "predicate", "object"))
    return " ".join(str(value) for value in values if value)


def build_reflection_packet(snapshot: Mapping[str, Any], draft: str, *, max_excerpt_chars: int = 1_200,
                            max_evidence_items: int = 24) -> dict[str, Any]:
    """Build a bounded, attributable input for an NCM runner.

    Personal memory, previous proposals and model analysis text are deliberately
    excluded. The runner receives only the request, the candidate baseline
    response, and documentary/symbolic/exact-verification context.
    """
    if not isinstance(draft, str) or not draft.strip():
        raise ValueError("A non-empty baseline draft is required")
    if max_excerpt_chars < 80 or max_evidence_items < 1:
        raise ValueError("Reflection packet bounds are too small")
    artifacts = snapshot.get("artifacts", [])
    evidence: list[dict[str, str]] = []
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if not isinstance(artifact, Mapping):
                continue
            kind = artifact.get("kind")
            identifier = artifact.get("id")
            if kind not in {"document", "symbolic_fact", "computation", "verification"}:
                continue
            if not isinstance(identifier, str) or not identifier:
                continue
            text = _evidence_text(artifact)
            if kind == "verification" and not text:
                content = artifact.get("content", {})
                if isinstance(content, Mapping):
                    text = json.dumps(content.get("checks", []), ensure_ascii=False)
            if not text:
                continue
            evidence.append({"artifact_id": identifier, "kind": str(kind), "excerpt": text[:max_excerpt_chars]})
            if len(evidence) >= max_evidence_items:
                break
    unresolved = []
    raw_uncertainties = snapshot.get("uncertainties", [])
    if isinstance(raw_uncertainties, list):
        for item in raw_uncertainties[:12]:
            if isinstance(item, Mapping) and isinstance(item.get("message"), str):
                unresolved.append(item["message"][:400])
    query = snapshot.get("normalized_text") or snapshot.get("user_text") or ""
    return {
        "contract_version": CONTRACT_VERSION,
        "request": str(query)[:4_000],
        "draft": draft[:MAX_CANDIDATE_CHARS],
        "evidence": evidence,
        "unresolved_limits": unresolved,
    }


def _claim_supported(claim: str, source_ids: list[str], evidence_by_id: Mapping[str, str]) -> bool:
    claim_normalized = " ".join(claim.casefold().split())
    claim_terms = _terms(claim)
    for source_id in source_ids:
        evidence = evidence_by_id.get(source_id, "")
        normalized_evidence = " ".join(evidence.casefold().split())
        if claim_normalized and claim_normalized in normalized_evidence:
            return True
        # This does not prove truth; it is merely a conservative lexical gate
        # for shadow review. Two significant overlapping terms avoids accepting
        # a claim that only cites an unrelated artifact ID.
        if len(claim_terms & _terms(evidence)) >= 2:
            return True
    return False


def gate_refinement_response(response: Any, reflection_packet: Mapping[str, Any]) -> NcmRefinementDecision:
    """Validate a local NCM refinement response against packet evidence.

    A successful decision is eligible for *developer shadow review only*. The
    final selection helper still retains the baseline, ensuring a malformed,
    unavailable, or overconfident NCM cannot alter a user answer.
    """
    payload = _json_object(response)
    packet = _json_object(reflection_packet)
    if packet is None:
        raise ValueError("Reflection packet must be a JSON object")
    evidence_by_id = {
        item.get("artifact_id"): str(item.get("excerpt", ""))
        for item in packet.get("evidence", []) if isinstance(item, Mapping) and isinstance(item.get("artifact_id"), str)
    }
    evidence_ids = tuple(sorted(evidence_by_id))
    if payload is None:
        return NcmRefinementDecision("rejected", None, (), (), (), ("NCM response must be one JSON object",), evidence_ids)
    errors: list[str] = []
    candidate = payload.get("candidate_answer")
    if not isinstance(candidate, str) or not candidate.strip():
        errors.append("candidate_answer must be a non-empty string")
        candidate_text: str | None = None
    elif len(candidate) > MAX_CANDIDATE_CHARS:
        errors.append(f"candidate_answer exceeds {MAX_CANDIDATE_CHARS} characters")
        candidate_text = None
    else:
        candidate_text = candidate.strip()
    intents_raw = payload.get("change_intents", [])
    intents: tuple[str, ...] = ()
    if not isinstance(intents_raw, list) or not all(isinstance(value, str) for value in intents_raw):
        errors.append("change_intents must be a list of strings")
    else:
        invalid = [value for value in intents_raw if value not in _ALLOWED_INTENTS]
        if invalid:
            errors.append(f"Unsupported change_intent(s): {', '.join(invalid[:3])}")
        else:
            intents = tuple(intents_raw[:8])
    uncertainties_raw = payload.get("uncertainties", [])
    uncertainties: tuple[str, ...] = ()
    if not isinstance(uncertainties_raw, list) or not all(isinstance(value, str) for value in uncertainties_raw):
        errors.append("uncertainties must be a list of strings")
    else:
        uncertainties = tuple(value.strip()[:400] for value in uncertainties_raw[:12] if value.strip())
    raw_claims = payload.get("claims", [])
    accepted_claims: list[dict[str, Any]] = []
    if not isinstance(raw_claims, list):
        errors.append("claims must be a list")
    elif len(raw_claims) > MAX_CLAIMS:
        errors.append(f"claims exceeds {MAX_CLAIMS} items")
    else:
        for index, raw_claim in enumerate(raw_claims):
            claim = _json_object(raw_claim)
            if claim is None:
                errors.append(f"claims[{index}] must be an object")
                continue
            text = claim.get("text")
            references = claim.get("source_artifact_ids")
            if not isinstance(text, str) or not text.strip() or len(text) > MAX_CLAIM_CHARS:
                errors.append(f"claims[{index}].text must be a bounded non-empty string")
                continue
            if not isinstance(references, list) or not references or not all(isinstance(value, str) for value in references):
                errors.append(f"claims[{index}].source_artifact_ids must be a non-empty string list")
                continue
            reference_ids = list(dict.fromkeys(references))
            missing = [source_id for source_id in reference_ids if source_id not in evidence_by_id]
            if missing:
                errors.append(f"claims[{index}] references unavailable evidence: {', '.join(missing[:3])}")
                continue
            if not _claim_supported(text.strip(), reference_ids, evidence_by_id):
                errors.append(f"claims[{index}] lacks lexical support in its cited evidence")
                continue
            accepted_claims.append({"text": text.strip(), "source_artifact_ids": reference_ids})
    if errors:
        return NcmRefinementDecision("rejected", candidate_text, tuple(accepted_claims), intents, uncertainties,
                                     tuple(errors), evidence_ids)
    return NcmRefinementDecision("accepted_for_shadow_review", candidate_text, tuple(accepted_claims), intents,
                                 uncertainties, (), evidence_ids, auto_apply=False)


def select_final_answer(baseline_answer: str, decision: NcmRefinementDecision, *, mode: str = "off") -> FinalAnswerSelection:
    """Return the baseline answer until a later independently tested gated mode.

    Keeping this policy explicit makes the initial NCM integration safe: the
    response is connected to the reflection trace but no generated wording can
    silently replace the evidence-preserving baseline.
    """
    if not isinstance(baseline_answer, str) or not baseline_answer.strip():
        raise ValueError("A non-empty baseline answer is required")
    if mode not in {"off", "shadow", "gated"}:
        raise ValueError("mode must be off, shadow, or gated")
    if mode == "off":
        reason = "NCM refinement is disabled; baseline retained"
    elif decision.status != "accepted_for_shadow_review":
        reason = "NCM refinement rejected or unavailable; baseline retained"
    else:
        reason = "NCM refinement recorded for shadow review; baseline retained pending gated evaluation"
    return FinalAnswerSelection(baseline_answer, applied_ncm=False, reason=reason, decision_status=decision.status)
