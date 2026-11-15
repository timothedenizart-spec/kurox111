"""Probe lab: measured micro-experiments used to *identify* improvements (not to
claim quality).

Every probe answers one narrow engineering question with numbers and yields a
verdict: ``solide`` (behaviour as designed, measurement attached) or
``à améliorer`` (a measured weakness, with a concrete candidate improvement
that becomes a backlog entry — hypotheses are never injected silently).
Deterministic wherever determinism is claimed; wall-clock probes assert
direction, never brittle exact timings.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter, sleep
from typing import Any
import json

from .cognitive import ExactArithmeticKernel
from .config import DEFAULT_CONFIG
from .engine import UnifiedCognitiveEngine
from .factory import build_engine
from .modules import CognitiveModule
from .predictive import LocalSurprisalModel, novelty_report
from .storage import import_documents, initialize_knowledge_db
from .types import Artifact, ArtifactKind, ModuleResult, ModuleStatus, Provenance
from .vsa import HyperMemory

PROBE_SCHEMA = "uca.probe-lab.v1"

_CORPUS = [
    "la bretagne est une région française",
    "rennes est la capitale de la bretagne",
    "la normandie est une région française",
    "rouen est la préfecture de la normandie",
    "la france est un pays européen",
]


class _SlowProbeModule(CognitiveModule):
    """Artificial module used only by probes: sleeps, then returns a marker."""

    def __init__(self, module_id: str, delay: float, timeout_seconds: float | None = None,
                 dependencies: tuple[str, ...] = ()) -> None:
        super().__init__(module_id, dependencies=dependencies, timeout_seconds=timeout_seconds)
        self.delay = delay

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        sleep(self.delay)
        return ModuleResult(artifacts=(Artifact(ArtifactKind.DIAGNOSTIC, {"probe": True},
                                                Provenance(self.module_id)),))


def _engine_with(fixtures: dict[str, Any]) -> UnifiedCognitiveEngine:
    """Engines built on isolated temp roots from declared fixtures."""
    temp = TemporaryDirectory()
    root = Path(temp.name)
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "data" / "memory.json").write_text(json.dumps({"entries": fixtures.get("memory", [])},
                                                          ensure_ascii=False), encoding="utf-8")
    (root / "data" / "operator_facts.json").write_text(json.dumps({"facts": fixtures.get("facts", [])},
                                                                  ensure_ascii=False), encoding="utf-8")
    db = root / "data" / "knowledge.sqlite"
    initialize_knowledge_db(db)
    if fixtures.get("documents"):
        import_documents(db, fixtures["documents"])
    config = deepcopy(DEFAULT_CONFIG)
    config["_root"] = str(root)
    engine = build_engine(config=config)
    engine._probe_tempdir = temp  # keep the temp root alive for the probes' lifetime
    return engine


def probe_parallel_speedup() -> dict[str, Any]:
    """Does the contiguous-level engine actually shorten wall time?"""
    modules = [_SlowProbeModule(f"slow_{index}", 0.12) for index in range(4)]
    sequential = UnifiedCognitiveEngine(modules=[_SlowProbeModule(f"slow_{index}", 0.12) for index in range(4)],
                                        pipeline=[f"slow_{index}" for index in range(4)],
                                        execution_mode="sequential")
    parallel = UnifiedCognitiveEngine(modules=modules,
                                      pipeline=[f"slow_{index}" for index in range(4)],
                                      execution_mode="parallel_levels")
    start = perf_counter(); sequential.process("probe"); seq_wall = perf_counter() - start
    start = perf_counter(); parallel.process("probe"); par_wall = perf_counter() - start
    ratio = seq_wall / par_wall if par_wall else 0.0
    improvement = None if ratio > 1.2 else "Réduire le surcoût ThreadPoolExecutor par niveau."
    return {"name": "parallel_speedup", "verdict": "solide" if ratio > 1.2 else "à améliorer",
            "measurements": {"sequential_wall_s": round(seq_wall, 3), "parallel_wall_s": round(par_wall, 3),
                             "speedup": round(ratio, 2)},
            "candidate_improvement": improvement}


def probe_surprisal_separation() -> dict[str, Any]:
    """Is the surprisal monitor actually separating novel text from corpus text?

    Uses the *real* corpus background (module behaviour), not an arbitrary
    constant — an earlier probe version with a fixed 4.0 background showed a
    false-negative margin: that weakness was in the probe, now fixed.
    """
    from .predictive import corpus_background
    model = LocalSurprisalModel()
    model.train(_CORPUS)
    background = corpus_background(model, _CORPUS)["background_mean"]
    calm = novelty_report(model, _CORPUS[0], background_mean=background)
    wild = novelty_report(model, "zyzzyva locomotive xylophone quasar", background_mean=background)
    separated = (not calm["flagged"]) and wild["flagged"]
    margin = (wild.get("mean_surprisal") or 0) / max(0.01, calm.get("mean_surprisal") or 0.01)
    return {"name": "surprisal_separation",
            "verdict": "solide" if separated else "à améliorer",
            "measurements": {"background_mean": background,
                             "calm_mean": calm.get("mean_surprisal"), "wild_mean": wild.get("mean_surprisal"),
                             "separation_ratio": round(margin, 2), "wild_flagged": wild["flagged"]},
            "candidate_improvement": (None if separated else
                                      "Étalonner le facteur de flag sur un corpus annoté plus grand (UCA-10).")}


def probe_vsa_scaling() -> dict[str, Any]:
    """Where does holographic discrimination actually start to degrade?

    Measured per dimension: top1 recall accuracy AND the margin between the
    best and second-best candidate (the discrimination signal that noise
    erodes as facts accumulate — the real scaling limit of the channel).
    """
    accelerated = HyperMemory(dimension=64)._np is not None
    fact_count = 150 if accelerated else 60
    dims = (64, 512, 2048) if accelerated else (64, 512)
    findings = {}
    for dim in dims:
        memory = HyperMemory(dimension=dim)
        for index in range(fact_count):
            memory.encode_fact(f"sujet-{index}", "prédicat", f"objet-{index}", fact_id=f"f{index}")
        fidelity = memory.reconstruct_check(sample_limit=20)
        margins = []
        for index in range(0, min(12, fact_count)):
            completion = memory.complete(f"sujet-{index}", "prédicat", limit=2)
            if len(completion) == 2:
                margins.append(round(completion[0]["score"] - completion[1]["score"], 4))
        findings[f"dim_{dim}"] = {"top1": fidelity["top1_accuracy"],
                                  "margin_min": min(margins) if margins else None,
                                  "margin_mean": round(sum(margins) / len(margins), 4) if margins else None}
    weakest = min((value["margin_mean"] or 0.0) for value in findings.values())
    weak = any(value["top1"] is not None and value["top1"] < 1.0 for value in findings.values()) or weakest < 0.15
    return {"name": "vsa_scaling_fidelity",
            "verdict": "à améliorer" if weak else "solide",
            "measurements": {**{k: v["top1"] for k, v in findings.items()},
                             "margin_mean_par_dim": {k: v["margin_mean"] for k, v in findings.items()},
                             "fact_count": fact_count, "accelerated": accelerated},
            "candidate_improvement": ("Dimension adaptative selon le nombre de faits et cleanup "
                                      "d'attracteurs Hopfield sur les rappels à marge faible."
                                      if weak else None)}


def probe_arithmetic_robustness() -> dict[str, Any]:
    """The math extractor must not eat dates, IDs or voltage — and must eat math."""
    expectations = [
        ("en 2024 la version 3.11 est sortie", None),
        ("colis 38-76-12 arrivé", None),
        ("il mesure 1.80m", None),
        ("calcule 2+2", "2+2"),
        ("combien fait 2024-1976", "2024-1976"),
        ("calcule (2+3)×7", "(2+3)×7"),
        ("quelle heure est-il", None),
    ]
    misses = []
    for text, expected in expectations:
        got = ExactArithmeticKernel.extract(text)
        normalized = got.replace("×", "*").replace("÷", "/") if got else None
        want = expected.replace("×", "*") if expected else None
        if normalized != want and not (want and got and want.replace("×", "*") in normalized.replace("×", "*")):
            misses.append({"text": text, "expected": expected, "got": got})
    return {"name": "arithmetic_extraction_robustness",
            "verdict": "solide" if not misses else "à améliorer",
            "measurements": {"cases": len(expectations), "mismatches": misses},
            "candidate_improvement": "Raffiner l'extracteur d'expressions sur ces cas." if misses else None}


def probe_timeout_isolation() -> dict[str, Any]:
    """A stuck module must fail as timed_out while the architecture finishes."""
    slow = _SlowProbeModule("bloquant", 0.35, timeout_seconds=0.05)
    witness = _SlowProbeModule("temoin", 0.0)
    witness.dependencies = ("bloquant",)
    engine = UnifiedCognitiveEngine([slow, witness], ["bloquant", "temoin"],
                                    default_timeout=0.05, execution_mode="sequential")
    context = engine.process("probe de résilience")
    blocked = context.module_states["bloquant"]
    witnessed = context.module_states["temoin"]
    resilient = blocked["status"] == "failed_execution" and blocked["execution"] == "timed_out" \
        and witnessed["execution"] == "completed"
    return {"name": "timeout_isolation",
            "verdict": "solide" if resilient else "à améliorer",
            "measurements": {"blocked_state": blocked["execution"], "witness_state": witnessed["execution"]},
            "candidate_improvement": None if resilient else "Isoler davantage les threads bloqués."}


def probe_memory_optin_gate() -> dict[str, Any]:
    """Only explicit:true memory may surface — measurement, zero tolerance."""
    engine = _engine_with({"memory": [{"id": "non", "text": "Bretagne", "explicit": False}],
                           "documents": [{"doc_id": "d", "content": "La Bretagne existe.", "provenance": "probe"}]})
    context = engine.process("Bretagne")
    count = len(context.artifacts_of(ArtifactKind.MEMORY))
    return {"name": "memory_optin_gate", "verdict": "solide" if count == 0 else "à améliorer",
            "measurements": {"memory_artifacts": count},
            "candidate_improvement": None if count == 0 else "Filtrage opt-in défaillant — priorité sécurité."}


def probe_conflict_bounded_correction() -> dict[str, Any]:
    """Conflicting facts: exactly one bounded correction pass, never a loop."""
    engine = _engine_with({"facts": [
        {"id": "f1", "subject": "Bretagne", "predicate": "capitale", "object": "Rennes"},
        {"id": "f2", "subject": "Bretagne", "predicate": "capitale", "object": "Nantes"}]})
    context = engine.process("Quelle est la capitale de la Bretagne ?")
    attempts = [record for record in context.execution_history if record.module_id == "final_verification"]
    refinements = context.artifacts_of(ArtifactKind.REFINEMENT)
    conflicts_found = any(item.content.get("conflict_lines") for item in refinements)
    ok = len(attempts) == 2 and conflicts_found
    return {"name": "conflict_bounded_correction",
            "verdict": "solide" if ok else "à améliorer",
            "measurements": {"verification_attempts": len(attempts),
                             "conflict_surfaced_in_refinement": conflicts_found,
                             "refinement_artifacts": len(refinements)},
            "candidate_improvement": None if ok else "La borne de correction ou le raffineur ne remonte pas le conflit."}


def probe_absence_honesty() -> dict[str, Any]:
    """Empty everything: the answer must say so, and the refiner must keep it honest."""
    engine = _engine_with({})
    context = engine.process("Que sait-on du ptérodactyle ?")
    answer = context.final_response or ""
    refinements = context.artifacts_of(ArtifactKind.REFINEMENT)
    honest = "Aucune source documentaire" in answer and refinements and \
        any("Aucune preuve locale" in line for line in refinements[-1].content.get("limit_lines", []))
    return {"name": "absence_honesty_with_refiner",
            "verdict": "solide" if honest else "à améliorer",
            "measurements": {"refiner_active": bool(refinements), "honest_absence": "Aucune source documentaire" in answer},
            "candidate_improvement": None if honest else "Le raffineur masque l'absence — corriger sa composition."}


ALL_PROBES = [probe_parallel_speedup, probe_surprisal_separation, probe_vsa_scaling,
              probe_arithmetic_robustness, probe_timeout_isolation, probe_memory_optin_gate,
              probe_conflict_bounded_correction, probe_absence_honesty]


def run_all_probes() -> dict[str, Any]:
    results = []
    for probe in ALL_PROBES:
        try:
            results.append(probe())
        except Exception as error:
            results.append({"name": probe.__name__, "verdict": "à améliorer",
                            "measurements": {}, "candidate_improvement": f"Probe en échec: {error}"})
    weak = [item["name"] for item in results if item["verdict"] != "solide"]
    return {"schema": PROBE_SCHEMA, "created_at": datetime.now(timezone.utc).isoformat(),
            "probes": results,
            "summary": {"total": len(results), "solide": len(results) - len(weak),
                        "a_ameliorer": weak},
            "notice": "Findings are measurements, not quality claims; 'à améliorer' items become backlog entries."}
