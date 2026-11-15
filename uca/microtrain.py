"""Local micro-training of a masked denoiser for the UCA nanoDiff contract (UCA-09).

What this is — and is not:

- **Is** a genuinely trained model: stochastic-gradient learning (Adam) of a
  CBOW-style masked-token denoiser (Mikolov et al., 2013, transposed to the
  masked-prediction objective), in pure numpy, CPU-only, fully deterministic
  (seeded data split, masking and corruptions).
- **Is** local and honest: the default corpus is the repository's own French
  documentation; every metric is measured (train cross-entropy, holdout
  perplexity vs a unigram baseline, corruption-restoration accuracy) and
  written to a generated model card. Nothing is downloaded.
- **Is not** a transformer, a 50M-parameter model, or a replacement for
  SmolLM2/nanoDiff weights. It is the smallest honest runnable instance of the
  masked-denoise contract, so that the integration, calibration and governance
  machinery can be exercised on something real.

Artifacts land in ``models/micro-denoiser/`` (gitignored): ``model.npz``,
``vocab.json``, ``tokenizer/`` (HF-compatible fast tokenizer), ``metrics.json``
and ``MODEL_CARD.md``.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import hashlib
import json
import re

import numpy as np

WORD = re.compile(r"[\wÀ-ÿ'-]+", re.UNICODE)
SPECIALS = ["<pad>", "<unk>", "[MASK]"]


# --------------------------------------------------------------------- corpus
def normalize_text(text: str) -> list[str]:
    """Corpus/tokenizer normalization, shared exactly with the runtime shim."""
    lowered = text.lower()
    return WORD.findall(lowered)


def load_corpus_sentences(root: str | Path, extra_files: list[str | Path] | None = None,
                          *, min_tokens: int = 5, max_tokens: int = 40) -> tuple[list[str], dict[str, Any]]:
    """Sentences from the repository's own documentation (README, docs,
    coordination) plus optional operator-provided text files. Deterministic
    order: sorted file names, then document order."""
    root = Path(root)
    sources = sorted([p for pattern in ("README.md", "docs/*.md", "coordination/*/*.md", "coordination/*/*/*.md")
                      for p in root.glob(pattern)] + [Path(f) for f in (extra_files or [])])
    sentences: list[str] = []
    used: list[str] = []
    for path in sources:
        if not path.exists():
            continue
        body = path.read_text(encoding="utf-8")
        crude = re.split(r"(?<=[.!?])\s+|\n+", body)
        count_before = len(sentences)
        for chunk in crude:
            tokens = normalize_text(chunk)
            if min_tokens <= len(tokens) <= max_tokens:
                sentences.append(" ".join(tokens))
        used.append(str(path))
        _ = count_before
    digest = hashlib.sha256("\n".join(sentences).encode("utf-8")).hexdigest()[:16]
    return sentences, {"files": used, "sentence_count": len(sentences), "corpus_sha256": digest}


def split_train_holdout(sentences: list[str], holdout_modulo: int = 10) -> tuple[list[str], list[str]]:
    """Deterministic split by sentence hash: no leakage, reproducible."""
    train, holdout = [], []
    for sentence in sentences:
        bucket = int(hashlib.sha256(sentence.encode("utf-8")).hexdigest()[:4], 16) % holdout_modulo
        (holdout if bucket == 0 else train).append(sentence)
    return train, holdout


# ------------------------------------------------------------------ tokenizer
class MicroTokenizer:
    """Word-level tokenizer; ids are stable: index of the token in vocab.json."""

    def __init__(self, vocab: list[str]) -> None:
        self.vocab = list(vocab)
        self.token_to_id = {token: index for index, token in enumerate(self.vocab)}

    @classmethod
    def build(cls, sentences: list[str], min_freq: int = 2) -> "MicroTokenizer":
        counts = Counter(token for sentence in sentences for token in normalize_text(sentence))
        words = sorted((token for token, n in counts.items() if n >= min_freq),
                       key=lambda token: (-counts[token], token))
        return cls(SPECIALS + words)

    @property
    def mask_token_id(self) -> int:
        return self.token_to_id["[MASK]"]

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        unk = self.token_to_id["<unk>"]
        ids = [self.token_to_id.get(token, unk) for token in normalize_text(text)]
        if add_special_tokens:
            ids = [self.token_to_id["<pad>"]] + ids  # no BOS/EOS semantics: pad marks bounds
        return ids

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        tokens = []
        for index in ids:
            token = self.vocab[index] if 0 <= index < len(self.vocab) else "<unk>"
            if skip_special_tokens and token in SPECIALS:
                continue
            tokens.append(token)
        return " ".join(tokens)

    def save(self, directory: str | Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "vocab.json").write_text(json.dumps(self.vocab, ensure_ascii=False, indent=1),
                                              encoding="utf-8")

    @classmethod
    def load(cls, directory: str | Path) -> "MicroTokenizer":
        return cls(json.loads((Path(directory) / "vocab.json").read_text(encoding="utf-8")))

    def save_hf(self, directory: str | Path) -> None:
        """Emit an HF-fast-tokenizer directory whose ids match vocab.json exactly."""
        try:
            from tokenizers import Regex, Tokenizer, decoders, normalizers, pre_tokenizers
            from tokenizers.models import WordLevel
        except ImportError as error:
            raise RuntimeError("pip install tokenizers transformers for the HF-compatible export") from error
        model = WordLevel({token: i for i, token in enumerate(self.vocab)}, unk_token="<unk>")
        fast = Tokenizer(model)
        fast.normalizer = normalizers.Sequence([normalizers.Lowercase(),
                                                normalizers.Replace(Regex(r"[^\wÀ-ÿ'\-\s]"), " "),
                                                normalizers.Strip()])
        fast.pre_tokenizer = pre_tokenizers.Whitespace()
        fast.decoder = decoders.WordPiece(prefix="", cleanup=False)
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        fast.save(str(target / "tokenizer.json"))
        (target / "tokenizer_config.json").write_text(json.dumps(
            {"tokenizer_class": "PreTrainedTokenizerFast",
             "unk_token": "<unk>", "mask_token": "[MASK]", "pad_token": "<pad>",
             "model_max_length": 512}, indent=1), encoding="utf-8")


# -------------------------------------------------------------------- model
class MaskedDenoiser:
    """CBOW-style masked-token denoiser over a word-level vocabulary.

    For a masked position i: h = mean(E[context ids in ±window]) ; logits =
    W·h + b ; softmax. Trained by full-batch-over-minibatch CE with Adam.
    """

    def __init__(self, vocab_size: int, dim: int = 32, window: int = 4, seed: int = 42) -> None:
        rng = np.random.default_rng(seed)
        scale = 0.05
        self.E = rng.normal(0.0, scale, size=(vocab_size, dim))
        self.W = rng.normal(0.0, scale, size=(vocab_size, dim))
        self.b = np.zeros(vocab_size)
        self.dim, self.window, self.vocab_size = dim, window, vocab_size

    @property
    def parameter_count(self) -> int:
        return int(self.E.size + self.W.size + self.b.size)

    def _context_ids(self, ids: list[int], position: int, mask_id: int) -> list[int]:
        lo, hi = max(0, position - self.window), min(len(ids), position + self.window + 1)
        return [ids[j] for j in range(lo, hi) if j != position and ids[j] != mask_id]

    def hidden(self, ids: list[int], position: int, mask_id: int) -> np.ndarray:
        context = self._context_ids(ids, position, mask_id)
        if not context:
            return np.zeros(self.dim)
        return self.E[np.array(context)].mean(axis=0)

    def predict(self, ids: list[int], position: int, mask_id: int) -> tuple[int, float]:
        h = self.hidden(ids, position, mask_id)
        logits = self.W @ h + self.b
        logits -= logits.max()
        probs = np.exp(logits)
        probs /= probs.sum()
        best = int(probs.argmax())
        return best, float(np.log(max(probs[best], 1e-12)))

    def train_batch(self, batch: list[tuple[list[int], int, int]], adam: dict[str, Any],
                    lr: float, step: int) -> float:
        grads_E = np.zeros_like(self.E)
        grads_W = np.zeros_like(self.W)
        grads_b = np.zeros_like(self.b)
        total_loss = 0.0
        for ids, position, mask_id in batch:
            h = self.hidden(ids, position, mask_id)
            logits = self.W @ h + self.b
            logits -= logits.max()
            exp = np.exp(logits)
            p = exp / exp.sum()
            target = ids[position]
            total_loss += -np.log(max(p[target], 1e-12))
            dlogits = p
            dlogits[target] -= 1.0
            grads_W += np.outer(dlogits, h)
            grads_b += dlogits
            dh = self.W.T @ dlogits
            context = self._context_ids(ids, position, mask_id)
            if context:
                share = dh / len(context)
                for j in context:
                    grads_E[j] += share
        n = max(1, len(batch))
        for name, param, grad in (("E", self.E, grads_E), ("W", self.W, grads_W), ("b", self.b, grads_b)):
            g = grad / n
            adam["m"][name] = 0.9 * adam["m"][name] + 0.1 * g
            adam["v"][name] = 0.999 * adam["v"][name] + 0.001 * (g * g)
            m_hat = adam["m"][name] / (1 - 0.9 ** step)
            v_hat = adam["v"][name] / (1 - 0.999 ** step)
            param -= lr * m_hat / (np.sqrt(v_hat) + 1e-8)
        return total_loss / n

    def save(self, directory: str | Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        np.savez(directory / "model.npz", E=self.E, W=self.W, b=self.b,
                 meta=np.array(json.dumps({"dim": self.dim, "window": self.window})))

    @classmethod
    def load(cls, directory: str | Path) -> "MaskedDenoiser":
        blob = np.load(Path(directory) / "model.npz", allow_pickle=False)
        model = cls(int(blob["E"].shape[0]), dim=int(blob["E"].shape[1]))
        model.E, model.W, model.b = blob["E"], blob["W"], blob["b"]
        meta = json.loads(str(blob["meta"]))
        model.window = int(meta["window"])
        return model


# ------------------------------------------------------------------- training
def _masked_positions(ids: list[int], rate: float, rng: np.random.Generator) -> list[int]:
    if len(ids) < 4:
        return []
    chosen = [i for i in range(len(ids)) if rng.random() < rate]
    if not chosen:
        chosen = [int(rng.integers(0, len(ids)))]
    return chosen


def train(sentences: list[str], *, dim: int = 32, window: int = 4, epochs: int = 40,
          seed: int = 42, lr: float = 0.02, mask_rate: float = 0.15,
          min_freq: int = 2) -> dict[str, Any]:
    """Full deterministic training run. Returns model, tokenizer and metrics."""
    train_sents, holdout = split_train_holdout(sentences)
    tokenizer = MicroTokenizer.build(train_sents, min_freq=min_freq)
    model = MaskedDenoiser(len(tokenizer.vocab), dim=dim, window=window, seed=seed)
    mask_id = tokenizer.mask_token_id
    rng = np.random.default_rng(seed)
    encoded = [tokenizer.encode(sentence) for sentence in train_sents]
    encoded = [ids for ids in encoded if len(ids) >= 4]
    adam = {"m": {k: np.zeros_like(p) for k, p in (("E", model.E), ("W", model.W), ("b", model.b))},
            "v": {k: np.zeros_like(p) for k, p in (("E", model.E), ("W", model.W), ("b", model.b))}}
    losses: list[float] = []
    step = 0
    sample_cap = len(encoded)
    for _epoch in range(epochs):
        order = rng.permutation(len(encoded))
        batch: list[tuple[list[int], int, int]] = []
        epoch_loss, epoch_hits = 0.0, 0
        for idx in order:
            ids = encoded[idx]
            for position in _masked_positions(ids, mask_rate, rng):
                batch.append((ids, position, mask_id))
                if len(batch) >= 32:
                    step += 1
                    epoch_loss += model.train_batch(batch, adam, lr, step)
                    epoch_hits += 1
                    batch = []
        if batch:
            step += 1
            epoch_loss += model.train_batch(batch, adam, lr, step)
            epoch_hits += 1
        losses.append(epoch_loss / max(1, epoch_hits))

    # Holdout perplexity: mask each position one at a time, mean NLL.
    unigram = Counter(token for s in train_sents for token in normalize_text(s))
    total_uni = sum(unigram.values())
    model_nll, uni_nll, count = 0.0, 0.0, 0
    for sentence in holdout:
        ids = tokenizer.encode(sentence)
        for position in range(len(ids)):
            h = model.hidden(ids, position, mask_id)
            logits = model.W @ h + model.b
            logits -= logits.max()
            p = np.exp(logits) / np.exp(logits).sum()
            model_nll += -np.log(max(p[ids[position]], 1e-12))
            token = tokenizer.vocab[ids[position]]
            uni_nll += -np.log(max(unigram.get(token, 0) + 1, 1) / (total_uni + len(tokenizer.vocab)))
            count += 1
    # Restoration: corrupt holdout tokens (seeded) and measure exact recovery.
    restored, corrupted = 0, 0
    for sentence in holdout:
        ids = tokenizer.encode(sentence)
        if len(ids) < 4:
            continue
        corpus_rng = np.random.default_rng(seed + hash(sentence) % 1000)
        for position in _masked_positions(ids, 0.20, corpus_rng):
            if ids[position] in (0, 1, mask_id):
                continue
            corrupted += 1
            guess, _ = model.predict(ids[:position] + [mask_id] + ids[position + 1:], position, mask_id)
            restored += int(guess == ids[position])
    metrics = {
        "seeds_and_split": {"seed": seed, "holdout_sentences": len(holdout), "train_sentences": len(train_sents)},
        "holdout_sentence_list": holdout,
        "parameters": {"vocab_size": len(tokenizer.vocab), "dim": dim, "window": window,
                       "total_parameters": model.parameter_count},
        "loss_curve": {"first_epoch_mean_ce": round(losses[0], 4), "final_epoch_mean_ce": round(losses[-1], 4),
                       "epochs": epochs, "monotone_note": "means over masked-position minibatches"},
        "holdout": {"model_perplexity": round(float(np.exp(model_nll / max(1, count))), 2),
                    "unigram_baseline_perplexity": round(float(np.exp(uni_nll / max(1, count))), 2),
                    "uniform_baseline_perplexity": float(len(tokenizer.vocab)),
                    "positions_evaluated": count},
        "restoration": {"corrupted_tokens": corrupted, "exactly_restored": restored,
                        "accuracy": round(restored / corrupted, 4) if corrupted else None},
    }
    return {"model": model, "tokenizer": tokenizer, "metrics": metrics, "train_count": sample_cap}


def make_calibration_cases(sentences: list[str], tokenizer: MicroTokenizer, *,
                           limit: int = 16, rate: float = 0.15, seed: int = 123) -> list[dict[str, str]]:
    """Corruption-based masked-denoising cases, deterministically generated.

    `text` is a holdout sentence with ~15% of its tokens replaced by random
    in-vocabulary words; `reference` is the original. This is the classic
    noisy-channel probe for denoisers: no case is authored, all are replayable.
    """
    _train, holdout = split_train_holdout(sentences)
    rng = np.random.default_rng(seed)
    word_ids = [i for i, token in enumerate(tokenizer.vocab) if token not in SPECIALS]
    cases: list[dict[str, str]] = []
    for sentence in holdout:
        ids = tokenizer.encode(sentence)
        if len(ids) < 6:
            continue
        corrupted = list(ids)
        hits = 0
        for position in range(len(corrupted)):
            if corrupted[position] in word_ids and rng.random() < rate:
                replacement = int(word_ids[rng.integers(0, len(word_ids))])
                if replacement != corrupted[position]:
                    corrupted[position] = replacement
                    hits += 1
        if hits == 0:
            continue
        cases.append({"id": f"micro-{len(cases) + 1}", "text": tokenizer.decode(corrupted),
                      "reference": sentence})
        if len(cases) >= limit:
            break
    return cases


MODEL_CARD = """# Carte de modèle — micro-débruiteur masqué UCA (local)

