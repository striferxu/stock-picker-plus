#!/usr/bin/env python3
"""
全市场扫描脚本 - A股智能选股
全量模式：扫描全部8687只A股，约15-20分钟
用途：生成正式报告、每日收盘简报
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine import run_full_scan

def main():
    """主函数"""
    print("=" * 60)
    print("📊 A股智能选股 - 全市场扫描")
    print("=" * 60)

    pool = "all"
    strategy = "multi_factor"

    if len(sys.argv) > 1:
        pool = sys.argv[1]
    if len(sys.argv) > 2:
        strategy = sys.argv[2]

    print(f"\n启动全市场扫描...")
    print(f"  股票池: {pool}（约8687只）")
    print(f"  策略: {strategy}")
    print(f"  预计耗时: 15-20分钟")
    print("")

    try:
        result = run_full_scan(pool=pool, strategy=strategy)

        if "error" in result:
            print(f"\n❌ 扫描失败: {result['error']}")
            sys.exit(1)

        selected = result['selected']
        stats = result['stats']

        print("\n" + "=" * 60)
        print("✅ 全市场扫描完成！")
        print("=" * 60)
        print(f"总耗时: {result['elapsed_seconds']:.1f} 秒 ({result['elapsed_seconds']/60:.1f} 分钟)")
        print(f"扫描股票: {stats['total_stocks']} 只")
        print(f"有效数据: {stats['data_fetched']} 只")
        print(f"推荐数量: {stats['selected']} 只")
        print(f"筛选比例: {stats['selection_ratio']:.1f}%")
        print(f"Excel报告: {result['excel_path']}")

        if not selected.empty:
            print("\n🏆 Top 10 推荐:")
            for idx, row in selected.head(10).iterrows():
                code = row.get('代码', '-')
                name = row.get('名称', '-')
                score = row.get('总分', 0)
                pe = row.get('PE', '-')
                print(f"  {code} {name} | 综合分:{score:.1f} | PE:{pe}")

        print("\n" + "=" * 60)

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
