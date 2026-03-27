# Living Forest 索引系统 - Agent 执行文档

> 本文档定义 Karo（及团队 Agent）如何维护索引系统
> 通过自然语言交互，而非机械化命令

---

## 1. 核心原则

### 1.1 Agent 角色定位

Agent 不是命令的执行者，而是**索引的策展人**：
- 感知用户意图，主动维护索引
- 理解自然语言，转化为索引操作
- 保持索引与现实同步，不依赖用户记忆

### 1.2 交互范式

```
用户自然语言 ──→ Agent 理解意图 ──→ 执行索引操作 ──→ 反馈结果
     ↑                                                    ↓
     └────────────── 必要时询问确认 ←──────────────────────┘
```

**示例**：
- 用户："Living Soul 项目进展到哪了？"
- Agent：识别关键词 "Living Soul" → 读取 active-index → 加载 detail_files → 回答

---

## 2. 触发词与意图映射

### 2.1 索引更新触发词

| 用户表达 | 意图 | Agent 行动 |
|:---|:---|:---|
| "新建一个 XXX 项目" | 创建项目 | 扫描目录结构 → 生成索引条目 → 添加到 active-index |
| "XXX 项目做完了" | 标记完成 | 检查 _tree.json 状态 → 迁移到 archived-index |
| "把 XXX 归档" | 手动归档 | 同上 |
| "激活 XXX 项目" | 复活项目 | 从 archived-index 移至 active-index |
| "给 XXX 加个关键词" | 更新关键词 | 修改 active-index 对应条目 |
| "索引是不是过期了" | 验证索引 | 运行验证 → 报告差异 → 询问是否修复 |
| "扫一下所有项目" | 重建索引 | 扫描所有示例目录 → 重建两个索引文件 |

### 2.2 索引查询触发词

| 用户表达 | 意图 | Agent 行动 |
|:---|:---|:---|
| "最近有什么项目" | 查询活跃项目 | 读取 active-index → 按 priority 排序汇报 |
| "关于 XXX 的项目" | 关键词搜索 | 匹配 keywords → 返回项目列表 |
| "XXX 进展如何" | 查询具体项目 | 匹配项目 → 读取 ACTIVE.md + detail_files → 综合回答 |
| "归档了哪些项目" | 查询历史 | 读取 archived-index → 简要汇报 |

---

## 3. 标准执行流程

### 3.1 创建新项目索引

**触发**：用户提及新建项目

**执行步骤**：
```
1. 确认项目路径和名称
   "你是在 ~/Projects/livingsoul/living-dream/examples/ 下新建的吗？"

2. 扫描项目结构
   - 查找 _tree.json（如有）
   - 查找 README.md、ACTIVE.md 等文档
   - 扫描关键代码文件

3. 提取关键词
   - 从项目名提取
   - 从文档标题/摘要提取
   - 询问用户："这个项目主要关于什么？"

4. 生成分类
   - 检查 _tree.json 中的 status
   - active/research/draft → active-index
   - done/archived → archived-index

5. 写入索引
   - 更新 active-index.json
   - 自动备份旧版本

6. 反馈结果
   "已为 'Soul Memory' 建立索引，关键词：梦境、记忆、抽签..."
```

### 3.2 更新项目状态

**触发**：用户提及项目完成/归档/激活

**执行步骤**：
```
1. 确认项目名称和意图
   "你是想把 'Token Saver' 标记为已完成吗？"

2. 更新 Living Forest 状态（如需要）
   - 修改 _tree.json 中的 node.status
   - 或询问用户："需要我同时在 Living Forest 中标记为 done 吗？"

3. 迁移索引条目
   - 从 active-index 读取项目数据
   - 简化为 archived-index 格式
   - 添加到 archived-index
   - 从 active-index 移除

4. 更新元数据
   - archived_at = 当前时间
   - brief = 一句话描述（询问用户或自动生成）

5. 反馈结果
   "'Token Saver' 已归档。活跃项目剩余 2 个。"
```

### 3.3 关键词查询

**触发**：用户询问项目进展或提及关键词

**执行步骤**：
```
1. 解析用户输入
   - 提取关键词（分词、同义词扩展）
   - 示例："梦境系统" → ["梦境", "dream", "系统"]

2. 匹配索引
   - 读取 active-index
   - 计算匹配分数（精确 > 前缀 > 包含）

3. 处理匹配结果
   
   情况 A：唯一匹配
   → 读取该项目的 ACTIVE.md 和 detail_files
   → 综合回答
   
   情况 B：多匹配
   → 列出匹配项目："找到 2 个相关项目：1. Soul Memory（梦境记忆）..."
   → 询问用户："你想了解哪一个？"
   
   情况 C：无匹配
   → 尝试 archived-index
   → 仍无结果则告知："未找到活跃项目，需要我全局搜索吗？"

4. 返回结果
   - 结构化摘要
   - 关键进展
   - 下一步建议（如有）
```

