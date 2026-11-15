"""Build the default UCA without downloading or assuming any external assets."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .auxiliary import AuxiliaryRegistry
from .config import load_config, local_path
from .engine import UnifiedCognitiveEngine
from .model_adapters import ExternalNcmAdapter, LocalCausalGenerator, MaskedNanoDiffAdapter
from .pipeline import (FinalResponseModule, FinalVerificationModule, GlobalWorkspaceModule,
                       InputProcessingModule, KnowledgeRetrievalModule, MettaSymbolicModule,
                       NanoDiffModule, NcmConceptModule, SmolAnalysisModule, UserMemoryModule)
from .storage import ExplicitMemoryStore, FTSKnowledgeStore, OperatorFactStore


def build_engine(root: str | Path = ".", config: dict[str, Any] | None = None) -> UnifiedCognitiveEngine:
    cfg = config or load_config(root)
    stores = cfg["stores"]
    memory = ExplicitMemoryStore(local_path(cfg, stores["memory_path"]))
    knowledge = FTSKnowledgeStore(local_path(cfg, stores["knowledge_db"]), stores.get("knowledge_table", "documents"),
                                  cache_enabled=bool(cfg["engine"].get("cache_enabled", False)))
    model135_config = cfg["models"]["smollm2_135"]
    model360_config = cfg["models"]["smollm2_360"]
    smol135 = SmolAnalysisModule("smollm2_135_analysis", "SmolLM2-135M-Instruct",
                                 LocalCausalGenerator(model135_config, cfg, "SmolLM2-135M-Instruct"),
                                 ("user_memory", "knowledge_retrieval", "symbolic_processing", "ncm_concept_generation"))
    smol135.enabled = bool(model135_config.get("enabled", True))
    smol360 = SmolAnalysisModule("smollm2_360_review", "SmolLM2-360M-Instruct",
                                 LocalCausalGenerator(model360_config, cfg, "SmolLM2-360M-Instruct"),
                                 ("smollm2_135_analysis",))
    smol360.enabled = bool(model360_config.get("enabled", True))
    ncm_spec = cfg["models"]["ncm"]
    nano_spec = cfg["models"]["nanodiff"]
    metta_spec = cfg["metta"]
    modules = [
        InputProcessingModule(),
        UserMemoryModule(memory, enabled=True),
        KnowledgeRetrievalModule(knowledge, enabled=True),
        MettaSymbolicModule(str(metta_spec.get("runner_command", "")),
                            OperatorFactStore(local_path(cfg, stores["facts_path"])),
                            enabled=bool(metta_spec.get("enabled", True))),
        NcmConceptModule(ExternalNcmAdapter(ncm_spec), enabled=bool(ncm_spec.get("enabled", False))),
        smol135,
        smol360,
        NanoDiffModule(MaskedNanoDiffAdapter(nano_spec, cfg), enabled=bool(nano_spec.get("enabled", False))),
        GlobalWorkspaceModule(),
        FinalVerificationModule(knowledge, str(metta_spec.get("runner_command", ""))),
        FinalResponseModule(),
    ]
    engine_spec = cfg["engine"]
    return UnifiedCognitiveEngine(
        modules, list(cfg["pipeline"]["order"]), resource_mode=str(engine_spec.get("mode", "sequential_unload")),
        default_timeout=float(engine_spec.get("default_timeout_seconds", 45)),
        max_corrections=int(engine_spec.get("max_corrections", 1)),
        run_history_limit=int(engine_spec.get("run_history_limit", 30)),
        auxiliary=AuxiliaryRegistry(cfg.get("auxiliary", {}), Path(cfg["_root"])),
    )
