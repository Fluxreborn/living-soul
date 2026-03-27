# 活树森林技术架构 / Living Forest Technical Architecture

> 基于现有开源方案的分层记忆系统实现

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    活树森林语义层 (Living Forest)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ _tree.md     │  │ _lineage.md  │  │ _forest.md       │  │
│  │ 活树解析器    │  │ 血统追踪器    │  │ 森林总图生成器    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    记忆抽象层 (Memory Abstraction)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 树形索引     │  │ 向量嵌入      │  │ 时序版本控制      │  │
│  │ (Tree Index) │  │ (Embedding)  │  │ (Versioning)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    存储层 (Storage Layer)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 文件系统     │  │ 向量数据库    │  │ 图数据库         │  │
│  │ (Markdown)   │  │ (FAISS/      │  │ (可选 Neo4j)     │  │
│  │              │  │  pgvector)   │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 分层设计

### 第一层：存储层（借用成熟技术）

#### 1.1 文件存储 - 原生 Markdown
**现状**：已使用，无需改动

```
projects/
├── <project>/
│   ├── _tree.md          # 纯文本，Git 版本控制
│   ├── _tree.v1.md       # 历史快照
│   ├── _lineage.md       # 血统声明
│   └── trunk/
│       └── xxx.md        # 分支详情
```

**优势**：
- 人可读、可编辑
- Git 原生版本控制
- 无需额外数据库

#### 1.2 向量存储 - 借用 Mem0/FAISS
**技术选型**：
- **简单版**：FAISS（Facebook 开源，纯本地）
- **增强版**：Mem0（支持多后端）

**数据流**：
```python
# _tree.md 内容 → 向量嵌入 → FAISS 索引
tree_content = read("_tree.md")
embedding = model.encode(tree_content)  # 如 text-embedding-3-small
faiss_index.add(embedding, metadata={
    "project": "soul-memory",
    "version": "v3",
    "path": "projects/soul-memory/_tree.md"
})
```

#### 1.3 图存储 - 可选 Neo4j
**场景**：跨项目复杂关系查询
**简化版**：直接在 `_forest.md` 中维护，无需数据库

### 第二层：记忆抽象层（借用 Cognee 思路）

#### 2.1 树形索引（活树森林特有）
**功能**：解析 `_tree.md` 生成结构化树

```python
class TreeIndex:
    """解析 _tree.md 生成可操作的结构"""
    
    def parse(self, tree_md: str) -> Tree:
        """
        解析 markdown 树形文本
        返回：Tree 对象（主干、分支、墓地）
        """
        
    def get_active_nodes(self) -> List[Node]:
        """获取当前活跃节点（用于新 session 加载）"""
        
    def get_evolution_history(self) -> List[Version]:
        """获取演化历史（v1 → v2 → v3）"""
        
    def find_resurrectable(self) -> List[Node]:
        """找出满足复活条件的节点"""
```

**技术借鉴**：Cognee 的 GraphRAG 解析器思路

#### 2.2 向量嵌入（借用 Mem0）
**功能**：将树节点内容向量化，支持语义搜索

```python
class TreeEmbedding:
    """树节点的向量表示"""
    
    def embed_node(self, node: Node) -> Vector:
        """单个节点的嵌入"""
        
    def search_similar(self, query: str, top_k: int = 3) -> List[Node]:
        """语义搜索："抽签机" → 找到相关节点"""
        # 借用 Mem0 的向量搜索逻辑
```

#### 2.3 时序版本控制（借用 Git + 自定义）
**功能**：`_tree.v1.md`, `_tree.v2.md` 的对比分析

```python
class TreeVersioning:
    """树形结构的版本控制"""
    
    def diff(self, v1: str, v2: str) -> Diff:
        """比较两个版本的差异"""
        
    def get_node_history(self, node_id: str) -> List[Change]:
        """追踪某个节点的变化历史"""
```

### 第三层：活树森林语义层（活树森林核心）

#### 3.1 活树解析器
```python
class LivingTreeParser:
    """解析 _tree.md 的业务语义"""
    
    def parse_trunk(self) -> List[TrunkNode]:
        """解析主干（活跃任务）"""
        
    def parse_branches(self) -> List[BranchNode]:
        """解析分支（实验性）"""
        
    def parse_graveyard(self) -> List[GraveyardNode]:
        """解析墓地（废弃但可复活）"""
        
    def check_resurrection_conditions(self) -> List[Resurrection]:
        """检查哪些节点满足复活条件"""
```

#### 3.2 血统追踪器
```python
class LineageTracker:
    """跨项目血统关系追踪"""
    
    def get_parent(self, project: str) -> Optional[Parent]:
        """获取父项目"""
        
    def get_children(self, project: str) -> List[Child]:
        """获取子项目"""
        
    def trace_bloodline(self, project: str) -> Tree:
        """追溯完整的血统链"""
```

#### 3.3 森林总图生成器
```python
class ForestMapper:
    """生成 _forest.md"""
    
    def scan_projects(self) -> List[Project]:
        """扫描所有项目"""
        
    def build_genealogy_table(self) -> Table:
        """构建血统表"""
        
    def generate_forest_md(self) -> str:
        """生成 markdown 格式的森林总图"""
```

## 技术选型决策

| 组件 | 借用方案 | 自研部分 | 理由 |
|------|---------|---------|------|
| 向量嵌入 | **Mem0** / FAISS | 树节点编码策略 | Mem0 成熟稳定 |
| 图关系 | **Cognee** 思路 | 树形特定结构 | Cognee 通用图太重 |
| 版本控制 | **Git** | 树形 diff 算法 | Git 原生支持 |
| 文件存储 | **文件系统** | 活树 markdown 格式 | 简单可编辑 |
| 语义解析 | **自研** | Tree/Lineage/Forest 解析器 | 业务特定 |

## 实现阶段

### Phase 1：文件层（已完成 ✅）
- [x] `_tree.md` 格式规范
- [x] `_lineage.md` 血统声明
- [x] `_forest.md` 森林总图
- [x] 示例项目（Soul Memory + Token Saver）

### Phase 2：解析层（当前 🔄）
- [ ] TreeIndex 解析器（Python/Node）
- [ ] LineageTracker 血统追踪
- [ ] ForestMapper 总图生成

### Phase 3：增强层（未来 📍）
- [ ] FAISS 向量索引
- [ ] 语义搜索集成
- [ ] 可视化界面（借鉴 Obsidian Graph）

### Phase 4：自动化（远景 🌅）
- [ ] 自动更新 `_tree.md`（从 session 提取）
- [ ] 自动检测复活条件
- [ ] 智能推荐项目关系

## 与现有系统对比

| 系统 | 定位 | 与活树森林关系 |
|------|------|---------------|
| **Cognee** | 通用知识图谱 | 底层借鉴，上层简化 |
| **Mem0** | 通用记忆层 | 向量存储后端 |
| **Obsidian** | 个人知识库 | 可视化参考 |
| **活树森林** | **项目管理专用语义层** | **本文方案** |

## 下一步行动

1. **实现 TreeIndex 解析器**（Python 优先）
2. **集成 FAISS 向量索引**
3. **测试语义搜索效果**

---
*架构设计：2026-03-24*
*技术调研：Cognee + Mem0 + FAISS*
