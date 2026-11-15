#!/usr/bin/env python3
"""Neural runner for UCA integrating the trained MiniTransformer.

Adheres to UCA JSON contracts:
- operation: 'masked_denoise' (for nanoDiff / denoiser specialist)
- operation: 'concept_generation' (for NCM concept generation)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import numpy as np

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from training.dataset import SimpleTokenizer
from training.model import MiniTransformer, softmax


CHECKPOINT_PATH = root_dir / "models" / "checkpoints" / "uca_transformer.npz"
TOKENIZER_PATH = root_dir / "models" / "checkpoints" / "tokenizer.json"

_MODEL: MiniTransformer | None = None
_TOKENIZER: SimpleTokenizer | None = None


def get_model_and_tokenizer() -> tuple[MiniTransformer, SimpleTokenizer]:
    global _MODEL, _TOKENIZER
    if _MODEL is None or _TOKENIZER is None:
        _TOKENIZER = SimpleTokenizer.load(TOKENIZER_PATH)
        _MODEL = MiniTransformer.load_checkpoint(CHECKPOINT_PATH)
    return _MODEL, _TOKENIZER


def handle_masked_denoise(payload: dict) -> dict:
    model, tokenizer = get_model_and_tokenizer()
    masked_ids = payload.get("masked_token_ids", [])
    positions = payload.get("mask_positions", [])

    if not masked_ids:
        return {"error": "Empty masked_token_ids"}

    # Pad or truncate to max_seq_len
    max_len = model.max_seq_len
    orig_len = len(masked_ids)
    arr = list(masked_ids)[:max_len]
    if len(arr) < max_len:
        arr += [tokenizer.pad_id] * (max_len - len(arr))

    x = np.array([arr], dtype=np.int32)
    logits = model.forward(x)  # (1, T, V)
    probs = softmax(logits, axis=-1)[0]  # (T, V)

    candidate_ids = list(masked_ids)
    total_score = 0.0
    for pos in positions:
        if pos < max_len:
            best_id = int(np.argmax(probs[pos]))
            total_score += float(probs[pos, best_id])
            candidate_ids[pos] = best_id

    mean_score = total_score / max(1, len(positions))
    return {
        "candidate_token_ids": candidate_ids[:orig_len],
        "candidate_score": round(mean_score, 4),
        "calibration_id": "uca_neural_denoiser_trained_v1",
        "status": "success",
    }


def handle_concept_generation(payload: dict) -> dict:
    model, tokenizer = get_model_and_tokenizer()
    query = str(payload.get("query", ""))

    encoded = tokenizer.encode(query, max_length=model.max_seq_len, add_special_tokens=True)
    x = np.array([encoded], dtype=np.int32)
    logits = model.forward(x)
    probs = softmax(logits, axis=-1)[0]  # (T, V)

    # Decode high probability tokens
    proposals = []
    top_indices = np.argsort(np.max(probs, axis=-1))[::-1][:4]
    generated_concepts = []
    for idx in top_indices:
        token_id = int(np.argmax(probs[idx]))
        if token_id not in (tokenizer.pad_id, tokenizer.token2id[tokenizer.BOS_TOKEN], tokenizer.token2id[tokenizer.EOS_TOKEN]):
            token = tokenizer.id2token[token_id]
            if len(token) > 2 and token not in generated_concepts:
                generated_concepts.append(token)

    if generated_concepts:
        concept_phrase = "Association neuronale : " + ", ".join(generated_concepts)
        proposals.append({
            "text": concept_phrase,
            "metadata": {
                "source": "trained_uca_minitransformer",
                "concepts": generated_concepts,
                "confidence_proxy": 0.85,
            }
        })

    return {"proposals": proposals, "status": "success"}


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
    if op == "masked_denoise":
        result = handle_masked_denoise(payload)
    elif op == "concept_generation":
        result = handle_concept_generation(payload)
    else:
        result = {"error": f"Unknown operation: {op}"}

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
