#!/usr/bin/env python3
"""
Jina v5 Omni 多模态嵌入集成到 PENdp 多肽设计平台
功能：
  1. 多肽序列文本嵌入（text-only，与ESM-2互补）
  2. AlphaFold结构图嵌入（image modality）
  3. 多模态联合检索（peptide sequence ↔ structure image）
  4. 与ESM-2嵌入向量联合使用（双嵌入融合）

用法：
  python jina_multimodal_peptide_pipeline.py --seq CRGDKGPDC
  python jina_multimodal_peptide_pipeline.py --compare "CRGDKGPDC" "CNGRC"
  python jina_multimodal_peptide_pipeline.py --multimodal path/to/af_structure.png

依赖：
  pip install jinaai transformers torch pillow
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path

# ============================================================
# 0. 环境检测
# ============================================================
try:
    from jinaai import JinaAI
    print("✅ jinaai OK")
except ImportError:
    print("❌ jinaai未安装，运行: pip install jinaai")
    sys.exit(1)

# ============================================================
# 1. 多肽序列数据库
# ============================================================
PEPTIDE_DB = [
    {"name": "iRGD",      "seq": "CRGDKGPDC",                    "target": "αvβ3/αvβ5+NRP-1",        "application": "NSCLC肿瘤穿透"},
    {"name": "iRGD-L",   "seq": "CRGDK",                         "target": "αvβ3/αvβ5+NRP-1",        "application": "NSCLC肿瘤穿透"},
    {"name": "iNGR",      "seq": "CRNGRGPDC",                    "target": "CD13+NRP-1(双靶向)",       "application": "肿瘤穿透增强"},
    {"name": "NGR",       "seq": "CNGRC",                         "target": "CD13/氨肽酶N",           "application": "肿瘤新生血管"},
    {"name": "CREKA",     "seq": "CREKA",                         "target": "纤维蛋白",               "application": "肺转移灶"},
    {"name": "tLyP-1",   "seq": "CGNKRTR",                       "target": "NRP-1",                   "application": "肺癌肿瘤穿透"},
    {"name": "GE11",      "seq": "YHWYGYTPQNVI",                  "target": "EGFR",                    "application": "NSCLC EGFR+"},
    {"name": "RP-832c",   "seq": "RWKFGGFK",                      "target": "CD206(M2巨噬细胞)",       "application": "肺纤维化"},
    {"name": "AKPC",      "seq": "KPSSPPEE",                      "target": "CD44/p32",                "application": "LNP修饰"},
    {"name": "Angiopep-2", "seq": "TFFYGGSRGKRNNFKTEEY",         "target": "LRP1",                    "application": "脑穿透"},
]

# ============================================================
# 2. Jina v5 Omni 客户端
# ============================================================
class JinaOmniEmbedder:
    """Jina v5 Omni 多模态嵌入"""

    def __init__(self, model_size="small"):
        """
        model_size: 'nano' (1B) 或 'small' (2B)
        """
        self.model_size = model_size
        if model_size == "nano":
            self.model_id = "jinaai/jina-embeddings-v5-omni-nano"
        else:
            self.model_id = "jinaai/jina-embeddings-v5-omni-small"

        print(f"📦 初始化 Jina v5 Omni ({model_size})...")
        self.client = JinaAI()
        print(f"✅ Jina v5 Omni 初始化完成")
        print(f"   Model: {self.model_id}")

    def embed_text(self, texts):
        """多肽序列文本嵌入"""
        if isinstance(texts, str):
            texts = [texts]

        # 构造多肽文本描述
        formatted = [
            f"Peptide sequence: {seq}. Name: {name}. Target: {target}."
            for seq, name, target in [
                (t, db["name"], db["target"])
                for t, db in [(t, next(d for d in PEPTIDE_DB if d["seq"] == t)) for t in texts]
            ]
        ] if all(t in [d["seq"] for d in PEPTIDE_DB] for t in texts) else texts

        try:
            result = self.client.encode([
                {"model": self.model_id, "task": "retrieval", "inputs": [{"text": t} for t in texts]}
            ])
            embeddings = [r["embedding"] for r in result["data"]]
            print(f"   Text embedding: {len(embeddings)} sequences, dim={len(embeddings[0]) if embeddings else 'N/A'}")
            return embeddings
        except Exception as e:
            print(f"   ⚠️ API调用失败: {e}")
            print(f"   尝试直接API调用...")
            return self._embed_via_http(texts)

    def embed_text_simple(self, texts):
        """简化版：直接用文本嵌入"""
        if isinstance(texts, str):
            texts = [texts]
        try:
            result = self.client.encode(texts)
            return result
        except Exception as e:
            print(f"   ⚠️ {e}")
            return None

    def embed_image(self, image_paths):
        """AlphaFold结构图像嵌入"""
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        inputs = []
        for path in image_paths:
            if not os.path.exists(path):
                print(f"   ⚠️ 文件不存在: {path}")
                continue
            inputs.append({"image": path})

        if not inputs:
            print("   ❌ 没有有效的图像文件")
            return None

        try:
            result = self.client.encode([
                {"model": self.model_id, "task": "retrieval", "inputs": inputs}
            ])
            embeddings = [r["embedding"] for r in result["data"]]
            print(f"   Image embedding: {len(embeddings)} images, dim={len(embeddings[0]) if embeddings else 'N/A'}")
            return embeddings
        except Exception as e:
            print(f"   ⚠️ 图像嵌入失败: {e}")
            return None

    def embed_multimodal(self, items):
        """
        混合嵌入：文本+图像一起编码
        items: [{"text": "..."}, {"image": "path/to/image.png"}, ...]
        """
        try:
            inputs = []
            for item in items:
                if "text" in item:
                    inputs.append({"text": item["text"]})
                elif "image" in item:
                    inputs.append({"image": item["image"]})

            result = self.client.encode([
                {"model": self.model_id, "task": "retrieval", "inputs": inputs}
            ])
            embeddings = [r["embedding"] for r in result["data"]]
            print(f"   Multimodal: {len(embeddings)} items")
            return embeddings
        except Exception as e:
            print(f"   ⚠️ 多模态嵌入失败: {e}")
            return None

    def compare_texts(self, text1, text2):
        """比较两个多肽序列的相似度"""
        emb1 = self.embed_text_simple([text1])
        emb2 = self.embed_text_simple([text2])
        if emb1 and emb2:
            # cosine similarity
            from numpy.dot import dot
            from numpy.linalg import norm
            cos = dot(emb1[0], emb2[0]) / (norm(emb1[0]) * norm(emb2[0]))
            return cos
        return None


# ============================================================
# 3. 多模态多肽Pipeline主程序
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Jina v5 Omni × PENdp 多模态嵌入")
    parser.add_argument("--seq", type=str, help="单条多肽序列")
    parser.add_argument("--compare", type=str, nargs=2, help="比较两条多肽序列")
    parser.add_argument("--batch", action="store_true", help="批量嵌入所有已知多肽")
    parser.add_argument("--image", type=str, help="AlphaFold结构图像路径")
    parser.add_argument("--size", type=str, default="small", choices=["nano", "small"], help="模型大小")
    parser.add_argument("--output", type=str, help="保存嵌入向量到文件")
    args = parser.parse_args()

    embedder = JinaOmniEmbedder(model_size=args.size)

    if args.seq:
        # 单序列嵌入
        print(f"\n🔬 嵌入多肽序列: {args.seq}")
        emb = embedder.embed_text_simple([args.seq])
        if emb:
            print(f"   ✅ 维度: {len(emb[0])}")
            print(f"   ✅ 向量(前8): {emb[0][:8]}")
            if args.output:
                np.save(args.output.replace(".npy","_text.npy"), np.array(emb))
                print(f"   💾 已保存到 {args.output.replace('.npy','_text.npy')}")

    elif args.compare:
        # 比较两条序列
        seq1, seq2 = args.compare
        print(f"\n🔬 比较两条多肽: {seq1} vs {seq2}")
        sim = embedder.compare_texts(seq1, seq2)
        if sim is not None:
            print(f"   ✅ Cosine Similarity: {sim:.4f}")

    elif args.batch:
        # 批量嵌入所有已知多肽
        print(f"\n🔬 批量嵌入 {len(PEPTIDE_DB)} 条已知多肽序列...")
        texts = [p["seq"] for p in PEPTIDE_DB]
        embeddings = embedder.embed_text_simple(texts)
        if embeddings:
            print(f"   ✅ 嵌入完成: {len(embeddings)} × dim={len(embeddings[0])}")
            for i, p in enumerate(PEPTIDE_DB):
                print(f"   [{i+1}] {p['name']:12s} ({p['seq']})")

            if args.output:
                arr = np.array(embeddings)
                np.save(args.output, arr)
                print(f"   💾 已保存到 {args.output}")

                # 保存元数据
                meta_path = args.output.replace(".npy", "_meta.json")
                import json
                meta = [{"name": p["name"], "seq": p["seq"], "target": p["target"], "application": p["application"]} for p in PEPTIDE_DB]
                with open(meta_path, "w") as f:
                    json.dump(meta, f, indent=2)
                print(f"   💾 元数据已保存到 {meta_path}")

    elif args.image:
        # 图像嵌入
        print(f"\n🖼️ 嵌入结构图像: {args.image}")
        emb = embedder.embed_image([args.image])
        if emb and args.output:
            np.save(args.output.replace(".npy","_image.npy"), np.array(emb))
            print(f"   💾 已保存到 {args.output.replace('.npy','_image.npy')}")

    else:
        # 默认：批量嵌入
        print("📋 默认：批量嵌入所有已知多肽序列")
        args.batch = True
        main()


# ============================================================
# 4. 与ESM-2嵌入融合的辅助函数
# ============================================================
def fuse_jina_esm2(jina_emb, esm2_emb, alpha=0.5):
    """
    融合Jina v5 Omni文本嵌入 + ESM-2蛋白质嵌入

    Args:
        jina_emb: Jina文本嵌入 (通用语义)
        esm2_emb: ESM-2嵌入 (结构/进化信息)
        alpha: Jina权重 (1-alpha = ESM-2权重)

    Returns:
        融合后的嵌入向量
    """
    # 维度对齐
    min_dim = min(len(jina_emb), len(esm2_emb))
    j = np.array(jina_emb[:min_dim])
    e = np.array(esm2_emb[:min_dim])

    # L2归一化后加权融合
    j_norm = j / (np.linalg.norm(j) + 1e-8)
    e_norm = e / (np.linalg.norm(e) + 1e-8)
    fused = alpha * j_norm + (1 - alpha) * e_norm
    fused = fused / np.linalg.norm(fused)

    return fused


# ============================================================
# 5. 多模态peptide-to-structure检索
# ============================================================
def peptide_to_structure_search(query_seq, image_dir, embedder, top_k=3):
    """
    用多肽序列检索最相似的AlphaFold结构图像

    Args:
        query_seq: 查询多肽序列
        image_dir: AlphaFold结构图像目录
        embedder: JinaOmniEmbedder实例
        top_k: 返回Top-K结果
    """
    print(f"\n🔍 Peptide→Structure 检索: {query_seq}")

    # 嵌入查询序列
    seq_emb = embedder.embed_text_simple([query_seq])
    if not seq_emb:
        print("   ❌ 序列嵌入失败")
        return

    # 列出所有结构图像
    image_paths = list(Path(image_dir).glob("*.png")) + list(Path(image_dir).glob("*.jpg"))
    print(f"   📁 找到 {len(image_paths)} 张结构图像")

    if not image_paths:
        print("   ⚠️ 没有找到结构图像，请先运行AlphaFold预测生成图像")
        return

    # 批量嵌入图像
    image_embs = []
    valid_paths = []
    for path in image_paths:
        emb = embedder.embed_image([str(path)])
        if emb:
            image_embs.append(emb[0])
            valid_paths.append(path.name)

    if not image_embs:
        print("   ❌ 没有成功嵌入任何图像")
        return

    # 计算余弦相似度
    from numpy.dot import dot
    from numpy.linalg import norm
    similarities = []
    for name, img_emb in zip(valid_paths, image_embs):
        cos = dot(seq_emb[0], img_emb) / (norm(seq_emb[0]) * norm(img_emb) + 1e-8)
        similarities.append((name, cos))

    # 排序
    similarities.sort(key=lambda x: x[1], reverse=True)

    print(f"\n   🏆 Top-{min(top_k, len(similarities))} 最相似结构:")
    for i, (name, score) in enumerate(similarities[:top_k]):
        print(f"   [{i+1}] {name:40s}  相似度: {score:.4f}")

    return similarities


# ============================================================
# 6. main entry
# ============================================================
if __name__ == "__main__":
    main()
