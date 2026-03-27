"""
检查命令 - lf check
"""

import sys
from pathlib import Path
from ..models import Tree


def run(args, work_dir: Path):
    """执行 check 命令"""
    tree_file = work_dir / "_tree.json"
    
    if not tree_file.exists():
        print(f"错误: 未找到项目文件: {tree_file}")
        sys.exit(1)
    
    tree = Tree.load(tree_file)
    errors = tree.validate()
    
    if not errors:
        print("✅ 验证通过：树结构完整")
        print(f"   节点数: {len(tree.nodes)}")
        print(f"   根节点: {len(tree.get_roots())}")
        return
    
    print(f"⚠️  发现 {len(errors)} 个问题:")
    for error in errors:
        print(f"   - {error}")
    
    if args.fix:
        print()
        print("尝试自动修复...")
        fixed = _auto_fix(tree, errors)
        if fixed:
            tree.save(tree_file)
            print(f"✅ 已修复 {fixed} 个问题")
        else:
            print("❌ 无法自动修复，请手动处理")
    else:
        print()
        print("提示: 使用 --fix 尝试自动修复")
        sys.exit(1)


def _auto_fix(tree: Tree, errors: list) -> int:
    """尝试自动修复问题，返回修复数量"""
    fixed = 0
    
    for error in errors[:]:  # 复制列表避免修改时出错
        if "孤儿节点" in error:
            # 提取节点 ID
            parts = error.split("")
            if len(parts) >= 2:
                node_id = parts[0].replace("孤儿节点: ", "").strip()
                node = tree.get_node(node_id)
                if node:
                    # 将孤儿节点设为根节点
                    node.parent = None
                    print(f"   修复: {node_id} 设为根节点")
                    fixed += 1
        
        elif "引用了不存在的子节点" in error:
            # 从 children 列表中移除无效引用
            parts = error.split(" ")
            if len(parts) >= 4:
                parent_id = parts[0]
                child_id = parts[-1]
                parent = tree.get_node(parent_id)
                if parent and child_id in parent.children:
                    parent.children.remove(child_id)
                    print(f"   修复: 从 {parent_id} 移除无效引用 {child_id}")
                    fixed += 1
    
    return fixed
