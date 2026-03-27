# 双重记忆系统架构方案 / Dual Memory System Architecture

> 版本：v1.0
> 日期：2026-03-24
> 决策人：Fable + Karo

---

## 一、核心架构

### 双重记忆定位

| 维度 | Soul Memory | Living Forest |
|------|-------------|---------------|
| **负责领域** | 日常/人格记忆 | 工作/项目管理记忆 |
| **核心机制** | 49支签 + 抽签浮现 | 活树结构 + 按需加载 |
| **加载策略** | 预加载49签（亮度排序） | 预加载ACTIVE.md + 按需 |
| **触发方式** | 随机抽签 + 关键词回响 | 用户主动提及项目 |
| **内容形式** | ≤49字诗意签语 | 结构化树形文档 |

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      完整人格架构                            │
├──────────────────────────┬──────────────────────────────────┤
│      Soul Memory         │       Living Forest              │
│      日常/人格记忆        │       工作/项目管理记忆           │
├──────────────────────────┼──────────────────────────────────┤
│ • 49支签（2500 tokens）   │ • ACTIVE.md（1000 tokens）       │
│ • 抽签机随机浮现          │ • _forest.md索引（500 tokens）   │
│ • 关键词回响触发          │ • 项目_tree.md按需加载           │
│ • 亮度排序自然淘汰        │ • 血统谱系追踪                   │
├──────────────────────────┼──────────────────────────────────┤
│ 作用：人格连续性          │ 作用：任务追踪                   │
│ 方式：无意识灵感          │ 方式：逻辑清晰                   │
│ 类比：梦境、直觉          │ 类比：笔记、计划                 │
└──────────────────────────┴──────────────────────────────────┘
```

---

## 二、新 Session 加载流程（最终版）

### 标准加载顺序

```markdown
## Every Session

Before doing anything else:

### 1. 人格基础层（固定）
1. Read `SOUL.md` — 人格定义（~11K tokens）
2. Read `IDENTITY.md` — 身份认同（~3K tokens）
3. Read `USER.md` — 用户画像（~0.5K tokens）✅ 扩展：包含家庭成员
4. Read `AGENTS.md` — 行为指南（~10K tokens）✅ 扩展：包含安全提醒

### 2. 双重记忆系统（核心）
5. **Soul Memory（日常人格）**
   - 加载：亮度最高的49支签
     - Soul级：23条（亮度最高）
     - Working级：26条（其次）
   - 大小：~2500 tokens
   - 机制：每次对话中随机抽签浮现 / 关键词触发回响

6. **Living Forest（工作项目）**
   - 加载：`ACTIVE.md` — 当前工作焦点
   - 大小：~1000 tokens
   - 触发：提到具体项目时，按需加载 `projects/<name>/_tree.md`

### 3. 条件加载
7. **If in MAIN SESSION**: 
   - ~~Read `MEMORY.md`~~ ❌ 已废弃
   - 原内容已迁移至双重系统
