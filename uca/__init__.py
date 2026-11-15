"""Unified Cognitive Architecture: a local, evidence-aware orchestrator."""

from .engine import UnifiedCognitiveEngine
from .evaluation import evaluate_context
from .factory import build_engine
from .types import ModuleStatus, CognitiveContext

__all__ = ["UnifiedCognitiveEngine", "build_engine", "evaluate_context", "ModuleStatus", "CognitiveContext"]
