# CODE AUDIT REPORT: PENdp V3/V4 Scoring Engine

Audit date: 2026-05-15

Scope reviewed:
- `pendp/scoring/gates.py`
- `pendp/scoring/structure.py`
- `pendp/scoring/evolution.py`
- `pendp/scoring/engine.py`
- `pendp/cli.py`

Verification performed:
- `python -m compileall -q pendp/scoring pendp/cli.py` passed.
- Runtime probes covered empty, single-character, valid reference, and invalid-character sequences.
- CLI scoring path was attempted and crashed before dispatch due eager MLX import from search registration.

## Critical Issues

1. Shared gate definitions are mutated globally during calibration.
   - Location: `pendp/scoring/gates.py:237-239`, `pendp/scoring/gates.py:286-295`
   - `GatePipeline.__init__` assigns `self.gates = gates or PENDP_GATES`, so every default pipeline shares the same mutable `GateDef` objects. `calibrate()` then mutates `gate_def.pass_threshold` in-place.
   - This is not safe for concurrent use. One request or CLI command can silently change thresholds for all later `GatePipeline()` instances in the process. In threaded or service use, evaluations can observe partially updated thresholds.
   - Minimal fix: deep-copy `PENDP_GATES` per pipeline, or make `GateDef` immutable and store calibrated threshold overrides in pipeline-local state.

2. The CLI can abort before any scoring command runs because search registration imports MLX eagerly.
   - Location: `pendp/cli.py:120-121`, `pendp/search/cli.py:3`, `pendp/search/engine.py:21`
   - `main()` imports `pendp.search.cli.register`, which imports `SemanticSearch`, which imports `mlx.core` at module import time. In this audit environment, `python -m pendp.cli score --seq CRGDKGPDC --gates --log-json` terminated with an uncaught native `NSRangeException` from `libmlx.dylib` before reaching scoring.
   - This makes the new scoring CLI flags unusable on systems where MLX cannot initialize, even though scoring itself does not require MLX.
   - Minimal fix: make search imports fully lazy inside `cmd_search()` or inside `SemanticSearch._ensure_model()`, and keep `register()` dependency-free.

3. `--rank` batch gate ranking computes results but prints nothing useful.
   - Location: `pendp/cli.py:249-265`
   - The branch calls `engine.batch_gate_score()`, reconstructs unused `ranked_grs`, optionally prints JSON, and returns without printing `pipeline.batch_summary()` or ranked rows.
   - User-facing behavior is effectively silent for `pendp score --file ... --gates --rank` unless `--log-json` is set.
   - Minimal fix: print `batch["pipeline"].batch_summary(...)` or a structured ranked table using `batch["ranked"]`.

4. `structure_score("")` crashes on empty input.
   - Location: `pendp/scoring/structure.py:68-69`, `pendp/scoring/structure.py:203-213`
   - `StructureAnalyzer.analyze("")` returns `{"error": "Empty sequence"}`, but `structure_score()` immediately indexes `a["flexibility"]`, causing `KeyError`.
   - CLI `--structure` also calls `StructureAnalyzer().summary(a)`, which assumes normal result keys and will also crash for empty input.
   - Minimal fix: validate sequences before analysis, or return a full zeroed analysis object for empty input.

5. `DirectedEvolution.evolve(rounds=0)` crashes.
   - Location: `pendp/scoring/evolution.py:203-238`
   - With zero rounds, `results` remains empty, but `lineage` handling dereferences `results[-1]`.
   - The CLI exposes `--rounds` as an unrestricted integer at `pendp/cli.py:69`; users can pass `--rounds 0` or negative values.
   - Minimal fix: validate `rounds >= 1` in CLI and API, or return a no-op result for zero rounds.

## Warnings

1. Several scoring functions count unique residue types instead of residue frequency.
   - Locations: `pendp/scoring/engine.py:115-117`, `pendp/scoring/engine.py:187`, `pendp/scoring/engine.py:252`, `pendp/scoring/engine.py:333`, `pendp/scoring/structure.py:103`
   - Patterns such as `sum(1 for aa in "AVILMFWY" if aa in seq_upper)` count whether each residue type appears, not how many positions are hydrophobic/aromatic/etc.
   - This materially distorts long or repetitive peptides. Example: `AAAAAAAAAA` is counted as one hydrophobic residue, not ten.
   - Minimal fix: use `sum(1 for aa in seq_upper if aa in "...")` consistently.

