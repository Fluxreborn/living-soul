"""
recent 命令 - 显示最近活跃的项目
"""

from datetime import datetime, timedelta
from pathlib import Path
import json


def run(args, work_dir: Path):
    """运行 recent 命令"""
    
    # 查找 _tree.json
    tree_file = work_dir / "_tree.json"
    if not tree_file.exists():
        print(f"错误: 未找到 _tree.json，请先运行 `lf init`")
        return
    
    # 读取数据
    with open(tree_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nodes = data.get("nodes", [])
    meta = data.get("meta", {})
    
    if not nodes:
        print("暂无节点")
        return
    
    # 计算时间阈值
    now = datetime.now()
    days = args.days
    threshold = now - timedelta(days=days)
    
    # 过滤最近活跃的节点
    recent_nodes = []
    for node in nodes:
        updated_at = node.get("updated_at") or node.get("created_at")
        if updated_at:
            try:
                updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00').replace('+00:00', ''))
                if updated >= threshold:
                    recent_nodes.append((node, updated))
            except:
                pass
    
    # 按时间排序
    recent_nodes.sort(key=lambda x: x[1], reverse=True)
    
    # 显示结果
    print(f"📅 最近 {days} 天活跃的项目")
    print(f"项目: {meta.get('name', 'Unknown')}")
    print(f"时间: {threshold.strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}")
    print()
    
    if not recent_nodes:
        print(f"  (最近 {days} 天无活跃项目)")
        return
    
    # 高亮图标
    highlight = "🔥" if days <= 3 else "⚡" if days <= 7 else "📌"
    
    for node, updated in recent_nodes:
        node_id = node.get("id", "?")
        label = node.get("label", "未命名")
        status = node.get("status", "unknown")
        node_type = node.get("type", "unknown")
        
        # 状态图标
        status_icons = {
            "active": "🔄",
            "done": "✅",
            "archived": "🪦",
            "draft": "📝",
            "research": "🧪"
        }
        icon = status_icons.get(status, "❓")
        
        # 类型颜色标记
        type_mark = {
            "trunk": "【主】",
            "branch": "【支】",
            "graveyard": "【墓】"
        }.get(node_type, "")
        
        # 计算天数差
        days_ago = (now - updated).days
        if days_ago == 0:
            time_str = "今天"
        elif days_ago == 1:
            time_str = "昨天"
        else:
            time_str = f"{days_ago}天前"
        
        print(f"  {highlight} {icon} {node_id} {label} {type_mark}")
        print(f"      状态: {status} | 更新: {time_str} ({updated.strftime('%m-%d %H:%M')})")
    
    print()
    print(f"共 {len(recent_nodes)} 个节点在最近 {days} 天内活跃")
    
    # 显示统计
    by_status = {}
    for node, _ in recent_nodes:
        s = node.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
    
    print("状态分布: ", end="")
    for s, c in sorted(by_status.items()):
        print(f"{status_icons.get(s, '❓')}{s}:{c} ", end="")
    print()
