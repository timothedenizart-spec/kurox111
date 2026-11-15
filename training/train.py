"""Training harness for UCA's native MiniTransformer Denoiser & Concept Generator."""
from __future__ import annotations

import json
import time
from pathlib import Path
import numpy as np

from .dataset import RAW_TRAINING_CORPUS, SimpleTokenizer, create_training_samples
from .model import AdamW, MiniTransformer, compute_masked_loss


def train_model(
    corpus: list[str] | None = None,
    epochs: int = 35,
    batch_size: int = 16,
    lr: float = 1.5e-3,
    output_dir: str = "models/checkpoints",
    seed: int = 42,
) -> dict:
    np.random.seed(seed)
    corpus_data = corpus or RAW_TRAINING_CORPUS
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print("=== Initialisation du Tokenizer UCA ===")
    tokenizer = SimpleTokenizer()
    tokenizer.fit(corpus_data)
    tokenizer.save(out_path / "tokenizer.json")
    print(f"Vocabulaire appris : {tokenizer.vocab_size} tokens.")

    print("\n=== Préparation des Échantillons Masqués ===")
    inputs, targets, mask_indices = create_training_samples(
        corpus_data, tokenizer, max_length=40, mask_prob=0.20, samples_per_sentence=8, seed=seed
    )
    N = len(inputs)
    print(f"Échantillons d'entraînement générés : {N} séquences.")

    # Convert to NumPy
    X = np.array(inputs, dtype=np.int32)
    Y = np.array(targets, dtype=np.int32)
    # Mask indicator matrix: 1 if position is masked, 0 otherwise
    M = np.zeros_like(X, dtype=np.float32)
    for i, indices in enumerate(mask_indices):
        M[i, indices] = 1.0

    print("\n=== Instanciation du MiniTransformer UCA ===")
    model = MiniTransformer(
        vocab_size=tokenizer.vocab_size,
        max_seq_len=40,
        d_model=64,
        n_heads=4,
        d_ff=128,
        n_layers=2,
    )
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    print(f"Paramètres du modèle : d_model={model.d_model}, n_heads={model.n_heads}, n_layers={model.n_layers}")
    print(f"Lancement de l'entraînement sur {epochs} époques (batch_size={batch_size})...\n")

    history: list[dict] = []
    start_time = time.perf_counter()

    indices = np.arange(N)
    for epoch in range(1, epochs + 1):
        np.random.shuffle(indices)
        X_shuffled = X[indices]
        Y_shuffled = Y[indices]
        M_shuffled = M[indices]

        epoch_loss = 0.0
        epoch_acc = 0.0
        batches = int(np.ceil(N / batch_size))

        for b in range(batches):
            b_start = b * batch_size
            b_end = min(b_start + batch_size, N)

            x_batch = X_shuffled[b_start:b_end]
            y_batch = Y_shuffled[b_start:b_end]
            m_batch = M_shuffled[b_start:b_end]

            # Forward
            logits = model.forward(x_batch)
            loss, dlogits, acc = compute_masked_loss(logits, y_batch, m_batch)

            # Backward
            model.backward(dlogits)

            # Optimizer Step
            optimizer.step()

            epoch_loss += loss * (b_end - b_start)
            epoch_acc += acc * (b_end - b_start)

        mean_loss = epoch_loss / N
        mean_acc = epoch_acc / N

        record = {"epoch": epoch, "loss": round(mean_loss, 4), "accuracy": round(mean_acc, 4)}
        history.append(record)

        if epoch == 1 or epoch % 5 == 0 or epoch == epochs:
            elapsed = time.perf_counter() - start_time
            print(f"Époque [{epoch:2d}/{epochs:2d}] | Perte : {mean_loss:.4f} | Précision masquée : {mean_acc*100:.2f}% | Temps : {elapsed:.2f}s")

    total_time = round(time.perf_counter() - start_time, 2)
    initial_loss = history[0]["loss"]
    final_loss = history[-1]["loss"]
    loss_reduction = round((initial_loss - final_loss) / initial_loss * 100, 2)

    print(f"\n=== Entraînement Terminé en {total_time}s ===")
    print(f"Perte initiale : {initial_loss:.4f} -> Perte finale : {final_loss:.4f} (Réduction : -{loss_reduction}%)")
    print(f"Précision finale sur tokens masqués : {history[-1]['accuracy']*100:.2f}%")

    # Save checkpoint
    checkpoint_file = out_path / "uca_transformer.npz"
    model.save_checkpoint(checkpoint_file, extra_meta={
        "epochs": epochs,
        "final_loss": final_loss,
        "final_accuracy": history[-1]["accuracy"],
        "training_time_s": total_time,
        "loss_reduction_pct": loss_reduction,
    })
    print(f"Point de contrôle sauvegardé dans : {checkpoint_file}")

    # Save training report
    report = {
        "status": "completed",
        "epochs": epochs,
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "loss_reduction_percent": loss_reduction,
        "final_accuracy": history[-1]["accuracy"],
        "total_training_time_s": total_time,
        "history": history,
    }
    (out_path / "training_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    train_model()
