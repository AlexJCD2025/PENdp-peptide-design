"""
ESM-2 Model Management — load, embed, batch process

Supports: 8M / 35M / 150M / 650M
Device: MPS (Apple Silicon) / CUDA / CPU

Note: transformers import is LAZY (only when load_esm_model is called),
so this module can be imported without transformers installed.
"""
import numpy as np
from typing import Iterable, List, Optional, Tuple
from pendp.config import ESM_MODELS, get_device

# Cache loaded model to avoid reloading
_MODEL_CACHE = {}


def _validate_sequence(seq: str) -> str:
    if not isinstance(seq, str):
        raise TypeError("sequence must be a string")
    seq = seq.strip().upper()
    if not seq:
        raise ValueError("sequence must not be empty")
    valid = set("ACDEFGHIKLMNPQRSTVWY")
    invalid = sorted(set(seq) - valid)
    if invalid:
        raise ValueError(f"Invalid amino acids: {''.join(invalid)}")
    return seq


def load_esm_model(model_size: str = "150M") -> Tuple[object, object, dict]:
    """Load ESM-2 model and tokenizer.

    Args:
        model_size: "8M", "35M", "150M", or "650M"

    Returns:
        (model, tokenizer, info) — model is moved to best device, set to
        eval mode. ``info`` is the ESM_MODELS config dict for this size.
    """
    from transformers import AutoTokenizer, AutoModel
    import torch

    if model_size in _MODEL_CACHE:
        return _MODEL_CACHE[model_size]

    if model_size not in ESM_MODELS:
        raise ValueError(f"Unknown ESM-2 size '{model_size}'. Valid: {list(ESM_MODELS.keys())}")

    info = ESM_MODELS[model_size]
    device = get_device()

    print(f"Loading ESM-2 {model_size} on {device}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(info["name"])
        model = AutoModel.from_pretrained(info["name"])
    except Exception as e:
        raise RuntimeError(f"Failed to load ESM-2 '{info['name']}': {e}") from e

    model = model.to(device)
    model.eval()
    model.embedding_dim = info["dim"]

    _MODEL_CACHE[model_size] = (model, tokenizer, info)
    return model, tokenizer, info


def get_embedding(model, tokenizer, sequence: str) -> np.ndarray:
    """Get mean-pooled ESM-2 embedding for a single peptide sequence."""
    return batch_get_embeddings(model, tokenizer, [sequence])[0]


def batch_get_embeddings(model, tokenizer, sequences: Iterable[str],
                         batch_size: int = 8) -> np.ndarray:
    """Get mean-pooled ESM-2 embeddings for multiple sequences.

    Returns:
        (n_sequences, embedding_dim) float32 array.
    """
    import torch

    seqs = [_validate_sequence(s) for s in sequences]
    if not seqs:
        return np.empty((0, int(getattr(model, "embedding_dim", 0))), dtype=np.float32)

    device = next(model.parameters()).device
    all_embs = []

    for i in range(0, len(seqs), batch_size):
        batch = seqs[i:i + batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True,
                           truncation=True, return_special_tokens_mask=True)
        attn = inputs["attention_mask"].to(device)
        spec = inputs["special_tokens_mask"].to(device)

        with torch.no_grad():
            inputs_dev = {k: v.to(device) for k, v in inputs.items()}
            outputs = model(**inputs_dev)

        # Mean pool: skip special tokens (CLS, EOS, PAD)
        mask = attn * (1 - spec)
        mask = mask.to(outputs.last_hidden_state.dtype).unsqueeze(-1)
        summed = (outputs.last_hidden_state * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1)
        batch_emb = (summed / counts).cpu().numpy()
        all_embs.append(batch_emb)

    return np.concatenate(all_embs, axis=0).astype(np.float32, copy=False)


def model_summary(model_size: str) -> dict:
    """Return model configuration summary."""
    if model_size not in ESM_MODELS:
        raise ValueError(f"Unknown size '{model_size}'")
    info = ESM_MODELS[model_size]
    return {
        "model_size": model_size,
        "huggingface_name": info["name"],
        "dimension": info["dim"],
        "speed_rating": info["speed"],
    }
