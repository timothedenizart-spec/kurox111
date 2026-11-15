"""Lightweight pure-NumPy Transformer Denoiser & Concept Generator for UCA.

Implements:
- Multi-Head Self-Attention with exact analytical gradients
- LayerNorm with learnable gain (gamma) and bias (beta)
- Positionwise Feed-Forward Network with GELU activation
- Token and learnable Positional Embeddings
- Cross-Entropy Loss with numerically stable Log-Sum-Exp
- AdamW Optimizer with weight decay and bias correction
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import numpy as np


def gelu(x: np.ndarray) -> np.ndarray:
    """Gaussian Error Linear Unit approximation."""
    return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * np.power(x, 3))))


def gelu_grad(x: np.ndarray) -> np.ndarray:
    """Exact analytical derivative of GELU."""
    k = np.sqrt(2.0 / np.pi)
    inner = k * (x + 0.044715 * np.power(x, 3))
    tanh_inner = np.tanh(inner)
    d_inner = k * (1.0 + 3.0 * 0.044715 * np.power(x, 2))
    sech2 = 1.0 - np.power(tanh_inner, 2)
    return 0.5 * (1.0 + tanh_inner) + 0.5 * x * sech2 * d_inner


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    max_x = np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x - max_x)
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


class LayerNorm:
    def __init__(self, dim: int, eps: float = 1e-5) -> None:
        self.dim = dim
        self.eps = eps
        self.gamma = np.ones(dim, dtype=np.float32)
        self.beta = np.zeros(dim, dtype=np.float32)
        self.dgamma = np.zeros_like(self.gamma)
        self.dbeta = np.zeros_like(self.beta)
        self.cache: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        # x shape: (B, T, D)
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        std_inv = 1.0 / np.sqrt(var + self.eps)
        x_norm = (x - mean) * std_inv
        out = self.gamma * x_norm + self.beta
        self.cache = (x, x_norm, mean, std_inv)
        return out

    def backward(self, dout: np.ndarray) -> np.ndarray:
        x, x_norm, mean, std_inv = self.cache  # type: ignore
        B, T, D = dout.shape
        self.dgamma = np.sum(dout * x_norm, axis=(0, 1))
        self.dbeta = np.sum(dout, axis=(0, 1))

        dx_norm = dout * self.gamma
        dvar = np.sum(dx_norm * (x - mean) * -0.5 * np.power(std_inv, 3), axis=-1, keepdims=True)
        dmean = np.sum(dx_norm * -std_inv, axis=-1, keepdims=True) + dvar * np.mean(-2.0 * (x - mean), axis=-1, keepdims=True)
        dx = dx_norm * std_inv + dvar * 2.0 * (x - mean) / D + dmean / D
        return dx


class MultiHeadAttention:
    def __init__(self, d_model: int, n_heads: int) -> None:
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        # Xavier initialization
        scale = np.sqrt(2.0 / (d_model + d_model))
        self.W_q = (np.random.randn(d_model, d_model) * scale).astype(np.float32)
        self.W_k = (np.random.randn(d_model, d_model) * scale).astype(np.float32)
        self.W_v = (np.random.randn(d_model, d_model) * scale).astype(np.float32)
        self.W_o = (np.random.randn(d_model, d_model) * scale).astype(np.float32)

        self.dW_q = np.zeros_like(self.W_q)
        self.dW_k = np.zeros_like(self.W_k)
        self.dW_v = np.zeros_like(self.W_v)
        self.dW_o = np.zeros_like(self.W_o)
        self.cache: Any = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        B, T, D = x.shape
        # Q, K, V projections
        Q = np.dot(x, self.W_q)  # (B, T, D)
        K = np.dot(x, self.W_k)  # (B, T, D)
        V = np.dot(x, self.W_v)  # (B, T, D)

        # Reshape to (B, H, T, d_k)
        Q_h = Q.reshape(B, T, self.n_heads, self.d_k).transpose(0, 2, 1, 3)
        K_h = K.reshape(B, T, self.n_heads, self.d_k).transpose(0, 2, 1, 3)
        V_h = V.reshape(B, T, self.n_heads, self.d_k).transpose(0, 2, 1, 3)

        # Scaled Dot-Product Attention: (B, H, T, T)
        scores = np.matmul(Q_h, K_h.transpose(0, 1, 3, 2)) / np.sqrt(self.d_k)
        attn_weights = softmax(scores, axis=-1)

        # Context output: (B, H, T, d_k)
        context_h = np.matmul(attn_weights, V_h)
        # Transpose back: (B, T, H, d_k) -> (B, T, D)
        context = context_h.transpose(0, 2, 1, 3).reshape(B, T, D)
        out = np.dot(context, self.W_o)

        self.cache = (x, Q_h, K_h, V_h, attn_weights, context)
        return out

    def backward(self, dout: np.ndarray) -> np.ndarray:
        x, Q_h, K_h, V_h, attn_weights, context = self.cache
        B, T, D = dout.shape

        # Gradient wrt W_o
        self.dW_o = np.dot(context.reshape(-1, D).T, dout.reshape(-1, D))
        dcontext = np.dot(dout, self.W_o.T)  # (B, T, D)
        dcontext_h = dcontext.reshape(B, T, self.n_heads, self.d_k).transpose(0, 2, 1, 3)

        # Gradient wrt V_h and attn_weights
        dV_h = np.matmul(attn_weights.transpose(0, 1, 3, 2), dcontext_h)
        dattn = np.matmul(dcontext_h, V_h.transpose(0, 1, 3, 2))  # (B, H, T, T)

        # Softmax backward
        dscores = attn_weights * (dattn - np.sum(dattn * attn_weights, axis=-1, keepdims=True))
        dscores = dscores / np.sqrt(self.d_k)

        # Gradients wrt Q_h and K_h
        dQ_h = np.matmul(dscores, K_h)
        dK_h = np.matmul(dscores.transpose(0, 1, 3, 2), Q_h)

        # Reshape to (B, T, D)
        dQ = dQ_h.transpose(0, 2, 1, 3).reshape(B, T, D)
        dK = dK_h.transpose(0, 2, 1, 3).reshape(B, T, D)
        dV = dV_h.transpose(0, 2, 1, 3).reshape(B, T, D)

        self.dW_q = np.dot(x.reshape(-1, D).T, dQ.reshape(-1, D))
        self.dW_k = np.dot(x.reshape(-1, D).T, dK.reshape(-1, D))
        self.dW_v = np.dot(x.reshape(-1, D).T, dV.reshape(-1, D))

        dx = np.dot(dQ, self.W_q.T) + np.dot(dK, self.W_k.T) + np.dot(dV, self.W_v.T)
        return dx


class FeedForward:
    def __init__(self, d_model: int, d_ff: int) -> None:
        scale1 = np.sqrt(2.0 / (d_model + d_ff))
        scale2 = np.sqrt(2.0 / (d_ff + d_model))
        self.W1 = (np.random.randn(d_model, d_ff) * scale1).astype(np.float32)
        self.b1 = np.zeros(d_ff, dtype=np.float32)
        self.W2 = (np.random.randn(d_ff, d_model) * scale2).astype(np.float32)
        self.b2 = np.zeros(d_model, dtype=np.float32)

        self.dW1 = np.zeros_like(self.W1)
        self.db1 = np.zeros_like(self.b1)
        self.dW2 = np.zeros_like(self.W2)
        self.db2 = np.zeros_like(self.b2)
        self.cache: Any = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        B, T, D = x.shape
        z1 = np.dot(x, self.W1) + self.b1
        h1 = gelu(z1)
        out = np.dot(h1, self.W2) + self.b2
        self.cache = (x, z1, h1)
        return out

    def backward(self, dout: np.ndarray) -> np.ndarray:
        x, z1, h1 = self.cache
        B, T, D = dout.shape
        dh1 = np.dot(dout, self.W2.T)
        self.dW2 = np.dot(h1.reshape(-1, self.W2.shape[0]).T, dout.reshape(-1, D))
        self.db2 = np.sum(dout, axis=(0, 1))

        dz1 = dh1 * gelu_grad(z1)
        self.dW1 = np.dot(x.reshape(-1, D).T, dz1.reshape(-1, self.W1.shape[1]))
        self.db1 = np.sum(dz1, axis=(0, 1))

        dx = np.dot(dz1, self.W1.T)
        return dx


class TransformerBlock:
    def __init__(self, d_model: int, n_heads: int, d_ff: int) -> None:
        self.ln1 = LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads)
        self.ln2 = LayerNorm(d_model)
        self.ffn = FeedForward(d_model, d_ff)

    def forward(self, x: np.ndarray) -> np.ndarray:
        # Pre-LN architecture
        norm1 = self.ln1.forward(x)
        attn_out = self.attn.forward(norm1)
        x = x + attn_out

        norm2 = self.ln2.forward(x)
        ffn_out = self.ffn.forward(norm2)
        x = x + ffn_out
        return x

    def backward(self, dout: np.ndarray) -> np.ndarray:
        # Backward through FFN & LN2
        dffn = self.ffn.backward(dout)
        dnorm2 = self.ln2.backward(dffn)
        dx2 = dout + dnorm2

        # Backward through Attn & LN1
        dattn = self.attn.backward(dx2)
        dnorm1 = self.ln1.backward(dattn)
        dx1 = dx2 + dnorm1
        return dx1


class MiniTransformer:
    """Compact Encoder-Denoiser Transformer."""

    def __init__(self, vocab_size: int, max_seq_len: int = 48, d_model: int = 64,
                 n_heads: int = 4, d_ff: int = 128, n_layers: int = 2) -> None:
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_ff = d_ff
        self.n_layers = n_layers

        # Token & Positional embeddings
        scale = np.sqrt(2.0 / d_model)
        self.token_emb = (np.random.randn(vocab_size, d_model) * scale).astype(np.float32)
        self.pos_emb = (np.random.randn(max_seq_len, d_model) * scale).astype(np.float32)

        self.blocks = [TransformerBlock(d_model, n_heads, d_ff) for _ in range(n_layers)]
        self.final_ln = LayerNorm(d_model)
        # Output projection head (tied or untied weights)
        self.head_w = (np.random.randn(d_model, vocab_size) * scale).astype(np.float32)
        self.head_b = np.zeros(vocab_size, dtype=np.float32)

        # Gradients
        self.dtoken_emb = np.zeros_like(self.token_emb)
        self.dpos_emb = np.zeros_like(self.pos_emb)
        self.dhead_w = np.zeros_like(self.head_w)
        self.dhead_b = np.zeros_like(self.head_b)

        self.cache: Any = None

    def forward(self, input_ids: np.ndarray) -> np.ndarray:
        # input_ids: (B, T)
        B, T = input_ids.shape
        tok = self.token_emb[input_ids]  # (B, T, D)
        pos = self.pos_emb[:T]           # (T, D)
        x = tok + pos

        for block in self.blocks:
            x = block.forward(x)

        x_norm = self.final_ln.forward(x)
        logits = np.dot(x_norm, self.head_w) + self.head_b  # (B, T, V)

        self.cache = (input_ids, x_norm)
        return logits

    def backward(self, dlogits: np.ndarray) -> None:
        input_ids, x_norm = self.cache
        B, T, V = dlogits.shape
        D = self.d_model

        # Head gradients
        self.dhead_w = np.dot(x_norm.reshape(-1, D).T, dlogits.reshape(-1, V))
        self.dhead_b = np.sum(dlogits, axis=(0, 1))

        dx = np.dot(dlogits, self.head_w.T)
        dx = self.final_ln.backward(dx)

        for block in reversed(self.blocks):
            dx = block.backward(dx)

        # Embedding gradients
        self.dtoken_emb.fill(0)
        self.dpos_emb.fill(0)
        np.add.at(self.dtoken_emb, input_ids, dx)
        self.dpos_emb[:T] += np.sum(dx, axis=0)

    def parameters(self) -> list[tuple[np.ndarray, np.ndarray]]:
        """Returns list of (param, grad) pairs for optimizer."""
        params = [
            (self.token_emb, self.dtoken_emb),
            (self.pos_emb, self.dpos_emb),
            (self.final_ln.gamma, self.final_ln.dgamma),
            (self.final_ln.beta, self.final_ln.dbeta),
            (self.head_w, self.dhead_w),
            (self.head_b, self.dhead_b),
        ]
        for b in self.blocks:
            params.extend([
                (b.ln1.gamma, b.ln1.dgamma), (b.ln1.beta, b.ln1.dbeta),
                (b.attn.W_q, b.attn.dW_q), (b.attn.W_k, b.attn.dW_k),
                (b.attn.W_v, b.attn.dW_v), (b.attn.W_o, b.attn.dW_o),
                (b.ln2.gamma, b.ln2.dgamma), (b.ln2.beta, b.ln2.dbeta),
                (b.ffn.W1, b.ffn.dW1), (b.ffn.b1, b.ffn.db1),
                (b.ffn.W2, b.ffn.dW2), (b.ffn.b2, b.ffn.db2),
            ])
        return params

    def save_checkpoint(self, path: str | Path, extra_meta: dict[str, Any] | None = None) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tensors = {
            "token_emb": self.token_emb,
            "pos_emb": self.pos_emb,
            "final_ln_gamma": self.final_ln.gamma,
            "final_ln_beta": self.final_ln.beta,
            "head_w": self.head_w,
            "head_b": self.head_b,
        }
        for i, b in enumerate(self.blocks):
            tensors[f"b{i}_ln1_gamma"] = b.ln1.gamma
            tensors[f"b{i}_ln1_beta"] = b.ln1.beta
            tensors[f"b{i}_attn_W_q"] = b.attn.W_q
            tensors[f"b{i}_attn_W_k"] = b.attn.W_k
            tensors[f"b{i}_attn_W_v"] = b.attn.W_v
            tensors[f"b{i}_attn_W_o"] = b.attn.W_o
            tensors[f"b{i}_ln2_gamma"] = b.ln2.gamma
            tensors[f"b{i}_ln2_beta"] = b.ln2.beta
            tensors[f"b{i}_ffn_W1"] = b.ffn.W1
            tensors[f"b{i}_ffn_b1"] = b.ffn.b1
            tensors[f"b{i}_ffn_W2"] = b.ffn.W2
            tensors[f"b{i}_ffn_b2"] = b.ffn.b2
        np.savez_compressed(p, **tensors)

        # Config metadata
        cfg_path = p.with_suffix(".json")
        meta = {
            "vocab_size": self.vocab_size,
            "max_seq_len": self.max_seq_len,
            "d_model": self.d_model,
            "n_heads": self.n_heads,
            "d_ff": self.d_ff,
            "n_layers": self.n_layers,
            "extra": extra_meta or {},
        }
        cfg_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    @classmethod
    def load_checkpoint(cls, path: str | Path) -> "MiniTransformer":
        p = Path(path)
        cfg_path = p.with_suffix(".json")
        meta = json.loads(cfg_path.read_text(encoding="utf-8"))
        model = cls(
            vocab_size=meta["vocab_size"],
            max_seq_len=meta["max_seq_len"],
            d_model=meta["d_model"],
            n_heads=meta["n_heads"],
            d_ff=meta["d_ff"],
            n_layers=meta["n_layers"]
        )
        loaded = np.load(p)
        model.token_emb[:] = loaded["token_emb"]
        model.pos_emb[:] = loaded["pos_emb"]
        model.final_ln.gamma[:] = loaded["final_ln_gamma"]
        model.final_ln.beta[:] = loaded["final_ln_beta"]
        model.head_w[:] = loaded["head_w"]
        model.head_b[:] = loaded["head_b"]
        for i, b in enumerate(model.blocks):
            b.ln1.gamma[:] = loaded[f"b{i}_ln1_gamma"]
            b.ln1.beta[:] = loaded[f"b{i}_ln1_beta"]
            b.attn.W_q[:] = loaded[f"b{i}_attn_W_q"]
            b.attn.W_k[:] = loaded[f"b{i}_attn_W_k"]
            b.attn.W_v[:] = loaded[f"b{i}_attn_W_v"]
            b.attn.W_o[:] = loaded[f"b{i}_attn_W_o"]
            b.ln2.gamma[:] = loaded[f"b{i}_ln2_gamma"]
            b.ln2.beta[:] = loaded[f"b{i}_ln2_beta"]
            b.ffn.W1[:] = loaded[f"b{i}_ffn_W1"]
            b.ffn.b1[:] = loaded[f"b{i}_ffn_b1"]
            b.ffn.W2[:] = loaded[f"b{i}_ffn_W2"]
            b.ffn.b2[:] = loaded[f"b{i}_ffn_b2"]
        return model


class AdamW:
    def __init__(self, params: list[tuple[np.ndarray, np.ndarray]], lr: float = 1e-3,
                 beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8,
                 weight_decay: float = 0.01) -> None:
        self.params = params
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.weight_decay = weight_decay
        self.m = [np.zeros_like(p) for p, _ in params]
        self.v = [np.zeros_like(p) for p, _ in params]
        self.t = 0

    def step(self) -> None:
        self.t += 1
        for i, (param, grad) in enumerate(self.params):
            if grad is None:
                continue
            # Weight decay (excluding biases and 1D norm params)
            if param.ndim > 1:
                param -= self.lr * self.weight_decay * param

            self.m[i] = self.beta1 * self.m[i] + (1.0 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1.0 - self.beta2) * np.square(grad)

            # Bias correction
            m_hat = self.m[i] / (1.0 - np.power(self.beta1, self.t))
            v_hat = self.v[i] / (1.0 - np.power(self.beta2, self.t))

            param -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


def compute_masked_loss(logits: np.ndarray, targets: np.ndarray, mask_mask: np.ndarray) -> tuple[float, np.ndarray, float]:
    """Computes cross-entropy loss and dlogits only on masked positions."""
    B, T, V = logits.shape
    probs = softmax(logits, axis=-1)  # (B, T, V)

    # Gather target probabilities
    flat_targets = targets.reshape(-1)
    flat_probs = probs.reshape(-1, V)
    flat_mask = mask_mask.reshape(-1)

    num_masked = np.sum(flat_mask)
    if num_masked == 0:
        return 0.0, np.zeros_like(logits), 1.0

    target_probs = flat_probs[np.arange(len(flat_targets)), flat_targets]
    eps = 1e-12
    log_probs = np.log(np.maximum(target_probs, eps))
    loss = -np.sum(log_probs * flat_mask) / num_masked

    # Compute dlogits: (P - Y) / N on masked positions
    dlogits_flat = np.zeros_like(flat_probs)
    dlogits_flat[np.arange(len(flat_targets)), flat_targets] -= 1.0
    dlogits_flat = (flat_probs + dlogits_flat) * flat_mask[:, None] / num_masked
    dlogits = dlogits_flat.reshape(B, T, V)

    # Accuracy
    preds = np.argmax(probs, axis=-1)
    acc = np.sum((preds == targets) * mask_mask) / num_masked

    return float(loss), dlogits, float(acc)
