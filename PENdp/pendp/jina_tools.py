"""PENdp Jina AI 工具桥接 — MCP over HTTP 直连，不走 Node.js proxy 问题"""

import json, os
from pathlib import Path
from typing import Optional

import httpx

API_KEY = os.environ.get("JINA_API_KEY", "jina_4f8331291ace4795b55d133c3683a052Jalpx-tW9l17nz3ZhGXwzF6pdYHP")
MCP_URL = "https://mcp.jina.ai/v1"
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or "http://127.0.0.1:7897"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def _mcp_call(method: str, params: dict = None) -> dict:
    """直接调用 Jina MCP 的 Streamable HTTP 端点"""
    kwargs = {"headers": HEADERS, "proxy": PROXY, "timeout": 60.0}
    with httpx.Client(**kwargs) as client:
        resp = client.post(MCP_URL, json={
            "jsonrpc": "2.0", "method": method,
            "params": params or {}, "id": 1,
        })
        for line in resp.text.split("\n"):
            if line.strip().startswith("data:"):
                return json.loads(line[5:].strip())
        return {"error": f"No SSE data in response (status {resp.status_code})"}


def extract_pdf(pdf_url: str, output_dir: Optional[str] = None) -> dict:
    """从 PDF URL 提取文字/表格/公式

    Args:
        pdf_url: PDF 文件的 URL
        output_dir: 可选，提取内容保存目录

    Returns:
        {"content": str, "figures": [...], "tables": [...]}
    """
    result = _mcp_call("tools/call", {
        "name": "extract_pdf",
        "arguments": {"url": pdf_url},
    })
    content = result.get("result", {}).get("content", [])
    text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
    full_text = "\n".join(text_parts)

    if output_dir and full_text:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        fname = pdf_url.split("/")[-1].split("?")[0].replace(".pdf", "") or "extracted"
        out_path = Path(output_dir) / f"{fname}.txt"
        out_path.write_text(full_text, encoding="utf-8")
        return {"path": str(out_path), "length": len(full_text)}
    return {"content": full_text[:5000], "length": len(full_text)}


def search_arxiv(query: str, limit: int = 5) -> list[dict]:
    """搜索 arXiv 论文

    Args:
        query: 搜索关键词
        limit: 返回结果数

    Returns:
        [{"title": str, "authors": str, "abstract": str, "url": str}, ...]
    """
    result = _mcp_call("tools/call", {
        "name": "search_arxiv",
        "arguments": {"query": query, "limit": limit},
    })
    return result.get("result", {}).get("content", [])


def search_web(query: str, limit: int = 5) -> list[dict]:
    """网页搜索（替代 Brave/Tavily）"""
    result = _mcp_call("tools/call", {
        "name": "search_web",
        "arguments": {"query": query, "limit": limit},
    })
    return result.get("result", {}).get("content", [])


def read_url(url: str) -> str:
    """URL 转 markdown 文本"""
    result = _mcp_call("tools/call", {
        "name": "read_url",
        "arguments": {"url": url},
    })
    content = result.get("result", {}).get("content", [])
    text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
    return "\n".join(text_parts)
