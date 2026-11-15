"""Offline consolidation: Hebbian co-occurrence associations over local stores.

A 'sleep-cycle' analogue: outside any chat request, replay the operator's
structured facts against the local FTS corpus and strengthen entity pairs that
repeatedly co-occur  ("neurons that fire together wire together", Hebb 1949).
Strength uses the Jaccard ratio  co / (n_a + n_b - co)  over document counts,
decays nothing (deterministic replay), and every edge keeps the document IDs
that support it. The result is written to a JSON store and later surfaced as
explicitly *unverified associative proposals* — never as facts.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import re
import sqlite3

_WORD = re.compile(r"[\wÀ-ÿ'-]+", re.UNICODE)
SCHEMA = "uca.consolidation.v1"
MAX_EDGES = 64
MIN_STRENGTH = 0.05


def _norm(text: str) -> str:
    return " ".join(token.lower() for token in _WORD.findall(text))


def _entities_from_facts(facts: list[dict[str, Any]]) -> list[str]:
    entities: set[str] = set()
    for fact in facts:
        for key in ("subject", "object"):
            value = str(fact.get(key, "")).strip()
            if value:
                entities.add(value)
    return sorted(entities)


def _document_rows(db_path: Path, table: str) -> list[tuple[str, str]]:
    if not db_path.exists():
        return []
    try:
        with sqlite3.connect(db_path) as connection:
            return [(str(doc), str(content)) for doc, content in
                    connection.execute(f"SELECT doc_id, content FROM {table}").fetchall()]
    except sqlite3.Error:
        return []


def consolidate(facts_path: str | Path, db_path: str | Path, table: str,
                output_path: str | Path) -> dict[str, Any]:
    """Replay stores and persist the association edges. Pure and idempotent:
    identical inputs produce an identical file (hash displayed for audit)."""
    facts_path, db_path, output_path = Path(facts_path), Path(db_path), Path(output_path)
    try:
        parsed = json.loads(facts_path.read_text(encoding="utf-8")) if facts_path.exists() else {}
        facts = [item for item in parsed.get("facts", []) if isinstance(item, dict)]
    except (OSError, json.JSONDecodeError):
        facts = []
    entities = _entities_from_facts(facts)
    rows = _document_rows(db_path, table)
    normalized_docs = [(doc_id, _norm(content)) for doc_id, content in rows]

    mentions: dict[str, set[str]] = {entity: set() for entity in entities}
    co_counts: Counter[tuple[str, str]] = Counter()
    co_docs: dict[tuple[str, str], list[str]] = {}
    for doc_id, body in normalized_docs:
        present = [entity for entity in entities if entity.lower() in body]
        for entity in present:
            mentions[entity].add(doc_id)
        for index, left in enumerate(present):
            for right in present[index + 1:]:
                pair = (left, right) if left <= right else (right, left)
                co_counts[pair] += 1
                co_docs.setdefault(pair, []).append(doc_id)

    edges: list[dict[str, Any]] = []
    for (left, right), co in co_counts.items():
        union = len(mentions[left]) + len(mentions[right]) - co
        strength = co / union if union else 0.0
        if strength >= MIN_STRENGTH:
            edges.append({"a": left, "b": right, "strength": round(strength, 4),
                          "co_occurrences": co,
                          "supporting_document_ids": sorted(set(co_docs[(left, right)]))[:12]})
    edges.sort(key=lambda item: (-item["strength"], item["a"], item["b"]))
    edges = edges[:MAX_EDGES]

    payload = {
        "schema": SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sources": {"facts_path": str(facts_path), "knowledge_db": str(db_path),
                    "fact_count": len(facts), "document_count": len(normalized_docs),
                    "entity_count": len(entities)},
        "method": "Hebbian document co-occurrence, Jaccard strength, deterministic replay",
        "epistemic_notice": "Associations are statistical co-occurrences with local provenance, not facts.",
        "edges": edges,
    }
    digest = hashlib.sha256(json.dumps(edges, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
    payload["consolidation_id"] = digest
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canonical = dict(payload)
    output_path.write_text(json.dumps(canonical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def load_associations(path: str | Path) -> list[dict[str, Any]]:
    """Read a consolidation store; absence or corruption yields an empty list,
    which callers must treat as inconclusive, never as negative evidence."""
    path = Path(path)
    if not path.exists():
        return []
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, dict) or parsed.get("schema") != SCHEMA:
        return []
    edges = parsed.get("edges", [])
    return [edge for edge in edges if isinstance(edge, dict) and edge.get("a") and edge.get("b")]
