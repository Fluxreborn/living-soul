# 06 - 实现路线图 / Implementation Roadmap

## 当前状态评估

| 层级 | 状态 | 文件 |
|------|------|------|
| 文件层（Markdown）| ✅ 完成 | 4 篇方法论 + 示例 |
| 解析层（TreeIndex）| 🔄 待实现 | 本文档 |
| 向量层（FAISS）| 📍 未开始 | 待实现 |
| 集成层（OpenClaw）| 📍 未开始 | 待实现 |

## 第一阶段：TreeIndex 解析器

### 1.1 数据结构定义

```python
# tree_types.py
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class NodeStatus(Enum):
    COMPLETED = "✅"
    IN_PROGRESS = "🔄"
    STANDBY = "⏸️"
    RESEARCH = "🧪"
    BLOCKED = "⚠️"
    ABANDONED = "🪦"

@dataclass
class TreeNode:
    id: str              # "001", "002.1", etc.
    name: str            # "立项", "抽签机"
    status: NodeStatus
    description: str     # 简要描述
    parent: Optional[str] = None  # 父节点 ID
    children: List[str] = None    # 子节点 IDs

@dataclass
class LivingTree:
    project_name: str
    root_description: str
    trunk: List[TreeNode]      # 主干
    branches: List[TreeNode]   # 分支
    graveyard: List[TreeNode]  # 墓地
    evolution_history: List[VersionInfo]
    resurrection_history: List[ResurrectionInfo]

@dataclass
class VersionInfo:
    version: str           # "v1", "v2"
    date: str
    summary: str           # 变化摘要
    changes: List[str]     # 具体变更

@dataclass
class ResurrectionInfo:
    new_id: str
    old_id: str
    date: str
    reason: str
```

### 1.2 解析器实现

```python
# tree_parser.py
import re
from pathlib import Path

class TreeParser:
    """解析 _tree.md 文件"""
    
    def __init__(self, tree_md_path: Path):
        self.path = tree_md_path
        self.content = tree_md_path.read_text()
    
    def parse(self) -> LivingTree:
        """主解析入口"""
        return LivingTree(
            project_name=self._extract_project_name(),
            root_description=self._extract_root_description(),
            trunk=self._parse_trunk(),
            branches=self._parse_branches(),
            graveyard=self._parse_graveyard(),
            evolution_history=self._parse_evolution(),
            resurrection_history=self._parse_resurrections()
        )
    
    def _parse_trunk(self) -> List[TreeNode]:
        """解析主干部分
        
        输入：
        ```tree
        Soul Memory
        ├── 001 立项 [✅]
        │   └── 核心概念
        ├── 002 抽签机 [🔄]
        │   ├── 002.1 签数生成 [✅]
        │   └── 002.2 梦境输出 [🔄]
        ```
        """
        # 正则提取树形结构
        tree_section = self._extract_section("主干（Trunk）")
        nodes = []
        
        for line in tree_section.split('\n'):
            # 匹配：├── 001 立项 [✅]
            match = re.match(r'[├└]──\s+(\d+(?:\.\d+)*)\s+(.+?)\s+\[(.+?)\]', line)
            if match:
                node_id, name, status_str = match.groups()
                nodes.append(TreeNode(
                    id=node_id,
                    name=name.strip(),
                    status=self._parse_status(status_str),
                    description=self._extract_description(node_id)
                ))
        
        return nodes
    
    def _parse_graveyard(self) -> List[TreeNode]:
        """解析墓地表格"""
        # 提取 markdown 表格
        table = self._extract_table("墓地（Graveyard）")
        nodes = []
        
        for row in table[1:]:  # 跳过表头
            nodes.append(TreeNode(
                id=row[0],           # 编号
                name=row[1],         # 名称
                status=NodeStatus.ABANDONED,
                description=f"废弃原因：{row[3]}，复活条件：{row[4]}"
            ))
        
        return nodes
    
    def get_active_context(self, max_tokens: int = 500) -> str:
        """获取用于新 session 的活跃上下文"""
        tree = self.parse()
        
        context = f"# {tree.project_name}\n\n"
        context += f"{tree.root_description}\n\n"
        context += "## 当前活跃\n"
        
        for node in tree.trunk:
            if node.status in [NodeStatus.IN_PROGRESS, NodeStatus.BLOCKED]:
                context += f"- {node.id} {node.name} [{node.status.value}]\n"
        
        return context[:max_tokens]
    
    def check_resurrection(self) -> List[ResurrectionInfo]:
        """检查满足复活条件的节点"""
        # 读取 graveyard 中的复活条件
        # 对比当前环境，返回可复活的节点
        pass
```

### 1.3 使用示例

```python
# usage.py
from tree_parser import TreeParser
from pathlib import Path

# 解析 Soul Memory 的活树
parser = TreeParser(Path("projects/soul-memory/_tree.md"))
tree = parser.parse()

# 获取活跃任务
print("进行中：")
for node in tree.trunk:
    if node.status == NodeStatus.IN_PROGRESS:
        print(f"  - {node.id}: {node.name}")

# 生成 session 上下文
context = parser.get_active_context(max_tokens=500)
# 用于 OpenClaw 的 session 加载
```

