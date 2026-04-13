#!/usr/bin/env python3
"""
A股智能选股系统 - 主入口

使用方法：
    python main.py [options]

或使用子命令：
    python main.py quick       # 快速采样
    python main.py full        # 全市场扫描
    python main.py cli         # 交互式界面
    python main.py daily       # 每日自动化

Author: Simon (with AI Agent)
Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(
        description="A股智能选股系统 - Stock Picker Plus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python main.py quick                    # 快速采样（200只）
  python main.py full --pool hs300        # 全市场沪深300
  python main.py cli                      # 交互式
  python main.py daily                    # 每日自动化（带QQ推送）
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # quick 命令
    subparsers.add_parser('quick', help='快速采样（默认200只）')

    # full 命令
    full_parser = subparsers.add_parser('full', help='全市场扫描')
    full_parser.add_argument('--pool', default='all', help='股票池')
    full_parser.add_argument('--strategy', default='multi_factor', help='策略')

    # cli 命令
    subparsers.add_parser('cli', help='交互式界面')

    # daily 命令
    subparsers.add_parser('daily', help='每日自动化（含QQ推送）')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 路由到对应模块
    if args.command == 'quick':
        from scripts.fast_scan import main as quick_main
        quick_main()

    elif args.command == 'full':
        from scripts.full_scan import main as full_main
        # 传递参数
        sys.argv = ['full_scan.py', '--pool', args.pool, '--strategy', args.strategy]
        full_main()

    elif args.command == 'cli':
        from cli.picker_cli import main as cli_main
        cli_main()

    elif args.command == 'daily':
        from scripts.daily_auto import main as daily_main
        daily_main()


if __name__ == "__main__":
    main()
