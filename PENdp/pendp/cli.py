#!/usr/bin/env python3
"""
PENdp AI Peptide Design Platform — CLI Entry Point

Usage:
    pendp score --seq CRGDKGPDC                     Score a peptide
    pendp score --seq X --gates                       🔬 V3: Gate pipeline
    pendp score --seq X --gates --log-json            📋 V4: Gate audit log
    pendp score --seq X --gates --calibrate           🎯 G0 calibration
    pendp score --seq X --structure                   🔬 Structure analysis
    pendp score --seq X --evolve --rounds 3           🧬 V4: Directed evolution
    pendp score --file seqs.txt --gates --rank        📊 V4: Batch gate ranking

    pendp db list                                     List lung v6 database
    pendp db search --query RGD                       Search peptides
    pendp db targets                                  Show target knowledge graph

    pendp pipeline --mode quick --seqs seqs.txt       Quick screen (Stage 1)
    pendp pipeline --mode full --seqs seqs.txt        Full pipeline (all 5 stages)
    pendp pipeline --db                               Run on lung v6 database

    pendp target --for ipf                             Recommend targets for disease
    pendp cpp --seq CRGDKGPDC                         Predict CPP

    pendp decision --subsystems                       List targeting subsystems
    pendp decision --pipeline                         Show pipeline priorities
    pendp decision --evaluate IPF                     Evaluate an indication
    pendp decision --parallel                         Suggest parallel paths

    pendp competition                                 Competitive landscape
    pendp wetlab                                      Wet-lab plan & status
    pendp literature                                  Literature database
    pendp score curated --seq iRGD                    Curated reference score

    pendp info                                         Platform information
"""
import argparse
import sys
import json
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="PENdp AI Peptide Design Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    from pendp import __version__
    parser.add_argument("--version", action="version",
                        version=f"PENdp {__version__}")
    sub = parser.add_subparsers(dest="command", help="Command")

    # ── score ──
    p_score = sub.add_parser("score", help="Score peptide(s)")
    p_score.add_argument("--seq", type=str, help="Single peptide sequence")
    p_score.add_argument("--file", type=str, help="File with sequences (one per line)")
    p_score.add_argument("--esm", type=str, default=None,
                         choices=["8M", "35M", "150M", "650M"],
                         help="ESM-2 model for D7 scoring")
    p_score.add_argument("--gates", action="store_true", default=False,
                         help="🔬 V3/V4: Run gate pipeline (PASS/FAIL/COND)")
    p_score.add_argument("--calibrate", action="store_true", default=False,
                         help="🎯 V4: G0 calibration with reference peptides")
    p_score.add_argument("--log-json", action="store_true", default=False,
                         help="📋 V4: Output gate decisions as JSONL audit log")
    p_score.add_argument("--structure", action="store_true", default=False,
                         help="🔬 V4: Run structure analysis (Chou-Fasman + ESM)")
    p_score.add_argument("--evolve", action="store_true", default=False,
                         help="🧬 V4: Virtual directed evolution")
    p_score.add_argument("--rounds", type=int, default=3,
                         help="Evolution rounds (default: 3)")
    p_score.add_argument("--rank", action="store_true", default=False,
                         help="📊 V4: Gate-aware ranking (with --file)")
    p_score.add_argument("--verbose", action="store_true", default=False)

    # ── compare ──
    p_cmp = sub.add_parser("compare", help="Compare two peptides")
    p_cmp.add_argument("--a", type=str, required=True, help="First sequence")
    p_cmp.add_argument("--b", type=str, required=True, help="Second sequence")

    # ── cpp ──
    p_cpp = sub.add_parser("cpp", help="Predict CPP")
    p_cpp.add_argument("--seq", type=str, required=True, help="Peptide sequence")
    p_cpp.add_argument("--verbose", action="store_true", default=False)

    # ── score curated ──
    p_score_curated = sub.add_parser("curated", help="Curated reference score")
    p_score_curated.add_argument("--seq", type=str, required=True,
                                  help="Peptide name or sequence")

    # ── decision ──
    p_dec = sub.add_parser("decision", help="Decision framework")
    p_dec.add_argument("--subsystems", action="store_true",
                        help="List targeting subsystems")
    p_dec.add_argument("--pipeline", action="store_true",
                        help="Show pipeline priorities")
    p_dec.add_argument("--evaluate", type=str, metavar="INDICATION",
                        help="Evaluate an indication")
    p_dec.add_argument("--parallel", action="store_true",
                        help="Suggest parallel paths")

    # ── competition ──
    sub.add_parser("competition", help="Competitive landscape")

    # ── wetlab ──
    p_wet = sub.add_parser("wetlab", help="Wet-lab plan")
    p_wet.add_argument("--update", type=str, nargs=2,
                        metavar=("TASK_ID", "STATUS"),
                        help="Update task status")
    p_wet.add_argument("--timeline", action="store_true",
                        help="Show timeline view")

    # ── literature ──
    p_lit = sub.add_parser("literature", help="Literature database")
    p_lit.add_argument("--search", type=str, help="Search papers (keyword)")
    p_lit.add_argument("--semantic", type=str, help="🔍 Semantic search (AI-powered)")
    p_lit.add_argument("--export", action="store_true",
                        help="Export as markdown")

    # ── search (standalone) ── V4 fix: lazy import to avoid MLX crash on non-MLX systems
    _search_registered = False
    if "search" in sys.argv:
        from pendp.search.cli import register as register_search
        register_search(sub)
        _search_registered = True

    # ── db ──
    p_db = sub.add_parser("db", help="Database operations")
    p_db_sub = p_db.add_subparsers(dest="db_cmd")
    p_db_list = p_db_sub.add_parser("list", help="List lung v6 peptides")
    p_db_list.add_argument("--top", type=int, default=10, help="Show top N")
    p_db_search = p_db_sub.add_parser("search", help="Search peptides")
    p_db_search.add_argument("--query", type=str, required=True, help="Search query")
    p_db_targets = p_db_sub.add_parser("targets", help="Show target knowledge graph")

    # ── pipeline ──
    p_pipe = sub.add_parser("pipeline", help="Run screening pipeline")
    p_pipe.add_argument("--mode", type=str, default="quick",
                        choices=["quick", "full"], help="Pipeline mode")
    p_pipe.add_argument("--seqs", type=str, help="File with sequences")
    p_pipe.add_argument("--db", action="store_true",
                        help="Run on lung v6 database")
    p_pipe.add_argument("--esm", type=str, default=None,
                        choices=["8M", "35M", "150M", "650M"],
                        help="ESM-2 model size")

    # ── target ──
    p_tgt = sub.add_parser("target", help="Target knowledge graph queries")
    p_tgt.add_argument("--for", dest="disease", type=str,
                       help="Find targets for disease")
    p_tgt.add_argument("--organ", type=str, help="Find targets by organ")
    p_tgt.add_argument("--prioritize", action="store_true",
                       help="PENdp-specific target prioritization")

    # ── info ──
    sub.add_parser("info", help="Platform information")

    # ── eval ── (ROADMAP Phase 0: validate scoring vs wet-lab readouts)
    p_eval = sub.add_parser("eval", help="Evaluate scoring against wet-lab results")
    p_eval.add_argument("--dataset", type=str, default=None,
                        help="CSV of wet-lab results (default: pendp/data/wetlab_results.csv)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # ── Dispatch ──
    start = time.time()

    if args.command == "score":
        cmd_score(args)
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "cpp":
        cmd_cpp(args)
    elif args.command == "curated":
        cmd_curated(args)
    elif args.command == "decision":
        cmd_decision(args)
    elif args.command == "competition":
        cmd_competition()
    elif args.command == "wetlab":
        cmd_wetlab(args)
    elif args.command == "literature":
        cmd_literature(args)
    elif args.command == "db":
        cmd_db(args)
    elif args.command == "pipeline":
        cmd_pipeline(args)
    elif args.command == "target":
        cmd_target(args)
    elif args.command == "search":
        from pendp.search.cli import cmd_search
        cmd_search(args)
    elif args.command == "info":
        cmd_info()
    elif args.command == "eval":
        cmd_eval(args)

    elapsed = time.time() - start
    if elapsed > 1:
        print(f"\n⏱ {elapsed:.1f}s")


# ── Command implementations ──

def cmd_score(args):
    from pendp.scoring.engine import ScoringEngine

    sequences = []
    if args.seq:
        sequences.append(args.seq)
    if args.file:
        with open(args.file) as f:
            sequences.extend(line.strip() for line in f if line.strip())

    if not sequences:
        print("❌ No sequences provided. Use --seq or --file")
        sys.exit(1)

    engine = ScoringEngine()

    if args.esm:
        from pendp.esm.model import load_esm_model
        print(f"Loading ESM-2 {args.esm}...")
        model, tokenizer, _ = load_esm_model(args.esm)
        engine.esm_model = model
        engine.esm_tokenizer = tokenizer

    # ── V4: G0 Calibration ──
    if args.calibrate:
        from pendp.scoring.gates import GatePipeline
        pipeline = GatePipeline(log_json=args.log_json)
        calibrated = pipeline.calibrate(scoring_engine=engine)
        if args.log_json:
            print(calibrated.flush_json())
        return

    # ── V4: Structure analysis ──
    if args.structure:
        for seq in sequences:
            from pendp.scoring.structure import StructureAnalyzer, structure_score
            if not seq.strip():
                print("❌ Empty sequence — skipping structure analysis")
                continue
            analyzer = StructureAnalyzer(
                engine.esm_model if args.esm else None,
                engine.esm_tokenizer if args.esm else None,
            )
            a = analyzer.analyze(seq)
            if "error" in a:
                print(f"❌ {seq}: {a['error']}")
                continue
            ss = structure_score(seq)
            print(StructureAnalyzer().summary(a))
            print(f"  Structure Quality Score: {ss}/10")
        return

    # ── V4: Directed evolution ──
    if args.evolve:
        if args.rounds < 1:
            print("❌ --rounds must be >= 1")
            return
        for seq in sequences:
            from pendp.scoring.evolution import DirectedEvolution
            evolver = DirectedEvolution(scoring_engine=engine)
            result = evolver.evolve(seq, rounds=args.rounds, verbose=True)
            print(evolver.evolution_summary(result))
        return

    # ── V4: Batch gate ranking (with --file) ──
    if args.rank and args.file and args.gates:
        named = {f"seq_{i}": s for i, s in enumerate(sequences)}
        batch = engine.batch_gate_score(named, log_json=args.log_json)
        pipeline = batch["pipeline"]
        # Reconstruct for batch_summary
        ranked_data = []
        for r in batch["ranked"]:
            sr = engine.score_sequence(r["sequence"])
            dims = {dim_id: d["score"] for dim_id, d in sr["dimensions"].items()}
            gr = pipeline.evaluate(dims, r["sequence"])
            ranked_data.append((r["name"], gr, r["combined_score"]))
        print(pipeline.batch_summary(ranked_data))
        if batch["json_log"]:
            print("\n--- JSON Audit Log ---")
            print(batch["json_log"])
        return

    # ── Standard scoring (with optional gates) ──
    for seq in sequences:
        if args.gates:
            result = engine.score_with_gates(seq, verbose=args.verbose, log_json=args.log_json)
            if args.log_json and "gate_pipeline" in result:
                print(result["gate_pipeline"].get("json_log", ""))
        else:
            result = engine.score_sequence(seq, verbose=args.verbose)
        if "error" in result:
            print(f"❌ {seq}: {result['error']}")
            continue
        if not args.verbose:
            gate_info = ""
            if args.gates and "gate_pipeline" in result:
                gp = result["gate_pipeline"]
                gate_info = f" [{gp['overall_status']}]"
            print(f"{seq}: {result['total_score']}/100 [{result['recommendation']}]{gate_info}")


def cmd_compare(args):
    from pendp.scoring.engine import ScoringEngine
    engine = ScoringEngine()
    result = engine.batch_compare(args.a, args.b)

    print(f"\n{'='*50}")
    print(f"Compare: {args.a} vs {args.b}")
    print(f"{'='*50}")

    # Find names if in database
    from pendp.database.sequences import PeptideDatabase
    db = PeptideDatabase()
    a_entry = db.get_by_sequence(args.a)
    b_entry = db.get_by_sequence(args.b)
    if a_entry:
        print(f"  {args.a:20s} = {a_entry.name} ({a_entry.target})")
    if b_entry:
        print(f"  {args.b:20s} = {b_entry.name} ({b_entry.target})")

    print(f"\n  {'':30s} {args.a:>15s} {args.b:>10s}  Δ")
    print(f"  {'─'*58}")
    for dim_id, dim in sorted(result["dimensions"].items()):
        diff = dim["a_score"] - dim["b_score"]
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "="
        print(f"  {dim_id} {dim['name']:20s} "
              f"{dim['a_score']:8.1f}/10  {dim['b_score']:8.1f}/10  "
              f"{arrow}{abs(diff):.1f}")
    print(f"  {'─'*58}")
    print(f"  {'TOTAL':27s} {result['a_total']:8.1f}   {result['b_total']:8.1f}   "
          f"{'▲' if result['diff'] > 0 else '▼'}{abs(result['diff']):.1f}")


def cmd_cpp(args):
    from pendp.cpp.classifier import CPPClassifier
    classifier = CPPClassifier()
    result = classifier.predict(args.seq)
    print(f"\nCPP Prediction for {args.seq}:")
    print(f"  Probability: {result['cpp_probability']:.1%}")
    print(f"  Is CPP: {'✅ Yes' if result['is_cpp'] else '❌ No'}")
    print(f"  Method: {result['method']}")


def cmd_curated(args):
    from pendp.scoring.engine import ScoringEngine
    engine = ScoringEngine()
    result = engine.curated_score(args.seq)
    if result["source"] == "curated_database":
        print(f"\n📚 Curated Score for {result['name']} ({result['sequence']}):")
        print(f"  Total: {result['total_score']}/100 {'✅' if result['meets_threshold'] else '❌'}")
        print(f"  Target: {result['target']}")
        for i, s in enumerate(result['scores'], 1):
            print(f"  D{i}: {s}/10")
    else:
        print(f"\n⚙️  Computed Score for {args.seq}:")
        print(f"  Total: {result['total_score']}/100")


def cmd_decision(args):
    from pendp.decision.framework import (
        DecisionFramework, list_subsystems, pipeline_summary)

    if args.subsystems:
        print(f"\n🏥 PENdp 五大靶向子系统:")
        print(f"  {'子系统':12s} {'器官':10s} {'首选适应症':25s} {'配体'}")
        print(f"  {'─'*65}")
        for s in list_subsystems():
            ligands = ", ".join(s['key_ligands'][:3]) if s['key_ligands'] else "—"
            print(f"  {s['name']:12s} {s['organ']:10s} {s['top_indication']:25s} {ligands}")

    if args.pipeline:
        print(f"\n🏆 PENdp 管线优先级:")
        for p in pipeline_summary():
            print(f"  #{p['rank']} {p['indication']:25s} {p['strategy']:30s} {p['timeline']}")

    if args.evaluate:
        decider = DecisionFramework()
        result = decider.evaluate_indication(args.evaluate)
        print(f"\n📊 适应症评估: {result['indication']}")
        for dim, score in result['dimensions'].items():
            bar = "█" * score + "░" * (10 - score)
            print(f"  {dim:12s} {score}/10 {bar}")
        print(f"  {'─'*30}")
        print(f"  平均: {result['average_score']}/10 → 决策: {result['decision']}")

    if args.parallel:
        print(f"\n🔄 并行路径建议:")
        from pendp.decision.framework import DecisionFramework
        for path in DecisionFramework().suggest_parallel_paths():
            print(f"  📌 {path['path']}")
            print(f"     适应症: {', '.join(path['indications'])}")
            print(f"     成本: {path['cost']} | 时间: {path['timeline']}")
            print(f"     理由: {path['rationale']}")
            print()


def cmd_competition():
    from pendp.decision.competition import CompetitiveLandscape
    cl = CompetitiveLandscape()
    print(f"\n🔬 PENdp 竞争格局")
    print(f"{'='*50}")
    s = cl.summary()
    print(f"  追踪: {s['total']} 个 (平台{s['platforms']} + 疗法{s['therapies']})")
    print(f"  最接近: {', '.join(s['closest'])}")
    print(f"  可合作: {', '.join(s['collaboration'])}")
    print(f"\n  IPF赛道:")
    ipf = cl.ipf_landscape()
    print(f"    核酸竞品: {ipf['nucleic_acid_competitors']}")
    print(f"    小分子: {ipf['small_molecule']}")
    print(f"    启示: {ipf['implication']}")


def cmd_wetlab(args):
    from pendp.wetlab.tracker import WetLabTracker
    tracker = WetLabTracker()

    if args.update:
        task_id, status = args.update
        tracker.update_status(task_id, status)
        print(f"✅ {task_id} → {status}")

    print(f"\n🧪 湿实验行动计划")
    print(f"{'='*50}")
    s = tracker.summary()
    print(f"  完成: {s['completion']}")

    if args.timeline:
        print(f"\n  📅 时间线:")
        for t in tracker.timeline():
            emoji = {"pending": "⬜", "in_progress": "🔄", "completed": "✅", "blocked": "🔴"}
            print(f"  {emoji.get(t['status'], '⬜')} {t['id']:6s} {t['desc']:45s} {t['timeline']}")
    else:
        print(f"\n  优先级排序:")
        for t in tracker.by_priority():
            emoji = {"pending": "⬜", "in_progress": "🔄", "completed": "✅", "blocked": "🔴"}
            print(f"  {emoji.get(t.status, '⬜')} {t.id:6s} {t.description:45s} [{t.timeline:12s}]")


def cmd_literature(args):
    from pendp.literature.papers import LiteratureDatabase
    ld = LiteratureDatabase()

    if args.semantic:
        from pendp.search.engine import SemanticSearch
        se = SemanticSearch()
        print()
        se.index_literature()
        print()
        results = se.query(args.semantic, top_k=5)
        print(f"\n🔍 语义搜索: '{args.semantic}'")
        se.show_results(results)
        return

    if args.export:
        md = ld.export_markdown()
        path = "/tmp/pendp_literature.md"
        with open(path, "w") as f:
            f.write(md)
        print(f"📄 已导出到 {path}")
        return

    if args.search:
        results = ld.search(args.search)
        print(f"\n📚 文献搜索: '{args.search}'")
        for p in results:
            print(f"  📄 {p.title}")
            print(f"     来源: {p.source} ({p.year})")
            print(f"     PENdp: {p.relevance_to_pendp}")
    else:
        print(f"\n📚 PENdp 文献数据库")
        s = ld.summary()
        print(f"  共 {s['total']} 篇 (高优先级 {s['high']})")
        for p in ld.by_priority("high"):
            print(f"  ⭐ {p.title}")
            print(f"     {p.authors} - {p.source} ({p.year})")


def cmd_db(args):
    from pendp.database.sequences import PeptideDatabase
    from pendp.database.targets import TargetKnowledgeGraph

    db = PeptideDatabase()

    if args.db_cmd == "list" or not args.db_cmd:
        n = args.top if hasattr(args, 'top') else 10
        print(f"\n{'='*60}")
        print(f"PENdp 肺靶向数据库 v6 — Top {n}")
        print(f"{'='*60}")
        print(f"  {'Rank':<5s} {'Name':<12s} {'Sequence':<20s} {'Target':<25s} {'Score':>6s}")
        print(f"  {'─'*68}")
        for p in db.top_n(n):
            stars = "⭐" * (4 if p.score_total >= 80 else 3 if p.score_total >= 70 else 2)
            print(f"  {p.rank:<5d} {p.name:<12s} {p.sequence:<20s} "
                  f"{p.target:<25s} {p.score_total:>5.1f} {stars}")

    elif args.db_cmd == "search":
        results = db.search(args.query)
        if not results:
            print(f"No results for '{args.query}'")
            return
        print(f"\nSearch results for '{args.query}':")
        print(f"  {'Name':<12s} {'Sequence':<20s} {'Score':>6s}  {'Target'}")
        print(f"  {'─'*60}")
        for p in results:
            print(f"  {p.name:<12s} {p.sequence:<20s} {p.score_total:>5.1f}  {p.target}")

    elif args.db_cmd == "targets":
        kg = TargetKnowledgeGraph()
        s = kg.summary()
        print(f"\nPENdp 靶点知识图谱")
        print(f"{'='*50}")
        print(f"  受体总数: {s['total_targets']}")
        print(f"  覆盖器官: {', '.join(s['organs_covered'])}")
        print(f"  多肽配体: {len(s['peptide_ligands'])} 条")
        print(f"\n  TOP 靶点 (按PENdp优先推荐):")
        for t in kg.prioritize_for_pendp()[:5]:
            print(f"  ⭐{'⭐' * (t['priority_raw']-2)} {t['target']:15s} "
                  f"| {t['organ']:10s} | 配体: {t['top_ligand']:15s} | {', '.join(t['diseases'][:2])}")


def cmd_pipeline(args):
    from pendp.pipeline.orchestrator import PipelineOrchestrator
    from pendp.database.sequences import PeptideDatabase

    sequences = []
    if args.db:
        db = PeptideDatabase()
        sequences = [p.sequence for p in db.lung_v6]
        print(f"📂 从数据库加载 {len(sequences)} 条序列")

    if args.seqs:
        with open(args.seqs) as f:
            file_seqs = [line.strip() for line in f if line.strip()]
            sequences.extend(file_seqs)
        print(f"📂 从文件加载 {len(file_seqs)} 条序列")

    if not sequences:
        print("❌ No sequences. Use --db or --seqs")
        sys.exit(1)

    orch = PipelineOrchestrator()

    if args.esm:
        orch.load_esm(args.esm)
    else:
        print("ℹ️  No ESM model specified, using rule-based scoring only")
        print("   (D7 ESM similarity defaults to neutral 5.0)")
    if args.mode == "quick":
        result = orch.run_quick_screen(sequences)
    else:
        result = orch.run_full_pipeline(sequences)


def cmd_target(args):
    from pendp.database.targets import TargetKnowledgeGraph
    kg = TargetKnowledgeGraph()

    if args.disease:
        targets = kg.by_disease(args.disease)
        print(f"\n🎯 Targets for '{args.disease}':")
        print(f"  {'Target':<12s} {'Organ':<10s} {'Ligands':<25s} {'Priority':<8s}")
        print(f"  {'─'*55}")
        for t in targets:
            ligands = ", ".join(t.ligands) if t.ligands else "(none)"
            stars = "⭐" * t.priority
            print(f"  {t.name:<12s} {t.organ:<10s} {ligands:<25s} {stars:<8s}")

    if args.organ:
        targets = kg.by_organ(args.organ)
        print(f"\n🎯 Targets in '{args.organ}':")
        for t in targets:
            ligands = ", ".join(t.ligands) if t.ligands else "(none)"
            print(f"  {t.name:15s} — {ligands} — 疾病: {', '.join(t.diseases[:2])}")

    if args.prioritize:
        print(f"\n🏆 PENdp 靶点优先推荐:")
        for t in kg.prioritize_for_pendp()[:7]:
            print(f"  {t['score']:2d}分 {t['target']:15s} {t['organ']:10s} "
                  f"→ {t['top_ligand']}")
            for d in t['diseases']:
                print(f"    关联疾病: {d}")
def cmd_eval(args):
    from pendp.eval import load_dataset, evaluate_scoring, DEFAULT_DATASET, SCHEMA_COLUMNS
    path = args.dataset or DEFAULT_DATASET
    records = load_dataset(path)
    if not records:
        print(f"ℹ️  No wet-lab results found in {path}.")
        print(f"   Add rows under this header, then re-run `pendp eval`:")
        print(f"   {','.join(SCHEMA_COLUMNS)}")
        print(f"   (direction = higher_better | lower_better)")
        return
    report = evaluate_scoring(records)
    print(report.summary())


def cmd_info():
    from pendp.decision.framework import list_subsystems, pipeline_summary
    from pendp.wetlab.tracker import WetLabTracker
    from pendp.literature.papers import LiteratureDatabase

    subs = list_subsystems()
    pipe = pipeline_summary()
    wet = WetLabTracker().summary()
    lit = LiteratureDatabase().summary()

    print(f"""
╔══════════════════════════════════════╗
║      PENdp AI Peptide Design         ║
║      积雪草酸+ELP-LNP+多肽修饰        ║
╚══════════════════════════════════════╝

Version: 1.0.0 (融合版)

Core Modules:
  📦 pendp.scoring       7维度评分引擎 v2.0 + D9偶联方向 + Custom Reference
  📦 pendp.database      肺靶向v6 + 靶点知识图谱 + 多器官数据库
  📦 pendp.esm           ESM-2 embedding (8M/35M/150M/650M)
  📦 pendp.cpp           CPP classifier (ML + 规则)
  📦 pendp.pipeline      五关融合漏斗 + Stage 0决策
  📦 pendp.decision      五大靶向子系统 + 管线优先级 + 竞争对标  🆕
  📦 pendp.wetlab        湿实验追踪 (7项任务)  🆕
  📦 pendp.literature    文献数据库 ({lit['total']}篇)  🆕
  📦 pendp.search        jina-embeddings-v5-omni 语义搜索 (MLX 本地推理) 🆕

Target: {len(subs)} 器官子系统 | {len(pipe)} 管线推荐
Wet-lab: {wet['completed']}/{wet['total']} 完成
Pipeline (五关漏斗):
  Stage 0: 决策框架 🆕  |  1️⃣ ML  |  2️⃣ AF3 ⏳  |  3️⃣ MD ⏳  |  4️⃣ QSAR ⏳  |  5️⃣ 湿实验

Quick start:
  $ pendp score --seq CRGDKGPDC
  $ pendp score curated --seq iRGD
  $ pendp decision --subsystems
  $ pendp pipeline --db --esm 150M
  $ pendp wetlab --timeline
""")


def _count_peptides():
    try:
        from pendp.database.sequences import PeptideDatabase
        return len(PeptideDatabase().lung_v6)
    except Exception:
        return "?"


if __name__ == "__main__":
    main()
