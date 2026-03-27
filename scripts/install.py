#!/usr/bin/env python3
"""
Living Soul 自动安装脚本

用法:
    python3 install.py --workspace ~/.openclaw/workspace
    python3 install.py --workspace ~/.openclaw/workspace --no-cron
    python3 install.py --workspace ~/.openclaw/workspace --uninstall
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path


def log(msg):
    print(f"[Living Soul] {msg}")


def create_symlink(workspace_path, project_path):
    """创建符号链接"""
    symlink_path = Path(workspace_path) / "living-soul"
    
    if symlink_path.exists():
        if symlink_path.is_symlink():
            log(f"符号链接已存在: {symlink_path}")
            return True
        else:
            log(f"错误: {symlink_path} 已存在但不是符号链接")
            return False
    
    try:
        symlink_path.symlink_to(project_path)
        log(f"✅ 创建符号链接: {symlink_path} -> {project_path}")
        return True
    except Exception as e:
        log(f"❌ 创建符号链接失败: {e}")
        return False


def remove_symlink(workspace_path):
    """移除符号链接"""
    symlink_path = Path(workspace_path) / "living-soul"
    
    if not symlink_path.exists():
        log(f"符号链接不存在: {symlink_path}")
        return True
    
    try:
        symlink_path.unlink()
        log(f"✅ 移除符号链接: {symlink_path}")
        return True
    except Exception as e:
        log(f"❌ 移除符号链接失败: {e}")
        return False


def update_agents_md(workspace_path, force=False):
    """更新 AGENTS.md，使用标记注释包裹配置"""
    agents_md_path = Path(workspace_path) / "AGENTS.md"
    
    if not agents_md_path.exists():
        log(f"❌ 未找到 AGENTS.md: {agents_md_path}")
        return False
    
    content = agents_md_path.read_text(encoding='utf-8')
    
    # 定义标记
    START_MARKER = "<!-- LIVING_SOUL_START -->"
    END_MARKER = "<!-- LIVING_SOUL_END -->"
    
    # Living Soul 配置内容
    living_soul_config = """3. **Living Dream**: Read `living-soul/living-dream/living-dream-context.md`
   - Soul级23签（亮度最高的记忆）
   - 昨日梦境叙事
   - 主题分布和人物统计
4. **Living Forest**: Read `living-soul/living-forest/index/active-index.json`
   - 活跃项目索引
   - 按需加载项目详情（关键词匹配时）
"""
    
    # 检查是否已有 Living Soul 配置（通过标记）
    if START_MARKER in content and END_MARKER in content:
        if not force:
            log("AGENTS.md 已包含 Living Soul 配置（使用标记注释）")
            log("如需强制更新，请使用 --force 参数")
            return True
        
        # 强制更新：替换标记之间的内容
        log("📝 强制更新 Living Soul 配置...")
        new_content = []
        in_living_soul = False
        
        for line in content.split('\n'):
            if START_MARKER in line:
                new_content.append(line)
                new_content.append(living_soul_config.rstrip())
                in_living_soul = True
                continue
            if END_MARKER in line:
                new_content.append(line)
                in_living_soul = False
                continue
            if not in_living_soul:
                new_content.append(line)
        
        content = '\n'.join(new_content)
    else:
        # 新安装：在 "Every Session" 章节后插入
        log("📝 首次安装 Living Soul...")
        
        insert_content = f"""
{START_MARKER}
{living_soul_config}{END_MARKER}

"""
        
        # 查找最佳插入位置
        if "## Every Session" in content:
            # 在 "Every Session" 后的第一个列表项后插入
            lines = content.split('\n')
            insert_idx = None
            in_every_session = False
            
            for i, line in enumerate(lines):
                if "## Every Session" in line:
                    in_every_session = True
                    continue
                if in_every_session and line.strip().startswith('2.'):
                    # 在第二个列表项后插入
                    insert_idx = i + 1
                    break
            
            if insert_idx:
                lines.insert(insert_idx, insert_content)
                content = '\n'.join(lines)
            else:
                # 备选：直接在 "## Every Session" 后插入
                content = content.replace(
                    "## Every Session",
                    f"## Every Session\n{insert_content}"
                )
        else:
            log("❌ AGENTS.md 中未找到 '## Every Session' 章节")
            return False
    
    # 备份原文件（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = Path(workspace_path) / f"AGENTS.md.backup.{timestamp}"
    shutil.copy2(agents_md_path, backup_path)
    log(f"✅ 备份 AGENTS.md: {backup_path.name}")
    
    # 写入新内容
    agents_md_path.write_text(content, encoding='utf-8')
    log("✅ 更新 AGENTS.md 完成")
    
    return True


def uninstall_agents_md(workspace_path):
    """从 AGENTS.md 移除 Living Soul 配置"""
    agents_md_path = Path(workspace_path) / "AGENTS.md"
    
    if not agents_md_path.exists():
        log(f"AGENTS.md 不存在: {agents_md_path}")
        return True
    
    content = agents_md_path.read_text(encoding='utf-8')
    
    # 定义标记
    START_MARKER = "<!-- LIVING_SOUL_START -->"
    END_MARKER = "<!-- LIVING_SOUL_END -->"
    
    if START_MARKER not in content or END_MARKER not in content:
        log("AGENTS.md 中没有找到 Living Soul 配置")
        return True
    
    # 移除标记之间的内容（包括标记）
    lines = content.split('\n')
    new_lines = []
    in_living_soul = False
    
    for line in lines:
        if START_MARKER in line:
            in_living_soul = True
            continue
        if END_MARKER in line:
            in_living_soul = False
            continue
        if not in_living_soul:
            new_lines.append(line)
    
    # 备份原文件（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = Path(workspace_path) / f"AGENTS.md.backup.{timestamp}"
    shutil.copy2(agents_md_path, backup_path)
    log(f"✅ 备份 AGENTS.md: {backup_path.name}")
    
    # 写入新内容
    new_content = '\n'.join(new_lines)
    # 清理多余空行
    new_content = '\n'.join(line for i, line in enumerate(new_lines) if line.strip() or (i > 0 and new_lines[i-1].strip()))
    
    agents_md_path.write_text(new_content, encoding='utf-8')
    log("✅ 已从 AGENTS.md 移除 Living Soul 配置")
    
    return True


def setup_cron(project_path):
    """配置 Cron 任务"""
    cron_line = f"30 3 * * * cd {project_path}/living-dream && python3 night_routine.py\n"
    
    log("📋 请手动添加以下 Cron 任务（运行 `crontab -e`）:")
    log(f"   {cron_line.strip()}")
    
    # 创建 cron.yaml 示例
    cron_yaml_path = Path(project_path).parent / "cron.yaml"
    cron_yaml_content = f"""- name: "living-dream-night-routine"
  schedule: "30 3 * * *"
  command: cd {project_path}/living-dream && python3 night_routine.py
  description: "Living Dream睡眠周期：衰减/抽签/融合/更新上下文"
