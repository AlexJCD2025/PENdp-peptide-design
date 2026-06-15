#!/usr/bin/env python3
"""
Jina v5 Omni 本地嵌入集成到 PENdp 多肽设计平台
===============================================
无需API Key，本地运行。

模型选择策略：
  - 纯文本嵌入（多肽序列）→ jina-embeddings-v5-text-small（MPS快速）
  - 多模态（文本+图像）→ jina-embeddings-v5-omni-nano（CPU模式）

用法：
  python jina_local_pipeline.py --seq CRGDKGPDC
  python jina_local_pipeline.py --compare "CRGDKGPDC" "CNGRC"
  python jina_local_pipeline.py --batch
  python jina_local_pipeline.py --image path/to/af_structure.png
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path

# ============================================================
# 0. 环境与模型检测
# ============================================================
import torch

DEVICE_MPS = torch.backends.mps.is_available()
DEVICE_CPU = "cpu"
DEFAULT_DEVICE = "mps" if DEVICE_MPS else "cpu"

print(f"🖥️  设备检测: MPS={'✅' if DEVICE_MPS else '❌'}, Apple Silicon Mac" if DEVICE_MPS else "🖥️  设备: Intel/非Apple Silicon")

# ============================================================
# 1. 多肽序列数据库
# ============================================================
PEPTIDE_DB = [
    {"name": "iRGD",       "seq": "CRGDKGPDC",                  "target": "αvβ3/αvβ5+NRP-1",      "application": "NSCLC肿瘤穿透"},
    {"name": "iRGD-L",    "seq": "CRGDK",                        "target": "αvβ3/αvβ5+NRP-1",      "application": "NSCLC肿瘤穿透"},
    {"name": "iNGR",       "seq": "CRNGRGPDC",                  "target": "CD13+NRP-1(双靶向)",     "application": "肿瘤穿透增强"},
    {"name": "NGR",        "seq": "CNGRC",                        "target": "CD13/氨肽酶N",         "application": "肿瘤新生血管"},
    {"name": "CREKA",      "seq": "CREKA",                        "target": "纤维蛋白",              "application": "肺转移灶"},
    {"name": "tLyP-1",    "seq": "CGNKRTR",                      "target": "NRP-1",                  "application": "肺癌肿瘤穿透"},
    {"name": "GE11",       "seq": "YHWYGYTPQNVI",                "target": "EGFR",                  "application": "NSCLC EGFR+"},
    {"name": "RP-832c",   "seq": "RWKFGGFK",                    "target": "CD206(M2巨噬细胞)",      "application": "肺纤维化"},
    {"name": "AKPC",       "seq": "KPSSPPEE",                    "target": "CD44/p32",              "application": "LNP修饰"},
    {"name": "Angiopep-2", "seq": "TFFYGGSRGKRNNFKTEEY",        "target": "LRP1",                  "application": "脑穿透"},
]

# ============================================================
# 2. Jina 本地模型加载器
# ============================================================
from transformers import AutoModel, AutoTokenizer

class JinaLocalEmbedder:
    """
    本地运行的Jina v5嵌入模型（无需API Key）
    
    两个可用模型：
      - text-small:   680M参数， MPS可跑，768维，纯文本嵌入
      - omni-nano:    1.04B参数， CPU模式，768维，支持text+image+audio+video
    """

    TEXT_MODEL = "jinaai/jina-embeddings-v5-text-small"  # MPS可用，0.68B
    OMNI_MODEL = "jinaai/jina-embeddings-v5-omni-nano"   # CPU模式，1.04B

    def __init__(self, mode="text"):
        """
        mode: 'text'  - jina-embeddings-v5-text-small（MPS快速）
              'omni'  - jina-embeddings-v5-omni-nano（CPU，多模态）
        """
        self.mode = mode
        self.model_name = self.TEXT_MODEL if mode == "text" else self.OMNI_MODEL
        self.device = DEFAULT_DEVICE
        
        print(f"\n📦 加载本地模型: {self.model_name}")
        print(f"   设备: {self.device} | 模式: {mode}")
        
        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True
        )
        print(f"   ✅ Tokenizer: {type(self.tokenizer).__name__}")
        
        # 加载模型
        dtype = torch.float32
        if mode == "text" and DEVICE_MPS:
            dtype = torch.float16
            self.device = "mps"
        
        self.model = AutoModel.from_pretrained(
            self.model_name, trust_remote_code=True, dtype=dtype
        )
        self.model = self.model.to(self.device).eval()
        
        params = sum(p.numel() for p in self.model.parameters()) / 1e9
        print(f"   ✅ 模型加载完成: {params:.2f}B 参数 | 设备: {self.device}")

    def encode(self, texts):
        """文本嵌入（CLS token pooling）"""
        if isinstance(texts, str):
            texts = [texts]
        
        inputs = self.tokenizer(
            texts, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Mean pooling with attention mask (CLS has MPS bug)
            hidden = outputs.last_hidden_state  # (batch, seq, hidden)
            mask = inputs["attention_mask"].unsqueeze(-1).float()
            pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1)
            embeddings = pooled.float().cpu().numpy()
        
        return embeddings

    def embed_peptides(self, peptide_list):
        """
        嵌入多肽序列（带描述）
        peptide_list: [{"name": "...", "seq": "...", "target": "...", "application": "..."}]
        """
        texts = [
            f"Peptide name: {p['name']}, sequence: {p['seq']}, target: {p['target']}, application: {p['application']}"
            for p in peptide_list
        ]
        
        print(f"   嵌入 {len(texts)} 条多肽...")
        embeddings = self.encode(texts)
        print(f"   ✅ 完成: {embeddings.shape[0]} × {embeddings.shape[1]}维")
        
        return embeddings, peptide_list

    def compare_peptides(self, seq1, seq2):
        """比较两条多肽的语义相似度"""
        print(f"\n🔬 比较: {seq1} vs {seq2}")
        emb = self.encode([seq1, seq2])
        
        cos = float(torch.nn.functional.cosine_similarity(
            torch.tensor(emb[0:1]), torch.tensor(emb[1:2]), dim=1
        ).item())
        
        print(f"   Cosine Similarity: {cos:.4f}")
        return cos, emb

    def batch_embed_all(self):
        """批量嵌入所有已知多肽"""
        print(f"\n📋 批量嵌入 {len(PEPTIDE_DB)} 条已知多肽...")
        embeddings, peptides = self.embed_peptides(PEPTIDE_DB)
        
        print(f"\n   {'序号':<4} {'名称':<14} {'序列':<12} {'Cosine@iRGD':<12}")
        print("   " + "-" * 50)
        
        # 以iRGD为基准计算相似度
        irgd_emb = embeddings[0]  # iRGD is first in PEPTIDE_DB
        for i, p in enumerate(PEPTIDE_DB):
            cos = float(torch.nn.functional.cosine_similarity(
                torch.tensor(irgd_emb.reshape(1,-1)),
                torch.tensor(embeddings[i:i+1]),
                dim=1
            ).item())
            print(f"   {i+1:<4} {p['name']:<14} {p['seq']:<12} {cos:.4f}")
        
        return embeddings, PEPTIDE_DB


# ============================================================
# 3. 与ESM-2嵌入融合
# ============================================================
def fuse_jina_esm2(jina_emb, esm2_emb, alpha=0.4):
    """
    融合Jina文本嵌入 + ESM-2蛋白质嵌入
    
    Args:
        jina_emb: Jina v5文本嵌入 (768维 or 1024维)
        esm2_emb: ESM-2嵌入 (1280维)
        alpha: Jina权重 (1-alpha = ESM-2权重)
    
    Returns:
        融合后的嵌入向量
    """
    j = np.array(jina_emb)
    e = np.array(esm2_emb)
    
    # 维度对齐（取交集）
    min_dim = min(len(j), len(e))
    j = j[:min_dim]
    e = e[:min_dim]
    
    # L2归一化后加权融合
    j_norm = j / (np.linalg.norm(j) + 1e-8)
    e_norm = e / (np.linalg.norm(e) + 1e-8)
    
    fused = alpha * j_norm + (1 - alpha) * e_norm
    fused = fused / np.linalg.norm(fused)
    
    return fused


# ============================================================
# 4. 主程序入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Jina v5 本地嵌入 × PENdp 多肽设计平台")
    parser.add_argument("--seq", type=str, help="单条多肽序列")
    parser.add_argument("--compare", type=str, nargs=2, help="比较两条多肽序列")
    parser.add_argument("--batch", action="store_true", help="批量嵌入所有已知多肽")
    parser.add_argument("--mode", type=str, default="text", choices=["text", "omni"], 
                        help="'text'=text-small(MPS), 'omni'=omni-nano(CPU)")
    parser.add_argument("--output", type=str, help="保存.npy文件路径")
    parser.add_argument("--fuse", action="store_true", help="与ESM-2嵌入融合（需要先跑ESM-2）")
    args = parser.parse_args()

    # 初始化嵌入器
    embedder = JinaLocalEmbedder(mode=args.mode)

    if args.seq:
        print(f"\n🔬 嵌入多肽序列: {args.seq}")
        emb = embedder.encode([args.seq])
        print(f"   维度: {emb.shape[1]} | 前6维: {emb[0][:6]}")
        if args.output:
            np.save(args.output, emb)
            print(f"   💾 已保存: {args.output}")

    elif args.compare:
        cos, emb = embedder.compare_peptides(args.compare[0], args.compare[1])

    elif args.batch:
        embeddings, peptides = embedder.batch_embed_all()
        if args.output:
            np.save(args.output, embeddings)
            print(f"\n   💾 嵌入矩阵已保存: {args.output}")
            
            # 保存元数据
            import json
            meta_path = args.output.replace(".npy", "_meta.json")
            meta = [{"name": p["name"], "seq": p["seq"], "target": p["target"]} for p in peptides]
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            print(f"   💾 元数据已保存: {meta_path}")

    else:
        print("📋 默认：批量嵌入所有已知多肽（text模式）")
        args.batch = True
        args.mode = "text"
        main()


# ============================================================
# 5. 工具函数（供外部调用）
# ============================================================
def get_jina_text_embedding(sequences, mode="text"):
    """
    外部调用接口：获取多肽序列的Jina文本嵌入
    
    Args:
        sequences: str or list of str (多肽序列)
        mode: 'text' or 'omni'
    
    Returns:
        numpy array (N × embedding_dim)
    """
    embedder = JinaLocalEmbedder(mode=mode)
    if isinstance(sequences, str):
        sequences = [sequences]
    return embedder.encode(sequences)


if __name__ == "__main__":
    main()