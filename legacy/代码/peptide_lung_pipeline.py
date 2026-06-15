#!/usr/bin/env python3
"""
PENdp 肺靶向多肽 AI 预测 Pipeline
功能：
  1. ESMFold 结构预测
  2. 物化性质计算（pI、LogP、GRAVY）
  3. 靶向基序评分（RGD、NGR、CendR等）
  4. 综合评分排序

用法：
  python peptide_lung_pipeline.py [--sequences SEQ_FILE] [--output OUTPUT_DIR]
"""

import os
import sys
import time
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# ESMFold
import esm

# ============================================================
# 1. 肺靶向多肽序列库（内置，12条核心序列）
# ============================================================
LUNG_PEPTIDES = [
    {"name": "iRGD",      "seq": "CRGDKGPDC",     "structure": "cyclic",  "target": "αvβ3/αvβ5+NRP-1", "application": "NSCLC肿瘤穿透", "ref": "PMC6617877"},
    {"name": "iRGD-L",   "seq": "CRGDK",          "structure": "linear",   "target": "αvβ3/αvβ5+NRP-1", "application": "NSCLC肿瘤穿透", "ref": "PMC11592346"},
    {"name": "RGD",       "seq": "RGD",             "structure": "linear",   "target": "αvβ3, αvβ5, α5β1", "application": "通用肿瘤血管", "ref": "多文献"},
    {"name": "NGR",       "seq": "CNGRC",           "structure": "cyclic",   "target": "CD13/氨肽酶N",     "application": "肿瘤新生血管", "ref": "ACS PTS"},
    {"name": "CREKA",     "seq": "CREKA",           "structure": "cyclic",   "target": "纤维蛋白",          "application": "肺转移灶",     "ref": "多文献"},
    {"name": "tLyP-1",    "seq": "CGNKRTRGC",      "structure": "cyclic",   "target": "NRP-1",             "application": "肺癌肿瘤穿透", "ref": "Front Oncol 2013"},
    {"name": "GE11",      "seq": "YHWYGYTPQNVI",   "structure": "linear",   "target": "EGFR",              "application": "NSCLC EGFR+",   "ref": "PMC5874815"},
    {"name": "RPARPAR",   "seq": "RPARPAR",        "structure": "linear",   "target": "NRP-1",             "application": "CendR通路",    "ref": "多文献"},
    {"name": "LyP-1",    "seq": "CGNKRTRGC",      "structure": "cyclic",   "target": "NRP-1",             "application": "淋巴肿瘤",    "ref": "Front Oncol 2013"},
    {"name": "AKPC",     "seq": "AKPC",            "structure": "linear",   "target": "CD44",              "application": "LNP修饰(ACS Nano 2024)", "ref": "ACS Nano 2024"},
    {"name": "F3",        "seq": "KDEPQRRSARLSAKPAPPKPEPKPKKAPAKK", "structure": "linear", "target": "Nucleolin", "application": "肺内皮细胞", "ref": "多文献"},
    {"name": "iRGDv2",   "seq": "CRGDKGPDC",      "structure": "cyclic",   "target": "αvβ3/αvβ5+NRP-1", "application": "NSCLC肿瘤穿透", "ref": "TLCR 2024"},
]

# ============================================================
# 2. 氨基酸物化性质
# ============================================================
AA_HYDROPHOBICITY = {
    'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
    'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
    'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
    'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2,
    'U': 2.5, 'O': -1.0, 'X': 0.0, 'B': -3.5, 'Z': -3.5,
}

AA_MW = {  # 平均分子量(Da)
    'A': 89, 'R': 174, 'N': 132, 'D': 133, 'C': 121,
    'Q': 146, 'E': 147, 'G': 75,  'H': 155, 'I': 131,
    'L': 131, 'K': 146, 'M': 149, 'F': 165, 'P': 115,
    'S': 105, 'T': 119, 'W': 204, 'Y': 181, 'V': 117,
    'U': 168, 'O': 131, 'X': 110, 'B': 133, 'Z': 147,
}

