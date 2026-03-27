"""
渲染命令 - lf render
"""

import sys
from pathlib import Path
from ..models import Tree
from ..renderer import MarkdownRenderer


def run(args, work_dir: Path):
    """执行 render 命令"""
    tree_file = work_dir / "_tree.json"
    output_file = work_dir / (args.output or "_tree.md")
    
    if not tree_file.exists():
        print(f"错误: 未找到项目文件: {tree_file}")
        sys.exit(1)
    
    tree = Tree.load(tree_file)
    
    renderer = MarkdownRenderer()
    markdown = renderer.render(tree, filter_status=args.filter)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    filter_info = f" (过滤: {args.filter})" if args.filter else ""
    print(f"✅ 生成 Markdown: {output_file}{filter_info}")
    
    # 显示统计
    stats = tree.get_stats()
    total = stats['total']
    if args.filter:
        filtered = len([n for n in tree.nodes if n.status == args.filter])
        print(f"   节点: {filtered}/{total}")
    else:
        print(f"   节点: {total}")
