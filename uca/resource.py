"""Memory policy for adapters that own heavyweight local models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import gc


class Unloadable(Protocol):
    def unload(self) -> None: ...


@dataclass
class ResourcePolicy:
    mode: str = "sequential_unload"  # sequential_unload | resident

    def after_step(self, module: Unloadable) -> None:
        if self.mode == "sequential_unload":
            module.unload()
            gc.collect()
            # torch is intentionally optional; importing it would consume memory.
            try:
                import torch  # type: ignore
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

    @staticmethod
    def notes() -> dict[str, str]:
        return {
            "sequential_unload": "Weights are released after each model stage; textual artifacts remain in context.",
            "resident": "Loaded adapters may stay in RAM/VRAM; use only when capacity is known.",
            "tokenizer_boundary": "No tensors or embeddings cross model boundaries: adapters exchange decoded text only.",
        }
