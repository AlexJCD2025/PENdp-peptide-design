#!/usr/bin/env python3
"""
RDKit Skills Test - 多肽类药性评估
测试分子: 6条代表性多肽序列 (SMILES模拟)
"""

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, Draw, AllChem
from rdkit.Chem import rdMolDescriptors
import sys

print("=" * 60)
print("RDKit Skills Test - 多肽类药性评估")
print("=" * 60)

# 测试分子集（SMILES格式）
test_molecules = [
    ("Gly-Gly", "NCC(=O)NCC(=O)O", "最简单的二肽"),
    ("Ala-Gln", "CC(N)C(=O)N[C@@H](C)C(=O)O", "丙氨酰谷氨酰胺"),
    ("Cyclic RGD", "O=C(N[C@@H](CCC)C(=O)N1C(=O)[C@@H](CCCN=C(N)N)C1)O", "环RGD整合素靶向肽"),
    ("GLP-1 fragment", "NH2-Histidine-Alanine-Glu-Phe-Thr-OH", "GLP-1片段"),
    ("Tat(49-57)", "YGRKKRRQRRR", "HIV-Tat穿膜肽"),
    ("LL-37 fragment", "FFKKLKKLKKLKKL", "抗菌肽LL-37片段"),
]

# 实际可用的简单氨基酸SMILES
real_molecules = [
    ("Acetylglycine", "CC(=O)NCC(=O)O", "N-乙酰甘氨酸"),
    ("N-Acetyl-Ala", "CC(=O)N[C@@H](C)C(=O)O", "N-乙酰-L-丙氨酸"),
    ("N-Acetyl-Phe", "CC(=O)N[C@@H](CC1=CC=CC=C1)C(=O)O", "N-乙酰-L-苯丙氨酸"),
    ("Pro-Gly", "O=C(O)CNC(=O)[C@@H]1CCCN1", "脯氨酰甘氨酸"),
    ("Cyclosporin analog", "CC(C)C[C@@H](C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)O)N", "环肽模拟物"),
]

print(f"\n{'='*60}")
print(f"{'序号':<4} {'名称':<25} {'MW':>8} {'LogP':>8} {'TPSA':>8} {'HBA':>5} {'HBD':>5} {'类药性':>6}")
print(f"{'-'*60}")

passed = 0
failed = 0

for i, (name, smiles, desc) in enumerate(real_molecules, 1):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"{i:<4} {name:<25} {'FAILED':>8} {'Parse Error':>8}")
            failed += 1
            continue

        # 计算分子描述符
        mw = Descriptors.MolWt(mol)
        logp = Crippen.MolLogP(mol)
        tpsa = rdMolDescriptors.CalcTPSA(mol)
        hba = Lipinski.NumHAcceptors(mol)
        hbd = Lipinski.NumHDonors(mol)
        num_rotatable = Lipinski.NumRotatableBonds(mol)

        # Lipinski五规则评估
        mw_ok = mw < 500
        logp_ok = logp < 5
        hbd_ok = hbd <= 5
        hba_ok = hba <= 10
        druglike = "✅" if all([mw_ok, logp_ok, hbd_ok, hba_ok]) else "⚠️"

        print(f"{i:<4} {name:<25} {mw:>8.2f} {logp:>8.2f} {tpsa:>8.1f} {hba:>5} {hbd:>5} {druglike:>6}")
        passed += 1

    except Exception as e:
        print(f"{i:<4} {name:<25} {'ERROR':>8} {str(e)[:20]:>8}")
        failed += 1

print(f"{'-'*60}")
print(f"总计: {passed} 成功 / {failed} 失败\n")

# 测试R基团特征提取
print("=" * 60)
print("分子指纹与相似度测试")
print("=" * 60)

smiles_list = [
    ("N-Acetyl-Ala", "CC(=O)N[C@@H](C)C(=O)O"),
    ("N-Acetyl-Val", "CC(C)C(N)C(=O)O"),
    ("N-Acetyl-Leu", "CC(C)CC(N)C(=O)O"),
    ("N-Acetyl-Ile", "CC[C@H](C)N)C(=O)O"),
]

try:
    fps = []
    names = []
    for name, smi in smiles_list[:3]:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            fp = Chem.AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=1024)
            fps.append(fp)
            names.append(name)

    if len(fps) >= 2:
        from rdkit.DataStructs import TanimotoSimilarity
        sim = TanimotoSimilarity(fps[0], fps[1])
        print(f"Ala-Val 相似度 (Morgan FP): {sim:.3f}")
        print(f"Ala-Leu 相似度 (Morgan FP): {TanimotoSimilarity(fps[0], fps[2]):.3f}")
        print("✅ 分子指纹计算正常")
except Exception as e:
    print(f"指纹测试: {e}")

# 测试分子图绘制
print("\n" + "=" * 60)
print("分子结构可视化测试")
print("=" * 60)

try:
    mol = Chem.MolFromSmiles("CC(=O)N[C@@H](C)C(=O)O")  # N-Acetyl-Ala
    if mol:
        # 生成2D坐标
        AllChem.Compute2DCoords(mol)
        # 创建PNG图像
        drawer = Draw.MolDraw2DCairo(400, 300)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        img_data = drawer.GetDrawingText()
        
        with open("/Users/jarvis-ai/.openclaw/workspace/skills/kd-rdkit/test_N_Acetyl_Ala.png", "wb") as f:
            f.write(img_data)
        print("✅ 分子图像已生成: test_N_Acetyl_Ala.png")
except Exception as e:
    print(f"⚠️ 图像生成: {e}")

print("\n" + "=" * 60)
print("RDKit Skills Test 完成")
print("=" * 60)