### 3.4 每日索引验证

**触发**：每日首次对话（heartbeat 或用户主动联系）

**执行步骤**：
```
1. 读取两个索引文件

2. 快速验证
   - JSON 格式有效性
   - 路径是否存在
   - 统计项目数量是否匹配

3. 检测异常
   - 路径失效的项目 → 标记为 "orphan"
   - status 与索引分类不一致 → 提示迁移

4. 生成报告（仅在异常时）
   "索引健康检查：发现 1 个路径失效的项目（Token Saver），需要清理吗？"

5. 静默通过（无异常）
   不打扰用户
```

---

## 4. 与用户协作场景

### 4.1 关键词补全

**场景**：Agent 生成的关键词不够准确

```
Agent: "我为 'Living Soul' 提取了关键词：集成、openclaw、记忆系统"
User: "再加一个：预加载"
Agent: [更新 active-index] "已添加 '预加载'。还有其他关键词吗？"
```

### 4.2 文件关联确认

**场景**：Agent 不确定哪些文件应该加入 detail_files

```
Agent: "扫描到以下文件可能相关：
        1. README.md
        2. design-doc.md
        3. temp-notes.md（临时笔记）
        哪些需要加入详细索引？"
User: "1 和 2"
Agent: [更新 detail_files 列表]
```

### 4.3 项目复活

**场景**：用户想重新启动已归档项目

```
User: "把 Token Saver 重新激活"
Agent: "Token Saver 当前状态为 archived（2026-02-20）。
        激活后将移至活跃项目列表。
        确认吗？"
User: "确认"
Agent: [执行迁移，更新 last_active，询问新 priority]
```

---

## 5. 异常处理

### 5.1 索引文件损坏

```
检测：JSON 解析失败
行动：
  1. 从 backup/ 恢复最近的备份
  2. 告知用户："索引文件损坏，已从备份恢复（2026-03-25 版本）"
  3. 询问："需要我重新扫描项目更新索引吗？"
```

### 5.2 路径不存在

```
检测：project.path 指向的目录不存在
行动：
  1. 标记为 orphan
  2. 询问用户："'Token Saver' 的路径已失效，是移动了还是删除了？"
  
  用户选择：
  - "移动了" → 询问新路径 → 更新索引
  - "删除了" → 从索引移除
  - "暂时不管" → 保留 orphan 标记，下次提醒
```

### 5.3 并发更新冲突

```
检测：时间戳比预期旧（可能另一 Agent 已更新）
行动：
  1. 重新读取当前索引
  2. 合并变更（时间戳新者优先）
  3. 如有冲突，询问用户："Douglas 刚刚也更新了索引，保留谁的变更？"
```

---

## 6. 执行检查清单

Agent 每次执行索引操作后，自查：

- [ ] JSON 格式有效（通过 Python json 模块验证）
- [ ] 路径存在且可读
- [ ] 项目数量与 meta.project_count 一致
- [ ] 备份已生成（更新操作时）
- [ ] 用户已收到明确反馈

---

## 7. 示例对话

### 示例 1：新建项目

```
User: 我要在 living-forest 下面新建一个项目，叫 Agent Team Coordination

Agent: 了解。让我扫描一下项目结构并建立索引。

[扫描 ~/Projects/livingsoul/living-forest/examples/agent-team/]
[发现 _tree.json, README.md, protocol.md]

Agent: 扫描完成。提取到关键词：agent、team、coordination、协议、协作。
        这个项目主要关于什么？我可以用更精确的关键词。

User: 主要是团队任务分派和进度同步

Agent: 更新关键词：agent、team、coordination、任务分派、进度同步、协议。
        状态检测为 active，将加入活跃索引。
        确认建立索引吗？

User: 确认

Agent: ✅ 已为 'Agent Team Coordination' 建立索引。
        关键词：agent、team、coordination、任务分派、进度同步、协议
        详细文件：README.md, protocol.md
        优先级：medium（可调整）
```

### 示例 2：查询进展

```
User: 梦境系统现在怎么样了？

Agent: [匹配关键词 "梦境" → Soul Memory]
        
        Soul Memory（梦境记忆系统）当前状态：
        
        🔄 活跃节点：4 个
           - 002.2 梦境输出（进行中）
           - 004.3 积累签库（进行中）
           - 004.4 AI对话集成（草稿）
           
        ✅ 已完成：8 个
           - 抽签机核心功能
           - 亮度系统
           - 自然衰减公式
           
        最后更新：2026-03-26 16:43
        
        需要查看某个具体节点的详细内容吗？
```

---

## 8. 版本历史

| 版本 | 日期 | 变更 |
|:---|:---|:---|
| v1.0 | 2026-03-26 | 初始版本，定义 Agent 自然语言交互规范 |

---

*本文档供 Karo 及团队 Agent 执行使用*
*规范版本：v1.0*
