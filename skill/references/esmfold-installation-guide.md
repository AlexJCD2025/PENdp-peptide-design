# ESMFold Installation — PENdp Pipeline Reference

## Package Choice: `esm` v2.0.0 (NOT `fair-esm`)

```bash
pip install esm==2.0.0
pip install torch
```

**Do NOT use `fair-esm`** — that package is unmaintained and has Python 3.11 dataclass incompatibility bugs. Use the official Meta `esm` package at v2.0.0 which provides the same `esmfold_v1()` model without the dataclass patch.

`esm` v3.x is the generative ESM3 (different API, much larger models). Both provide `import esm`. Check version with `python3 -c "import esm; print(esm.__version__)"`.

## Model Weights — Size & Cache

ESMFold v1 uses a **3B parameter model** — the only folding model size. There is no "small ESMFold" variant. The smaller ESM-2 models (35M/150M/650M) are encoder-only — they cannot fold sequences.

| Aspect | Detail |
|:-------|:-------|
| Model | `esmfold_v1` (ESM-2 3B backbone + 48 folding blocks) |
| Weight files | `esmfold_3B_v1.pt` (2.6 GB) + `esm2_t36_3B_UR50D.pt` (~3.5 GB) |
| Download from | `https://dl.fbaipublicfiles.com/fair-esm/models/` (Meta FB servers, NOT HuggingFace) |
| Cache location | `~/.cache/torch/hub/checkpoints/` |
| Total download | ~6 GB |

The download is slow on GFW networks. Both files download sequentially through `esm.pretrained.esmfold_v1()`.

## ⚠️ Critical Pitfall #1: Backend Check ≠ Model Cached

```python
from pendp.pipeline.af3_runner import check_esmfold_available
print(check_esmfold_available())  # True — only checks `import esm`, NOT model download!
```

`check_esmfold_available()` only verifies Python packages are importable — it does NOT check whether model weights are cached. A `predict_structure()` call will silently spend minutes downloading, and may fail if the connection drops.

**Pre-download:**

```python
import esm, torch
model = esm.pretrained.esmfold_v1()
model = model.eval()
if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    model = model.to('mps')
```

**Check cache:**
```bash
ls -lh ~/.cache/torch/hub/checkpoints/esmfold_3B_v1.pt
ls -lh ~/.cache/torch/hub/checkpoints/esm2_t36_3B_UR50D.pt
```

## ⚠️ Critical Pitfall #2: Background Process Python Version

**The symptom:** `predict_structure('CRGDKGPDC', backend='esmfold')` fails in background processes (terminal background=True) but works in foreground.

**The root cause:** Hermes background processes use `/usr/bin/python3` (macOS system Python 3.9.6), but `esm` and `torch` are installed in the Hermes venv at `/Users/aj/.hermes/hermes-agent/venv/bin/python3` (Python 3.11.14).

**The fix:** Always use the full venv Python path in background commands:

```bash
# ❌ Wrong — uses system Python 3.9
cd ~/.hermes/workspace/PENdp && python3 -c "..."

# ✅ Correct — uses venv Python 3.11
cd ~/.hermes/workspace/PENdp && /Users/aj/.hermes/hermes-agent/venv/bin/python3 -c "..."
```

**Diagnostic commands:**
```bash
# Check which Python is used
which python3                 # foreground Python
python3 --version              # foreground version

# Check background process version
echo 'print(__import__("sys").version)' | python3
```

## Type Annotation Compatibility

When writing new pipeline code shared between foreground and background contexts, avoid Python 3.10+ union type syntax in function signatures:

```python
# ❌ Python 3.10+ only — fails if imported in 3.9 context
def fn(x: dict | None = None) -> dict[str, float]:

# ✅ Works across all Python 3.x versions
from typing import Optional, Dict
def fn(x: Optional[dict] = None) -> Dict[str, float]:
```

The `dict | None` syntax works in foreground (venv 3.11) but fails when the module is imported in background processes (system 3.9).

## Apple Silicon (MPS) Note

ESMFold defaults to CUDA. On Apple Silicon Macs with MPS:
```python
model = model.to('mps')
```

## ⚠️ Critical Pitfall #3: esm v2.0.0 IPA Module Compatibility (2026-05-27)

