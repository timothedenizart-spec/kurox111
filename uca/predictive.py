"""Local surprisal monitor: Shannon information over the installed corpus only.

Predictive-coding theories describe the brain as minimising prediction error;
UCA borrows the *signal*, not the claim. An adaptive bigram model trained on
the local evidence (documents + symbolic fact statements) assigns every token
a surprisal  s(w) = -log2 P(w | previous).  Generated analysis whose surprisal
far exceeds the corpus background is *novel relative to local evidence*: it is
queued for verification, never judged false. An empty corpus means no model,
hence an honest unconclusive report instead of fabricated expectations.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Iterable

_WORD = re.compile(r"[\wÀ-ÿ'-]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in _WORD.findall(text)]


class LocalSurprisalModel:
    """Bigram model with additive smoothing; fully deterministic."""

    def __init__(self, alpha: float = 0.1) -> None:
        self.alpha = alpha
        self.unigrams: Counter[str] = Counter()
        self.bigrams: Counter[tuple[str, str]] = Counter()
        self.trained_tokens = 0

    def train(self, texts: Iterable[str]) -> int:
        before = self.trained_tokens
        for text in texts:
            tokens = ["<s>"] + _tokens(text) + ["</s>"]
            for index, token in enumerate(tokens):
                self.unigrams[token] += 1
                self.trained_tokens += 1
                if index:
                    self.bigrams[(tokens[index - 1], token)] += 1
        return self.trained_tokens - before

    @property
    def is_trained(self) -> bool:
        return self.trained_tokens > 0

    def token_surprisal(self, previous: str, token: str) -> float:
        vocab = max(1, len(self.unigrams))
        count = self.bigrams.get((previous, token), 0) + self.alpha
        context_total = self.unigrams.get(previous, 0) + self.alpha * vocab
        return -math.log2(count / context_total)

    def sentence_profile(self, text: str) -> dict[str, Any]:
        tokens = ["<s>"] + _tokens(text)
        if len(tokens) < 2:
            return {"mean_surprisal": None, "max_surprisal": None, "surprising_tokens": []}
        values = [(tokens[i - 1], token, self.token_surprisal(tokens[i - 1], token))
                  for i, token in enumerate(tokens) if i]
        mean = sum(item[2] for item in values) / len(values)
        ranked = sorted(values, key=lambda item: (-item[2], item[1]))
        return {"mean_surprisal": round(mean, 4),
                "max_surprisal": round(values and max(v[2] for v in values) or 0.0, 4),
                "surprising_tokens": [{"token": token, "surprisal": round(value, 4)}
                                      for _, token, value in ranked[:6] if token != "</s>"][:6]}


def corpus_background(model: LocalSurprisalModel, texts: list[str]) -> dict[str, float]:
    """Mean surprisal of the very corpus used for training — the baseline to
    which generated text is compared. Also a model sanity signal."""
    profiles = [model.sentence_profile(text) for text in texts]
    means = [p["mean_surprisal"] for p in profiles if p["mean_surprisal"] is not None]
    if not means:
        return {"background_mean": None}
    return {"background_mean": round(sum(means) / len(means), 4)}


def novelty_report(model: LocalSurprisalModel, text: str, *,
                   background_mean: float | None, factor: float = 1.6) -> dict[str, Any]:
    """Flag text whose mean surprisal exceeds `factor` × corpus background.

    The flag means 'requires verification against evidence'; it is deliberately
    symmetrical with the grounding-gap register and never a falsity verdict.
    """
    profile = model.sentence_profile(text)
    if profile["mean_surprisal"] is None or background_mean is None:
        return {"flagged": False, "reason": "inconclusive", **profile}
    flagged = profile["mean_surprisal"] >= factor * background_mean
    return {"flagged": flagged,
            "reason": ("mean surprisal far above local corpus background"
                       if flagged else "within local corpus surprise range"),
            "background_mean": background_mean,
            **profile}
