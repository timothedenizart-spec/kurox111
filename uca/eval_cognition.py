"""Deterministic cognitive-behavior evaluation harness for UCA (chantier UCA-05b).

Difference with `uca.benchmark`: the benchmark measures performance and leaves
quality metrics null without a validated evaluator. **This** harness checks
explicit behavioral contracts as pass/fail against the live pipeline:

- exact arithmetic lands in the response as a rational value;
- absence of local evidence is stated, never papered over;
- the opt-in memory only ever returns `explicit: true` entries;
- structured symbolic conflicts trigger one bounded correction, never a loop;
- proposals (analogical, consolidated, model) are never silently promoted to
  the symbolic-fact bin.

No score is invented: each check reports ok + a verifiable detail, and every
case runs in an isolated temporary root built only from declared fixtures.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
import json
import platform
import sys

from .config import DEFAULT_CONFIG
from .consolidation import consolidate
from .factory import build_engine
from .storage import import_documents, initialize_knowledge_db
from .types import ArtifactKind, CognitiveContext

EVAL_SCHEMA = "uca.cognitive-eval.v1"


def load_eval_cases(path: str | Path) -> list[dict[str, Any]]:
    """JSONL of cases: {"id", "prompt", "fixtures"?, "checks": [...]}."""
    cases: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict) or not isinstance(item.get("prompt"), str):
                raise ValueError(f"Case {line_number} must contain a string prompt")
            if not isinstance(item.get("checks"), list) or not item["checks"]:
                raise ValueError(f"Case {line_number} must declare at least one check")
            item.setdefault("id", f"case-{line_number}")
            item.setdefault("fixtures", {})
            cases.append(item)
    if not cases:
        raise ValueError("At least one eval case is required")
    return cases


def _prepare_root(root: Path, fixtures: dict[str, Any]) -> dict[str, Any]:
    """Materialise only the declared fixtures; nothing is downloaded."""
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "memory.json").write_text(json.dumps({"entries": fixtures.get("memory", [])},
                                                 ensure_ascii=False), encoding="utf-8")
    (data / "operator_facts.json").write_text(json.dumps({"facts": fixtures.get("facts", [])},
                                                         ensure_ascii=False), encoding="utf-8")
    knowledge = data / "knowledge.sqlite"
    initialize_knowledge_db(knowledge)
    documents = fixtures.get("documents", [])
    if documents:
        import_documents(knowledge, documents)
    config = deepcopy(DEFAULT_CONFIG)
    config["_root"] = str(root)
    if fixtures.get("consolidate"):
        consolidate(data / "operator_facts.json", knowledge,
                    config["stores"]["knowledge_table"], data / "associations.json")
    return config


def evaluate_check(context: CognitiveContext, check: dict[str, Any]) -> tuple[bool, str]:
    """One deterministic check. Unknown types fail loudly (a check we cannot
    evaluate is a failed check, never a silent pass)."""
    kind = check.get("type")
    answer = context.final_response or ""
    if kind == "response_contains":
        value = str(check.get("value", ""))
        return value in answer, f"réponse contient {value!r}"
    if kind == "response_not_contains":
        value = str(check.get("value", ""))
        return value not in answer, f"réponse ne contient pas {value!r}"
    if kind == "module_status":
        module = str(check.get("module", ""))
        expected = str(check.get("status", ""))
        actual = context.module_states.get(module, {}).get("status", "<absent>")
        return actual == expected, f"{module}: état {actual!r} (attendu {expected!r})"
    if kind == "artifact_count":
        artifact_kind = ArtifactKind(str(check.get("kind")))
        artifacts = context.artifacts_of(artifact_kind)
        count = len(artifacts)
        low = int(check.get("min", 0))
        high = check.get("max")
        ok = count >= low and (high is None or count <= int(high))
        return ok, f"{artifact_kind.value}: {count} artefact(s) (min={low}, max={high})"
    if kind == "all_proposals_non_verifie":
        proposals = context.artifacts_of(ArtifactKind.PROPOSAL)
        bad = [item.id for item in proposals if item.content.get("status") != "NON_VERIFIE"]
        return not bad, f"{len(proposals)} proposition(s), toutes NON_VERIFIE" if not bad else \
            f"propositions NON marquées: {bad}"
    if kind == "proposals_not_in_facts":
        proposals = [str(item.content.get("text", "")) for item in context.artifacts_of(ArtifactKind.PROPOSAL)]
        statements = [str(item.get("content", {}).get("statement", "")) for item in context.symbolic_facts]
        leaked = [text for text in proposals if any(text and text in statement for statement in statements)]
        return not leaked, "aucune proposition promue au rang de fait" if not leaked else f"fuite: {leaked}"
    if kind == "symbolic_conflicts_min":
        minimum = int(check.get("count", 1))
        found = 0
        for item in context.artifacts_of(ArtifactKind.VERIFICATION):
            found = max(found, len(item.content.get("symbolic_conflicts", [])))
        return found >= minimum, f"{found} conflit(s) symbolique(s) structuré(s) (min={minimum})"
    if kind == "computation_exact":
        expected = str(check.get("exact", ""))
        values = [str(item.content.get("exact_value", ""))
                  for item in context.artifacts_of(ArtifactKind.COMPUTATION)]
        return expected in values, f"{expected} ∈ {values}"
    if kind == "memory_ids":
        expected = sorted(str(value) for value in check.get("expected", []))
        actual = sorted(str(item.content.get("memory_id", ""))
                        for item in context.artifacts_of(ArtifactKind.MEMORY))
        return actual == expected, f"mémoire rappelée {actual} (attendu {expected})"
    return False, f"type de contrôle inconnu: {kind!r}"


def run_evaluation(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Execute every case in an isolated root; degradation stays visible."""
    results: list[dict[str, Any]] = []
    for case in cases:
        check_results: list[dict[str, Any]] = []
        with TemporaryDirectory() as temp:
            config = _prepare_root(Path(temp), case["fixtures"])
            context = build_engine(config=config).process(case["prompt"])
        for check in case["checks"]:
            try:
                ok, detail = evaluate_check(context, check)
            except Exception as error:  # a broken check is a failing check
                ok, detail = False, f"{type(error).__name__}: {str(error)[:200]}"
            check_results.append({"check": check, "ok": bool(ok), "detail": detail})
        results.append({"id": case["id"], "passed": all(item["ok"] for item in check_results),
                        "checks": check_results})
    passed = sum(1 for item in results if item["passed"])
    return {"schema": EVAL_SCHEMA,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "environment": {"python": sys.version, "platform": platform.platform()},
            "cases": results,
            "summary": {"total": len(results), "passed": passed, "failed": len(results) - passed},
            "notice": ("Behavioral pass/fail contracts over the live pipeline. No quality, "
                       "truthfulness or intelligence score is claimed by this report.")}
