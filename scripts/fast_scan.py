#!/usr/bin/env python3
"""
快速扫描脚本 - A股智能选股
采样模式：随机抽取200只股票，约20-30秒完成
用途：快速预览、测试策略、验证数据
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine import run_quick_scan

def main():
    """主函数"""
    print("=" * 60)
    print("📊 A股智能选股 - 快速扫描（采样200只）")
    print("=" * 60)

    # 默认参数
    pool = "all"
    strategy = "multi_factor"

    # 从命令行读取参数
    if len(sys.argv) > 1:
        pool = sys.argv[1]
    if len(sys.argv) > 2:
        strategy = sys.argv[2]

    print(f"\n启动扫描...")
    print(f"  股票池: {pool}")
    print(f"  策略: {strategy}")
    print(f"  采样: 200只")
    print("")

    try:
        # 运行快速扫描
        result = run_quick_scan(pool=pool, sample_size=200, strategy=strategy)

        if "error" in result:
            print(f"\n❌ 扫描失败: {result['error']}")
            sys.exit(1)

        # 显示结果
        selected = result['selected']
        stats = result['stats']

        print("\n" + "=" * 60)
        print("✅ 扫描完成！")
        print("=" * 60)
        print(f"总耗时: {result['elapsed_seconds']:.1f} 秒")
        print(f"推荐股票: {stats['selected']} 只")
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
