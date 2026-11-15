"""Hyperdimensional vector-symbolic memory (VSA / Holographic Reduced Representations).

Inspired by distributed neural codes (Plate's HRR, Kanerva's sparse distributed
memory): every symbol is a high-dimensional bipolar vector; composite structures
are built with bundling (superposition, the sum) and binding (elementwise
product, an involution). This provides:

- holographic fact encodings that can be *unbound* to recover a component;
- graceful degradation: recalls are similarity-ranked, never absolute;
- structural similarity between entities inferred from their relational roles.

Everything is deterministic: atom vectors derive from SHA-256 seeds of their
keys. A recall score is a cosine over noise — it is *not* a probability of
truth, and downstream modules must keep that invariant.
"""
from __future__ import annotations

import hashlib
import math
import random
from typing import Any, Iterable

DEFAULT_DIMENSION = 2048


def _seed(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")


def atom(key: str, dim: int = DEFAULT_DIMENSION) -> list[int]:
    """Deterministic pseudo-random bipolar vector for one symbol."""
    rng = random.Random(_seed("vsa-atom:" + key))
    return [1 if rng.random() < 0.5 else -1 for _ in range(dim)]


def bind(left: list[int], right: list[int]) -> list[int]:
    """Binding: elementwise product. Self-inverse (bind(bind(a,b),b) == a)."""
    return [a * b for a, b in zip(left, right)]


def bundle(*vectors: list[int]) -> list[int]:
    """Superposition: summed then re-binarized. Ties break by index parity
    (deterministic); bundling keeps each member partially retrievable."""
    if not vectors:
        raise ValueError("bundle() requires at least one vector")
    dim = len(vectors[0])
    summed = [sum(vec[i] for vec in vectors) for i in range(dim)]
    return [1 if value > 0 else (-1 if value < 0 else (1 if i % 2 == 0 else -1))
            for i, value in enumerate(summed)]


def similarity(left: list[int], right: list[int]) -> float:
    """Cosine similarity in [-1, 1]; ~0 for unrelated random hypervectors."""
    dot = sum(a * b for a, b in zip(left, right))
    norm = math.sqrt(len(left)) * math.sqrt(len(right))
    return dot / norm if norm else 0.0


class HyperMemory:
    """A small, auditable holographic memory for structured facts.

    A fact (subject, predicate, object) is encoded as the superposition of its
    bound role-fillers::

        fact_vec = bundle(bind(S, R_subject), bind(P, R_predicate), bind(O, R_object))

    Because binding is an involution, a paired probe (subject + predicate)
    approximately unbinds the object channel; remaining cross-terms are noise
    that averages out when several facts agree. Nothing recalled here is a
    verified fact: it is a *memory completion* ranked by cosine similarity.
    """

    ROLE_SUBJECT = "role:subject"
    ROLE_PREDICATE = "role:predicate"
    ROLE_OBJECT = "role:object"

    def __init__(self, dimension: int = DEFAULT_DIMENSION) -> None:
        if dimension < 64:
            raise ValueError("Hyperdimensional memory needs at least 64 dimensions")
        self.dimension = dimension
        self._atoms: dict[str, list[int]] = {}
        self._facts: list[dict[str, Any]] = []

    def vector(self, key: str) -> list[int]:
        if key not in self._atoms:
            self._atoms[key] = atom(key, self.dimension)
        return self._atoms[key]

    @property
    def vocabulary(self) -> tuple[str, ...]:
        return tuple(sorted(self._atoms))

    def encode_fact(self, subject: str, predicate: str, obj: str, *,
                    fact_id: str = "", source: str = "") -> list[int]:
        triple = tuple(value.strip() for value in (subject, predicate, obj))
        if not all(triple):
            raise ValueError("Fact encoding requires non-empty subject, predicate and object")
        filler_s = bind(self.vector(triple[0]), self.vector(self.ROLE_SUBJECT))
        filler_p = bind(self.vector(triple[1]), self.vector(self.ROLE_PREDICATE))
        filler_o = bind(self.vector(triple[2]), self.vector(self.ROLE_OBJECT))
        fact_vec = bundle(filler_s, filler_p, filler_o)
        self._facts.append({"subject": triple[0], "predicate": triple[1], "object": triple[2],
                            "fact_id": fact_id, "source": source, "vector": fact_vec})
        return fact_vec

    def complete(self, subject: str, predicate: str, *, limit: int = 3) -> list[dict[str, Any]]:
        """Holographic completion by generate-and-test re-encoding.

        For every known symbol O the hypothetical triple  (subject, predicate, O)
        is re-encoded and compared with each stored fact vector. A hypothesis
        that exactly reproduces a stored encoding scores 1.0; unrelated
        hypotheses sit near the random-vector noise floor (~1/3 of a full match
        or lower). Cosine scores are reported raw — similarity, never truth.
        """
        if not self._facts:
            return []
        role_s, role_p, role_o = (self.vector(self.ROLE_SUBJECT), self.vector(self.ROLE_PREDICATE),
                                  self.vector(self.ROLE_OBJECT))
        part_s = bind(self.vector(subject), role_s)
        part_p = bind(self.vector(predicate), role_p)
        scores: dict[str, float] = {}
        for key, vec in self._atoms.items():
            if key.startswith("role:"):
                continue
            hypothesis = bundle(part_s, part_p, bind(vec, role_o))
            scores[key] = max(similarity(hypothesis, fact["vector"]) for fact in self._facts)
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return [{"object": key, "score": round(score, 4)} for key, score in ranked[:limit]]

    def reconstruct_check(self) -> dict[str, Any]:
        """Self-fidelity probe: does each encoded fact recall its own object?

        This is an internal consistency diagnostic of the encoding capacity,
        not a validation of the facts themselves.
        """
        if not self._facts:
            return {"facts": 0, "top1_accuracy": None, "note": "empty memory"}
        hits = 0
        details = []
        for fact in self._facts:
            completion = self.complete(fact["subject"], fact["predicate"], limit=1)
            best = completion[0]["object"] if completion else ""
            score = completion[0]["score"] if completion else 0.0
            ok = best == fact["object"]
            hits += int(ok)
            details.append({"fact_id": fact["fact_id"], "expected": fact["object"],
                            "recalled": best, "score": round(score, 4), "ok": ok})
        return {"facts": len(self._facts), "top1_accuracy": round(hits / len(self._facts), 4),
                "details": details}

    def entity_profile(self, entity: str, facts: Iterable[dict[str, str]]) -> list[int]:
        """Distributional profile: superposition of an entity's predicate-object
        roles. Entities sharing relational roles become structurally similar —
        the holographic analogue of a distributional semantic vector."""
        roles = [bind(self.vector(f["predicate"]), self.vector(f["object"]))
                 for f in facts if f.get("subject") == entity]
        if not roles:
            raise ValueError(f"No roles encoded for entity: {entity}")
        return bundle(*roles)

    def analogical_transfer(self, target: str, predicate: str, *,
                            sources: list[str], facts: list[dict[str, str]],
                            limit: int = 2) -> list[dict[str, Any]]:
        """Transfer by structural neighbourhood: objects used with `predicate`
        by entities whose role-profiles resemble `target`'s.

        weight(o) = Σ over sources s of cos(profile(s), profile(target)) where
        (s, predicate, o) is encoded. This is an explicit analogical heuristic
        (Gentner-style structure mapping, loosely), producing *proposals* only.
        """
        try:
            target_profile = self.entity_profile(target, facts)
        except ValueError:
            return []
        proposals: dict[str, float] = {}
        for source in sources:
            if source == target:
                continue
            try:
                source_profile = self.entity_profile(source, facts)
            except ValueError:
                continue
            affinity = similarity(source_profile, target_profile)
            if affinity <= 0:
                continue
            for fact in facts:
                if fact.get("subject") == source and fact.get("predicate") == predicate:
                    obj = fact.get("object", "")
                    proposals[obj] = proposals.get(obj, 0.0) + affinity
        ranked = sorted(proposals.items(), key=lambda item: (-item[1], item[0]))
        return [{"object": obj, "analogy_weight": round(weight, 4)}
                for obj, weight in ranked[:limit] if weight > 0]
