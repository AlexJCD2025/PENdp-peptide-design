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
import os

import numpy as np

from pendp.config import DATA_DIR


def default_dataset_path() -> Path:
    """Resolve where wet-lab results live, in priority order:

    1. $PENDP_WETLAB_DATA, if set (explicit override).
    2. The in-tree data file, when running from a checkout / editable install
       (DATA_DIR exists). This is the common dev path.
    3. A user-writable fallback (~/.pendp/wetlab_results.csv) — used when
       installed from a wheel, where DATA_DIR is not packaged and the install
       dir may be read-only.
    """
    env = os.environ.get("PENDP_WETLAB_DATA")
    if env:
        return Path(env)
    if DATA_DIR.exists():
        return DATA_DIR / "wetlab_results.csv"
    return Path.home() / ".pendp" / "wetlab_results.csv"

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
    path = Path(path) if path else default_dataset_path()
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


def _baseline_cv_predictions(sequences: List[str], y_eff: List[float]):
    """Cross-validated predictions of a linear fit on naive features.

    Cross-validated so the baseline is a fair floor for the fit-free
    heuristic scorer. Falls back to in-sample on tiny N / CV errors;
    returns None if even that fails.
    """
    n = len(sequences)
    if n < 3:
        return None
    X = np.array([naive_features(s) for s in sequences], dtype=float)
    y = np.asarray(y_eff, dtype=float)
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import cross_val_predict, KFold
        n_splits = min(5, n)
        if n_splits < 2:
            raise ValueError("too few samples for CV")
        return cross_val_predict(
            LinearRegression(), X, y,
            cv=KFold(n_splits=n_splits, shuffle=True, random_state=0),
        )
    except Exception:
        try:
            from sklearn.linear_model import LinearRegression
            return LinearRegression().fit(X, y).predict(X)
        except Exception:
            return None


# ── Within-group normalization + pooling (the defensible single metric) ──

def _rank_percentile(a) -> np.ndarray:
    """Within-group rank percentile in (0,1); removes scale and offset."""
    a = np.asarray(a, dtype=float)
    if len(a) == 0:
        return a
    return (_rankdata(a) - 0.5) / len(a)


def _zscore(a) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    s = a.std()
    return (a - a.mean()) / s if s > 0 else np.zeros_like(a)


def _pool_and_corr(per_group_xy, normalizer) -> float:
    """Normalize x,y WITHIN each group, pool, then Pearson.

    Because each group is normalized to a common (scale/offset-free) range
    before pooling, cross-group differences in assay scale cannot distort the
    result — this is the statistically valid way to get ONE number.
    """
    xs, ys = [], []
    for x, y in per_group_xy:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
            continue  # group carries no correlation signal
        xs.append(normalizer(x))
        ys.append(normalizer(y))
    if not xs:
        return float("nan")
    return _pearson(np.concatenate(xs), np.concatenate(ys))


def _fisher_mean(pairs) -> float:
    """Fisher z-transform mean of per-group correlations, weighted by (n-3)."""
    zs, ws = [], []
    for rho, n in pairs:
        if math.isnan(rho) or n < 4:
            continue
        rho = max(min(rho, 0.999), -0.999)
        zs.append(math.atanh(rho))
        ws.append(n - 3)
    if not zs or sum(ws) <= 0:
        return float("nan")
    zbar = sum(z * w for z, w in zip(zs, ws)) / sum(ws)
    return math.tanh(zbar)


@dataclass
class GroupResult:
    key: tuple                 # (target, assay, readout, unit, batch_id)
    n: int
    spearman: float
    pearson: float
    baseline_spearman: float


@dataclass
class EvalReport:
    n: int                     # total valid records (across groups)
    n_skipped: int
    spearman: float            # pooled within-group Spearman (the headline)
    pearson: float             # pooled within-group Pearson
    spearman_fisher_mean: float = float("nan")  # Fisher-z mean of per-group ρ
    per_dimension_spearman: Dict[str, float] = field(default_factory=dict)
    baseline_spearman: float = float("nan")
    groups: List[GroupResult] = field(default_factory=list)
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
            f"  Comparable groups (target/assay/readout/unit/batch): {len(self.groups)}",
        ]
        if self.note:
            lines.append(f"  ⚠️  {self.note}")
        if not math.isnan(self.spearman):
            lines.append(f"  {'─'*52}")
            lines.append(f"  Pooled within-group   Spearman ρ = {self.spearman:+.3f}  (headline)")
            lines.append(f"                        Pearson  r = {self.pearson:+.3f}")
            lines.append(f"  Fisher-z mean of per-group ρ     = {self.spearman_fisher_mean:+.3f}")
            lines.append(f"  Naive baseline (len/charge/hydro) ρ = {self.baseline_spearman:+.3f}")
            verdict = self.beats_baseline()
            if verdict is True:
                lines.append("  ✅ Heuristic scorer beats the naive baseline.")
            elif verdict is False:
                lines.append("  ❌ Heuristic scorer does NOT beat the naive baseline.")
            if len(self.groups) > 1:
                lines.append(f"  {'─'*52}")
                lines.append("  Per-group ρ (raw pooling across these would be invalid):")
                for g in self.groups:
                    label = "/".join(x for x in g.key if x) or "(unlabeled)"
                    lines.append(f"    {label:34s} n={g.n:<3d} ρ={g.spearman:+.3f}")
            if self.per_dimension_spearman:
                lines.append(f"  {'─'*52}")
                lines.append("  Per-dimension ρ vs outcome (pooled within-group):")
                for d, rho in sorted(self.per_dimension_spearman.items(),
                                     key=lambda kv: (math.isnan(kv[1]), -abs(kv[1]) if not math.isnan(kv[1]) else 0)):
                    flag = "" if math.isnan(rho) else ("  ⟵ strong" if abs(rho) >= 0.4 else ("  ·noise?" if abs(rho) < 0.1 else ""))
                    lines.append(f"    {d:5s} ρ = {rho:+.3f}{flag}")
        lines.append(f"{'='*56}")
        return "\n".join(lines)


