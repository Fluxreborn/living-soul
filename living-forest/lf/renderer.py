"""
Markdown 渲染器 - 将 Tree 渲染为 Markdown
"""

from datetime import datetime
from typing import List, Optional
from .models import Tree, Node


class MarkdownRenderer:
    """Markdown 渲染器"""
    
    STATUS_LABELS = {
        "active": "进行中",
        "done": "完成",
        "archived": "已归档",
        "draft": "草稿",
        "research": "研究中",
        "blocked": "阻塞"
    }
    
    TYPE_LABELS = {
        "trunk": "主干",
        "branch": "分支",
        "graveyard": "墓地"
    }
    
    def render(self, tree: Tree, filter_status: Optional[str] = None) -> str:
        """渲染树为 Markdown"""
        lines = []
        
        # 标题
        lines.append(f"# {tree.meta.get('name', 'Untitled')}")
        lines.append("")
        
        # 元信息
        lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        if "version" in tree.meta:
            lines.append(f"> 版本：{tree.meta['version']}")
        if "status" in tree.meta:
            status_icon = {"active": "🔄", "archived": "🪦", "draft": "📝"}.get(tree.meta["status"], "⚪")
            lines.append(f"> 状态：{status_icon} {tree.meta['status']}")
        lines.append("")
        
        # 项目描述
        if tree.meta.get("description"):
            lines.append("## 项目根")
            lines.append("")
            lines.append(tree.meta["description"])
            lines.append("")
        
        # 按类型分组渲染
        self._render_section(lines, tree, "trunk", "主干（Trunk）", filter_status)
        self._render_section(lines, tree, "branch", "分支（Branches）", filter_status)
        self._render_section(lines, tree, "graveyard", "墓地（Graveyard）", filter_status)
        
        # 演化历史
        if tree.evolution:
            lines.append("---")
            lines.append("")
            lines.append("## 演化历史")
            lines.append("")
            for evo in tree.evolution:
                lines.append(f"- **{evo.get('version')}** ({evo.get('date', '未知日期')})")
                lines.append(f"  - {evo.get('summary', '')}")
                for change in evo.get("changes", []):
                    lines.append(f"  - {change}")
            lines.append("")
        
        # 复活记录
        if tree.resurrections:
            lines.append("---")
            lines.append("")
            lines.append("## 复活记录")
            lines.append("")
            for res in tree.resurrections:
                lines.append(f"- **{res.get('date', '未知日期')}**：{res.get('old_id')} → {res.get('new_id')}")
                lines.append(f"  - 原因：{res.get('reason', '')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_section(
        self, 
        lines: List[str], 
        tree: Tree, 
        type_filter: str, 
        title: str,
        status_filter: Optional[str] = None
    ) -> None:
        """渲染一个区域"""
        nodes = [n for n in tree.nodes if n.type == type_filter]
        if status_filter:
            nodes = [n for n in nodes if n.status == status_filter]
        
        if not nodes:
            return
        
        lines.append("---")
        lines.append("")
        lines.append(f"## {title}")
        lines.append("")
        
        if type_filter == "graveyard":
            # 墓地用表格
            lines.append("| 编号 | 名称 | 状态 | 描述 |")
            lines.append("|------|------|------|------|")
            for node in sorted(nodes, key=lambda n: n.get_sort_key()):
                status_label = self.STATUS_LABELS.get(node.status, node.status)
                desc = node.description[:50] + "..." if len(node.description) > 50 else node.description
                lines.append(f"| {node.id} | {node.label} | {status_label} | {desc} |")
            lines.append("")
        else:
            # 主干和分支用树形结构
            lines.append("```tree")
            roots = tree.get_roots()
            for root in roots:
                if root.type == type_filter:
                    self._render_tree_node(lines, tree, root, "", True, status_filter)
            lines.append("```")
            lines.append("")
            
            # 详细描述
            for node in sorted(nodes, key=lambda n: n.get_sort_key()):
                if node.description:
                    lines.append(f"**{node.id}** {node.label}")
                    lines.append(f"> {node.description}")
                    lines.append("")
    
    def _render_tree_node(
        self, 
        lines: List[str], 
        tree: Tree, 
        node: Node, 
        prefix: str, 
        is_last: bool,
        status_filter: Optional[str] = None
    ) -> None:
        """递归渲染树节点"""
        connector = "└── " if is_last else "├── "
        status_label = self.STATUS_LABELS.get(node.status, node.status)
        lines.append(f"{prefix}{connector}{node.id} {node.label} [{node.get_status_icon()} {status_label}]")
        
        children = tree.get_children(node.id)
        if status_filter:
            children = [c for c in children if c.status == status_filter]
        
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            self._render_tree_node(lines, tree, child, child_prefix, is_last_child, status_filter)
    
    def render_forest(self, trees: List[Tree]) -> str:
        """渲染森林总图"""
        lines = []
        lines.append("# 项目森林总图 / Project Forest Map")
        lines.append("")
        lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        
        # 按状态分组
        active_trees = [t for t in trees if t.meta.get("status") == "active"]
        archived_trees = [t for t in trees if t.meta.get("status") == "archived"]
        draft_trees = [t for t in trees if t.meta.get("status") == "draft"]
        
        # 活跃项目
        if active_trees:
            lines.append("## 活跃项目（Active）")
            lines.append("")
            lines.append("```forest")
            for tree in active_trees:
                lines.append(f"🌲 {tree.meta.get('name', 'Untitled')}")
                roots = tree.get_roots()
                for root in roots[:3]:  # 只显示前3个根节点
                    lines.append(f"  └── {root.id} {root.label} {root.get_status_icon()}")
            lines.append("```")
            lines.append("")
        
        # 归档项目
        if archived_trees:
            lines.append("## 归档项目（Archived）")
            lines.append("")
            for tree in archived_trees:
                lines.append(f"- 🪦 **{tree.meta.get('name', 'Untitled')}**")
            lines.append("")
        
        # 统计
        lines.append("---")
        lines.append("")
        lines.append("## 统计")
        lines.append("")
        lines.append(f"| 状态 | 数量 |")
        lines.append(f"|------|------|")
        lines.append(f"| 🔄 活跃 | {len(active_trees)} |")
        lines.append(f"| 📝 草稿 | {len(draft_trees)} |")
        lines.append(f"| 🪦 归档 | {len(archived_trees)} |")
        lines.append(f"| **总计** | **{len(trees)}** |")
        lines.append("")
        
        return "\n".join(lines)
