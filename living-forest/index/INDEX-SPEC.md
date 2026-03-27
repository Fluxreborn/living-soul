# Living Forest 索引系统 SPEC

> 状态感知分层索引架构 v1.0

---

## 1. 架构概述

### 1.1 核心原则

- **分层存储**：活跃项目详细索引 / 非活跃项目简易索引
- **状态驱动**：根据项目状态自动分类，无需手动维护
- **按需加载**：关键词触发定向读取，避免遍历式搜索
- **显式维护**：索引生成/更新由命令触发，确保一致性

### 1.2 文件位置

```
~/Projects/livingsoul/living-forest/index/
├── active-index.json      # 活跃项目详细索引
├── archived-index.json    # 非活跃项目简易索引
└── INDEX-SPEC.md         # 本规范文档
```

---

## 2. JSON Schema

### 2.1 active-index.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["meta", "projects"],
  "properties": {
    "meta": {
      "type": "object",
      "required": ["generated_at", "version"],
      "properties": {
        "generated_at": { "type": "string", "format": "date-time" },
        "version": { "type": "string", "enum": ["v1"] },
        "project_count": { "type": "integer" },
        "generator": { "type": "string" }
      }
    },
    "projects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "path", "keywords", "status"],
        "properties": {
          "name": { "type": "string", "description": "项目名称" },
          "path": { "type": "string", "description": "绝对或相对路径" },
          "keywords": { 
            "type": "array", 
            "items": { "type": "string" },
            "description": "检索关键词（中文/英文）"
          },
          "status": { 
            "type": "string", 
            "enum": ["active", "research", "draft"],
            "description": "项目状态"
          },
          "main_tree": { 
            "type": ["string", "null"], 
            "description": "_tree.json 相对路径" 
          },
          "active_md": { 
            "type": ["string", "null"], 
            "description": "ACTIVE.md 相对路径" 
          },
          "detail_files": { 
            "type": "array", 
            "items": { "type": "string" },
            "description": "详细文档路径列表"
          },
          "last_active": { 
            "type": "string", 
            "format": "date-time",
            "description": "最后活跃时间"
          },
          "priority": { 
            "type": "string", 
            "enum": ["high", "medium", "low"],
            "description": "加载优先级"
          }
        }
      }
    }
  }
}
```

### 2.2 archived-index.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["meta", "projects"],
  "properties": {
    "meta": {
      "type": "object",
      "properties": {
        "generated_at": { "type": "string", "format": "date-time" },
        "version": { "type": "string" }
      }
    },
    "projects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "path", "status"],
        "properties": {
          "name": { "type": "string" },
          "path": { "type": "string" },
          "status": { 
            "type": "string", 
            "enum": ["done", "archived", "blocked"] 
          },
          "archived_at": { 
            "type": "string", 
            "format": "date-time" 
          },
          "brief": { 
            "type": "string", 
            "description": "一句话描述" 
          }
        }
      }
    }
  }
}
```

---

## 3. 维护操作规范

> **执行层**：由 Agent（Karo）通过自然语言交互触发，详见 `AGENT-EXECUTION.md`
> 本节仅定义规范，不涉及具体命令

### 3.1 索引更新触发条件

| 触发场景 | Agent 响应 | 优先级 |
|:---|:---|:---|
| 用户说"新项目 XXX" | 扫描项目结构 → 生成索引条目 | 高 |
| 节点状态从 active → done | 自动迁移到 archived-index | 高 |
| 用户添加/修改关键文件 | 更新 detail_files 列表 | 中 |
| 每日首次对话 | 快速验证索引有效性 | 低 |
| 用户问"最近有什么项目" | 读取 active-index 汇报 | 中 |

### 3.2 状态迁移规则

```
状态变更时 Agent 自动处理：

active → done     : 从 active-index 移除，加入 archived-index
active → archived : 同上
research → active : 保持在 active-index，更新 priority 为 high
draft → active    : 从 archived-index 移至 active-index
done → active     : 复活项目，反向迁移，更新 last_active
```

### 3.3 关键词维护来源

Agent 提取关键词的优先级：
1. **显式配置**：`_tree.json` 中的 `meta.keywords` 字段
2. **节点标签**：所有 `node.label` 去重提取
3. **描述内容**：`node.description` 关键词提取（停用词过滤）
4. **文件路径**：路径中的有意义的目录名
5. **用户输入**：用户提及项目时的用词（学习记忆）

关键词规范：
- 中英文混合存储
- 同义词合并（如 "梦境" = "dream"）
- 每个项目 5-15 个关键词为宜
- 禁止：项目名本身、无意义词汇（"项目"、"文件"）