def evaluate_scoring(records: List[WetlabRecord],
                     scorer: Optional[Callable[[str], Dict]] = None) -> EvalReport:
    """Correlate a scorer against measured outcomes — comparably.

    Records are bucketed by comparable condition — (target, assay, readout,
    unit, batch_id). Within each group, scores and outcomes are
    rank-normalized (removing assay scale/offset), then pooled into ONE
    Spearman (the headline). A Fisher-z mean of per-group ρ is reported as
    an alternative aggregate, alongside the per-group breakdown. Raw outcomes
    are never pooled across groups (nM affinity vs %delivery aren't comparable).

    Args:
        records: wet-lab records (with value + direction).
        scorer: callable seq -> result dict with 'total_score' and 'dimensions'.
                Defaults to the heuristic ScoringEngine.
    """
    if scorer is None:
        from pendp.scoring.engine import ScoringEngine
        scorer = ScoringEngine().score_sequence

    # Score each record, bucketed by comparable condition.
    buckets: Dict[tuple, Dict[str, list]] = {}
    skipped = 0
    n_valid = 0
    for r in records:
        res = scorer(r.sequence)
        if "error" in res or not res.get("dimensions"):
            skipped += 1
            continue
        n_valid += 1
        key = (r.target, r.assay, r.readout, r.unit, r.batch_id)
        b = buckets.setdefault(key, {"seqs": [], "totals": [], "dims": [], "ys": []})
        b["seqs"].append(r.sequence)
        b["totals"].append(res["total_score"])
        b["dims"].append({d: res["dimensions"][d]["score"] for d in res["dimensions"]})
        b["ys"].append(r.effective_outcome)

    groups: List[GroupResult] = []
    total_xy = []                          # [(scores, outcomes)] per group
    baseline_xy = []                       # [(baseline_preds, outcomes)] per group
    per_dim_xy: Dict[str, list] = {}       # dim -> [(dim_scores, outcomes)] per group
    for key, b in buckets.items():
        gn = len(b["seqs"])
        if gn < 3:
            continue  # not enough comparable points to correlate
        preds = _baseline_cv_predictions(b["seqs"], b["ys"])
        g_base = _spearman(preds, b["ys"]) if preds is not None else float("nan")
        groups.append(GroupResult(
            key=key, n=gn,
            spearman=_spearman(b["totals"], b["ys"]),
            pearson=_pearson(b["totals"], b["ys"]),
            baseline_spearman=g_base,
        ))
        total_xy.append((b["totals"], b["ys"]))
        if preds is not None:
            baseline_xy.append((preds, b["ys"]))
        for d in {dd for row in b["dims"] for dd in row}:
            col = [row.get(d, float("nan")) for row in b["dims"]]
            if not any(math.isnan(v) for v in col):
                per_dim_xy.setdefault(d, []).append((col, b["ys"]))

    if not groups:
        return EvalReport(
            n=n_valid, n_skipped=skipped, spearman=float("nan"), pearson=float("nan"),
            note="Need >= 3 valid records within a single comparable "
                 "(target, assay, readout, unit, batch) group to compute correlation.")

    per_dim = {d: _pool_and_corr(xy, _rank_percentile) for d, xy in per_dim_xy.items()}
    return EvalReport(
        n=n_valid,
        n_skipped=skipped,
        spearman=_pool_and_corr(total_xy, _rank_percentile),
        pearson=_pool_and_corr(total_xy, _zscore),
        spearman_fisher_mean=_fisher_mean([(g.spearman, g.n) for g in groups]),
        per_dimension_spearman=per_dim,
        baseline_spearman=_pool_and_corr(baseline_xy, _rank_percentile),
        groups=sorted(groups, key=lambda g: -g.n),
    )