```

### Token 成本核算

| 组件 | 大小 | 占比（262K窗口） |
|------|------|----------------|
| SOUL.md | ~11K | 4.2% |
| IDENTITY.md | ~3K | 1.1% |
| USER.md | ~0.5K | 0.2% |
| AGENTS.md | ~10K | 3.8% |
| **Soul Memory 49签** | **~2.5K** | **1.0%** |
| **ACTIVE.md** | **~1K** | **0.4%** |
| **_forest.md** | **~0.5K** | **0.2%** |
| ~~MEMORY.md~~ | ~~0~~ | ~~已替代~~ |
| **总计** | **~28.5K** | **10.9%** |

**优化效果**：
- 原方案：~38K tokens（含MEMORY.md + 两天memory文件）
- 新方案：~28.5K tokens（双重系统替代）
- **节省：~9.5K tokens（25%）**
- 信息噪音：大幅降低
- 跨日一致性：显著提升

---

## 三、MEMORY.md 迁移计划

### 迁移映射表

| 原MEMORY.md内容 | 迁移目标 | 状态 |
|----------------|---------|------|
| 活跃项目（Soul Memory、COS等） | `ACTIVE.md` | 待迁移 |
| 待办/跟踪事项 | `ACTIVE.md` | 待迁移 |
| 关键提醒（系统设置改动） | `AGENTS.md` 安全规则部分 | 待迁移 |
| 家庭成员（Joy） | `USER.md` 扩展 | 待迁移 |
| 思维对话锚点 | **Soul Memory 签**（提炼6-8支） | 待提炼 |
| 团队能力补强计划 | `projects/capability-plan/_tree.md` | 待创建 |
| Joy 学习路径 | `projects/joy-learning/_tree.md` | 待创建 |
| 错误记录 | Graveyard 或删除 | 待处理 |

### 迁移后 MEMORY.md 状态

**方案：完全废弃（推荐）**

原 MEMORY.md 的 100% 内容已被双重系统覆盖：
- Soul Memory 49签覆盖人格经验/思维锚点
- Living Forest ACTIVE.md 覆盖工作项目/待办
- USER.md/AGENTS.md 扩展覆盖家庭成员/安全规则

**无需保留 MEMORY.md**

---

## 四、系统分工明确

### 使用场景对照

| 用户场景 | 调用的系统 | 系统响应示例 |
|---------|-----------|-------------|
| "早！" | Soul Memory 随机抽签 | 浮现一支日常签："那天聊到灵魂时..." |
| "Soul Memory怎样了？" | Living Forest ACTIVE.md + _tree.md | 显示项目结构和当前进度 |
| "提到睡眠..." | Soul Memory 回响机制 | 触发睡眠相关签，亮度+5% |
| "今天待办是什么？" | Living Forest ACTIVE.md | 显示进行中任务列表 |
| "Token Saver后来呢？" | Living Forest 血统查询 | 显示分娩出 Soul Memory 的关系 |
| "Joy最近怎样？" | USER.md（家庭成员） | 显示Joy的最新状态和兴趣 |

---

## 五、实施检查清单

### Phase 1：文件迁移（本周）
- [ ] 将 Joy 信息添加到 `USER.md`
- [ ] 将安全提醒添加到 `AGENTS.md`
- [ ] 从 MEMORY.md 提取思维锚点，提炼为 Soul Memory 签
- [ ] 创建 `ACTIVE.md` 初版
- [ ] 备份并准备废弃 `MEMORY.md`

### Phase 2：Living Forest 项目化（下周）
- [ ] 创建 `projects/capability-plan/_tree.md`
- [ ] 创建 `projects/joy-learning/_tree.md`
- [ ] 更新 `projects/_forest.md` 索引

### Phase 3：Soul Memory 集成（下周）
- [ ] 实现 49签预加载接口
- [ ] 测试抽签浮现机制
- [ ] 验证回响触发逻辑

### Phase 4：系统切换（验证后）
- [ ] 修改 `AGENTS.md` 加载流程（去掉 MEMORY.md）
- [ ] 废弃 `session-memory` hook 的旧机制
- [ ] 全系统测试新加载流程

---

## 六、技术依赖

### Soul Memory 系统
- 存储：`soulos/soul_memory_system_v3.py`
- 数据：`soul-memory-simple.json`
- 亮度算法：自然衰减 5%/晚 + 回响 ×1.30 + 使用 +5%
- 分层：Soul级23条 + Working级26条 = 49条固定

### Living Forest 系统
- 文档：`projects/*/_tree.md`, `_lineage.md`
- 索引：`projects/_forest.md`, `ACTIVE.md`
- 解析器：待实现 TreeParser（Python）

---

## 七、设计原则

1. **单一可信源**：同一信息只存一处，避免重复加载
2. **固定数量**：49签固定，不随总签库膨胀
3. **自然淘汰**：低亮签被排序挤出前49，无需主动删除
4. **分层压缩**：工作记忆（树形）+ 人格记忆（签）分离
5. **按需加载**：项目详情不预加载，提及才读取

---

## 八、后续优化方向

| 优化点 | 时机 | 方案 |
|--------|------|------|
| 向量检索加速 | 签库 >200支 | 为49签建立FAISS索引 |
| 自动更新ACTIVE.md | TreeParser完成后 | 从_tree.md自动提取 |
| 可视化界面 | 远期 | Obsidian Graph风格项目树 |
| 跨Agent记忆同步 | 远期 | 子Agent共享核心49签 |

---

*方案确立：2026-03-24*
*下次回顾：ACTIVE.md和49签预加载实现后*
