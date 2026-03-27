"""
状态命令 - lf status
"""

import sys
from pathlib import Path
from ..models import Tree


def run(args, work_dir: Path):
    """执行 status 命令"""
    tree_file = work_dir / "_tree.json"
    
    if not tree_file.exists():
        print(f"错误: 未找到项目文件: {tree_file}")
        sys.exit(1)
    
    tree = Tree.load(tree_file)
    stats = tree.get_stats()
    
    print(f"📊 {tree.meta.get('name', 'Untitled')} 统计")
    print()
    print(f"版本: {tree.meta.get('version', 'v1')}")
    print(f"状态: {tree.meta.get('status', 'active')}")
    print(f"更新: {tree.meta.get('updated_at', '未知')}")
    print()
    print("节点统计:")
    print(f"  总计: {stats['total']}")
    print(f"  ├─ 主干(Trunk): {stats['trunk']}")
    print(f"  ├─ 分支(Branch): {stats['branch']}")
    print(f"  └─ 墓地(Graveyard): {stats['graveyard']}")
    print()
    print("状态分布:")
    print(f"  🔄 活跃: {stats['active']}")
    print(f"  ✅ 完成: {stats['done']}")
    print(f"  🪦 归档: {stats['archived']}")
    print(f"  📝 草稿: {stats['draft']}")
    
    if args.verbose:
        print()
        print("节点列表:")
        for node in sorted(tree.nodes, key=lambda n: n.get_sort_key()):
            parent_info = f" ← {node.parent}" if node.parent else ""
            print(f"  {node.id} {node.label} [{node.status}]{parent_info}")
