"""Typed, append-only exchange objects used by every UCA module."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4
import json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ModuleStatus(str, Enum):
    FUNCTIONAL = "functional"
    UNAVAILABLE = "unavailable"
    NON_VALIDATED = "non_validated"
    DISABLED = "disabled_voluntarily"
    FAILED = "failed_execution"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ArtifactKind(str, Enum):
    MEMORY = "memory"
    DOCUMENT = "document"
    SYMBOLIC_FACT = "symbolic_fact"
    PROPOSAL = "proposal"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    VERIFICATION = "verification"
    REFINEMENT = "refinement"
    COMPUTATION = "computation"
    FINAL = "final"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True)
class Provenance:
    """Origin metadata. `producer` is mandatory for every substantive artifact."""
    producer: str
    created_at: str = field(default_factory=utc_now)
    input_artifact_ids: tuple[str, ...] = ()
    references: tuple[str, ...] = ()
    implementation: str = ""


@dataclass(frozen=True)
class Artifact:
    """An append-only result. Content must be JSON-serializable."""
    kind: ArtifactKind
    content: Mapping[str, Any]
    provenance: Provenance
    confidence: float | None = None
    uncertainty: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class ModuleReport:
    module_id: str
    status: ModuleStatus
    started_at: str
    ended_at: str
    duration_ms: float
    message: str = ""
    error: str | None = None
    output_ids: tuple[str, ...] = ()
    attempt: int = 1

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class ModuleResult:
    """Returned by a module; modules must never mutate CognitiveContext directly."""
    artifacts: tuple[Artifact, ...] = ()
    warnings: tuple[str, ...] = ()
    message: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class CognitiveContext:
    """The common format required by the UCA execution contract.

    Category lists are views maintained by `add_artifact`; `artifacts` preserves
    the complete, ordered provenance ledger and is the source of truth.
    """
    request_id: str
    user_text: str
    normalized_text: str = ""
    query_type: str = "unknown"
    available_context: dict[str, Any] = field(default_factory=dict)
    sources: list[dict[str, Any]] = field(default_factory=list)
    symbolic_facts: list[dict[str, Any]] = field(default_factory=list)
    propositions: list[dict[str, Any]] = field(default_factory=list)
    computations: list[dict[str, Any]] = field(default_factory=list)
    scores: list[dict[str, Any]] = field(default_factory=list)
    uncertainties: list[dict[str, Any]] = field(default_factory=list)
    execution_history: list[ModuleReport] = field(default_factory=list)
    module_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    artifacts: list[Artifact] = field(default_factory=list)
    final_response: str | None = None
    created_at: str = field(default_factory=utc_now)

    def add_artifact(self, artifact: Artifact) -> None:
        """Append an artifact and maintain explicit non-overlapping evidence bins."""
        self.artifacts.append(artifact)
        serialized = artifact.to_dict()
        if artifact.kind is ArtifactKind.DOCUMENT:
            self.sources.append(serialized)
        elif artifact.kind is ArtifactKind.SYMBOLIC_FACT:
            self.symbolic_facts.append(serialized)
        elif artifact.kind is ArtifactKind.PROPOSAL:
            # Proposal is intentionally separate from fact/source bins.
            self.propositions.append(serialized)
        elif artifact.kind is ArtifactKind.COMPUTATION:
            # Exact calculations are a separate substrate, never silently promoted
            # into a documentary or symbolic fact.
            self.computations.append(serialized)
        if artifact.confidence is not None:
            self.scores.append({"artifact_id": artifact.id, "score": artifact.confidence,
                                "producer": artifact.provenance.producer})
        for item in artifact.uncertainty:
            self.uncertainties.append({"artifact_id": artifact.id, "message": item,
                                       "producer": artifact.provenance.producer})
        if artifact.kind is ArtifactKind.FINAL:
            answer = artifact.content.get("answer")
            if isinstance(answer, str):
                self.final_response = answer

    def artifacts_of(self, *kinds: ArtifactKind) -> list[Artifact]:
        allowed = set(kinds)
        return [item for item in self.artifacts if item.kind in allowed]

    def snapshot(self) -> dict[str, Any]:
        """A JSON-only immutable-by-convention input passed to modules."""
        return {
            "request_id": self.request_id,
            "user_text": self.user_text,
            "normalized_text": self.normalized_text,
            "query_type": self.query_type,
            "available_context": json.loads(json.dumps(self.available_context)),
            "sources": json.loads(json.dumps(self.sources)),
            "symbolic_facts": json.loads(json.dumps(self.symbolic_facts)),
            "propositions": json.loads(json.dumps(self.propositions)),
            "computations": json.loads(json.dumps(self.computations)),
            "scores": json.loads(json.dumps(self.scores)),
            "uncertainties": json.loads(json.dumps(self.uncertainties)),
            "execution_history": [record.to_dict() for record in self.execution_history],
            "artifacts": [item.to_dict() for item in self.artifacts],
            "module_states": json.loads(json.dumps(self.module_states)),
            "final_response": self.final_response,
        }

    def to_dict(self, developer: bool = True) -> dict[str, Any]:
        answer = {
            "request_id": self.request_id,
            "answer": self.final_response,
            "query_type": self.query_type,
            "created_at": self.created_at,
            "sources": self.sources,
            "uncertainties": self.uncertainties,
            "module_states": self.module_states,
        }
        if developer:
            answer.update({
                "normalized_text": self.normalized_text,
                "symbolic_facts": self.symbolic_facts,
                "propositions": self.propositions,
                "computations": self.computations,
                "scores": self.scores,
                "execution_history": [record.to_dict() for record in self.execution_history],
                "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            })
        return answer