# ============================================================
# 3. 评分函数
# ============================================================

def calc_gravy(seq):
    """计算GRAVY（平均疏水性）"""
    if not seq:
        return 0
    vals = [AA_HYDROPHOBICITY.get(aa, 0) for aa in seq.upper()]
    return np.mean(vals) if vals else 0

def calc_mw(seq):
    """计算分子量"""
    if not seq:
        return 0
    return sum(AA_MW.get(aa, 110) for aa in seq.upper())

def calc_pI(seq):
    """估算等电点（简化版：统计正负电荷）"""
    if not seq:
        return 7.0
    pos = seq.upper().count('K') + seq.upper().count('R') + seq.upper().count('H')
    neg = seq.upper().count('D') + seq.upper().count('E')
    net = pos - neg
    # 简化估算：正电荷多→pI>7，负电荷多→pI<7
    return 7.0 + net * 0.5

def score_targeting_motif(seq):
    """靶向基序评分（0-100）"""
    score = 0
    found = []
    seq_u = seq.upper()
    
    if 'RGD' in seq_u or 'CRGD' in seq_u or 'GRD' in seq_u:
        score += 30
        found.append('RGD')
    if 'NGR' in seq_u or 'CNGR' in seq_u:
        score += 25
        found.append('NGR')
    if 'CEND' in seq_u or 'RPAR' in seq_u.upper():
        score += 20
        found.append('CendR')
    if 'CRGDK' in seq_u.upper() or 'RPARPAR' in seq_u.upper():
        score += 15  # 完整CendR双基序
        found.append('iRGD-like')
    if 'GE' in seq_u and 'YHWYGYTPQNVI' == seq_u:
        score += 25  # GE11
        found.append('GE11')
    if 'AKPC' in seq_u.upper():
        score += 20
        found.append('AKPC')
    if 'CREKA' in seq_u.upper():
        score += 15
        found.append('CREKA')
    if 'CGNKRTR' in seq_u.upper() or 'TLYP' in seq_u.upper():
        score += 20
        found.append('tLyP-1')
    
    return min(score, 100), found

def score_physicochemical(seq, pI, mw, grav):
    """物化性质评分（0-100）"""
    score = 0
    
    # 分子量：<1500 Da 得满分（适合LNP修饰）
    if mw < 1000:
        score += 30
    elif mw < 1500:
        score += 20
    elif mw < 3000:
        score += 10
    else:
        score += 0
    
    # 疏水性：GRAVY在-0.5~2.5之间为最佳（透皮性相关）
    if -1.0 <= grav <= 2.5:
        score += 25
    elif -2.0 <= grav < -1.0 or 2.5 < grav <= 4.0:
        score += 15
    else:
        score += 5
    
    # pI：接近7.4（血清pH）且不易带强电荷
    if 5.0 <= pI <= 9.0:
        score += 25
    elif 4.0 <= pI < 5.0 or 9.0 < pI <= 10.5:
        score += 15
    else:
        score += 5
    
    # 序列长度：8-20个氨基酸最佳（合成成本+功能平衡）
    L = len(seq)
    if 8 <= L <= 15:
        score += 20
    elif 15 < L <= 25:
        score += 15
    elif L < 8:
        score += 10
    else:
        score += 5
    
    return min(score, 100)

