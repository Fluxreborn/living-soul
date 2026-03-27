---
name: living-soul
description: AI 灵魂生态系统 —— 为 OpenClaw Agent 提供 Living Dream（梦境记忆）、Living Forest（项目索引）、Living Companion（认知合伙人）三重机制。当用户需要为 Agent 构建长期记忆、梦境叙事、项目索引、双向关系深化时启用。支持六维闪回记忆模型（时间、画面、人物、事件、情绪、身体）、签筒抽签、睡眠周期、自动衰减与回响加成。
metadata:
  openclaw:
    requires:
      bins: [python3]
    emoji: "🌙"
    homepage: https://github.com/fluxreborn/living-soul
---

# Living Soul

AI 灵魂生态系统，为 OpenClaw Agent 提供三重记忆与关系机制。

> *"木头会呼吸，塑料不会。夜里生长。"*

## 功能组成

### 🌙 Living Dream - 梦境记忆
通过**六维闪回结构**构建 AI 的"梦境"体验：
- **六维输入**: 时间、画面、人物、事件、情绪、身体
- **双轨制记忆**: Soul级(>0.85) + Working级(7天窗口)
- **自然衰减**: 每晚 -5%
- **回响加成**: 相似度>0.3 触发 +30%
- **抽签梦境**: 1-49签，反向概率，无标点

### 🌲 Living Forest - 项目索引
活性森林项目索引系统：
- **分层索引**: active-index.json + archived-index.json
- **按需加载**: 关键词匹配时加载详情
- **状态追踪**: active/research/archived/graveyard
- **CLI工具**: 零依赖的 Python CLI 管理

### 🤝 Living Companion - 认知合伙人
双向关系深化系统：
- **双模式运行**: 常规模式(质量≥0.6) + 紧急模式(情绪≥0.5)
- **质量评估**: 相关性×0.4 + 新颖性×0.3 + 可行动性×0.3
- **主动贡献**: 基于共同历史生成合伙人级视角
- **社交情境层**: 可选的社交数据导入

## 安装

### 1. 自动安装（推荐）

```bash
python3 scripts/install.py --workspace ~/.openclaw/workspace
```

此命令会：
- 创建符号链接 `~/.openclaw/workspace/living-soul`
- 修改 `AGENTS.md` 添加启动加载指令
- 可选：配置 Cron 定时任务

### 2. 手动安装

```bash
# 1. 克隆或复制项目到任意位置
# 例如: ~/Projects/living-soul

# 2. 创建符号链接
cd ~/.openclaw/workspace
ln -s ~/Projects/living-soul living-soul

# 3. 修改 AGENTS.md
# 在 "Every Session" 章节添加:
# - **Living Dream**: Read `living-soul/living-dream/living-dream-context.md`
# - **Living Forest**: Read `living-soul/living-forest/index/active-index.json`
```

## 首次配置

### 1. 初始化签筒

```bash
cd living-dream
python3 night_routine.py --init
```

这会创建 `living-dream-memory.json` 存储核心记忆签。

### 2. 配置 Cron（可选）

添加每日睡眠周期：

```yaml
# cron.yaml
- name: "living-dream-night-routine"
  schedule: "30 3 * * *"
  command: cd ~/.openclaw/workspace/living-soul/living-dream && python3 night_routine.py
```

## 日常使用

### 添加新记忆签

```python
# 六维结构
sign = {
    "id": "YYYYMMDD-XXX",
    "time": "那天下午",
    "scene": "灯变暗时",
    "characters": ["我", "你"],
    "event": "你问我关于灵魂的问题",
    "emotion": "焦虑",
    "emotion_intensity": 0.8,
    "body": True,
    "brightness": 0.70
}
```

### 更新 OpenClaw 上下文

```bash
cd living-dream
python3 update_context.py
```

这会生成 `living-dream-context.md` 供 Agent 冷启动加载。

### 添加项目到索引

编辑 `living-forest/index/active-index.json`，添加项目对象：

```json
{
  "name": "项目名",
  "path": "~/Projects/xxx",
  "keywords": ["关键词1", "关键词2"],
  "status": "active",
  "priority": "high"
}
```

## 文件结构

```
living-soul/
├── living-dream/
│   ├── living-dream-context.md    # OpenClaw 预加载文件
│   ├── living-dream-memory.json   # 签筒数据
│   ├── living_dream_system_v31.py # 核心系统
│   ├── night_routine.py           # 睡眠周期
│   └── update_context.py          # 上下文生成
│
├── living-forest/
│   ├── lf.py                      # CLI入口
│   ├── lf/                        # CLI模块
│   └── index/
│       ├── active-index.json      # 活跃项目索引
│       └── INDEX-SPEC.md          # 索引规范
│
├── living-companion/
│   ├── companion.py               # 合伙人核心逻辑
│   └── companion-state.json       # 关系状态存储
│
└── references/                    # 详细文档
    ├── ARCHITECTURE.md            # 架构设计
    ├── MEMORY-MODEL.md            # 六维记忆模型
    └── INSTALLATION.md            # 完整安装指南
```

## 数据备份

定期备份以下文件：
- `living-dream/living-dream-memory.json`
- `living-forest/index/active-index.json`
- `living-companion/companion-state.json`

```bash
# 自动备份
cd living-dream && python3 backup.sh
```

## 故障排除

**问题**: Agent 启动未加载梦境上下文  
**解决**: 检查 `AGENTS.md` 是否包含 Living Dream 读取指令

**问题**: 签筒数据丢失  
**解决**: 从 backup/ 目录恢复最近的备份

**问题**: 索引文件损坏  
**解决**: 运行 `living-forest/migrate_md_to_json.py` 重新生成

## 参考文档

- **架构设计**: [references/ARCHITECTURE.md](references/ARCHITECTURE.md)
- **六维记忆模型**: [references/MEMORY-MODEL.md](references/MEMORY-MODEL.md)
- **完整安装指南**: [references/INSTALLATION.md](references/INSTALLATION.md)
- **认知合伙人**: [living-companion/README.md](living-companion/README.md)
