#!/usr/bin/env python3
"""Validate UCA supervised-training JSONL without loading ML packages."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SPLITS = {"train", "validation", "test"}
ROLES = {"system", "user", "assistant"}
UNKNOWN_LICENSES = {"unknown", "inconnue", "n/a", "na", "none", ""}


def canonical_conversation(messages: list[dict[str, str]]) -> str:
    normalized = [{"role": item["role"], "content": " ".join(item["content"].split())}
                  for item in messages]
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).casefold()


def validate(path: Path, require_all_splits: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    counts = {split: 0 for split in sorted(SPLITS)}
    ids: dict[str, int] = {}
    contents: dict[str, tuple[int, str]] = {}
    try:
        handle = path.open(encoding="utf-8")
    except OSError as exc:
        return {"valid": False, "errors": [f"Cannot read dataset: {exc}"], "warnings": warnings, "counts": counts}

    with handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(item, dict):
                errors.append(f"line {line_number}: expected a JSON object")
                continue
            identifier = item.get("id")
            if not isinstance(identifier, str) or not identifier.strip():
                errors.append(f"line {line_number}: 'id' must be a non-empty string")
            elif identifier in ids:
                errors.append(f"line {line_number}: duplicate id {identifier!r} (first at line {ids[identifier]})")
            else:
                ids[identifier] = line_number

            split = item.get("split")
            if split not in SPLITS:
                errors.append(f"line {line_number}: split must be one of {sorted(SPLITS)}")
            else:
                counts[split] += 1
            for field in ("source", "license"):
                value = item.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"line {line_number}: '{field}' must be a non-empty string")
                elif field == "license" and value.strip().casefold() in UNKNOWN_LICENSES:
                    errors.append(f"line {line_number}: license must be identified; unknown rights cannot enter training")

            messages = item.get("messages")
            valid_messages = isinstance(messages, list) and bool(messages)
            if not valid_messages:
                errors.append(f"line {line_number}: 'messages' must be a non-empty list")
                continue
            clean: list[dict[str, str]] = []
            seen_user = False
            seen_assistant = False
            last_role: str | None = None
            for index, message in enumerate(messages):
                if not isinstance(message, dict):
                    errors.append(f"line {line_number}: message {index} must be an object")
                    continue
                role, content = message.get("role"), message.get("content")
                if role not in ROLES:
                    errors.append(f"line {line_number}: message {index} has unsupported role {role!r}")
                    continue
                if not isinstance(content, str) or not content.strip():
                    errors.append(f"line {line_number}: message {index} content must be non-empty text")
                    continue
                if role == "user":
                    seen_user = True
                if role == "assistant":
                    seen_assistant = True
                if role == "system" and index != 0:
                    errors.append(f"line {line_number}: system message is allowed only at the beginning")
                if role == last_role and role != "system":
                    errors.append(f"line {line_number}: adjacent {role} messages are not supported by this v1 schema")
                last_role = role
                clean.append({"role": role, "content": content})
            if clean and (not seen_user or not seen_assistant or clean[-1]["role"] != "assistant"):
                errors.append(f"line {line_number}: require a user message and a final assistant answer")
            if clean and split in SPLITS:
                digest = hashlib.sha256(canonical_conversation(clean).encode("utf-8")).hexdigest()
                previous = contents.get(digest)
                if previous:
                    errors.append(f"line {line_number}: exact conversation duplicate across/within splits; first at line {previous[0]} ({previous[1]})")
                else:
                    contents[digest] = (line_number, str(split))

    if not any(counts.values()):
        errors.append("dataset has no examples")
    if require_all_splits:
        missing = sorted(split for split, count in counts.items() if count == 0)
        if missing:
            errors.append(f"empty required split(s): {', '.join(missing)}")
    warnings.append("Schema checks cannot verify truth, licensing, personal data, paraphrase leakage or instructional quality; human review is required.")
    return {"valid": not errors, "example_count": sum(counts.values()), "counts": counts,
            "errors": errors, "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--allow-empty-splits", action="store_true",
                        help="Do not require train, validation and test to all have examples")
    args = parser.parse_args(argv)
    report = validate(args.dataset, require_all_splits=not args.allow_empty_splits)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
