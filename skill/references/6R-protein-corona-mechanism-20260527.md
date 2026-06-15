# 阳离子多肽/LNP肺靶向的蛋白冠—内源性配体机制

**调研日期**: 2026-05-27
**相关肽**: 6R (RRRRRR), 3R, DOTAP/SORT LNPs

## 核心结论

6R的肺靶向不依赖受体配体识别，而是通过"**正电荷→招募RGD血浆蛋白→αvβ3整合素**"的三步间接机制。

## 三步分子链

### Step 1: 6R → 表面正电荷
- Arg的胍基在pH 7.4全部质子化，6×Arg提供+6净正电荷
- 6R修饰LNP的ζ电位从~0mV跃升至+20~+35mV
- 与SORT LNP的DOTAP（阳离子脂质）机制一致

### Step 2: 正电荷→招募RGD血浆蛋白（蛋白冠）
肺靶向LNP的蛋白冠特异性富集含RGD序列的血浆蛋白：
- **Vitronectin（玻连蛋白，Vtn）** — 核心靶向蛋白，αvβ3天然配体
- **Fibrinogen（纤维蛋白原，Fgb/Fgg）** — 多个RGD基序
- **Fibronectin（纤连蛋白，Fn1）** — 细胞外基质RGD蛋白

来源：He et al., "Lung-Specific mRNA Delivery by Ionizable Lipids with Defined Structure-Function Relationship and Unique Protein Corona Feature", Advanced Science 2025

### Step 3: RGD蛋白→αvβ3整合素→肺内皮捕获
- αvβ3（玻连蛋白受体）在**肺毛细血管内皮细胞中高表达**
- αvβ3调控肺毛细血管通透性（Bhattacharya et al., Am J Physiol 1995）
- 蛋白冠上的RGD基序结合肺内皮αvβ3，触发内吞

## 关键文献

| 序号 | 文献 | 期刊 | 要点 |
|:----|:-----|:-----|:-----|
| 1 | Dilliard et al., SORT LNPs | PNAS 2021 | 阳离子→肺，阴离子→脾，中性→肝 |
| 2 | He et al., Lung-specific LNPs | Adv Sci 2025 | RGD蛋白在肺靶向LNP冠中富集 |
| 3 | LoPresti et al., SORT mechanism | J Control Release 2023 | Vitronectin是肺靶向内源性配体 |
| 4 | Zamora et al., LNP clotting | Adv Materials 2023 | 阳离子LNP凝血风险及解决方案 |
| 5 | Bhattacharya et al., αvβ3 lung | Am J Physiol 1995 | 肺内皮αvβ3控制毛细血管通透性 |

## 对PENdp评分的启示

| 维度 | 当前行为 | 机制解释 |
|:----|:---------|:---------|
| D1 靶向基序 → 6R=5.0 | 不给高分 | ✅ 正确——序列本身无受体基序，靶向来自蛋白冠 |
| D4 蛋白冠+LNP → 6R高分 | R+K高→高分 | ✅ 完全正确——正电荷→RGD蛋白富集是核心机制 |
| D10/D12 → 6R低分 | Poly-Arg扣分 | ✅ 正确——Fibrinogen招募带来凝血风险 |
