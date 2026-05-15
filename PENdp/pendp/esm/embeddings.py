"""
ESM-2 embedding utilities for PENdp peptide workflows.
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

from pendp.database.sequences import LUNG_PEPTIDES_V6
from pendp.esm.model import batch_get_embeddings, get_embedding


def _resolve_model_tokenizer(model, tokenizer=None):
    """Support both (model, tokenizer) tuples and separate arguments."""
    if tokenizer is not None:
        return model, tokenizer

    if isinstance(model, (tuple, list)) and len(model) >= 2:
        return model[0], model[1]

    if isinstance(model, dict) and "model" in model and "tokenizer" in model:
        return model["model"], model["tokenizer"]

    raise ValueError(
        "tokenizer is required unless model is a (model, tokenizer) tuple "
        "or a {'model': ..., 'tokenizer': ...} dictionary"
    )


def _as_embedding_matrix(embeddings: np.ndarray) -> np.ndarray:
    embeddings = np.asarray(embeddings, dtype=np.float32)
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)
    if embeddings.ndim != 2:
        raise ValueError("reference_embeddings must be a 1D or 2D array")
    return embeddings


def _cosine_similarity_matrix(query: np.ndarray, database: np.ndarray) -> np.ndarray:
    query = _as_embedding_matrix(query)
    database = _as_embedding_matrix(database)

    query_norm = np.linalg.norm(query, axis=1, keepdims=True)
    database_norm = np.linalg.norm(database, axis=1, keepdims=True)

    query_norm = np.maximum(query_norm, 1e-12)
    database_norm = np.maximum(database_norm, 1e-12)

    query_unit = query / query_norm
    database_unit = database / database_norm
    return query_unit @ database_unit.T


def calc_similarity_to_reference(
    seq: str,
    model,
    tokenizer=None,
    reference_embeddings: Optional[np.ndarray] = None,
) -> float:
    """Calculate cosine similarity between a sequence and lung_v6 references.

    Returns the maximum similarity to the reference set, clipped to ``0-1``.
    """
    model, tokenizer = _resolve_model_tokenizer(model, tokenizer)
    query_embedding = get_embedding(model, tokenizer, seq)

    if reference_embeddings is None:
        reference_sequences = [entry.sequence for entry in LUNG_PEPTIDES_V6]
        reference_embeddings = batch_get_embeddings(model, tokenizer, reference_sequences)

    similarities = _cosine_similarity_matrix(query_embedding, reference_embeddings)[0]
    if similarities.size == 0:
        raise ValueError("reference_embeddings must contain at least one embedding")

    return float(np.clip(np.max(similarities), 0.0, 1.0))


def embed_peptide_dataset(sequences: Iterable[str], model, tokenizer) -> np.ndarray:
    """Embed a list of peptide sequences and return an ``(n, dim)`` array."""
    return batch_get_embeddings(model, tokenizer, list(sequences))


def find_most_similar(
    query_seq: str,
    database_sequences: Sequence[str],
    model,
    tokenizer,
    top_k: int = 5,
) -> List[dict]:
    """Find the top_k database sequences most similar to query_seq."""
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer")

    database_sequences = list(database_sequences)
    if not database_sequences:
        return []

    query_embedding = get_embedding(model, tokenizer, query_seq)
    database_embeddings = batch_get_embeddings(model, tokenizer, database_sequences)
    similarities = _cosine_similarity_matrix(query_embedding, database_embeddings)[0]
    similarities = np.clip(similarities, 0.0, 1.0)

    limit = min(top_k, len(database_sequences))
    top_indices = np.argsort(similarities)[::-1][:limit]

    return [
        {
            "sequence": database_sequences[index],
            "similarity": float(similarities[index]),
            "index": int(index),
        }
        for index in top_indices
    ]


def generate_variant_embeddings(
    base_sequence: str,
    variants: Sequence[str],
    model,
    tokenizer,
) -> Tuple[np.ndarray, List[str]]:
    """Generate embeddings for a base peptide and its sequence variants."""
    sequences = [base_sequence] + list(variants)
    embeddings = batch_get_embeddings(model, tokenizer, sequences)
    return embeddings, sequences
