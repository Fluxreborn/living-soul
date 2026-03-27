"""
分支命令 - lf branch
"""

import sys
from pathlib import Path
from ..models import Tree, Node


def run(args, work_dir: Path):
    """执行 branch 命令"""
    tree_file = work_dir / "_tree.json"
    
    if not tree_file.exists():
        print(f"错误: 未找到项目文件: {tree_file}")
        print("请先运行: lf init <project-name>")
        sys.exit(1)
    
    tree = Tree.load(tree_file)
    
    # 检查父节点
    parent = tree.get_node(args.parent)
    if not parent:
        print(f"错误: 父节点不存在: {args.parent}")
        print(f"可用节点: {', '.join(n.id for n in tree.nodes)}")
        sys.exit(1)
    
    # 生成新 ID
    new_id = tree.get_next_id(args.parent)
    
    # 创建节点
    node = Node(
        id=new_id,
        label=args.label,
        status="draft",
        type=args.type,
        parent=args.parent
    )
    
    tree.add_node(node)
    tree.save(tree_file)
    
    print(f"✅ 创建分支: {new_id}")
    print(f"   父节点: {args.parent} ({parent.label})")
    print(f"   名称: {args.label}")
    print(f"   类型: {args.type}")
