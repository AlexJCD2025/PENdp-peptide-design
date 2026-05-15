"""
PENdp 语义搜索引擎 v1.0
========================
基于 jina-embeddings-v5-omni-nano-retrieval MLX 模型，本地 Apple Silicon 推理。
支持文本 + 图片（未来）跨模态语义搜索，用于文献库、数据库、分子序列的混搜。

用法:
    from pendp.search import SemanticSearch
    se = SemanticSearch()           # 首次加载约 1s
    se.index_literature()           # 编码所有文献到内存
    results = se.query("LNP 肺靶向多肽")  # 返回 [(Paper, score), ...]
"""

import json
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable

import mlx.core as mx
from tokenizers import Tokenizer

# ── 模型路径 ──
MODEL_DIR = Path.home() / ".hermes/workspace/PENdp/models/jina-embeddings-v5-omni-small-retrieval-mlx"
_LAZY: dict = {"model": None, "tokenizer": None, "model_type": "small"}


# ══════════════════════════════════════════════════
# 文档索引基类
# ══════════════════════════════════════════════════

@dataclass
class SearchDoc:
    """索引中的一条文档"""
    id: str
    title: str
    content: str          # 用于 embedding 的文本
    metadata: dict = None  # 额外的可展示字段


# ══════════════════════════════════════════════════
# 核心搜索引擎
# ══════════════════════════════════════════════════

