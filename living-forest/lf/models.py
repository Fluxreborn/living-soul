"""
Living Forest 数据模型
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class Node:
    """树节点"""
    
    VALID_STATUSES = ["active", "done", "archived", "draft", "research", "blocked"]
    VALID_TYPES = ["trunk", "branch", "graveyard"]
    
    def __init__(
        self,
        id: str,
        label: str,
        status: str = "draft",
        type: str = "trunk",
        parent: Optional[str] = None,
        children: Optional[List[str]] = None,
        description: str = "",
        files: Optional[List[Dict]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        self.id = id
        self.label = label
        self.status = status if status in self.VALID_STATUSES else "draft"
        self.type = type if type in self.VALID_TYPES else "trunk"
        self.parent = parent
        self.children = children or []
        self.description = description
        self.files = files or []
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.metadata = metadata or {}
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Node":
        return cls(**data)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "label": self.label,
            "status": self.status,
            "type": self.type,
            "parent": self.parent,
            "children": self.children,
            "description": self.description,
            "files": self.files,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }
    
    def get_level(self) -> int:
        """获取节点层级（001=1, 002.1=2）"""
        return len(self.id.split("."))
    
    def get_sort_key(self) -> tuple:
        """获取排序键"""
        parts = self.id.split(".")
        result = []
        for p in parts:
            try:
                result.append(int(p))
            except ValueError:
                # 非数字部分，放在最后
                result.append(9999)
                result.append(p)
        return tuple(result)
    
    def get_status_icon(self) -> str:
        """获取状态图标"""
        icons = {
            "active": "🔄",
            "done": "✅",
            "archived": "🪦",
            "draft": "📝",
            "research": "🧪",
            "blocked": "⚠️"
        }
        return icons.get(self.status, "⚪")


class Tree:
    """活树"""
    
    def __init__(
        self,
        meta: Dict,
        nodes: Optional[List[Node]] = None,
        evolution: Optional[List[Dict]] = None,
        resurrections: Optional[List[Dict]] = None
    ):
        self.meta = meta
        self.nodes = nodes or []
        self.evolution = evolution or []
        self.resurrections = resurrections or []
        self._node_map = {n.id: n for n in self.nodes}
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Tree":
        nodes = [Node.from_dict(n) for n in data.get("nodes", [])]
        return cls(
            meta=data.get("meta", {}),
            nodes=nodes,
            evolution=data.get("evolution", []),
            resurrections=data.get("resurrections", [])
        )
    
    @classmethod
    def load(cls, path: Path) -> "Tree":
        """从文件加载"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict:
        return {
            "meta": self.meta,
            "nodes": [n.to_dict() for n in self.nodes],
            "evolution": self.evolution,
            "resurrections": self.resurrections
        }
    
    def save(self, path: Path) -> None:
        """保存到文件"""
        self.meta["updated_at"] = datetime.now().isoformat()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """获取节点"""
        return self._node_map.get(node_id)
    
    def add_node(self, node: Node) -> None:
        """添加节点"""
        if node.id in self._node_map:
            raise ValueError(f"节点已存在: {node.id}")
        self.nodes.append(node)
        self._node_map[node.id] = node
        
        # 更新父节点的 children
        if node.parent:
            parent = self._node_map.get(node.parent)
            if parent and node.id not in parent.children:
                parent.children.append(node.id)
    
    def remove_node(self, node_id: str) -> None:
        """删除节点"""
        node = self._node_map.get(node_id)
        if not node:
            raise ValueError(f"节点不存在: {node_id}")
        
        # 从父节点的 children 中移除
        if node.parent:
            parent = self._node_map.get(node.parent)
            if parent and node_id in parent.children:
                parent.children.remove(node_id)
        
        # 删除所有子节点
        for child_id in node.children[:]:
            self.remove_node(child_id)
        
        # 从列表中移除
        self.nodes.remove(node)
        del self._node_map[node_id]
    
    def get_roots(self) -> List[Node]:
        """获取根节点（无主节点）"""
        return sorted(
            [n for n in self.nodes if n.parent is None],
            key=lambda n: n.get_sort_key()
        )
    
    def get_children(self, parent_id: str) -> List[Node]:
        """获取子节点"""
        parent = self._node_map.get(parent_id)
        if not parent:
            return []
        return sorted(
            [self._node_map[cid] for cid in parent.children if cid in self._node_map],
            key=lambda n: n.get_sort_key()
        )
    
    def get_next_id(self, parent_id: Optional[str] = None) -> str:
        """生成下一个可用 ID"""
        if parent_id is None:
            # 根级别节点
            root_ids = [n.id for n in self.nodes if n.parent is None]
            if not root_ids:
                return "001"
            max_num = max(int(rid) for rid in root_ids)
            return f"{max_num + 1:03d}"
        else:
            # 子节点
            parent = self._node_map.get(parent_id)
            if not parent:
                raise ValueError(f"父节点不存在: {parent_id}")
            
            existing = [cid for cid in parent.children if cid in self._node_map]
            if not existing:
                return f"{parent_id}.1"
            
            # 找出最大子序号
            max_sub = 0
            for cid in existing:
                sub_id = cid.split(".")[-1]
                max_sub = max(max_sub, int(sub_id))
            return f"{parent_id}.{max_sub + 1}"
    
    def validate(self) -> List[str]:
        """验证树结构，返回错误列表"""
        errors = []
        
        # 检查孤儿节点（parent 指向不存在的节点）
        for node in self.nodes:
            if node.parent and node.parent not in self._node_map:
                errors.append(f"孤儿节点: {node.id} 的父节点 {node.parent} 不存在")
        
        # 检查循环引用
        for node in self.nodes:
            visited = set()
            current = node.id
            while current:
                if current in visited:
                    errors.append(f"循环引用: {node.id}")
                    break
                visited.add(current)
                n = self._node_map.get(current)
                current = n.parent if n else None
        
        # 检查 children 一致性
        for node in self.nodes:
            for child_id in node.children:
                child = self._node_map.get(child_id)
                if not child:
                    errors.append(f"{node.id} 引用了不存在的子节点 {child_id}")
                elif child.parent != node.id:
                    errors.append(f"父子关系不一致: {node.id} -> {child_id}, 但 {child_id}.parent = {child.parent}")
        
        # 检查 ID 格式
        for node in self.nodes:
            if not re.match(r'^\d{3}(\.\d+)*$', node.id):
                errors.append(f"非法ID格式: {node.id}")
        
        return errors
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "total": len(self.nodes),
            "trunk": len([n for n in self.nodes if n.type == "trunk"]),
            "branch": len([n for n in self.nodes if n.type == "branch"]),
            "graveyard": len([n for n in self.nodes if n.type == "graveyard"]),
            "active": len([n for n in self.nodes if n.status == "active"]),
            "done": len([n for n in self.nodes if n.status == "done"]),
            "archived": len([n for n in self.nodes if n.status == "archived"]),
            "draft": len([n for n in self.nodes if n.status == "draft"]),
        }


def create_default_tree(name: str, description: str = "") -> Tree:
    """创建默认树"""
    meta = {
        "name": name,
        "version": "v1",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "description": description,
        "status": "active"
    }
    return Tree(meta=meta)
