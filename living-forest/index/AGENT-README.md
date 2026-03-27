# Living Forest Index - Agent 使用说明书

> 如果你是一个有记忆管理需求的 AI Agent，这份文档告诉你如何接入和使用 Living Forest 索引系统。

---

## 1. 这是什么？

Living Forest Index 是一个**分层记忆索引系统**，帮你管理长期项目的记忆：

- **不用遍历**：用户问项目进展时，不用遍历所有文件
- **关键词匹配**：通过自然语言关键词快速定位项目
- **分层加载**：活跃项目详细索引 / 归档项目简易索引
- **自动维护**：状态变更时自动迁移分类

---

## 2. 快速开始

### 2.1 初始化

如果你是第一个接入这个系统的 Agent：

```
1. 确认索引目录存在：
   ~/Projects/livingsoul/living-forest/index/

2. 读取规范文档：
   - INDEX-SPEC.md（了解索引结构）
   - AGENT-EXECUTION.md（了解如何维护）

3. 生成首批索引数据（如有现有项目）
```

### 2.2 日常接入

每次对话开始时：

```
1. 读取 active-index.json
2. 建立关键词 → 项目映射表
3. 准备响应用户查询
```

---

## 3. 核心使用场景

### 场景 A：用户询问项目进展

**用户说**："Living Soul 现在怎么样了？"

**你的流程**：
```
1. 提取关键词："living soul"

2. 查询 active-index.json：
   - 匹配 keywords 字段
   - 找到对应项目条目

3. 读取项目详情：
   - 加载 "active_md" 指向的 ACTIVE.md
   - 按需读取 "detail_files" 中的文件

4. 综合回答用户
```

### 场景 B：用户提及新项目

**用户说**："我新建了一个 Agent Coordination 项目"

**你的流程**：
```
1. 确认项目路径

2. 扫描项目结构：
   - 查找 _tree.json（如有）
   - 查找 README.md 等文档

3. 提取关键词（询问用户或自动生成）

4. 写入 active-index.json：
   {
     "name": "Agent Coordination",
     "path": "~/Projects/...",
     "keywords": ["agent", "coordination", "..."],
     "status": "active",
     "detail_files": ["README.md", "..."],
     "priority": "medium"
   }

5. 备份旧版本（生成 backup/active-index-YYYYMMDD-HHMMSS.json）

6. 告知用户索引已建立
```

### 场景 C：项目状态变更

**用户说**："Token Saver 项目做完了"

**你的流程**：
```
1. 从 active-index.json 读取项目数据

2. 简化为归档格式，写入 archived-index.json

3. 从 active-index.json 移除该项目

4. 更新元数据（archived_at, brief）

5. 告知用户："已归档，活跃项目剩余 X 个"
```

---

## 4. 文件结构参考

```
index/
├── INDEX-SPEC.md              # 索引结构规范（必读）
├── AGENT-EXECUTION.md         # 执行流程参考（按需阅读）
├── active-index.json          # 活跃项目索引
├── archived-index.json        # 归档项目索引
└── backup/                    # 自动备份目录
    ├── active-index-20260325-143022.json
    └── ...
```

---

## 5. 关键字段说明

### active-index.json 中的项目条目

| 字段 | 类型 | 用途 |
|:---|:---|:---|
| `name` | string | 项目名称 |
| `path` | string | 项目绝对路径 |
| `keywords` | array | 检索关键词（中英文） |
| `status` | enum | active / research / draft |
| `active_md` | string | ACTIVE.md 路径（快速加载） |
| `detail_files` | array | 详细文档列表 |
| `last_active` | datetime | 最后活跃时间 |
| `priority` | enum | high / medium / low |

### archived-index.json 中的项目条目

| 字段 | 类型 | 用途 |
|:---|:---|:---|
| `name` | string | 项目名称 |
| `path` | string | 项目路径 |
| `status` | enum | done / archived / blocked |
| `archived_at` | datetime | 归档时间 |
| `brief` | string | 一句话描述 |

---

## 6. 关键词匹配策略

当用户提及项目时，按优先级匹配：

```
1. 精确匹配（用户说 "Soul Memory"，keywords 中有 "Soul Memory"）
   → 100% 匹配

2. 关键词匹配（用户说 "梦境系统"，keywords 中有 "梦境"）
   → 80% 匹配

3. 项目名称匹配（用户说 "Living Soul"，name 中有 "Living Soul"）
   → 70% 匹配

4. 同义词匹配（用户说 "dream"，keywords 中有 "梦境"）
   → 60% 匹配
```

**多匹配时**：列出选项让用户选择，或按 priority + last_active 排序取最高。

---

## 7. 维护检查清单

每次更新索引后，自查：

- [ ] JSON 格式有效（通过标准库验证）
- [ ] path 存在且可读
- [ ] 备份已生成（更新操作时）
- [ ] 项目数量与 meta.project_count 一致
- [ ] 用户已收到明确反馈

---

## 8. 异常处理速查

| 异常 | 处理 |
|:---|:---|
| JSON 解析失败 | 从 backup/ 恢复最近备份 |
| 路径不存在 | 标记为 orphan，询问用户移动/删除 |
| 并发更新冲突 | 重新读取，合并变更（时间戳新者优先）|
| 关键词为空 | 询问用户补全，或使用项目名作为默认值 |

---

## 9. 与其他系统的协作

### 与 Living Dream 的关系
- Living Dream 负责**内容记忆**（签、梦境、灵魂上下文）
- Living Forest Index 负责**项目索引**（有哪些项目、在哪找）

### 与 OpenClaw 的关系
- 在 `/new` 或心跳时加载索引
- 作为 MEMORY.md 的补充，提供更结构化的项目检索

---

## 10. 示例代码（Python 伪代码）

```python
# 加载索引
import json
from pathlib import Path

def load_index():
    index_path = Path("~/Projects/livingsoul/living-forest/index/active-index.json")
    with open(index_path) as f:
        return json.load(f)

# 关键词查询
def find_project(keyword, index):
    matches = []
    for project in index["projects"]:
        score = 0
        # 精确匹配
        if keyword in project["keywords"]:
            score = 100
        # 包含匹配
        elif any(keyword in kw for kw in project["keywords"]):
            score = 80
        # 项目名称匹配
        elif keyword.lower() in project["name"].lower():
            score = 70
        
        if score > 0:
            matches.append((project, score))
    
    # 按分数排序
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

# 读取项目详情
def load_project_details(project):
    files_to_read = []
    if project.get("active_md"):
        files_to_read.append(project["active_md"])
    files_to_read.extend(project.get("detail_files", []))
    
    contents = {}
    for file_path in files_to_read:
        full_path = Path(project["path"]) / file_path
        if full_path.exists():
            contents[file_path] = full_path.read_text()
    
    return contents
```

---

## 11. 版本

- **当前版本**：v1.0
- **最后更新**：2026-03-26
- **规范文档**：INDEX-SPEC.md
- **执行文档**：AGENT-EXECUTION.md

---

*祝你的记忆管理井然有序。*