class SemanticSearch:
    """语义搜索引擎。惰性加载 MLX 模型 + tokenizer。

    文档检索流程：
      1. index_docs(docs) 或 index_literature() — 对所有文档编码
      2. query(text, top_k=5) — 返回相似度排序结果
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._docs: List[SearchDoc] = []
        self._embeddings: Optional[mx.array] = None  # (N, 768)
        self._loaded = False

    # ── 模型加载 ──

    def _ensure_model(self):
        """惰性加载 MLX 模型 + tokenizer"""
        if _LAZY["model"] is not None:
            return
        t0 = time.time()
        sys.path.insert(0, str(MODEL_DIR))
        from model import JinaOmniSmallEmbeddingModel, OmniSmallConfig

        cfg = OmniSmallConfig.from_dict(json.load(open(f"{MODEL_DIR}/config.json")))
        model = JinaOmniSmallEmbeddingModel(cfg)
        weights = mx.load(f"{MODEL_DIR}/model.safetensors")
        weights = model.sanitize(weights)
        model.load_weights(list(weights.items()))
        mx.eval(model.parameters())

        tokenizer = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))

        _LAZY["model"] = model
        _LAZY["tokenizer"] = tokenizer
        if self.verbose:
            print(f"  📦 模型加载: {time.time()-t0:.1f}s (small 1.57B, 1024-dim)")

    @property
    def _model(self):
        self._ensure_model()
        return _LAZY["model"]

    @property
    def _tokenizer(self):
        self._ensure_model()
        return _LAZY["tokenizer"]

    # ── 编码 ──

    def _encode(self, texts: List[str]) -> mx.array:
        """批量编码文本为归一化向量 (batch, 768)"""
        encodings = self._tokenizer.encode_batch(texts)
        max_len = max(len(e.ids) for e in encodings)
        max_len = min(max_len, 8192)  # 截断

        input_ids_list = []
        attention_mask_list = []
        for e in encodings:
            ids = e.ids[:max_len]
            pad_len = max_len - len(ids)
            input_ids_list.append(ids + [0] * pad_len)
            attention_mask_list.append([1] * len(ids) + [0] * pad_len)

        input_ids = mx.array(input_ids_list)
        attention_mask = mx.array(attention_mask_list)

        embs = self._model.encode_text(input_ids, attention_mask)
        mx.eval(embs)
        return embs

    # ── 索引构建 ──

    def index_docs(self, docs: List[SearchDoc], batch_size: int = 32):
        """对文档列表编码建索引"""
        self._docs = docs
        t0 = time.time()
        all_embeddings = []
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            texts = [d.content for d in batch]
            embs = self._encode(texts)
            all_embeddings.append(embs)
        self._embeddings = mx.concatenate(all_embeddings, axis=0)
        if self.verbose:
            print(f"  📚 索引 {len(docs)} 条文档: {time.time()-t0:.1f}s")

    def index_literature(self):
        """索引 PENdp 文献库 + 全文（如已获取）"""
        from pendp.literature.papers import PAPERS
        texts_dir = Path(__file__).parent.parent / "literature" / "texts"

        docs = []
        for i, p in enumerate(PAPERS, 1):
            full_text = None
            txt_path = texts_dir / f"paper_{i}.txt"
            if txt_path.exists():
                content = txt_path.read_text(encoding="utf-8", errors="replace")
                # 去掉文件头部的元数据标记行（===...=== 之间的是元数据），保留正文
                lines = content.split("\n")
                body_lines = []
                in_header = True
                for line in lines:
                    if line.startswith("===") and in_header:
                        continue  # skip separator lines
                    if in_header and ":" not in line and line.strip():
                        in_header = False  # first non-metadata line
                    if not in_header:
                        body_lines.append(line)
                full_text = "\n".join(body_lines).strip()

            content = full_text or f"{p.title}. {p.key_finding}. {p.relevance_to_pendp}"
            docs.append(SearchDoc(
                id=f"paper-{i}",
                title=p.title,
                content=content,
                metadata={
                    "authors": p.authors,
                    "source": p.source,
                    "year": p.year,
                    "doi": p.doi,
                    "priority": p.priority,
                    "type": "literature",
                    "has_fulltext": full_text is not None,
                }
            ))
        # 也索引序列数据库
        from pendp.database.sequences import LUNG_PEPTIDES_V6
        for seq in LUNG_PEPTIDES_V6:
            docs.append(SearchDoc(
                id=f"seq-{seq.name[:12]}",
                title=seq.name,
                content=f"多肽序列: {seq.sequence}. 靶点: {seq.target} ({seq.target_detail}). 机制: {seq.mechanism}. 评分: {seq.score_total:.1f}",
                metadata={
                    "sequence": seq.sequence,
                    "target": seq.target,
                    "target_detail": seq.target_detail,
                    "structure_type": seq.structure_type,
                    "score": seq.score_total,
                    "type": "peptide_sequence",
                }
            ))
        self.index_docs(docs)

    # ── 查询 ──

    def query(self, query_text: str, top_k: int = 5) -> List[Tuple[SearchDoc, float]]:
        """语义搜索，返回 [(doc, cosine_similarity), ...]"""
        if self._embeddings is None:
            raise RuntimeError("请先调用 index_docs() 或 index_literature() 建索引")

        q_emb = self._encode([query_text])[0]  # (768,)
        scores = self._embeddings @ q_emb         # (N,)
        # 取 top_k
        idx = mx.argpartition(-scores, top_k)[:top_k]
        idx_list = idx.tolist()
        scores_list = scores.tolist()

        results = [(self._docs[i], float(scores_list[i])) for i in idx_list]
        results.sort(key=lambda x: -x[1])
        return results

    # ── 显示 ──

    def show_results(self, results: List[Tuple[SearchDoc, float]], max_per_type: int = 5):
        """格式化展示搜索结果"""
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text

        console = Console()
        table = Table(title=f"🔍 搜索结果 ({len(results)} 条)", title_style="bold cyan")
        table.add_column("#", style="dim", width=3)
        table.add_column("类型", style="magenta", width=8)
        table.add_column("标题", style="bold yellow")
        table.add_column("相似度", justify="right", width=8)
        table.add_column("摘要", style="dim", width=60)

        for i, (doc, score) in enumerate(results[:max_per_type], 1):
            t = doc.metadata.get("type", "text") if doc.metadata else "text"
            label = {
                "literature": "📄 文献",
                "peptide_sequence": "🧬 序列",
            }.get(t, "📄")
            title = doc.title[:50] + "..." if len(doc.title) > 50 else doc.title
            summary = doc.content[:80] + "..." if len(doc.content) > 80 else doc.content
            table.add_row(str(i), label, title, f"{score:.3f}", summary)

        console.print(table)


# 全局单例（惰性初始化）
_SEARCHER: Optional[SemanticSearch] = None


def get_searcher() -> SemanticSearch:
    """获取全局搜索引擎实例（惰性初始化）"""
    global _SEARCHER
    if _SEARCHER is None:
        _SEARCHER = SemanticSearch(verbose=False)
    return _SEARCHER
