"""
active 命令 - 生成 ACTIVE.md 上下文预加载文件
"""

from datetime import datetime, timedelta
from pathlib import Path
import json


def run(args, work_dir: Path):
    """生成 ACTIVE.md 上下文文件"""
    
    # 查找 _tree.json
    tree_file = work_dir / "_tree.json"
    if not tree_file.exists():
        print(f"错误: 未找到 _tree.json")
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
    recent_days = 3
    recent_threshold = now - timedelta(days=recent_days)
    
    # 分类节点
    recent_active = []  # 3日内活跃
    active_nodes = []   # 所有活跃状态
    blocked_nodes = []  # 阻塞的
    
    for node in nodes:
        status = node.get("status", "")
        updated_at = node.get("updated_at") or node.get("created_at")
        
        # 检查是否最近活跃
        is_recent = False
        if updated_at:
            try:
                updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00').replace('+00:00', ''))
                is_recent = updated >= recent_threshold
            except:
                pass
        
        if is_recent:
            recent_active.append(node)
        
        if status == "active":
            active_nodes.append(node)
        elif status == "blocked":
            blocked_nodes.append(node)
    
    # 生成 ACTIVE.md
    output_file = work_dir / "ACTIVE.md"
    
    content = f"""# ACTIVE — 当前工作焦点

> 项目：{meta.get('name', 'Unknown')}
> 生成时间：{now.strftime('%Y-%m-%d %H:%M')}
> 版本：{meta.get('version', 'v1')}

---

## 🔥 最近 {recent_days} 天活跃（优先关注）

"""
    
    if recent_active:
        # 按时间排序
        recent_active.sort(
            key=lambda x: x.get('updated_at', x.get('created_at', '')), 
            reverse=True
        )
        
        for node in recent_active[:10]:  # 最多显示10个
            node_id = node.get("id", "?")
            label = node.get("label", "未命名")
            status = node.get("status", "unknown")
            node_type = node.get("type", "unknown")
            description = node.get("description", "")[:50]
            
            # 状态图标
            status_icons = {
                "active": "🔄",
                "done": "✅",
                "archived": "🪦",
                "draft": "📝",
                "research": "🧪",
                "blocked": "⏸️"
            }
            icon = status_icons.get(status, "❓")
            
            # 类型标记
            type_mark = {
                "trunk": "【主】",
                "branch": "【支】",
                "graveyard": "【墓】"
            }.get(node_type, "")
            
            content += f"- {icon} **{node_id}** {label} {type_mark}\n"
            if description:
                content += f"  └─ {description}...\n"
    else:
        content += "（最近 3 天无活跃项目）\n"
    
    content += f"""

---

## 🔄 进行中（所有活跃状态）

"""
    
    if active_nodes:
        for node in active_nodes:
            node_id = node.get("id", "?")
            label = node.get("label", "未命名")
            progress = node.get("progress", 0)
            progress_bar = "█" * int(progress * 10) + "░" * (10 - int(progress * 10))
            
            content += f"- **{node_id}** {label}\n"
            content += f"  └─ 进度: [{progress_bar}] {progress*100:.0f}%\n"
    else:
        content += "（暂无进行中的任务）\n"
    
    content += f"""

---

## ⏸️ 阻塞/等待

"""
    
    if blocked_nodes:
        for node in blocked_nodes:
            node_id = node.get("id", "?")
            label = node.get("label", "未命名")
            description = node.get("description", "")[:60]
            content += f"- **{node_id}** {label}\n"
            if description:
                content += f"  └─ {description}...\n"
    else:
        content += "（暂无阻塞任务）\n"
    
    content += f"""

---

## 📍 项目位置

- **工作目录**：`{work_dir}`
- **树文件**：`_tree.json`
- **完整文档**：`_tree.md`
- **血统谱系**：`_lineage.md`（如有）

---

## 📝 快速命令

```bash
# 查看最近活跃
lf recent

# 查看统计
lf status

# 创建分支
lf branch <parent-id> "分支名称"

# 生成 Markdown
lf render
```

---

*此文件由 `lf active` 自动生成*
*下次更新：项目状态变更时*
"""
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 生成上下文文件: {output_file}")
    print(f"   最近 {recent_days} 天活跃: {len(recent_active)} 个")
    print(f"   进行中: {len(active_nodes)} 个")
    print(f"   阻塞: {len(blocked_nodes)} 个")
    print()
    print(f"文件包含：")
    print(f"  - 🔥 最近活跃项目（优先关注）")
    print(f"  - 🔄 所有进行中任务")
    print(f"  - ⏸️ 阻塞/等待任务")
    print(f"  - 📍 项目位置信息")
    print(f"  - 📝 常用命令")