### 3.4 文件维护规范

#### 生成后验证
Agent 每次更新索引后，自动验证：
- JSON 格式有效性
- path 是否存在
- detail_files 是否可读
- keywords 是否为空

#### 备份策略
- 每次生成自动备份旧版本：`index/backup/active-index-YYYYMMDD-HHMMSS.json`
- 保留最近 10 个版本
- 超过 30 天的备份自动清理

#### 合并冲突
多 Agent 同时更新时，策略：时间戳较新者优先，冲突时保留 active-index 内容

### 3.5 人工干预

允许场景（Agent 协助用户执行）：
- 添加遗漏的关键词
- 修正文件路径
- 调整 priority

禁止场景：
- 直接修改 `generated_at`
- 手动更改 `project_count`（由生成器自动计算）
- 修改 status（应通过 Living Forest 状态变更）

人工编辑后，Agent 必须运行验证。

---

## 4. 使用流程

### 4.1 OpenClaw 加载流程

```
用户执行 /new
    ↓
1. 读取 active-index.json
2. 建立关键词 → 项目映射表
3. 预加载高优先级项目的 ACTIVE.md（可选）
    ↓
用户提问涉及关键词
    ↓
4. 匹配项目 → 定向读取 detail_files
5. 返回精准回答
```

### 4.2 关键词匹配优先级

```
精确匹配 > 前缀匹配 > 包含匹配 > 同义词匹配

示例：
用户说 "梦境系统"
- 精确："梦境系统" → 100% 匹配
- 前缀："梦境" → 80% 匹配  
- 包含："梦" → 60% 匹配
- 同义词："dream" → 70% 匹配
```

### 4.3 降级策略

```
活跃项目未找到 → 尝试 archived-index → 尝试全局搜索 → 告知无结果
```

---

## 5. 示例

### 5.1 完整 active-index.json

```json
{
  "meta": {
    "generated_at": "2026-03-26T18:30:00+08:00",
    "version": "v1",
    "project_count": 2,
    "generator": "lf-index v0.1"
  },
  "projects": [
    {
      "name": "Soul Memory",
      "path": "~/Projects/livingsoul/living-dream",
      "keywords": ["梦境", "记忆", "抽签", "睡眠", "soul", "dream", "签筒", "亮度"],
      "status": "active",
      "main_tree": "examples/soul-memory/_tree.json",
      "active_md": "examples/soul-memory/ACTIVE.md",
      "detail_files": [
        "README.md",
        "soul-context.md",
        "soul-memory-simple.json",
        "soul_memory_system_v31.py"
      ],
      "last_active": "2026-03-26T16:43:43",
      "priority": "high"
    },
    {
      "name": "Living Soul Integration",
      "path": "~/Projects/livingsoul",
      "keywords": ["集成", "openclaw", "预加载", "记忆系统", "分层索引"],
      "status": "research",
      "main_tree": null,
      "active_md": null,
      "detail_files": [
        "README.md",
        "LIVING-SOUL-RECOVERY.md"
      ],
      "last_active": "2026-03-26T17:51:00",
      "priority": "high"
    }
  ]
}
```

### 5.2 完整 archived-index.json

```json
{
  "meta": {
    "generated_at": "2026-03-26T18:30:00+08:00",
    "version": "v1"
  },
  "projects": [
    {
      "name": "Token Saver",
      "path": "~/Projects/livingsoul/living-forest/examples/token-saver",
      "status": "archived",
      "archived_at": "2026-02-20T10:00:00",
      "brief": "Token 优化项目，已归档"
    },
    {
      "name": "Echo Network",
      "path": "~/Projects/livingsoul/living-dream/legacy",
      "status": "archived", 
      "archived_at": "2026-03-24T00:00:00",
      "brief": "回声网络原方案，技术复杂度过高废弃"
    }
  ]
}
```

---

## 6. 配套文档

| 文档 | 用途 | 读者 |
|:---|:---|:---|
| `INDEX-SPEC.md` | 规范定义（本文件） | 开发者、Agent 设计者 |
| `AGENT-EXECUTION.md` | Agent 执行流程 | Karo、团队 Agent |
| `active-index.json` | 活跃项目索引数据 | Agent 运行时读取 |
| `archived-index.json` | 归档项目索引数据 | Agent 运行时读取 |

---

## 7. 版本历史

| 版本 | 日期 | 变更 |
|:---|:---|:---|
| v1.0 | 2026-03-26 | 初始版本，定义状态感知分层索引架构 |

---

*此文档由 Living Forest 索引系统生成*
*规范版本：v1.0*