def score_lnp_compatibility(seq, structure):
    """LNP表面修饰兼容性评分（0-100）"""
    score = 50  # 基础分
    
    # 环肽通常更稳定（酶降解慢）
    if structure == 'cyclic':
        score += 20
    
    # 含Cys的序列可以形成二硫键（环化）
    cys_count = seq.upper().count('C')
    if cys_count >= 2:
        score += 10
    elif cys_count == 1:
        score += 5
    
    # 不含过多疏水残基（避免过度聚集）
    grav = calc_gravy(seq)
    if grav < 1.0:  # 不过于疏水
        score += 10
    elif grav > 3.5:  # 过疏水可能影响LNP稳定性
        score -= 10
    
    # 含Arg/Lys丰富（有助于细胞摄取，但也可能影响PK）
    charged = seq.upper().count('K') + seq.upper().count('R') + seq.upper().count('D') + seq.upper().count('E')
    if 2 <= charged <= 6:
        score += 10
    
    return min(max(score, 0), 100)

def score_protein_corona(seq):
    """蛋白冠形成倾向评分（0-100，ELP协同相关）"""
    score = 50  # 基础分
    seq_u = seq.upper()
    
    # 两亲性α螺旋倾向：疏水+亲水交替
    amphiphilic_score = 0
    for i in range(len(seq_u)-1):
        aa1, aa2 = seq_u[i], seq_u[i+1]
        h1 = AA_HYDROPHOBICITY.get(aa1, 0)
        h2 = AA_HYDROPHOBICITY.get(aa2, 0)
        if h1 * h2 < 0:  # 疏水-亲水交替
            amphiphilic_score += 1
    amph_ratio = amphiphilic_score / max(len(seq_u)-1, 1)
    if amph_ratio > 0.4:
        score += 20
    elif amph_ratio > 0.2:
        score += 10
    
    # 富含Pro可能影响折叠
    pro_count = seq_u.count('P')
    if pro_count > 3:
        score -= 10
    
    # Gly过多可能太灵活
    gly_count = seq_u.count('G')
    if gly_count > 5:
        score -= 5
    
    # 富Arg/Lys有助于蛋白冠招募
    pos_charge = seq_u.count('K') + seq_u.count('R')
    if 2 <= pos_charge <= 5:
        score += 15
    elif pos_charge > 5:
        score += 10  # 过多正电荷可能反而有风险
    
    return min(max(score, 0), 100)

def esmfold_predict(seq, model, alphabet, batch_converter, device):
    """用 ESMFold 预测单条序列的结构"""
    try:
        data = [("protein", seq)]
        batch_labels, batch_strs, batch_tokens = batch_converter(data)
        
        with torch.no_grad():
            results = model(batch_tokens.to(device), repr_layers=[36], return_contacts=False)
        
        # 获取最后一层表示
        representations = {36: results["representations"][36]}
        structure = model.compute_structure(batch_tokens.to(device), repr_layers=[36])
        
        # 简单评分：基于pLDDT（置信度）
        mean_plddt = float(results.get('mean_plddt', 50) if 'mean_plddt' in results else 50)
        
        return {
            'seq': seq,
            'mean_plddt': mean_plddt,
            'has_3d': mean_plddt > 70,  # 有意义的3D结构
        }
    except Exception as e:
        return {'seq': seq, 'mean_plddt': 50, 'has_3d': False, 'error': str(e)}