## 第二阶段：与 OpenClaw 集成

### 2.1 可选方案对比

| 方案 | 复杂度 | 侵入性 | 推荐度 |
|------|--------|--------|--------|
| A: Python 脚本 + 文件读取 | 低 | 无 | ⭐⭐⭐ 推荐 |
| B: OpenClaw 插件 | 中 | 中 | ⭐⭐ 未来 |
| C: 完全自研 | 高 | 高 | ⭐ 不推荐 |

### 2.2 推荐方案：A（Python 脚本）

```python
# living_forest_loader.py
# 独立脚本，不修改 OpenClaw 核心

import json
from pathlib import Path
from tree_parser import TreeParser

class LivingForestLoader:
    """为 OpenClaw 生成记忆加载内容"""
    
    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir
        self.forest_path = projects_dir / "_forest.md"
    
    def load_for_session(self, project_hint: Optional[str] = None) -> dict:
        """
        生成新 session 需要的记忆内容
        
        Returns:
            {
                "forest_overview": str,      # 森林总览（30秒阅读）
                "active_context": str,       # 当前项目活跃上下文
                "relevant_history": List[str] # 相关历史文件
            }
        """
        result = {
            "forest_overview": self._load_forest_overview(),
            "active_context": "",
            "relevant_history": []
        }
        
        if project_hint:
            # 用户提到了具体项目
            tree_path = self.projects_dir / project_hint / "_tree.md"
            if tree_path.exists():
                parser = TreeParser(tree_path)
                result["active_context"] = parser.get_active_context()
        
        return result
    
    def _load_forest_overview(self) -> str:
        """加载森林总图的前 30 行"""
        content = self.forest_path.read_text()
        lines = content.split('\n')[:30]
        return '\n'.join(lines)

# 命令行接口
if __name__ == "__main__":
    import sys
    
    loader = LivingForestLoader(Path("./projects"))
    
    # 用法: python living_forest_loader.py [project_name]
    project = sys.argv[1] if len(sys.argv) > 1 else None
    result = loader.load_for_session(project)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 2.3 与 AGENTS.md 配合

修改后的加载流程：

```markdown
## Every Session（修订版 - 未来实施）

Before doing anything else:

1. Read `SOUL.md` — 我是谁
2. Read `USER.md` — 我在帮谁
3. **Read `ACTIVE.md`** — 当前焦点（替代两天的 memory 文件）
4. **Read `projects/_forest.md`（前30行）** — 森林总览
5. **If discussing specific project**: 
   - Run `python living_forest_loader.py <project>`
   - 读返回的 `active_context`
```

## 第三阶段：向量增强（可选）

### 3.1 何时需要向量

| 场景 | 是否需要向量 | 替代方案 |
|------|------------|---------|
| 项目 < 10 个 | ❌ 不需要 | 直接文件读取 |
| 项目 > 20 个 | ✅ 需要 | FAISS 索引 |
| 跨项目语义搜索 | ✅ 需要 | 向量相似度 |

### 3.2 FAISS 集成

```python
# vector_index.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class TreeVectorIndex:
    """树节点的向量索引"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)  # 384维向量
        self.metadata = {}
    
    def index_tree(self, tree: LivingTree):
        """将整棵树向量化"""
        for node in tree.trunk + tree.branches:
            text = f"{node.id} {node.name} {node.description}"
            embedding = self.model.encode(text)
            
            idx = len(self.metadata)
            self.index.add(np.array([embedding]))
            self.metadata[idx] = {
                "project": tree.project_name,
                "node_id": node.id,
                "text": text
            }
    
    def search(self, query: str, k: int = 3) -> List[dict]:
        """语义搜索"""
        query_vec = self.model.encode(query)
        distances, indices = self.index.search(
            np.array([query_vec]), k
        )
        
        results = []
        for idx in indices[0]:
            if idx in self.metadata:
                results.append(self.metadata[idx])
        
        return results

# 使用
index = TreeVectorIndex()
index.index_tree(tree)

# 搜索
results = index.search("抽签机最近进展", k=3)
# 返回相关节点，无需加载整棵树
```

## 实施检查清单

### Phase 1（本周）
- [ ] 创建 `tree_types.py` 数据类
- [ ] 实现基础 `TreeParser`
- [ ] 测试解析 Soul Memory 的 `_tree.md`
- [ ] 验证 `get_active_context()` 输出

### Phase 2（下周）
- [ ] 创建 `living_forest_loader.py`
- [ ] 测试命令行接口
- [ ] 准备 AGENTS.md 修订草案
- [ ] 模拟新 session 加载流程

### Phase 3（未来）
- [ ] 评估是否需要向量索引（项目数量 > 20？）
- [ ] 如需，集成 FAISS
- [ ] 可选：可视化界面（树形图）

## 预期效果

| 指标 | 当前 | Phase 1 后 | Phase 2 后 |
|------|------|-----------|-----------|
| Session 启动加载 | ~10K tokens | ~10K tokens | ~7K tokens |
| 跨项目上下文恢复 | 困难 | 中等 | 容易 |
| 废弃想法复活 | 手动查找 | 自动检测 | 自动检测 + 推荐 |

---
*路线图版本：2026-03-24*
*下一步：实现 TreeParser*
