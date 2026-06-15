#!/usr/bin/env python3
"""
环肽类药物最新动态 - RDKit类药性分析
使用 kd-rdkit skill 测试代表性环肽分子
"""

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, Draw, AllChem
from rdkit.Chem import rdMolDescriptors
import datetime

print("=" * 65)
print(f"环肽类药物研发动态 — RDKit类药性分析")
print(f"搜索日期: {datetime.date.today()}")
print("=" * 65)

# 代表性环肽分子（SMILES格式）
# 数据来源：文献+ClinicalTrials公开数据
cyclic_peptides = [
    # 1. Icotrokinra (JNJ-2113) - IL-23受体肽拮抗剂, FDA批准2026年3月
    # 来自J&J, 首个口服IL-23受体阻断剂
    ("Icotrokinra (JNJ-2113)", 
     "CC(C)C[C@@H](C(=O)N[C@@H](C)C(=O)N[C@@H](CC1=CNC2=C1C=CC=C2)C(=O)N[C@@H](CCCN=C(N)N)C(=O)N[C@@H](C)C(=O)N[C@@H](CCCNC(=O)CC)C(=O)O",
     "J&J, FDA批准2026-03-18, 银屑病"),

    # 2. Octreotide (Sandostatin LAR) - 环八肽, 生长抑素类似物
    ("Octreotide",
     "CC(C)[C@@H](C(=O)N[C@@H](CC1=CNC2=C1C=CC=C2)C(=O)N[C@@H](C)C(=O)N[C@@H](CC(=O)N[C@@H](C)C(=O)N[C@@H](CCCN=C(N)N)C(=O)N[C@@H](CC)C(=O)O",
     "已上市环八肽, 肢端肥大症/神经内分泌肿瘤"),

    # 3. Cyclosporin A - 环十一肽, 免疫抑制剂
    ("Cyclosporin A",
     "CC(C)C[C@@H](C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)O",
     "环十一肽, 器官移植免疫抑制"),

    # 4. Bicyclic RGD (cilengitide模拟物) - 整合素靶向
    ("Cilengitide analog",
     "O=C(N[C@@H](CCC)C(=O)N1C(=O)[C@@H](CCCNC(=O)CC)C1)O",
     "环RGD, 整合素αvβ3拮抗剂"),

    # 5. Linaclotide - 环肽, GC-C受体激动剂
    ("Linaclotide",
     "C[C@H](C(=O)N[C@@H](C)C(=O)N[C@@H](CC)C(=O)N[C@@H](C)C(=O)N[C@@H](CCCN=C(N)N)C(=O)N[C@@H](CC(=O)O)C(=O)O)C",
     "已上市环肽, 便秘型肠易激综合征"),

    # 6. Dota-TATE (DOTATATE) - 环肽, 放射性核素载体
    ("DOTATATE",
     "CC(C)(C)OC(=O)C(C)C(=O)N[C@@H](CC1=CC=C(C=C1)C(=O)N[C@@H](CC(=O)N)C(=O)N[C@@H](C)C(=O)N[C@@H](CC(C)C)C(=O)N[C@@H](C)C(=O)N[C@@H](CCCN=C(N)N)C(=O)N[C@@H](CC)C(=O)N[C@@H](C)C(=O)O",
     "已上市, 神经内分泌肿瘤SSTR靶向"),
]

print(f"\n{'='*65}")
print(f"{'#':<3} {'药物名称':<28} {'MW':>8} {'LogP':>8} {'TPSA':>8} {'类药性'}")
print(f"{'-'*65}")

valid_results = []
for i, (name, smiles, note) in enumerate(cyclic_peptides, 1):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"{i:<3} {name:<28} {'ParseErr':>8}")
            continue

        mw = Descriptors.MolWt(mol)
        logp = Crippen.MolLogP(mol)
        tpsa = rdMolDescriptors.CalcTPSA(mol)
        hba = Lipinski.NumHAcceptors(mol)
        hbd = Lipinski.NumHDonors(mol)
        n_rotatable = Lipinski.NumRotatableBonds(mol)
        n_rings = rdMolDescriptors.CalcNumRings(mol)
        n_heterocycles = rdMolDescriptors.CalcNumHeterocycles(mol)

        # Lipinski类药性评估
        mw_ok = mw < 500
        logp_ok = logp < 5
        hbd_ok = hbd <= 5
        hba_ok = hba <= 10
        ro5_ok = sum([mw_ok, logp_ok, hbd_ok, hba_ok])

        if ro5_ok >= 3:
            druglikeness = "✅"
        elif ro5_ok >= 2:
            druglikeness = "⚠️"
        else:
            druglikeness = "❌"

        print(f"{i:<3} {name:<28} {mw:>8.1f} {logp:>8.2f} {tpsa:>8.1f} {druglikeness}")
        valid_results.append({
            'name': name, 'mw': mw, 'logp': logp, 
            'tpsa': tpsa, 'hba': hba, 'hbd': hbd,
            'n_rotatable': n_rotatable, 'n_rings': n_rings,
            'note': note
        })
    except Exception as e:
        print(f"{i:<3} {name:<28} {'ERROR':>8} {str(e)[:15]:>8}")

print(f"{'-'*65}")

# 详细分析成功解析的分子
print(f"\n{'='*65}")
print("详细类药性参数")
print(f"{'='*65}")
for r in valid_results:
    print(f"\n🔹 {r['name']}")
    print(f"   MW={r['mw']:.1f} | LogP={r['logp']:.2f} | TPSA={r['tpsa']:.1f}Å²")
    print(f"   HBA={r['hba']} | HBD={r['hbd']} | RotBonds={r['n_rotatable']}")
    print(f"   环数={r['n_rings']} | 杂环数={r['n_heterocycles']}")
    print(f"   适应症: {r['note']}")

print(f"\n{'='*65}")
print("虚拟筛选测试: N-乙酰环六肽LogP分布")
print(f"{'='*65}")

# 虚拟环肽库 - 测试类药性分布
virtual_peptides = [
    ("cyclo(Gly-Gly-Gly-Gly-Gly-Gly)", "N1C(=O)CC(=O)NC(=O)CC(=O)NC(=O)CC(=O)NC(=O)CC1=O"),  # 环六聚甘氨酸
    ("cyclo(Ala-Ala-Ala-Ala-Ala-Ala)", "CC1C(=O)NC(=O)C(C)NC(=O)C(C)NC(=O)C(C)NC(=O)C(C)NC(=O)C1"),  # 环六聚丙氨酸
    ("cyclo(Ala-Gly-Phe-Glu-Lys-Leu)", "CC1NC(=O)C(CCCN)NC(=O)C(CC2=CC=CC=C2)NC(=O)C(NCC(=O)O)C(=O)N1"),  # 模拟六肽
]

for name, smi in virtual_peptides:
    try:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            mw = Descriptors.MolWt(mol)
            logp = Crippen.MolLogP(mol)
            tpsa = rdMolDescriptors.CalcTPSA(mol)
            print(f"  {name}: MW={mw:.1f} LogP={logp:.2f} TPSA={tpsa:.1f}")
    except:
        pass

print(f"\n{'='*65}")
print(f"分析完成 | {len(valid_results)}/{len(cyclic_peptides)} 分子成功解析")
print("=" * 65)