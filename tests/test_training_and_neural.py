from __future__ import annotations

import unittest
from pathlib import Path
import numpy as np

from training.dataset import SimpleTokenizer, create_training_samples
from training.model import AdamW, MiniTransformer, compute_masked_loss
from uca.model_adapters import invoke_json_runner


class TrainingAndNeuralTests(unittest.TestCase):

    def test_tokenizer_encode_decode(self) -> None:
        corpus = ["le cerveau humain contient un thalamus.", "la logique formelle est exacte."]
        tokenizer = SimpleTokenizer()
        tokenizer.fit(corpus)
        encoded = tokenizer.encode("le thalamus", max_length=6, add_special_tokens=True)
        self.assertEqual(encoded[0], tokenizer.token2id[tokenizer.BOS_TOKEN])
        self.assertEqual(encoded[-1], tokenizer.pad_id)
        decoded = tokenizer.decode(encoded)
        self.assertIn("thalamus", decoded)

    def test_minitransformer_forward_backward(self) -> None:
        vocab_size = 30
        model = MiniTransformer(vocab_size=vocab_size, max_seq_len=8, d_model=16, n_heads=2, d_ff=32, n_layers=1)
        x = np.random.randint(0, vocab_size, size=(2, 8), dtype=np.int32)
        logits = model.forward(x)
        self.assertEqual(logits.shape, (2, 8, vocab_size))

        dlogits = np.random.randn(*logits.shape).astype(np.float32)
        model.backward(dlogits)
        self.assertIsNotNone(model.dtoken_emb)
        self.assertEqual(model.dtoken_emb.shape, (vocab_size, 16))

    def test_training_loss_decreases(self) -> None:
        np.random.seed(42)
        vocab_size = 20
        model = MiniTransformer(vocab_size=vocab_size, max_seq_len=6, d_model=16, n_heads=2, d_ff=32, n_layers=1)
        optimizer = AdamW(model.parameters(), lr=0.01)

        X = np.random.randint(0, vocab_size, size=(4, 6), dtype=np.int32)
        Y = np.random.randint(0, vocab_size, size=(4, 6), dtype=np.int32)
        M = np.ones((4, 6), dtype=np.float32)

        initial_loss, _, _ = compute_masked_loss(model.forward(X), Y, M)
        for _ in range(15):
            logits = model.forward(X)
            loss, dlogits, _ = compute_masked_loss(logits, Y, M)
            model.backward(dlogits)
            optimizer.step()

        final_loss, _, _ = compute_masked_loss(model.forward(X), Y, M)
        self.assertLess(final_loss, initial_loss)

    def test_neural_runner_concept_generation(self) -> None:
        runner_cmd = "python3 scripts/neural_runner.py"
        res = invoke_json_runner(runner_cmd, {"operation": "concept_generation", "query": "thalamus cortex", "contract_version": 1}, 10.0)
        self.assertEqual(res.get("status"), "success")
        self.assertIn("proposals", res)


if __name__ == "__main__":
    unittest.main()
