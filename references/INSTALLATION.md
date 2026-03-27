# Living Soul 完整安装指南

## 系统要求

- Python 3.8+
- OpenClaw (任意版本)
- Cron (可选，用于自动睡眠周期)

## 安装步骤

### 步骤 1: 获取代码

```bash
# 方式 1: Git 克隆
git clone https://github.com/yourusername/living-soul.git ~/Projects/living-soul

# 方式 2: 直接下载解压
# 解压到 ~/Projects/living-soul
```

### 步骤 2: 验证 Python 版本

```bash
python3 --version  # 需要 3.8+
```

### 步骤 3: 创建符号链接

```bash
cd ~/.openclaw/workspace
ln -s ~/Projects/livingsoul living-soul
```

### 步骤 4: 修改 AGENTS.md

编辑 `~/.openclaw/workspace/AGENTS.md`，在 "Every Session" 章节添加：

```markdown
3. **Living Dream**: Read `living-soul/living-dream/living-dream-context.md`
   - Soul级23签（亮度最高的记忆）
   - 昨日梦境叙事
   - 主题分布和人物统计
4. **Living Forest**: Read `living-soul/living-forest/index/active-index.json`
   - 活跃项目索引
   - 按需加载项目详情（关键词匹配时）
```

### 步骤 5: 初始化签筒

```bash
cd ~/.openclaw/workspace/living-soul/living-dream
python3 night_routine.py --init
```

这会创建空的 `living-dream-memory.json` 文件。

### 步骤 6: 测试运行

```bash
# 手动运行睡眠周期
python3 night_routine.py

# 检查生成的上下文文件
ls -la living-dream-context.md
```

### 步骤 7: 配置自动运行（可选）

#### macOS/Linux Cron

```bash
crontab -e

# 添加以下行（每天凌晨 3:30 运行）
30 3 * * * cd ~/.openclaw/workspace/living-soul/living-dream && python3 night_routine.py
```

#### 使用 cron.yaml (如果 OpenClaw 支持)

在项目根目录创建 `cron.yaml`:

```yaml
- name: "living-dream-night-routine"
  schedule: "30 3 * * *"
  command: cd ~/.openclaw/workspace/living-soul/living-dream && python3 night_routine.py
  description: "Living Dream睡眠周期：衰减/抽签/融合/更新上下文"
```

## 升级

### 从旧版本升级

```bash
cd ~/Projects/livingsoul
git pull  # 或手动下载新版本

# 重新生成上下文
cd living-dream
python3 update_context.py
```

### 数据迁移

如果需要迁移数据到新的工作目录：

```bash
# 备份旧数据
cp -r ~/old-workspace/living-soul/living-dream/living-dream-memory.json \
      ~/backup/

# 复制到新位置
cp ~/backup/living-dream-memory.json \
   ~/.openclaw/workspace/living-soul/living-dream/
```

## 卸载

```bash
# 1. 删除符号链接
rm ~/.openclaw/workspace/living-soul

# 2. 恢复 AGENTS.md
# 手动删除 Living Dream 和 Living Forest 的读取指令

# 3. 删除 Cron 任务
crontab -e
# 删除相关行

# 4. 可选：删除项目文件
rm -rf ~/Projects/livingsoul
```

## 故障排除

### 问题 1: ModuleNotFoundError

**现象**: `ModuleNotFoundError: No module named 'sklearn'`

**解决**:
```bash
pip3 install scikit-learn numpy
```

### 问题 2: Permission Denied

**现象**: 无法创建符号链接

**解决**:
```bash
# 检查目录权限
ls -la ~/.openclaw/workspace/

# 使用绝对路径
ln -s /Users/YOURNAME/Projects/livingsoul /Users/YOURNAME/.openclaw/workspace/living-soul
```

### 问题 3: Agent 未加载上下文

**现象**: 启动后没有梦境记忆

**检查**:
1. `AGENTS.md` 是否正确修改
2. 符号链接是否指向正确位置
3. `living-dream-context.md` 是否存在且非空

### 问题 4: 签筒数据丢失

**恢复**:
```bash
# 从备份恢复
cp living-dream/backup/living-dream-memory-*.json \
   living-dream/living-dream-memory.json
```

## 自定义配置

### 修改衰减率

编辑 `living_dream_system_v31.py`:

```python
# 原代码
new_brightness = max(0.3, sign["brightness"] * 0.95)

# 改为每天 -3%
new_brightness = max(0.3, sign["brightness"] * 0.97)
```

### 修改抽签数量

```python
# 原代码
selected_count = min(7, max(3, len(eligible) // 5))

# 改为固定 5 签
selected_count = 5
```

### 添加新的维度

在 `references/MEMORY-MODEL.md` 中定义新维度，然后修改签的数据结构。

## 多 Agent 配置

如果多个 Agent 需要共享 Living Soul：

```bash
# 每个 Agent 的 workspace 创建符号链接
ln -s ~/Projects/livingsoul ~/.openclaw/agents/fino/workspace/living-soul
ln -s ~/Projects/livingsoul ~/.openclaw/agents/turing/workspace/living-soul
# ...
```

注意：多 Agent 同时写入可能导致数据冲突，建议：
- 指定一个 Agent 作为主写入者
- 或使用文件锁机制