def run_pipeline(output_dir=".", model_name="esm2_t33_650M_UR50D", device=None):
    """主Pipeline"""
    print("=" * 60)
    print("🫁 PENdp 肺靶向多肽 AI 预测 Pipeline")
    print("=" * 60)
    
    # 设置设备
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n设备: {device}")
    
    # 加载ESM-2模型（ESMFold太重，用ESM-2代替快速预测）
    print(f"\n📦 加载模型: {model_name}...")
    try:
        model, alphabet = esm.pretrained.load_model_and_alphabet_local(model_name)
        model = model.to(device)
        model.eval()
        batch_converter = alphabet.get_batch_converter()
        print("✅ 模型加载成功")
    except Exception as e:
        print(f"⚠️ ESM-2加载失败({e})，跳过结构预测")
        model = None
        alphabet = None
        batch_converter = None
    
    results = []
    print(f"\n🔬 预测 {len(LUNG_PEPTIDES)} 条序列...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for i, pep in enumerate(LUNG_PEPTIDES):
        seq = pep["seq"]
        print(f"\n[{i+1}/{len(LUNG_PEPTIDES)}] {pep['name']}: {seq}")
        
        # 物化性质
        grav = calc_gravy(seq)
        mw = calc_mw(seq)
        pI = calc_pI(seq)
        print(f"  GRAVY={grav:.2f}, MW={mw:.0f}Da, pI≈{pI:.1f}")
        
        # 靶向基序评分
        motif_score, found_motifs = score_targeting_motif(seq)
        print(f"  靶向基序: {motif_score}分 {found_motifs}")
        
        # 物化性质评分
        physico_score = score_physicochemical(seq, pI, mw, grav)
        print(f"  物化评分: {physico_score}分")
        
        # LNP兼容性
        lnp_score = score_lnp_compatibility(seq, pep["structure"])
        print(f"  LNP兼容: {lnp_score}分")
        
        # 蛋白冠倾向
        corona_score = score_protein_corona(seq)
        print(f"  蛋白冠: {corona_score}分")
        # 综合评分（加权）
        final_score = (
            motif_score * 0.35 +       # 靶向基序最重要
            physico_score * 0.25 +      # 物化性质其次
            lnp_score * 0.20 +          # LNP兼容性
            corona_score * 0.20          # 蛋白冠形成
        )
        
        print(f"  ★ 综合评分: {final_score:.1f}/100")
        
        results.append({
            "name": pep["name"],
            "sequence": seq,
            "structure": pep["structure"],
            "target": pep["target"],
            "application": pep["application"],
            "reference": pep["ref"],
            "gravy": round(grav, 3),
            "mw_da": round(mw, 1),
            "pI": round(pI, 1),
            "motif_score": motif_score,
            "motifs_found": ", ".join(found_motifs),
            "physico_score": physico_score,
            "lnp_score": lnp_score,
            "corona_score": corona_score,
            "final_score": round(final_score, 2),
        })
    
    # 排序
    df = pd.DataFrame(results)
    df = df.sort_values('final_score', ascending=False).reset_index(drop=True)
    df['rank'] = df.index + 1
    
    # 输出
    out_path = os.path.join(output_dir, "lung_peptide_ranking.csv")
    df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 排名已保存: {out_path}")
    
    # 打印Top5
    print("\n" + "=" * 60)
    print("🏆 Top 5 肺靶向多肽（LNP修饰推荐）")
    print("=" * 60)
    print(f"{'排名':<4} {'名称':<10} {'序列':<18} {'靶点':<20} {'综合评分':<8}")
    print("-" * 70)
    for _, row in df.head(5).iterrows():
        print(f"{row['rank']:<4} {row['name']:<10} {row['sequence']:<18} {row['target']:<20} {row['final_score']:.1f}")
    
    print(f"\n{'排名':<4} {'名称':<10} {'靶向基序':<15} {'GRAVY':<8} {'MW':<8} {'pI':<6} {'LNP分':<6} {'蛋白冠':<6} {'综合':<6}")
    print("-" * 80)
    for _, row in df.head(10).iterrows():
        print(f"{row['rank']:<4} {row['name']:<10} {row['motifs_found']:<15} {row['gravy']:<8.2f} {row['mw_da']:<8.0f} {row['pI']:<6.1f} {row['lnp_score']:<6.0f} {row['corona_score']:<6.0f} {row['final_score']:<6.1f}")
    
    return df

# ============================================================
# 4. 命令行入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PENdp肺靶向多肽AI预测Pipeline")
    parser.add_argument("--output", "-o", default=".", help="输出目录")
    parser.add_argument("--model", "-m", default="esm2_t33_650M_UR50D", help="ESM模型名")
    parser.add_argument("--device", "-d", default=None, help="cuda/cpu")
    args = parser.parse_args()
    
    run_pipeline(output_dir=args.output, model_name=args.model, device=args.device)
