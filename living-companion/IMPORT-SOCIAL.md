# Living Companion - 社交情境层：记录导入模块设计

## 核心原则

- **用户主动选择导入**：你决定导入哪些记录
- **提取后确认**：系统提取候选信息，你确认后才入库
- **最小化存储**：只保留对决策有用的信息，不存完整对话

---

## 支持格式

### 1. 飞书会话导出
**格式**：飞书原生导出（JSON/HTML）
```json
{
  "messages": [
    {
      "sender": "张（技术负责人）",
      "timestamp": "2026-03-24T14:30:00",
      "content": "这个方案时间上可能来不及，我们需要再评估一下",
      "type": "text"
    }
  ]
}
```

**提取目标**：
- 关系人：张（技术负责人）
- 关键事件：方案时间争议
- 情绪信号：担忧、抵触
- 项目关联：Living Soul 技术实现

---

### 2. 微信聊天记录
**格式**：微信导出文本/截图OCR
```
[2026-03-24 14:30] 张（技术负责人）
这个方案时间上可能来不及
我们需要再评估一下

[2026-03-24 14:35] 你
那你的建议是？

[2026-03-24 14:40] 张
我觉得分阶段上线比较现实
```

**解析逻辑**：
- 识别发送者（你 vs 他人）
- 时间戳提取
- 关键词匹配（"来不及"、"评估"、"建议"）

---

### 3. 会议记录
**格式**：飞书文档/Notion/Markdown
```markdown
## Living Soul 项目对齐会
**时间**：2026-03-24  
**参与者**：你、张（技术）、李（运营）

### 关键结论
- 张：技术实现需要 3 周，担心时间太紧
- 李：运营准备需要提前 1 周，希望 4 月初启动
- 冲突点：时间预期不一致

### 待办
- [ ] 你：协调双方时间预期
- [ ] 张：提供详细排期
```

**提取目标**：
- 参与者关系图谱
- 各方立场和顾虑
- 冲突点和待办

---

## 导入流程

```
┌─────────────────────────────────────────┐
│ 1. 用户上传记录                          │
│    - 飞书导出文件                        │
│    - 微信聊天记录                        │
│    - 会议记录文档                        │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ 2. 系统自动解析                          │
│    - 提取参与者                          │
│    - 识别关键事件                        │
│    - 检测情绪信号                        │
│    - 关联项目（Forest匹配）               │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ 3. 生成候选摘要                          │
│    ├─ 发现关系人：张（技术负责人）         │
│    │   关键事件：方案时间争议              │
│    │   情绪信号：担忧                      │
│    │   关联项目：Living Soul              │
│    │                                      │
│    └─ 发现关系人：李（运营负责人）         │
│        关键事件：未明确表态                │
│        需求：提前1周准备时间               │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ 4. 用户确认/编辑                         │
│    - [✓] 确认张的信息                    │
│    - [✓] 确认李的信息                    │
│    - [ ] 忽略其他参与者                   │
│    - [编辑] 修改关系描述                  │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ 5. 入库                                  │
│    - 保存到 social_context.json          │
│    - 关联 Forest 项目                    │
│    - 丢弃原始记录（不存储）               │
└─────────────────────────────────────────┘
```

---

## 数据结构（导入后）

```json
{
  "social_context": {
    "import_history": [
      {
        "import_id": "imp_001",
        "source": "飞书会话导出_张_20260324.json",
        "import_date": "2026-03-27T15:40:00",
        "records_extracted": 2,
        "user_confirmed": 2,
        "user_ignored": 0
      }
    ],
    "relationships": [
      {
        "id": "rel_zhang_001",
        "name": "张",
        "title": "技术负责人",
        "source": "imported",  // imported | manual
        "import_id": "imp_001",
        "first_seen": "2026-03-24T14:30:00",
        "last_updated": "2026-03-27T15:40:00",
        "communication_pattern": "直接表达担忧，需要提前预警",
        "key_events": [
          {
            "date": "2026-03-24",
            "event": "对方案时间表示担忧",
            "sentiment": "concerned",
            "project": "Living Soul",
            "quote": "这个方案时间上可能来不及"
          }
        ],
        "current_status": "时间紧张，有抵触情绪",
        "projects_involved": ["Living Soul"],
        "user_notes": "他觉得 AI 方案太激进",
        "privacy_level": "project_only"  // project_only | full_access
      }
    ]
  }
}
```

---

## 关键特性

### 1. 自动关联 Forest 项目
- 从对话内容提取项目名称
- 匹配 Forest 中的活跃项目
- 自动创建 `social_dependencies`

### 2. 情绪信号提取
```python
# 关键词匹配
anxiety_signals = ["来不及", "担心", "害怕", "压力", "紧张"]
resistance_signals = ["再评估", "不太现实", "可能不行", "需要再考虑"]
support_signals = ["支持", "同意", "没问题", "可以推进"]

# 输出
events.append({
    "sentiment": "concerned",  // concerned | resistant | supportive | neutral
    "confidence": 0.8
})
```

### 3. 冲突检测
```python
# 同一项目中不同参与者的立场对比
conflict = {
    "type": "timeline_disagreement",
    "party_a": {"name": "张", "stance": "需要3周"},
    "party_b": {"name": "李", "stance": "希望4月初启动"},
    "gap": "时间预期不一致"
}
```

### 4. 隐私分级
```json
{
  "privacy_level": "project_only"  // 只在项目上下文中使用
  // 可选：full_access（全局可用）
}
```

---

## 命令行接口

```bash
# 导入飞书记录
python3 import_social.py \
  --source feishu \
  --file /path/to/export.json \
  --project "Living Soul" \
  --dry-run  # 先预览，不保存

# 导入会议记录
python3 import_social.py \
  --source markdown \
  --file /path/to/meeting.md \
  --interactive  # 交互式确认

# 查看已导入关系
python3 companion.py --list-social

# 删除某条导入记录
python3 companion.py --delete-relationship rel_zhang_001
```

---

## 使用示例

### 场景：导入与张的技术对齐会记录

**步骤 1：上传记录**
```bash
python3 import_social.py --source feishu --file zhang_chat_20260324.json
```

**步骤 2：系统提取**
```
发现 1 个关系人：
  姓名：张
  推断身份：技术负责人（基于对话内容）
  关键事件：
    - 2026-03-24：对方案时间表示担忧（"来不及"）
    - 2026-03-24：建议分阶段上线
  情绪信号：concerned（置信度 0.8）
  关联项目：Living Soul（匹配 Forest）

确认导入？（y/n/edit）
```

**步骤 3：用户确认**
```
> y
> 编辑身份：技术负责人 → 后端技术负责人
> 添加备注：他对 AI 有顾虑

已保存到 social_context.json
关联到 Forest 项目：Living Soul
```

**步骤 4：后续使用**
```
你： "这个项目推进不了"

Companion： "我注意到 Living Soul 卡在'技术实现'。
          从导入的记录看，张（后端技术负责人）在 3 天前表示时间担忧，
          建议分阶段上线。
          
          这是同一问题延续，还是新的阻塞？"
```

---

## 下一步实现

1. **解析器开发**：飞书/微信/会议记录解析
2. **确认界面**：命令行交互式确认
3. **关联逻辑**：自动匹配 Forest 项目
4. **隐私控制**：分级存储和访问控制

要我立即开始实现导入模块吗？
