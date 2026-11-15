"""Dataset preparation and tokenizer for training UCA's neural transformer/denoiser."""
from __future__ import annotations

import json
import random
import re
from pathlib import Path


RAW_TRAINING_CORPUS = [
    "le routage thalamo-cortical synchronise les aires cerebrales dans le cerveau humain.",
    "le thalamus regule les etats attentionnels et transmet les signaux au cortex.",
    "l espace de travail neuronal global diffuse l information consciente aux modules cognitifs.",
    "l inference active et le principe de l energie libre minimisent l erreur de prediction.",
    "le cerveau calcule des erreurs de prediction entre modeles descendants et signaux sensoriels.",
    "le calcul hyperdimensionnel utilise des hypervecteurs orthogonaux en dimension elevee.",
    "la liaison vsa associe un role et une entite par produit de hadamard.",
    "la superposition vsa combine plusieurs concepts en memoire holographique sans augmenter la taille.",
    "le corps des nombres rationnels q permet des calculs arithmetiques exacts sans approximation.",
    "une equation lineaire a fois x plus b egale c admet pour solution x egale c moins b divise par a.",
    "la logique propositionnelle de horn permet une deduction formelle exacte par chainage avant.",
    "les clauses de horn garantissent une deduction automatique en temps polynomial strict.",
    "une tautologie est une formule propositionnelle toujours vraie quel que soit le modele.",
    "la causalite structurelle de judea pearl distingue correlation et intervention active.",
    "l operateur do supprime les causes entrantes pour bloquer les chemins de confusion.",
    "la bretagne est une region historique situee a l ouest de la france.",
    "rennes est la capitale administrative de la region bretagne.",
    "paris est la capitale politique de la france.",
    "la memoire de travail bornee alloue une capacite stricte aux preuves les plus pertinentes.",
    "le critere mdl d occam penalise les hypotheses inutilement complexes et sans preuve.",
    "la decomposition en facteurs premiers factorise un entier de maniere unique.",
    "l algorithme d euclide calcule le plus grand commun diviseur pgcd de deux entiers.",
    "la verification locale controle la coherence sans presumer qu absence vaut negation.",
    "les propositions generees par un modele neuronal restent distinctes des faits symboliques averes.",
]


class SimpleTokenizer:
    """Word and sub-token tokenizer with special tokens."""

    PAD_TOKEN = "[PAD]"
    UNK_TOKEN = "[UNK]"
    MASK_TOKEN = "[MASK]"
    BOS_TOKEN = "[BOS]"
    EOS_TOKEN = "[EOS]"

    def __init__(self, vocab: list[str] | None = None) -> None:
        self.special_tokens = [self.PAD_TOKEN, self.UNK_TOKEN, self.MASK_TOKEN, self.BOS_TOKEN, self.EOS_TOKEN]
        if vocab is not None:
            self.id2token = list(vocab)
            self.token2id = {token: i for i, token in enumerate(self.id2token)}
        else:
            self.id2token = list(self.special_tokens)
            self.token2id = {token: i for i, token in enumerate(self.special_tokens)}

    @property
    def pad_id(self) -> int:
        return self.token2id[self.PAD_TOKEN]

    @property
    def unk_id(self) -> int:
        return self.token2id[self.UNK_TOKEN]

    @property
    def mask_id(self) -> int:
        return self.token2id[self.MASK_TOKEN]

    @property
    def vocab_size(self) -> int:
        return len(self.id2token)

    @staticmethod
    def tokenize_text(text: str) -> list[str]:
        # Normalize and split into words/symbols
        normalized = text.lower().replace("-", " ").replace("'", " ")
        return [w for w in re.findall(r"[\w]+|[^\s\w]", normalized) if w.strip()]

    def fit(self, texts: list[str]) -> None:
        word_counts: dict[str, int] = {}
        for text in texts:
            for w in self.tokenize_text(text):
                word_counts[w] = word_counts.get(w, 0) + 1
        sorted_words = sorted(word_counts.keys())
        for w in sorted_words:
            if w not in self.token2id:
                self.token2id[w] = len(self.id2token)
                self.id2token.append(w)

    def encode(self, text: str, max_length: int = 48, add_special_tokens: bool = True) -> list[int]:
        words = self.tokenize_text(text)
        ids = [self.token2id.get(w, self.unk_id) for w in words]
        if add_special_tokens:
            ids = [self.token2id[self.BOS_TOKEN]] + ids + [self.token2id[self.EOS_TOKEN]]
        if len(ids) > max_length:
            ids = ids[:max_length]
        else:
            ids = ids + [self.pad_id] * (max_length - len(ids))
        return ids

    def decode(self, token_ids: list[int]) -> str:
        words = []
        for tid in token_ids:
            if 0 <= tid < len(self.id2token):
                token = self.id2token[tid]
                if token in (self.PAD_TOKEN, self.BOS_TOKEN, self.EOS_TOKEN):
                    continue
                words.append(token)
        return " ".join(words)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps({"vocab": self.id2token}, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "SimpleTokenizer":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(vocab=data["vocab"])


def create_training_samples(
    corpus: list[str],
    tokenizer: SimpleTokenizer,
    max_length: int = 40,
    mask_prob: float = 0.20,
    samples_per_sentence: int = 6,
    seed: int = 42,
) -> tuple[list[list[int]], list[list[int]], list[list[int]]]:
    """Generates (inputs_with_masks, targets, mask_indicators)."""
    random.seed(seed)
    all_inputs: list[list[int]] = []
    all_targets: list[list[int]] = []
    all_mask_indices: list[list[int]] = []

    for text in corpus:
        tokens = tokenizer.encode(text, max_length=max_length, add_special_tokens=True)
        # Identify content token positions (excluding PAD, BOS, EOS)
        content_positions = [
            i for i, tid in enumerate(tokens)
            if tid not in (tokenizer.pad_id, tokenizer.token2id[tokenizer.BOS_TOKEN], tokenizer.token2id[tokenizer.EOS_TOKEN])
        ]
        if not content_positions:
            continue

        for _ in range(samples_per_sentence):
            masked_tokens = list(tokens)
            num_to_mask = max(1, int(len(content_positions) * mask_prob))
            chosen_pos = random.sample(content_positions, min(num_to_mask, len(content_positions)))
            for pos in chosen_pos:
                masked_tokens[pos] = tokenizer.mask_id

            all_inputs.append(masked_tokens)
            all_targets.append(list(tokens))
            all_mask_indices.append(sorted(chosen_pos))

    return all_inputs, all_targets, all_mask_indices
