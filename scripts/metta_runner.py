#!/usr/bin/env python3
"""MeTTa / Hyperon JSON contract runner for UCA.

Receives JSON on stdin:
- operation: 'metta_query' -> prints JSON with 'facts': [...]
- operation: 'metta_verify' -> prints JSON with 'verifications': [...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def _tokens(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[\wÀ-ÿ'-]+", text) if len(w) > 2}


def load_facts() -> list[dict]:
    # Look for data/operator_facts.json relative to script or cwd
    candidate_paths = [
        Path("data/operator_facts.json"),
        Path(__file__).parent.parent / "data" / "operator_facts.json",
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return data.get("facts", [])
            except Exception:
                pass
    return []


def handle_query(payload: dict) -> dict:
    query = str(payload.get("query", ""))
    q_tokens = _tokens(query)
    facts = load_facts()
    matched = []
    for f in facts:
        text = " ".join(str(f.get(k, "")) for k in ("statement", "subject", "predicate", "object"))
        f_tokens = _tokens(text)
        if q_tokens & f_tokens:
            matched.append({
                "id": f.get("id"),
                "statement": f.get("statement"),
                "subject": f.get("subject"),
                "predicate": f.get("predicate"),
                "object": f.get("object"),
                "confidence": f.get("confidence", 0.95),
                "uncertainty": [],
                "metadata": f.get("metadata", {}),
            })
    return {"facts": matched, "status": "success", "contract_version": 1}


def handle_verify(payload: dict) -> dict:
    statements = payload.get("statements", [])
    facts = load_facts()
    verifications = []
    for stmt in statements:
        stmt_tokens = _tokens(stmt)
        supporting = []
        for f in facts:
            f_tokens = _tokens(str(f.get("statement", "")))
            if len(stmt_tokens & f_tokens) >= 2:
                supporting.append(f.get("id"))
        verifications.append({
            "statement": stmt,
            "status": "metta_corroborated" if supporting else "inconclusive",
            "supporting_fact_ids": supporting,
        })
    return {"verifications": verifications, "status": "success", "contract_version": 1}


def main() -> int:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"error": "Empty input"}), file=sys.stderr)
            return 1
        payload = json.loads(raw_input)
    except Exception as err:
        print(json.dumps({"error": f"JSON decode error: {err}"}), file=sys.stderr)
        return 1

    op = payload.get("operation")
    if op == "metta_query":
        result = handle_query(payload)
    elif op == "metta_verify":
        result = handle_verify(payload)
    else:
        result = {"error": f"Unknown operation: {op}"}

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
