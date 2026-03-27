# Living Soul

**解决 AI 失忆症的终极方案** —— 让你的 OpenClaw Agent 拥有长期记忆、智能项目管理和深度对话能力。

> 不再每次重启都从零开始。不再在几十个项目中迷失。不再让 AI 变成"问了才答"的工具。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 💡 它能为你解决什么问题？

| 你的痛点 | Living Soul 的解决方案 |
|:---|:---|
| **AI 失忆** — 每次对话重新开始，之前的讨论都忘了 | 🌙 **Living Dream**：自动整理记忆，记住你们的共同历史 |
| **项目混乱** — 几十个文件夹找不到当前在做什么 | 🌲 **Living Forest**：智能项目索引，一句话就能定位 |
| **AI 被动** — 永远是"你问我答"，不会主动思考 | 🤝 **Living Companion**：主动贡献观点，像真正的思考伙伴 |

---

## 🌙 Living Dream：AI 终于能记住你了

### 问题

传统 AI 是"金鱼记忆"——对话结束就忘。下次打开，一切从头来过。

### 解决方案

Living Dream 让 AI 拥有**睡眠周期**，每天自动整理记忆：

- ✅ 记住你们讨论过的重要决策
- ✅ 自然遗忘不重要的闲聊
- ✅ 在对话中引用之前的讨论（"我记得你上周说过..."）

### 核心特性

| 特性 | 效果 |
|------|------|
**六维记忆标签** | 每段记忆记录时间、画面、人物、事件、情绪、身体感知 |
**智能分级** | 重要记忆长期保留，普通记忆自然衰减 |
**夜间整理** | 每天凌晨自动运行，无需人工干预 |
**梦境生成** | 将记忆整合成连贯的"昨日回顾" |

### 使用示例

```
用户：我们继续昨天那个项目...

Agent：我记得昨晚我们讨论到 API 设计部分，
       你当时倾向于用 REST 而不是 GraphQL。
       要我调出那个项目的完整上下文吗？
```

---

## 🌲 Living Forest：告别项目迷宫

### 问题

当你的 Workspace 里有 20+ 个项目时，AI 只能笨拙地遍历文件夹，效率极低。

### 解决方案

Living Forest 建立**智能项目索引**，让 AI 秒速定位：

```
用户：帮我看看那个"梦境"项目的进度

Agent：（直接加载 Living Soul 项目，而非遍历所有文件夹）
```

### 核心特性

| 状态 | 含义 | 加载策略 |
|------|------|----------|
| **active** | 正在做的 | 启动时预加载 |
| **research** | 调研中的 | 关键词匹配时加载 |
| **archived** | 已完成的 | 显式查询时加载 |
| **graveyard** | 废弃的 | 不加载，仅存档 |

### 效果

- ✅ 秒速定位当前项目
- ✅ 按需加载历史上下文
- ✅ 再也不用在文件夹迷宫里迷路

---

## 🤝 Living Companion：从工具到伙伴

### 问题

普通 AI 永远是被动的——你问它答，从不主动贡献。

### 解决方案

Living Companion 让 AI 成为**主动的思考伙伴**：

| 场景 | 传统 AI | Living Companion |
|------|---------|------------------|
| 技术选型 | "你可以选 A 或 B" | "我记得三周前你也遇到过类似选择，当时你选了渐进式迁移..." |
| 代码 review | "这行可以优化" | "我注意到你最近三次都在处理同类 bug，这可能是系统性问题" |
| 头脑风暴 | 等待你的提问 | 主动说："基于我们的讨论历史，我想补充一个角度..." |

### 智能质量评估

AI 会评估自己的发言是否有价值，只在真正有用时主动开口：

```
质量分数 = 相关性 × 0.4 + 新颖性 × 0.3 + 可行动性 × 0.3
```

---

## 🚀 5 分钟快速开始

### 第一步：安装

```bash
# 克隆项目
git clone https://github.com/fluxreborn/living-soul.git ~/Projects/living-soul

# 一键安装
cd ~/Projects/livingsoul
python3 scripts/install.py --workspace ~/.openclaw/workspace
```

### 第二步：配置自动记忆（可选但推荐）

```bash
# 添加定时任务，让 AI 每天自动整理记忆
crontab -e

# 粘贴这行：
30 3 * * * cd ~/.openclaw/workspace/living-soul/living-dream && python3 night_routine.py
```

### 第三步：重启 Agent，开始使用

完成！现在你的 Agent 会：
- ✅ 记住你们的对话历史
- ✅ 智能管理你的项目
- ✅ 在合适的时候主动发言

---

## 📁 项目结构

```
living-soul/
├── SKILL.md                    # OpenClaw Skill 定义
├── README.md                   # 本文件
│
├── living-dream/               # 🌙 记忆系统
│   ├── living_dream_system_v31.py
│   ├── night_routine.py        # 夜间记忆整理
│   └── living-dream-memory.json
│
├── living-forest/              # 🌲 项目索引
│   └── index/
│       ├── active-index.json
│       └── INDEX-SPEC.md
│
├── living-companion/           # 🤝 认知合伙人
│   ├── companion.py
│   └── companion-state.json
│
├── scripts/
│   └── install.py              # 一键安装
│
└── references/                 # 详细文档
    ├── ARCHITECTURE.md         # 系统架构
    ├── MEMORY-MODEL.md         # 记忆模型详解
    └── INSTALLATION.md         # 完整安装指南
```

---

## 🎯 适合谁用？

| 用户类型 | 使用场景 |
|----------|----------|
| **重度 AI 用户** | 每天和 Agent 对话数小时，需要保持上下文连续性 |
| **多项目管理者** | 同时推进 5+ 个项目，需要快速切换上下文 |
| **深度思考者** | 希望 AI 不只是回答，而是能参与思考和讨论 |
| **长期陪伴需求** | 希望 AI 记得你们的共同历史和偏好 |

---

## 📊 与传统方案对比

| 特性 | 传统 Agent | Living Soul |
|------|-----------|-------------|
| 记忆 | 单次对话，重启即失 | 永久记忆，自然遗忘 |
| 项目管理 | 遍历文件夹 | 智能索引，秒速定位 |
| 对话模式 | 被动应答 | 主动参与，像合伙人 |
| 夜间活动 | 无 | 自动整理记忆 |
| 学习曲线 | 低 | 低（一键安装） |

---

## 📚 详细文档

- **[INSTALLATION.md](references/INSTALLATION.md)** — 完整安装指南、故障排除
- **[ARCHITECTURE.md](references/ARCHITECTURE.md)** — 系统架构与数据流
- **[MEMORY-MODEL.md](references/MEMORY-MODEL.md)** — 记忆模型技术细节
- **[INDEX-SPEC.md](living-forest/index/INDEX-SPEC.md)** — Living Forest 索引规范

---

## 🛠️ 技术栈

- **Python 3.8+** — 纯标准库，零依赖
- **JSON** — 数据存储
- **Cron** — 定时任务

---

## 📜 许可证

MIT License —— 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) — AI 运行时系统
- [SoulmeAI](https://github.com/fable-kss/soulmeai) — 灵魂力量唤醒框架

---

**准备好让你的 Agent 拥有记忆了吗？** → [5 分钟快速开始](#5-分钟快速开始)