2. Invalid amino-acid characters are silently accepted and scored as plausible peptides.
   - Locations: broadly across `engine.py`, `structure.py`, and `evolution.py`
   - Runtime probe: `"!!!!"` received a normal total score and structure score instead of validation failure.
   - Unknown residues default to neutral weights/propensities, which can hide malformed input from files or CLI.
   - Minimal fix: centralize sequence validation against the standard 20 amino acids plus any explicitly supported ambiguity codes.

3. Variant generation is capped after full list construction and is biased toward early positions.
   - Location: `pendp/scoring/evolution.py:66-108`
   - `generate_variants()` builds all variants, deduplicates, then returns `unique[:max_variants]`. For target 5-30aa peptides this is usually bounded, but with unvalidated long input it can allocate far more than needed.
   - For a 30-aa sequence in full mode, 570 point mutations plus enhancing variants are generated, but the first 500 are returned. This drops later positions and can drop all enhancing variants.
   - Minimal fix: stream variants with early stopping, or generate prioritized buckets and cap after preserving enhancing and terminal-position variants.

4. Evolution ranks by gate score and total score, not by the computed improvement.
   - Location: `pendp/scoring/evolution.py:146-164`, `pendp/scoring/evolution.py:189-190`
   - The code computes `improvement`, then sorts by `(eliminated, -gate_score, -total_score)`. `improvers[0]` is therefore not guaranteed to be the largest improvement.
   - The next parent can be selected from a variant that has a higher absolute score but smaller delta than another improver.
   - Minimal fix: decide whether evolution optimizes absolute score or delta; if delta, sort by `-improvement` after non-eliminated status.

5. Multi-round evolution reports only the final round's best improvement as `total_improvement`.
   - Location: `pendp/scoring/evolution.py:233-236`
   - This is not cumulative and can understate or misstate multi-round improvement.
   - Minimal fix: compare final score/gate score to original, or sum accepted round deltas.

6. Gate summary metrics are internally inconsistent after early critical failure.
   - Location: `pendp/scoring/gates.py:325-363`, `pendp/scoring/gates.py:88-131`
   - Evaluation stops at the first critical fail, so `total_gates` is the number evaluated, not the configured number. Pass rates and gate scores are not comparable between eliminated and non-eliminated candidates.
   - `overall_status` displays `critical_pass_count/total_gates`, but `critical_pass_count` actually includes both critical and important gates.
   - Minimal fix: append explicit `SKIP` results for remaining gates or separately report evaluated vs configured gates.

7. CLI `--verbose` is always enabled.
   - Location: `pendp/cli.py:73`, `pendp/cli.py:275-280`
   - `action="store_true", default=True` makes non-verbose output unreachable through argparse.
   - Minimal fix: use `default=False`, add `--quiet`, or use paired `BooleanOptionalAction` if Python 3.9 compatibility is not required.

8. `--calibrate --log-json` does not produce meaningful JSON audit logs.
   - Location: `pendp/cli.py:221-228`, `pendp/scoring/gates.py:244-313`
   - Calibration scores reference peptides but does not call gate evaluation, so `pipeline.flush_json()` is empty.
   - If calibration is expected to produce an audit artifact, log calibration stats and threshold changes explicitly.

9. `score_with_gates()` always creates a fresh uncalibrated `GatePipeline`.
   - Location: `pendp/scoring/engine.py:507-510`
   - This is not a resource leak by itself, but it means calibrated thresholds cannot be reused through this API except indirectly through the global mutation bug.
   - Minimal fix: accept an optional pipeline or pipeline factory, and remove global threshold mutation.

## Suggestions

1. Centralize peptide validation and normalization.
   - Add a shared helper such as `normalize_sequence(seq, allow_ambiguous=False)` and call it from scoring, gates, structure, evolution, and CLI file loading.
   - Validate target domain length of 5-30aa where applicable, or report when scoring outside the intended design space.

