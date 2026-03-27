# Living Forest 系统改版报告

> **改版时间**: 2026-03-26  
> **执行者**: Woz  
> **版本**: v0.1.0

---

## 改版概述

将 Living Forest 从纯 Markdown 格式升级为 **JSON 主数据 + CLI 自动化架构**。

---

## 改版前状态

### 问题

1. **纯文本编辑** - 需要手动维护 `_tree.md` 的树形结构
2. **无校验机制** - 容易出现格式错误、ID 冲突
3. **手动编号** - 新增节点需要手动分配 ID
4. **难以自动化** - 无法程序化更新

### 文件格式

```markdown
```tree
Soul Memory
├── 001 立项 [✅ 完成]
│   └── 核心概念
└── 002 抽签机 [🔄 进行中]
    ├── 002.1 签数生成 [✅]
    └── 002.2 梦境输出 [🔄]
```
```

---

## 改版后架构

### 核心组件

```
living-forest/
├── lf.py                   # CLI 入口点
├── lf/
│   ├── cli.py             # 命令解析
│   ├── models.py          # Tree/Node 模型
│   ├── renderer.py        # Markdown 渲染器
│   └── commands/          # 子命令实现
├── schema/
│   └── tree-schema.json   # JSON Schema 定义
└── examples/              # 迁移后的示例
```

### 数据格式

**JSON 主数据** (`_tree.json`):

```json
{
  "meta": {
    "name": "Soul Memory",
    "version": "v3",
    "created_at": "2026-03-24T12:45:00",
    "status": "active"
  },
  "nodes": [
    {
      "id": "001",
      "label": "立项",
      "status": "done",
      "type": "trunk",
      "parent": null,
      "children": ["001.1"]
    }
  ]
}
```

---

## CLI 功能

### 已实现命令

| 命令 | 功能 | 状态 |
|------|------|------|
| `lf init` | 初始化新项目 | ✅ 完成 |
| `lf branch` | 创建分支（自动编号） | ✅ 完成 |
| `lf status` | 查看统计信息 | ✅ 完成 |
| `lf render` | 生成 Markdown | ✅ 完成 |
| `lf check` | 验证结构完整性 | ✅ 完成 |

### 使用示例

```bash
# 初始化项目
python3 lf.py init "My Project" -d "描述"

# 创建分支（自动分配 001.1）
python3 lf.py branch 001 "子任务"

# 查看统计
python3 lf.py status -v

# 生成 Markdown
python3 lf.py render -o _tree.md

# 验证结构
python3 lf.py check --fix
```

---

## 数据迁移

### 迁移的项目

| 项目 | 原文件 | 新文件 | 节点数 |
|------|--------|--------|--------|
| soul-memory | `_tree.md` | `_tree.json` | 13 |
| token-saver | `_tree.md` | `_tree.json` | 13 |

### 迁移脚本

`migrate_md_to_json.py`:
- 解析 Markdown 树形结构
- 提取节点关系
- 生成 JSON 文件

---

## 技术亮点

### 1. 零外部依赖

- 纯 Python 标准库
- 无需 pip install
- argparse + pathlib + json

### 2. 自动编号

```python
def get_next_id(self, parent_id=None):
    if parent_id is None:
        # 根节点：001, 002...
        return f"{max_root_num + 1:03d}"
    else:
        # 子节点：001.1, 001.2...
        return f"{parent_id}.{max_sub + 1}"
```

### 3. 结构验证

检查项：
- 孤儿节点（parent 不存在）
- 循环引用
- children 一致性
- ID 格式合法性

### 4. Markdown 渲染

从 JSON 生成：
- 树形结构图
- 状态表格
- 演化历史
- 复活记录

---

## 验证测试

### 测试用例

```bash
# 测试 1: 初始化
cd /tmp && mkdir test && cd test
python3 lf.py init "测试项目"
# ✅ 生成 _tree.json

# 测试 2: 创建分支
python3 lf.py branch 001 "需求分析"
# ✅ 创建 001.1

# 测试 3: 查看状态
python3 lf.py status -v
# ✅ 显示 2 个节点

# 测试 4: 渲染
python3 lf.py render
# ✅ 生成 _tree.md

# 测试 5: 验证
python3 lf.py check
# ✅ 结构完整
```

---

## 文件清单

### 新增文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `lf.py` | 231B | CLI 入口 |
| `lf/__init__.py` | 72B | 包初始化 |
| `lf/cli.py` | 3.1KB | 命令解析 |
| `lf/models.py` | 8.8KB | 数据模型 |
| `lf/renderer.py` | 7.1KB | 渲染器 |
| `lf/commands/*.py` | ~5KB | 命令实现 |
| `schema/tree-schema.json` | 4.0KB | JSON Schema |
| `migrate_md_to_json.py` | 7.3KB | 迁移脚本 |

### 更新文件

| 文件 | 变更 |
|------|------|
| `README.md` | 完全重写 |
| `examples/soul-memory/_tree.json` | 新增（迁移）|
| `examples/token-saver/_tree.json` | 新增（迁移）|

---

## 后续建议

### 短期优化

1. **树形渲染优化** - 修复根节点连接符显示
2. **批量导入** - 支持从 CSV/Excel 导入节点
3. **搜索功能** - `lf search "关键词"`

### 中期规划

1. **Forest 视图** - `lf forest` 生成森林总图
2. **版本对比** - `lf diff v1 v2`
3. **自动备份** - 保存时自动创建 .backup

### 长期愿景

1. **可视化界面** - Web 端树形编辑器
2. **协作支持** - Git 合并冲突处理
3. **集成 OpenClaw** - 自动加载到 session

---

## 总结

**核心成果**: 
- ✅ 完成 JSON + CLI 架构转型
- ✅ 实现 5 个核心 CLI 命令
- ✅ 成功迁移 2 个示例项目
- ✅ 零外部依赖，开箱即用

**架构升级**:
```
Markdown (手动编辑)
    ↓
JSON (结构化数据) + CLI (自动化工具)
```

**价值**:
- 自动化减少人工错误
- 结构化便于程序处理
- 可验证保证数据质量
- 可渲染保持人可读

---

*报告生成: 2026-03-26*  
*Woz | Living Forest v0.1.0*