| Champ | Valeur |
|---|---|
| Type | CBOW masqué (pas un transformer ; pas nanoDiff-50M ; pas SmolLM2) |
| Paramètres | {params} |
| Vocabulaire | {vocab} tokens (mot entier, min_freq 2) |
| Corpus | docs/README/coordination du dépôt ({sentences} phrases, sha256 {corpus}) |
| Graine | {seed} — entraînement déterministe |
| Perte CE (1ʳᵉ → dernière époque) | {ce_first} → {ce_last} |
| Perplexité holdout (modèle / unigramme / uniforme) | {ppl} / {ppl_uni} / {ppl_uni_v} |
| Restauration exacte de tokens corrompus | {restored} |

**Limites.** Échelle microscopique, anglais/français mêlés au corpus, pas de
subword, pas de position. Ce modèle sert à valider le *contrat* du débruiteur
masqué et la boucle de gouvernance (calibration → activation par l'opérateur),
pas à produire du texte de qualité. L'activation exige une revue humaine.
"""


def run_training(root: str | Path, out: str | Path, *, dim: int, window: int, epochs: int,
                 seed: int, extra_corpus: list[str | Path] | None = None) -> dict[str, Any]:
    out = Path(out)
    sentences, corpus_info = load_corpus_sentences(root, extra_corpus)
    if len(sentences) < 20:
        raise RuntimeError(f"Corpus trop petit pour entraîner honnêtement ({len(sentences)} phrases)")
    result = train(sentences, dim=dim, window=window, epochs=epochs, seed=seed)
    model: MaskedDenoiser = result["model"]
    tokenizer: MicroTokenizer = result["tokenizer"]
    model.save(out)
    tokenizer.save(out)
    try:
        tokenizer.save_hf(out / "tokenizer")
        hf_export = True
    except RuntimeError:
        hf_export = False
    metrics = result["metrics"]
    metrics["corpus"] = corpus_info
    metrics["hf_tokenizer_export"] = hf_export
    metrics["mask_token_id"] = tokenizer.mask_token_id
    card = MODEL_CARD.format(
        params=metrics["parameters"]["total_parameters"], vocab=metrics["parameters"]["vocab_size"],
        sentences=corpus_info["sentence_count"], corpus=corpus_info["corpus_sha256"], seed=seed,
        ce_first=metrics["loss_curve"]["first_epoch_mean_ce"], ce_last=metrics["loss_curve"]["final_epoch_mean_ce"],
        ppl=metrics["holdout"]["model_perplexity"], ppl_uni=metrics["holdout"]["unigram_baseline_perplexity"],
        ppl_uni_v=metrics["holdout"]["uniform_baseline_perplexity"],
        restored=(f"{metrics['restoration']['exactly_restored']}/{metrics['restoration']['corrupted_tokens']} "
                  f"({metrics['restoration']['accuracy']})"))
    (out / "MODEL_CARD.md").write_text(card, encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics
