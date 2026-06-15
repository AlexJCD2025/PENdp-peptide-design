"""
PENdp Scoring Evaluation Harness (ROADMAP Phase 0)

The single most important missing piece: a number that says how well the
scoring actually predicts real outcomes. This module correlates PENdp scores
against measured wet-lab readouts and reports Spearman/Pearson, per-dimension
correlations, and a naive baseline to beat.

Convention: correlations are reported so that **positive = good** — a scorer
whose higher scores track better outcomes gets ρ > 0, regardless of whether
the assay readout is "higher better" (e.g. %delivery) or "lower better"
(e.g. IC50 in nM). This is handled via the `direction` column.

No fabricated data ships here: pendp/data/wetlab_results.csv contains only the
schema header until real results are added.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional
import csv
import math

import numpy as np

from pendp.config import DATA_DIR

DEFAULT_DATASET = DATA_DIR / "wetlab_results.csv"

SCHEMA_COLUMNS = [
    "sequence", "target", "assay", "readout", "value", "unit",
    "direction", "n_replicates", "batch_id", "date", "source", "notes",
]


@dataclass
class WetlabRecord:
    sequence: str
    value: float
    direction: str = "higher_better"   # or "lower_better"
    target: str = ""
    assay: str = ""
    readout: str = ""
    unit: str = ""
    n_replicates: int = 1
    batch_id: str = ""
    date: str = ""
    source: str = ""
    notes: str = ""

    @property
    def effective_outcome(self) -> float:
        """Outcome oriented so that larger == better (for correlation)."""
        return self.value if self.direction != "lower_better" else -self.value


def load_dataset(path=None) -> List[WetlabRecord]:
    """Load wet-lab results from a CSV with SCHEMA_COLUMNS. Rows missing a
    sequence or a numeric value are skipped."""
    path = Path(path) if path else DEFAULT_DATASET
    if not path.exists():
        return []
    records: List[WetlabRecord] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            seq = (row.get("sequence") or "").strip()
            raw = (row.get("value") or "").strip()
            if not seq or not raw:
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            try:
                nrep = int(float(row.get("n_replicates") or 1))
            except ValueError:
                nrep = 1
            records.append(WetlabRecord(
                sequence=seq,
                value=value,
                direction=(row.get("direction") or "higher_better").strip() or "higher_better",
                target=(row.get("target") or "").strip(),
                assay=(row.get("assay") or "").strip(),
                readout=(row.get("readout") or "").strip(),
                unit=(row.get("unit") or "").strip(),
                n_replicates=nrep,
                batch_id=(row.get("batch_id") or "").strip(),
                date=(row.get("date") or "").strip(),
                source=(row.get("source") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            ))
    return records


# ── Correlation (numpy-only, average-rank Spearman) ──

def _rankdata(a) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    order = a.argsort(kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(1, len(a) + 1)
    # average ranks for ties
    sorted_a = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sorted_a[j + 1] == sorted_a[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return ranks


def _pearson(x, y) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _spearman(x, y) -> float:
    if len(x) < 3:
        return float("nan")
    return _pearson(_rankdata(x), _rankdata(y))


# ── Naive baseline features (the floor any real scorer must beat) ──

def naive_features(seq: str) -> List[float]:
    """Length, net charge, hydrophobic ratio — the trivial baseline."""
    s = seq.upper()
    n = len(s)
    if n == 0:
        return [0.0, 0.0, 0.0]
    net_charge = (s.count("R") + s.count("K")) - (s.count("D") + s.count("E"))
    hydrophobic = sum(1 for aa in s if aa in "AVILMFWY")
    return [float(n), float(net_charge), hydrophobic / n]


def _baseline_spearman(sequences: List[str], y_eff: List[float]) -> float:
    """Cross-validated Spearman of a linear fit on naive features.

    Cross-validated so it is comparable to (and a fair floor for) the
    fit-free heuristic scorer. Falls back to in-sample on tiny N / CV errors.
    """
    n = len(sequences)
    if n < 3:
        return float("nan")
    X = np.array([naive_features(s) for s in sequences], dtype=float)
    y = np.asarray(y_eff, dtype=float)
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import cross_val_predict, KFold
        n_splits = min(5, n)
        if n_splits < 2:
            raise ValueError("too few samples for CV")
        preds = cross_val_predict(
            LinearRegression(), X, y,
            cv=KFold(n_splits=n_splits, shuffle=True, random_state=0),
        )
        return _spearman(preds, y)
    except Exception:
        try:
            from sklearn.linear_model import LinearRegression
            model = LinearRegression().fit(X, y)
            return _spearman(model.predict(X), y)
        except Exception:
            return float("nan")


@dataclass
class EvalReport:
    n: int
    n_skipped: int
    spearman: float
    pearson: float
    per_dimension_spearman: Dict[str, float] = field(default_factory=dict)
    baseline_spearman: float = float("nan")
    note: str = ""

    def beats_baseline(self) -> Optional[bool]:
        if math.isnan(self.spearman) or math.isnan(self.baseline_spearman):
            return None
        return self.spearman > self.baseline_spearman

    def summary(self) -> str:
        lines = [
            f"\n{'='*56}",
            "PENdp Scoring Evaluation (ROADMAP Phase 0)",
            f"{'='*56}",
            f"  Records used: {self.n}   (skipped: {self.n_skipped})",
        ]
        if self.note:
            lines.append(f"  ⚠️  {self.note}")
        if self.n >= 3:
            lines.append(f"  {'─'*52}")
            lines.append(f"  Total score  → outcome   Spearman ρ = {self.spearman:+.3f}")
            lines.append(f"                            Pearson  r = {self.pearson:+.3f}")
            lines.append(f"  Naive baseline (len/charge/hydro) ρ = {self.baseline_spearman:+.3f}")
            verdict = self.beats_baseline()
            if verdict is True:
                lines.append("  ✅ Heuristic scorer beats the naive baseline.")
            elif verdict is False:
                lines.append("  ❌ Heuristic scorer does NOT beat the naive baseline.")
            if self.per_dimension_spearman:
                lines.append(f"  {'─'*52}")
                lines.append("  Per-dimension ρ vs outcome (predictive power):")
                for d, rho in sorted(self.per_dimension_spearman.items(),
                                     key=lambda kv: (math.isnan(kv[1]), -abs(kv[1]) if not math.isnan(kv[1]) else 0)):
                    flag = "" if math.isnan(rho) else ("  ⟵ strong" if abs(rho) >= 0.4 else ("  ·noise?" if abs(rho) < 0.1 else ""))
                    lines.append(f"    {d:5s} ρ = {rho:+.3f}{flag}")
        lines.append(f"{'='*56}")
        return "\n".join(lines)


def evaluate_scoring(records: List[WetlabRecord],
                     scorer: Optional[Callable[[str], Dict]] = None) -> EvalReport:
    """Correlate a scorer against measured outcomes.

    Args:
        records: wet-lab records (with value + direction).
        scorer: callable seq -> result dict with 'total_score' and 'dimensions'.
                Defaults to the heuristic ScoringEngine.
    """
    if scorer is None:
        from pendp.scoring.engine import ScoringEngine
        scorer = ScoringEngine().score_sequence

    seqs: List[str] = []
    totals: List[float] = []
    dim_rows: List[Dict[str, float]] = []
    ys: List[float] = []
    skipped = 0

    for r in records:
        res = scorer(r.sequence)
        if "error" in res or not res.get("dimensions"):
            skipped += 1
            continue
        seqs.append(r.sequence)
        totals.append(res["total_score"])
        dim_rows.append({d: res["dimensions"][d]["score"] for d in res["dimensions"]})
        ys.append(r.effective_outcome)

    n = len(seqs)
    if n < 3:
        return EvalReport(n=n, n_skipped=skipped, spearman=float("nan"),
                          pearson=float("nan"),
                          note="Need >= 3 valid records with measured values to compute correlation.")

    per_dim = {}
    all_dims = sorted({d for row in dim_rows for d in row})
    for d in all_dims:
        col = [row.get(d, float("nan")) for row in dim_rows]
        if any(math.isnan(v) for v in col):
            per_dim[d] = float("nan")
        else:
            per_dim[d] = _spearman(col, ys)

    return EvalReport(
        n=n,
        n_skipped=skipped,
        spearman=_spearman(totals, ys),
        pearson=_pearson(totals, ys),
        per_dimension_spearman=per_dim,
        baseline_spearman=_baseline_spearman(seqs, ys),
    )
