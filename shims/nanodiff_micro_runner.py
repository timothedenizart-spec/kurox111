#!/usr/bin/env python3
"""Contract runner for the locally trained micro masked-denoiser (UCA-09).

Implements the exact JSON-on-stdin / JSON-on-stdout contract documented in
docs/INTEGRATION.md for nanoDiff:

    in : {"operation":"masked_denoise","architecture":"nanodiff_masked_denoiser",
          "strategy":...,"token_ids":[...],"masked_token_ids":[...],
          "mask_positions":[...],"mask_token_id":123,"contract_version":1}
    out: {"candidate_token_ids":[...],"candidate_score":0.0,"calibration_id":"..."}

Each masked position is filled with the model's argmax prediction given its
local context window. ``candidate_score`` is the mean log-probability of the
predictions (a raw model score, not a quality proof). Usage:

    python3 shims/nanodiff_micro_runner.py models/micro-denoiser
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys


def main() -> int:
    model_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "models/micro-denoiser")
    payload = json.load(sys.stdin)
    if payload.get("operation") != "masked_denoise":
        print(json.dumps({"error": "unsupported operation"}, ensure_ascii=False))
        return 0
    import os
    for candidate in (Path(__file__).resolve().parent.parent, Path(os.getcwd())):
        if (candidate / "uca").is_dir():
            sys.path.insert(0, str(candidate))
            break
    from uca.microtrain import MaskedDenoiser, MicroTokenizer

    model = MaskedDenoiser.load(model_dir)
    tokenizer = MicroTokenizer.load(model_dir)
    mask_id = int(payload.get("mask_token_id", tokenizer.mask_token_id))
    original = [int(value) for value in payload["token_ids"]]
    candidate = [int(value) for value in payload["masked_token_ids"]]
    logprobs: list[float] = []
    for position in payload.get("mask_positions", []):
        position = int(position)
        if not (0 <= position < len(candidate)):
            continue
        guess, logprob = model.predict(candidate, position, mask_id)
        candidate[position] = guess
        logprobs.append(logprob)
    score = sum(logprobs) / len(logprobs) if logprobs else 0.0
    calibration = hashlib.sha256(json.dumps([original, candidate]).encode()).hexdigest()[:16]
    print(json.dumps({"candidate_token_ids": candidate,
                      "candidate_score": round(score, 6),
                      "calibration_id": calibration}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
