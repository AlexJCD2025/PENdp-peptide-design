"""PENdp 语义搜索 CLI 子命令"""

from .engine import SemanticSearch, get_searcher


def register(subparsers):
    """注册 pendp search 子命令"""
    p = subparsers.add_parser("search", help="🔍 语义搜索（文献+序列数据库）")
    p.add_argument("query", nargs="?", help="搜索查询语句")
    p.add_argument("-k", "--top-k", type=int, default=5, help="返回结果数 (默认 5)")
    p.add_argument("--full", action="store_true", help="完整展示（含全部字段）")
    p.add_argument("--index-only", action="store_true", help="仅建索引，不查询")


def cmd_search(args):
    """执行搜索"""
    se = SemanticSearch(verbose=True)
    print()
    se.index_literature()

    if args.index_only:
        print("  ✅ 索引构建完成。运行 `pendp search <query>` 查询")
        return

    if not args.query:
        print()
        print("  ❓ 请输入搜索查询。用法: pendp search \"你的问题\"")
        print("     例: pendp search \"LNP肺靶向多肽\"")
        return

    print()
    results = se.query(args.query, top_k=args.top_k)

    if args.full:
        import textwrap
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(f"  #{i} [{score:.3f}] {doc.title}")
            print(f"{'='*60}")
            print(f"  {doc.content}")
            if doc.metadata:
                for k, v in doc.metadata.items():
                    print(f"  {k}: {v}")
    else:
        se.show_results(results)
