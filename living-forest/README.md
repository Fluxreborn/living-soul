# Living Forest System / 活树森林系统

> 项目式记忆管理方法论 - JSON 主数据 + CLI 自动化架构 + 分层索引系统

---

## 新增：分层索引系统（v1.0）

Living Forest 现在包含**状态感知的分层索引**，让 AI Agent 可以：

- **快速定位**：通过关键词匹配找到项目，无需遍历文件
- **分层加载**：活跃项目详细索引 / 归档项目简易索引
- **自然语言交互**：用户说"梦境系统进展如何"→自动匹配→加载详情

### 索引文件

```
index/
├── AGENT-README.md        # Agent 快速接入指南
├── AGENT-EXECUTION.md     # Agent 执行流程参考
├── INDEX-SPEC.md          # 索引规范定义
├── active-index.json      # 活跃项目详细索引
└── archived-index.json    # 归档项目简易索引
```

### 当前索引项目

| 项目 | 状态 | 关键词 |
|:---|:---|:---|
| Soul Memory | 🔄 active | 梦境、记忆、抽签、睡眠 |
| Living Soul Integration | 🧪 research | 集成、openclaw、分层索引 |
| Token Saver | 🪦 archived | - |

### Agent 如何使用

```
1. 对话开始时读取 index/active-index.json
2. 建立关键词 → 项目映射表
3. 用户提及关键词时，定向加载项目详情
4. 项目状态变更时，自动迁移索引分类
```

详见 `index/AGENT-README.md`

---

## 快速开始

### 安装

无需安装，直接克隆使用：

```bash
git clone <repo>
cd living-forest

# 使用 CLI
python3 lf.py --help
```

### 零依赖

- 纯 Python 标准库
- 无需 pip install
- Python 3.7+ 即可运行

---

## CLI 命令

### `lf init` - 初始化项目

```bash
# 创建新活树项目
python3 lf.py init my-project -d "项目描述"

# 生成 _tree.json
```

### `lf branch` - 创建分支

```bash
# 在节点 001 下创建子任务
python3 lf.py branch 001 "子任务名称"

# 自动编号：001.1, 001.2...
```

### `lf status` - 查看统计

```bash
# 显示项目统计
python3 lf.py status

# 详细模式（显示所有节点）
python3 lf.py status -v
```

### `lf render` - 生成 Markdown

```bash
# 生成 _tree.md
python3 lf.py render

# 指定输出文件
python3 lf.py render -o README.md

# 只显示活跃节点
python3 lf.py render -f active
```

### `lf check` - 验证结构

```bash
# 检查树结构完整性
python3 lf.py check

# 自动修复问题
python3 lf.py check --fix
```

---

## JSON 数据结构

### `_tree.json` 结构

```json
{
  "meta": {
    "name": "项目名称",
    "version": "v1",
    "created_at": "2026-03-26T16:00:00",
    "updated_at": "2026-03-26T16:00:00",
    "description": "项目描述",
    "status": "active"
  },
  "nodes": [
    {
      "id": "001",
      "label": "立项",
      "status": "done",
      "type": "trunk",
      "parent": null,
      "children": ["001.1"],
      "description": ""
    }
  ],
  "evolution": [],
  "resurrections": []
}
```

### 状态枚举

| 状态 | 图标 | 说明 |
|------|------|------|
| active | 🔄 | 进行中 |
| done | ✅ | 完成 |
| archived | 🪦 | 已归档 |
| draft | 📝 | 草稿 |
| research | 🧪 | 研究中 |
| blocked | ⚠️ | 阻塞 |

### 类型枚举

| 类型 | 说明 |
|------|------|
| trunk | 主干（核心任务）|
| branch | 分支（实验性）|
| graveyard | 墓地（废弃但可复活）|

---

## 工作流示例

### 1. 初始化项目

```bash
mkdir my-project
cd my-project
python3 /path/to/lf.py init "My Project" -d "项目描述"
```

### 2. 添加主干节点

编辑 `_tree.json` 添加初始节点：

```json
{
  "nodes": [
    {
      "id": "001",
      "label": "立项",
      "status": "done",
      "type": "trunk",
      "parent": null,
      "children": []
    }
  ]
}
```

### 3. 创建分支

```bash
python3 /path/to/lf.py branch 001 "需求分析"
# 生成 001.1

python3 /path/to/lf.py branch 001 "技术设计"
# 生成 001.2
```

### 4. 查看状态

```bash
python3 /path/to/lf.py status -v
```

### 5. 生成文档

```bash
python3 /path/to/lf.py render -o _tree.md
```

---

## 数据迁移

从旧版 Markdown 迁移到 JSON：

```bash
python3 migrate_md_to_json.py
```

自动转换 `_tree.md` → `_tree.json`

---

## 项目结构

```
living-forest/
├── lf.py                   # CLI 入口
├── lf/                     # CLI 模块
│   ├── cli.py             # 主命令解析
│   ├── models.py          # 数据模型
│   ├── renderer.py        # Markdown 渲染
│   └── commands/          # 子命令
│       ├── init.py
│       ├── branch.py
│       ├── status.py
│       ├── render.py
│       └── check.py
├── schema/
│   └── tree-schema.json   # JSON Schema
├── examples/              # 示例项目
│   ├── soul-memory/
│   │   ├── _tree.md      # 源文件
│   │   └── _tree.json    # 生成的 JSON
│   └── token-saver/
│       ├── _tree.md
│       └── _tree.json
└── README.md
```

---

## 架构对比

| 特性 | 旧版 (Markdown) | 新版 (JSON + CLI) |
|------|----------------|-------------------|
| 编辑 | 手动编辑 | CLI 自动化 |
| 校验 | 无 | 自动验证 |
| 排序 | 手动 | 自动编号 |
| 渲染 | 手动 | `lf render` |
| 依赖 | 无 | 无（标准库）|

---

## 设计原则

1. **零外部依赖** - 只用 Python 标准库
2. **人可读** - JSON 格式清晰易读
3. **自动化** - CLI 处理重复工作
4. **可验证** - 自动检查结构完整性
5. **可渲染** - 随时生成 Markdown 文档

---

## 示例项目

- `examples/soul-memory/` - Soul Memory 人格记忆系统
- `examples/token-saver/` - Token Saver 优化项目（已归档）

---

*基于 Living Forest 方法论*
*JSON 主数据 + CLI 自动化架构 v0.1*
