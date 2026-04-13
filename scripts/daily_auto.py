#!/usr/bin/env python3
"""
每日自动化任务 - A股智能选股
每天早上08:00自动运行，生成报告并推送到QQ

配置方式：
1. 使用 OpenClaw 定时任务系统
   openclaw cron create --schedule "0 8 * * 1-5" -- python scripts/daily_auto.py

2. 或直接 crontab -e
   0 8 * * 1-5 cd /path/to/stock-picker-plus && python scripts/daily_auto.py

Author: Simon (with AI Agent)
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine import StockPickerEngine
from output.qq_notifier import QQNotifier

def main():
    """每日自动化主函数"""
    print("=" * 60)
    print("📊 A股智能选股 - 每日自动化任务")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 初始化引擎
        engine = StockPickerEngine()

        # 运行全市场扫描（使用缓存加速）
        print("\n【Step 1】运行选股扫描...")
        result = engine.run(
            pool="all",
            strategy_name="multi_factor",
            use_cache=True,      # 使用缓存加速
            send_qq=False,       # 手动推送
            top_n=30
        )

        if "error" in result:
            print(f"❌ 扫描失败: {result['error']}")
            sys.exit(1)

        selected = result['selected']
        stats = result['stats']

        print(f"✅ 扫描完成: {stats['selected']} 只推荐股票")
        print(f"   耗时: {result['elapsed_seconds']:.1f} 秒")

        # 生成Markdown报告（用于QQ消息）
        report_md = result['report_md']
        excel_path = result['excel_path']

        # 推送到QQ
        print("\n【Step 2】推送到QQ...")
        notifier = QQNotifier()
        success = notifier.send(report_md, excel_path)

        if success:
            print("✅ QQ推送成功")
        else:
            print("⚠️ QQ推送失败，请检查配置")

        print("\n" + "=" * 60)
        print("✅ 每日自动化任务完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 任务失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