2. Add focused regression tests for V3/V4 behavior.
   - Empty sequence for `score_with_gates`, `structure_score`, `StructureAnalyzer.summary`, and `DirectedEvolution.evolve`.
   - Invalid characters.
   - Calibration does not affect independent pipeline instances.
   - `--rank` prints ranked output.
   - Evolution chooses the intended best variant.
   - Python/package import of `pendp.cli` does not load MLX unless search is invoked.

3. Make Chou-Fasman and structural constants configurable, but keep defaults.
   - Location: `pendp/scoring/structure.py:20-51`
   - Hardcoded defaults are acceptable for a small CPU-only module, but scientific reproducibility would benefit from named parameter sets or constructor injection.
   - Suggested shape: `StructureAnalyzer(propensity_table: Optional[StructureParams] = None, esm_model=None)`.

4. Make JSON logs structured around whole candidate evaluations.
   - Current JSONL records are per gate and omit total score, recommendation, and final gate decision.
   - Consider one candidate-level record with nested gates, or emit both candidate and per-gate records with a stable evaluation id.

5. Avoid broad `except Exception` around ESM-derived features unless failures are surfaced.
   - Locations: `pendp/scoring/engine.py:435-440`, `pendp/scoring/structure.py:161-173`
   - Silent fallback to neutral values is convenient, but it hides model/config failures during audit and benchmarking.
   - Consider warning-level logging or an optional strict mode.

## Design Feedback

The V3/V4 additions are directionally useful but need clearer state boundaries. `GatePipeline` should be a pure evaluator with explicit configuration, not a mutable global threshold manager. Calibration should produce a new calibrated pipeline/config object or a threshold override map. This would also answer the concurrency concern cleanly and make tests deterministic.

The scoring, structure, and evolution modules currently mix scientific heuristics with CLI-oriented display strings and emoji-rich messages. That is acceptable for a prototype, but production use would benefit from a strict data layer and a separate presentation layer. This matters for JSON audit logs and downstream batch processing.

The evolution engine needs an explicit optimization objective. The code currently computes improvement but selects mostly by absolute gate/total score. Both objectives can be valid, but the API and implementation should agree.

The CLI should avoid importing optional heavyweight subsystems during parser setup. Scoring should remain available on CPU-only or non-MLX environments, especially because the audit brief states no GPU is required.

## Answers to the 5 Key Questions

1. Is `calibrate()` in-place threshold modification safe for concurrent use?
   - No. It mutates shared `PENDP_GATES` objects because default pipelines reuse the global list. It is unsafe for concurrent use and can contaminate later evaluations in the same process.

2. Can `generate_variants()` producing up to 500 variants cause performance concerns?
   - For the intended 5-30aa peptides, CPU scoring of 500 variants is probably acceptable. The concerns are implementation quality: it constructs more than the cap before slicing, lacks input length validation, and the cap biases results toward early positions while potentially dropping enhancing variants.

3. Should hardcoded Chou-Fasman propensities be configurable?
   - Yes, ideally. Keeping defaults is fine, but they should be injectable or selected by named parameter set for reproducibility, benchmarking, and future calibration.

4. Does `score_with_gates()` creating a new `GatePipeline` every call leak resources?
   - No obvious resource leak. The pipeline is small and short-lived. The real issue is state design: fresh pipelines cannot intentionally reuse calibration, while the current global mutation can unintentionally reuse calibration.

5. Any code that would fail on Python 3.9 vs 3.11+?
   - Packaging declares `python_requires=">=3.10"`, so normal installation on Python 3.9 should be rejected. The reviewed V3/V4 source does not rely on obvious Python 3.11-only syntax, but `pendp/search/engine.py` uses `dict[...]` annotations, which are valid in 3.9, and `cli.py` should not use `BooleanOptionalAction` unless the project intentionally stays at 3.9+. Current metadata says 3.9 is unsupported.

## Overall Score

5/10

The core idea is coherent and the modules compile, but there are must-fix state-safety, CLI usability, empty-input, and ranking correctness issues. I would not treat the V3/V4 scoring path as production-ready until the critical issues and residue-counting bugs are fixed and covered by tests.
