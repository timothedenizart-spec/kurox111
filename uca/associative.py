"""Hopfield attractor network for pattern completion and denoising (stdlib-only).

Classical content-addressable memory: Hebbian weights W = (1/n) Σ p pᵀ store
bipolar patterns as minima of the energy E(x) = -½ xᵀW x. Asynchronous updates
monotonically decrease E (Lyapunov function), so recall provably converges to
a fixed point — a brain-inspired analogue of hippocampal pattern completion.

Honest limits are explicit: capacity is ~0.15·n patterns before spurious
attractors dominate; a converged state is the nearest learned pattern, which
may itself be wrong. Completion is *recall*, not verification.
"""
from __future__ import annotations

import hashlib
import random
from typing import Iterable

DEFAULT_SIZE = 256
CAPACITY_RATIO = 0.15
MAX_SWEEPS = 40


def bipolar_code(key: str, size: int = DEFAULT_SIZE) -> list[int]:
    """Deterministic bipolar pattern derived from a key's SHA-256 seed."""
    digest = hashlib.sha256(("hopfield-code:" + key).encode("utf-8")).digest()
    rng = random.Random(int.from_bytes(digest[:8], "big"))
    return [1 if rng.random() < 0.5 else -1 for _ in range(size)]


class HopfieldNetwork:
    """Stores bipolar patterns; completes corrupted cues by energy descent."""

    def __init__(self, size: int = DEFAULT_SIZE, *, max_patterns: int | None = None) -> None:
        if size < 16:
            raise ValueError("Attractor memory needs at least 16 neurons")
        self.size = size
        self.max_patterns = max_patterns or max(1, int(size * CAPACITY_RATIO))
        self._weights = [[0.0] * size for _ in range(size)]
        self._patterns: list[list[int]] = []

    @property
    def pattern_count(self) -> int:
        return len(self._patterns)

    def store(self, pattern: list[int]) -> None:
        """Hebbian one-shot storage; refuses to exceed the stated capacity."""
        if len(pattern) != self.size:
            raise ValueError("Pattern size mismatch")
        if len(self._patterns) >= self.max_patterns:
            raise ValueError(
                f"Hopfield capacity reached ({self.max_patterns}); adding more would "
                "create spurious attractors — refusal is the honest behaviour")
        n = self.size
        for i in range(n):
            row = self._weights[i]
            pi = pattern[i]
            for j in range(n):
                if i != j:
                    row[j] += pi * pattern[j] / n
        self._patterns.append(list(pattern))

    def store_all(self, patterns: Iterable[list[int]]) -> int:
        count = 0
        for pattern in patterns:
            self.store(list(pattern))
            count += 1
        return count

    def energy(self, state: list[int]) -> float:
        total = 0.0
        for i in range(self.size):
            row = self._weights[i]
            si = state[i]
            for j in range(self.size):
                total += row[j] * si * state[j]
        return -0.5 * total

    def recall(self, cue: list[int]) -> dict:
        """Asynchronous energy descent in a fixed neuron order (deterministic).

        Returns the converged state, the number of sweeps used, the final
        energy, and whether the cue changed — callers can see exactly what the
        network did, including when nothing was corrected.
        """
        if len(cue) != self.size:
            raise ValueError("Cue size mismatch")
        if not self._patterns:
            raise ValueError("No stored patterns: recall is impossible")
        state = list(cue)
        for sweep in range(MAX_SWEEPS):
            changed = False
            for i in range(self.size):
                field = sum(self._weights[i][j] * state[j] for j in range(self.size))
                new = 1 if field >= 0 else -1
                if new != state[i]:
                    state[i] = new
                    changed = True
            if not changed:
                return {"state": state, "sweeps": sweep + 1, "converged": True,
                        "energy": round(self.energy(state), 3)}
        return {"state": state, "sweeps": MAX_SWEEPS, "converged": False,
                "energy": round(self.energy(state), 3)}

    def nearest_stored(self, state: list[int]) -> tuple[int, float]:
        """(index, overlap in [0,1]) of the closest stored pattern."""
        best_index, best_overlap = -1, -1.0
        for index, pattern in enumerate(self._patterns):
            overlap = sum(a == b for a, b in zip(state, pattern)) / self.size
            if overlap > best_overlap:
                best_index, best_overlap = index, overlap
        return best_index, round(best_overlap, 4)


def corrupt(pattern: list[int], flips: int, *, seed: int) -> list[int]:
    """Deterministic bit-flip corruption used to test completion honestly."""
    rng = random.Random(seed)
    state = list(pattern)
    for index in rng.sample(range(len(state)), min(flips, len(state))):
        state[index] *= -1
    return state
