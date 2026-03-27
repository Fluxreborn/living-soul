# 预加载配置草案 / Preload Configuration Draft

## 现状 vs 目标

### 现状（需要优化）
```
每次 Session 加载：
├── SOUL.md (~11K)
├── IDENTITY.md (~3K)
├── USER.md (~0.5K)
├── AGENTS.md (~10K)
├── MEMORY.md (~9K) — 仅 main session
├── memory/2026-03-23.md (~2K) — 昨天的记录
└── memory/2026-03-24.md (可能不存在)

总计：~28-38K tokens
问题：包含大量已完成/不相关的历史项目
```

### 目标（压缩后）
```
每次 Session 加载：
├── SOUL.md (~11K) — 人格，必须
├── IDENTITY.md (~3K) — 身份，必须
├── USER.md (~0.5K) — 用户，必须
├── AGENTS.md (~10K) — 行为指南，必须
├── ACTIVE.md (~1K) — 当前焦点 ✅ 新增，替代 daily memory
└── _forest.md (~1.5K) — 项目索引 ✅ 新增，压缩版

总计：~27K tokens（基础）+ 按需加载

节省：~10K tokens（去掉不相关的历史项目）
```

## 新的预加载体系

### 固定预加载（始终）

| 文件 | 大小 | 作用 | 更新频率 |
|------|------|------|---------|
| SOUL.md | ~11K | 人格定义 | 极少 |
| IDENTITY.md | ~3K | 身份认同 | 极少 |
| USER.md | ~0.5K | 用户画像 | 偶尔 |
| AGENTS.md | ~10K | 行为指南 | 偶尔 |

**小计：~25K tokens（固定开销，无法压缩）**

### 动态预加载（替代 memory/*.md）

| 文件 | 大小 | 作用 | 更新频率 |
|------|------|------|---------|
| ACTIVE.md | ~1K | 当前工作焦点 | 每日 |
| _forest.md | ~1.5K | 项目索引（压缩版） | 项目变更时 |

**小计：~2.5K tokens（动态维护，保持精简）**

### 按需加载（不预加载）

| 内容 | 触发条件 | 大小 |
|------|---------|------|
| `projects/<name>/_tree.md` | 提到具体项目 | ~1K/项目 |
| `projects/<name>/_lineage.md` | 跨项目查询 | ~0.5K |
| `memory/<date>.md` | 主动回忆某天 | ~2K/天 |

## ACTIVE.md 设计

**位置**：`workspace/ACTIVE.md`

**内容**：
```markdown
# ACTIVE — 当前工作焦点

## 进行中 🔄
- **Living Forest System**：方法论文档完成，待实现 TreeParser
- **Soul Memory**：睡眠周期积累签库（8/30）

## 阻塞 ⏸️
- 无

## 今日待办
- [ ] 审阅 Living Forest 方法论
- [ ] 确认技术选型

## 已完成（仅一句话）
- Token Saver — 已归档，分娩出 Soul Memory

---
*上次更新：2026-03-24 13:00*
*下次更新：任务状态变化时*
```

**生成方式**：
1. 从 `projects/*/_tree.md` 提取活跃项目
2. 自动汇总进行中/阻塞的任务
3. 归档项目自动压缩为一句话

**更新触发**：
- 项目状态变更时
- 每日首次 session 时检查
- 手动编辑

## _forest.md 压缩版

**位置**：`workspace/projects/_forest.md`

**内容**：
```markdown
# 项目森林总图（预加载版）

## 活跃项目（详细）
- [soul-memory/](soul-memory/) — 日常记忆系统
- [living-forest-system/](living-forest-system/) — 工作项目管理
- [openclaw-optimization/](openclaw-optimization/) — OpenClaw 优化

## 归档项目（仅一句话）
| 项目 | 一句话摘要 |
|------|-----------|
| token-saver | 已归档，分娩出 Soul Memory |
| trade-services | 已完成，山西贸易服务报告 2026-02 |

## 历史项目（仅计数）
- archive/ 下 5 个项目，详见文件夹

---
*完整版见：projects/living-forest-system/demo/_forest.md*
```

## 实施步骤

### Phase 1：创建新文件（今天）
- [ ] 创建 `workspace/ACTIVE.md`
- [ ] 创建压缩版 `workspace/projects/_forest.md`
- [ ] 测试新的加载流程

### Phase 2：修改 AGENTS.md（验证后）
```markdown
## Every Session（修订版）

Before doing anything else:

1. Read `SOUL.md` — 人格
2. Read `USER.md` — 用户
3. Read `ACTIVE.md` — 当前焦点 ✅ 新增
4. Read `projects/_forest.md` — 项目索引 ✅ 新增（替代两天的 memory）
5. **If in MAIN SESSION**: Read `MEMORY.md` — 长期精华
6. **If discussing specific project**: Read `projects/<name>/_tree.md`
```

### Phase 3：废弃旧机制（验证后）
- [ ] 停止使用 `memory/YYYY-MM-DD.md` 固定加载
- [ ] session-memory hook 改为更新 `ACTIVE.md`（而非保存全文）

## 预期收益

| 指标 | 当前 | 目标 | 节省 |
|------|------|------|------|
| 基础预加载 | ~28K | ~27.5K | -0.5K |
| 动态部分 | ~3K（两天 memory） | ~2.5K（ACTIVE + forest） | -0.5K |
| 信息噪音 | 高（无关历史） | 低（只保留活跃） | 显著 |
| 跨日一致性 | 差（每天加载不同文件） | 好（ACTIVE 统一维护） | 显著 |

## 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| ACTIVE.md 遗漏重要信息 | 每天首次 session 自动检查更新 |
| 归档项目信息丢失 | 完整保留在项目文件夹，只是不预加载 |
| 忘记历史项目 | _forest.md 保留索引，可手动查阅 |

---
*预加载配置草案：2026-03-24*
*待 Fable 审阅后实施*
