# Living Soul 发布清单

## GitHub 发布步骤

### 1. 准备仓库

```bash
# 初始化 Git 仓库（如果还没做）
cd ~/Projects/livingsoul
git init
git add .
git commit -m "Initial commit: Living Soul v1.0"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/living-soul.git
git branch -M main
git push -u origin main
```

### 2. 创建 GitHub Release

1. 访问 GitHub 仓库页面
2. 点击 "Releases" → "Create a new release"
3. 设置版本号：`v1.0.0`
4. 填写发布说明（见下文模板）
5. 发布

### 3. 发布说明模板

```markdown
## Living Soul v1.0.0

AI 梦境与记忆系统 —— 为 OpenClaw Agent 提供双重记忆机制。

### 功能
- 🌙 Living Dream: 六维闪回结构 + 签筒抽签 + 睡眠周期
- 🌲 Living Forest: 分层项目索引 + 按需加载
- 🤝 Living Companion: 认知合伙人 + 双向关系深化

### 安装
```bash
git clone https://github.com/YOUR_USERNAME/living-soul.git ~/Projects/living-soul
cd ~/Projects/livingsoul
python3 scripts/install.py --workspace ~/.openclaw/workspace
```

### 文档
- [README.md](README.md)
- [安装指南](references/INSTALLATION.md)
- [架构设计](references/ARCHITECTURE.md)

### 系统要求
- Python 3.8+
- OpenClaw

### 首次运行
```bash
cd living-dream
python3 night_routine.py
```
```

### 4. 打包 Skill 文件（可选）

如果使用 OpenClaw Skill 系统：

```bash
# 使用 OpenClaw 的 package_skill.py 打包
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
    ~/Projects/livingsoul \
    ./dist

# 上传 dist/living-soul.skill 到 Release 附件
```

**注意**: 确保没有符号链接，否则打包会失败。

### 5. 提交到 ClawHub（可选）

如果使用 [ClawHub](https://clawhub.com)：

```bash
# 安装 clawhub CLI
npm install -g clawhub

# 登录
clawhub login

# 发布 Skill
clawhub publish living-soul
```

## 预发布检查清单

### 代码检查
- [ ] `SKILL.md` 完整且格式正确
- [ ] `scripts/install.py` 可正常运行
- [ ] `living-dream/update_context.py` 可正常运行
- [ ] 没有敏感信息（API Key、密码等）
- [ ] 没有大文件（>10MB）

### 文档检查
- [ ] `README.md` 包含安装说明
- [ ] `references/INSTALLATION.md` 完整
- [ ] 所有链接可点击
- [ ] 版本号一致

### 测试检查
- [ ] 在新环境测试安装流程
- [ ] 验证符号链接创建成功
- [ ] 验证 AGENTS.md 更新正确
- [ ] 验证上下文生成正常

## 安装测试

在新机器上测试：

```bash
# 1. 克隆
git clone https://github.com/YOUR_USERNAME/living-soul.git ~/Projects/living-soul

# 2. 安装
cd ~/Projects/livingsoul
python3 scripts/install.py --workspace ~/.openclaw/workspace --no-cron

# 3. 测试生成上下文
cd living-dream
python3 update_context.py

# 4. 检查输出
cat living-dream-context.md
```

## 发布后维护

### 版本号规范

使用 [SemVer](https://semver.org/)：
- `MAJOR.MINOR.PATCH`
- 例如: `v1.2.3`

### 更新流程

```bash
# 1. 修改代码
# ...

# 2. 更新版本号（在相关文件中）

# 3. 提交
git add .
git commit -m "feat: xxx"
git push

# 4. 打标签
git tag v1.1.0
git push origin v1.1.0

# 5. 创建 Release
```

## 推广

发布后可以在以下渠道分享：

1. **OpenClaw Discord** - #showcase 频道
2. **ClawHub** - 提交到 Skill 市场
3. **Twitter/X** - @OpenClaw 相关账号
4. **个人博客** - 写使用心得

## 常见问题

### Q: 用户报告安装失败？

检查：
1. Python 版本 >= 3.8
2. 是否有写权限到 workspace
3. AGENTS.md 是否存在

### Q: 上下文未生成？

检查：
1. `living-dream-memory.json` 是否存在
2. JSON 格式是否有效
3. 是否有读权限

### Q: 如何更新到新版本？

```bash
cd ~/Projects/livingsoul
git pull
python3 scripts/install.py --workspace ~/.openclaw/workspace --no-cron
```
