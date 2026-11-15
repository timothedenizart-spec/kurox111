"""Unified Cognitive Architecture: a local, evidence-aware orchestrator."""

from .engine import UnifiedCognitiveEngine
from .factory import build_engine
from .types import ModuleStatus, CognitiveContext

__all__ = ["UnifiedCognitiveEngine", "build_engine", "ModuleStatus", "CognitiveContext"]