"""
    cron_yaml_path.write_text(cron_yaml_content, encoding='utf-8')
    log(f"✅ 创建 Cron 配置示例: {cron_yaml_path}")


def init_memory(project_path):
    """初始化记忆文件"""
    memory_path = Path(project_path) / "living-dream" / "living-dream-memory.json"
    
    if memory_path.exists():
        log(f"记忆文件已存在: {memory_path}")
        return True
    
    # 创建空的记忆文件结构
    import json
    initial_memory = {
        "meta": {
            "version": "v3.1",
            "created_at": datetime.now().isoformat(),
            "sign_count": 0
        },
        "signs": [],
        "dreams": []
    }
    
    memory_path.write_text(
        json.dumps(initial_memory, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    log(f"✅ 初始化记忆文件: {memory_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Living Soul 安装脚本")
    parser.add_argument(
        "--workspace",
        default="~/.openclaw/workspace",
        help="OpenClaw workspace 路径"
    )
    parser.add_argument(
        "--no-cron",
        action="store_true",
        help="跳过 Cron 配置"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="卸载 Living Soul（从 AGENTS.md 移除配置）"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制更新（即使已有配置）"
    )
    
    args = parser.parse_args()
    
    # 解析路径
    workspace_path = Path(args.workspace).expanduser().resolve()
    project_path = Path(__file__).parent.parent.resolve()
    
    log(f"Workspace: {workspace_path}")
    log(f"Project: {project_path}")
    
    # 检查 workspace 是否存在
    if not workspace_path.exists():
        log(f"❌ Workspace 不存在: {workspace_path}")
        sys.exit(1)
    
    # 卸载模式
    if args.uninstall:
        log("\n" + "="*50)
        log("开始卸载 Living Soul")
        log("="*50 + "\n")
        
        # 移除 AGENTS.md 配置
        if not uninstall_agents_md(workspace_path):
            log("⚠️ AGENTS.md 配置移除失败")
        
        # 移除符号链接
        if not remove_symlink(workspace_path):
            log("⚠️ 符号链接移除失败")
        
        log("\n" + "="*50)
        log("卸载完成!")
        log("="*50 + "\n")
        log("注意：记忆文件和项目数据未被删除")
        log("如需完全删除，请手动移除:")
        log(f"  - {project_path}")
        log(f"  - {workspace_path / 'living-soul'}")
        return
    
    # 检查 AGENTS.md 是否存在
    if not (workspace_path / "AGENTS.md").exists():
        log(f"❌ AGENTS.md 不存在于 workspace，请确认路径正确")
        sys.exit(1)
    
    log("\n" + "="*50)
    log("开始安装 Living Soul")
    log("="*50 + "\n")
    
    # 步骤 1: 创建符号链接
    if not create_symlink(workspace_path, project_path):
        sys.exit(1)
    
    # 步骤 2: 更新 AGENTS.md
    if not update_agents_md(workspace_path, force=args.force):
        log("⚠️ AGENTS.md 更新失败，请手动配置")
    
    # 步骤 3: 初始化记忆文件
    if not init_memory(project_path):
        log("⚠️ 记忆文件初始化失败")
    
    # 步骤 4: Cron 配置
    if not args.no_cron:
        setup_cron(project_path)
    
    log("\n" + "="*50)
    log("安装完成!")
    log("="*50 + "\n")
    
    log("下一步:")
    log("1. 重启 OpenClaw Agent 测试加载")
    log("2. 运行 `python3 night_routine.py` 生成首个梦境")
    log("3. 查看 references/INSTALLATION.md 了解更多配置")
    log("")
    log("其他命令:")
    log("  --force       强制更新配置")
    log("  --uninstall   卸载 Living Soul")


if __name__ == "__main__":
    main()