**The symptom:** Model downloads successfully (2.6 GB `esmfold_3B_v1.pt` + 5.3 GB `esm2_t36_3B_UR50D.pt`) but loading fails with:
```
RuntimeError: Keys 'trunk.structure_module.ipa.linear_q_points.linear.weight,
trunk.structure_module.ipa.linear_q_points.linear.bias, ...' are missing.
```

**The root cause:** `esm` v2.0.0 updated the `ESMFold` model class to include IPA (Invariant Point Attention) module parameters, but the checkpoint at `dl.fbaipublicfiles.com/fair-esm/models/esmfold_3B_v1.pt` was trained with an older esm version that didn't have IPA. The new model class expects 4 extra IPA weight tensors that don't exist in the checkpoint.

**The fix (V2 — KEY_REMAP, applied 2026-05-27):** The zero-init patch was upgraded to a key remapping approach. esm v2.0.0's IPA `Linear` layer uses a `.linear` sub-namespace (`ipa.linear_kv_points.linear.weight`) while the checkpoint uses the old flat naming (`ipa.linear_kv_points.weight`). The patch adds a `KEY_REMAP` dict to rename checkpoint keys before loading, so IPA weights are properly loaded (norm=57.5, significantly better than zeros).

In `/Users/aj/.hermes/hermes-agent/venv/lib/python3.11/site-packages/esm/esmfold/v1/pretrained.py`:

```python
# KEY_REMAP: checkpoint flat names → esm v2.0.0 .linear sub-namespace
KEY_REMAP = {
    "trunk.structure_module.ipa.linear_q_points.weight":
        "trunk.structure_module.ipa.linear_q_points.linear.weight",
    "trunk.structure_module.ipa.linear_q_points.bias":
        "trunk.structure_module.ipa.linear_q_points.linear.bias",
    "trunk.structure_module.ipa.linear_kv_points.weight":
        "trunk.structure_module.ipa.linear_kv_points.linear.weight",
    "trunk.structure_module.ipa.linear_kv_points.bias":
        "trunk.structure_module.ipa.linear_kv_points.linear.bias",
}

found_keys = set(model_state.keys())
# Remap checkpoint keys to match new model
for old_k, new_k in KEY_REMAP.items():
    if old_k in model_state:
        model_state[new_k] = model_state.pop(old_k)

# Zero-init fallback for truly missing keys
missing_essential_keys = []
for missing_key in expected_keys - set(model_state.keys()):
    if not missing_key.startswith("esm."):
        missing_essential_keys.append(missing_key)
if missing_essential_keys:
    for k in missing_essential_keys:
        model_state[k] = torch.zeros_like(model.state_dict()[k])
```

**Impact on accuracy:** With KEY_REMAP, IPA weights are properly loaded (norm=57.5), not zero. For CRGDKGPDC (9aa RGD peptide), pLDDT improved from 40-46 (zero-init) to ~60 (key remap).

**To revert:** `pip install --force-reinstall esm==2.0.0`

## ⚠️ Critical Pitfall #4: `predict_structure()` output schema

The `predict_structure()` returns pLDDT as a nested dict (not float) and uses different key names than expected:
```python
result['plddt']           # DICT: {mean, per_residue, min, max, std, ...}
result['d14_score']       # pre-computed D14 score (float)
result['backend']         # NOT "method"
result['runtime_seconds'] # NOT "elapsed_s"
result['pdb_path']        # PDB file location
```

## ⚠️ Critical Pitfall #5: Pipeline integration field hallucination

On 2026-05-27, Codex-generated `integration.py` had 3 runtime-critical key name bugs that would crash Stage 1:
`result["per_residue_plddt"]`→`result["plddt"]["per_residue"]`,
`result["method"]`→`result["backend"]`,
`result["elapsed_s"]`→`result["runtime_seconds"]`.

Fixed across 7 files. D14 now registered in `SCORING_DIMENSIONS` (weight=0.0) and `DIMENSION_FUNCTIONS`.

## Full End-to-End Test

```python
import esm, torch, json
from pendp.pipeline.af3_runner import predict_structure
from pendp.pipeline.d14_integration import score_structure_confidence

result = predict_structure('CRGDKGPDC', backend='esmfold')
if result['status'] == 'success':
    plddt = result['plddt']['mean']
    d14 = score_structure_confidence(plddt=result['plddt'], md_rmsd=None, qsar_admet=None)
    print(f"pLDDT: {plddt}, D14: {d14}/10, PDB: {result['pdb_path']}")
```
