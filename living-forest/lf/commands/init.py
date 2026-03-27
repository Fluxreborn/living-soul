"""
初始化命令 - lf init
"""

import sys
from pathlib import Path
from ..models import create_default_tree


def run(args, work_dir: Path):
    """执行 init 命令"""
    tree_file = work_dir / "_tree.json"
    
    if tree_file.exists():
        print(f"错误: 项目已存在: {tree_file}")
        sys.exit(1)
    
    tree = create_default_tree(
        name=args.name,
        description=args.description
    )
    
    tree.save(tree_file)
    print(f"✅ 初始化项目: {args.name}")
    print(f"   文件: {tree_file}")
    print(f"   描述: {args.description or '(无)'}")
