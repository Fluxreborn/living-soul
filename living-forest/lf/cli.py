"""
CLI 主入口
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .commands import init, branch, status, render, check, recent, active


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        prog="lf",
        description="Living Forest - 活树森林项目管理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  lf init my-project              # 初始化新项目
  lf branch 001 "子任务"          # 创建分支
  lf status                       # 查看统计
  lf render                       # 生成 Markdown
  lf check                        # 验证结构
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "-C", "--directory",
        default=".",
        help="指定工作目录 (默认: 当前目录)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init 命令
    init_parser = subparsers.add_parser(
        "init",
        help="初始化新的活树项目"
    )
    init_parser.add_argument(
        "name",
        help="项目名称"
    )
    init_parser.add_argument(
        "-d", "--description",
        default="",
        help="项目描述"
    )
    init_parser.set_defaults(func=init.run)
    
    # branch 命令
    branch_parser = subparsers.add_parser(
        "branch",
        help="创建新分支"
    )
    branch_parser.add_argument(
        "parent",
        help="父节点ID (如 001, 002.1)"
    )
    branch_parser.add_argument(
        "label",
        help="分支名称"
    )
    branch_parser.add_argument(
        "-t", "--type",
        choices=["trunk", "branch", "graveyard"],
        default="trunk",
        help="节点类型 (默认: trunk)"
    )
    branch_parser.set_defaults(func=branch.run)
    
    # status 命令
    status_parser = subparsers.add_parser(
        "status",
        help="查看项目统计"
    )
    status_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细信息"
    )
    status_parser.set_defaults(func=status.run)
    
    # render 命令
    render_parser = subparsers.add_parser(
        "render",
        help="生成 Markdown 文档"
    )
    render_parser.add_argument(
        "-o", "--output",
        help="输出文件路径 (默认: _tree.md)"
    )
    render_parser.add_argument(
        "-f", "--filter",
        choices=["active", "done", "archived", "draft"],
        help="只显示指定状态的节点"
    )
    render_parser.set_defaults(func=render.run)
    
    # check 命令
    check_parser = subparsers.add_parser(
        "check",
        help="验证树结构完整性"
    )
    check_parser.add_argument(
        "-f", "--fix",
        action="store_true",
        help="尝试自动修复问题"
    )
    check_parser.set_defaults(func=check.run)
    
    # active 命令
    active_parser = subparsers.add_parser(
        "active",
        help="生成 ACTIVE.md 上下文预加载文件"
    )
    active_parser.set_defaults(func=active.run)
    
    # recent 命令
    recent_parser = subparsers.add_parser(
        "recent",
        help="显示最近活跃的项目"
    )
    recent_parser.add_argument(
        "-d", "--days",
        type=int,
        default=3,
        help="时间范围（天数）(默认: 3)"
    )
    recent_parser.set_defaults(func=recent.run)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 切换工作目录
    work_dir = Path(args.directory).resolve()
    if not work_dir.exists():
        print(f"错误: 目录不存在: {work_dir}")
        sys.exit(1)
    
    # 执行命令
    try:
        args.func(args, work_dir)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
