#!/usr/bin/env python3
"""
交互式命令行界面 - 完整版
整合自 ai-stock-picker/stock_picker/picker.py

功能：
- 交互式问答选择股票池和策略
- 支持命令行参数模式
- 友好的进度显示

Author: Simon (with AI Agent)
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine import StockPickerEngine
from core.strategies import list_strategies

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============== 配置常量 ==============

POOL_OPTIONS = {
    "1": ("沪深300", "hs300", "大盘蓝筹，300只"),
    "2": ("中证500", "zz500", "中盘成长，500只"),
    "3": ("中证1000", "zz1000", "小盘潜力，1000只"),
    "4": ("全部A股", "all", "全市场扫描，约8687只"),
}

STRATEGY_OPTIONS = {
    "1": ("pe_value", "低PE价值策略", "要求低估值高盈利"),
    "2": ("multi_factor", "多因子策略", "综合估值+盈利+规模"),
    "3": ("three_dimensional", "三维评分策略", "基本面+技术面+情绪面"),
}


# ============== 交互式收集用户偏好 ==============

def collect_user_preferences() -> Dict[str, Any]:
    """
    交互式收集用户选择

    Returns:
        {'pool': 'all', 'strategy': 'multi_factor', 'sample': True, ...}
    """
    print("\n" + "=" * 60)
    print("📊 AI 智能选股助手（完整版）")
    print("=" * 60)

    # --- 股票池选择 ---
    print("\n请选择股票池：")
    for key, (name, code, desc) in POOL_OPTIONS.items():
        print(f"  {key}. {name} — {desc}")
    choice = input("\n请输入编号 [默认: 4]: ").strip() or "4"

    pool_info = POOL_OPTIONS.get(choice, POOL_OPTIONS["4"])
    pool_name, pool_code, pool_desc = pool_info

    print(f"✅ 已选择: {pool_name}")

    # --- 策略选择 ---
    print("\n请选择投资策略：")
    for key, (code, name, desc) in STRATEGY_OPTIONS.items():
        print(f"  {key}. {name} — {desc}")
    choice = input("\n请输入编号 [默认: 2]: ").strip() or "2"

    strategy_info = STRATEGY_OPTIONS.get(choice, STRATEGY_OPTIONS["2"])
    strategy_code, strategy_name, strategy_desc = strategy_info

    print(f"✅ 已选择: {strategy_name}")

    # --- 采样模式选择 ---
    print("\n请选择运行模式：")
    print("  1. 快速采样（约30秒，采样200只）— 适合快速预览")
    print("  2. 全市场扫描（约15-20分钟，全部A股）— 正式报告")
    mode = input("\n请输入编号 [默认: 1]: ").strip() or "1"
    sample_mode = (mode == "1")

    if sample_mode:
        print("✅ 模式: 快速采样（200只）")
    else:
        print("✅ 模式: 全市场扫描（8687只）")

    # --- 其他选项 ---
    print("\n其他选项：")
    use_cache = input("  是否使用缓存加速？(Y/n) ").strip().lower() != 'n'
    print(f"✅ 缓存: {'开启' if use_cache else '关闭'}")

    run_backtest = input("  是否运行回测验证？(y/N) ").strip().lower() == 'y'
    print(f"✅ 回测: {'开启' if run_backtest else '跳过'}")

    send_qq = input("  是否自动推送到QQ？(y/N) ").strip().lower() == 'y'
    print(f"✅ QQ推送: {'开启' if send_qq else '关闭'}")

    return {
        "pool": pool_code,
        "pool_name": pool_name,
        "strategy": strategy_code,
        "strategy_name": strategy_name,
        "sample": sample_mode,
        "sample_size": 200 if sample_mode else None,
        "use_cache": use_cache,
        "run_backtest": run_backtest,
        "send_qq": send_qq,
    }


# ============== 命令行参数解析 ==============

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="AI 智能选股助手（A股版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 交互式运行
  python picker_cli.py

  # 快速采样（默认策略）
  python picker_cli.py --pool all --strategy multi_factor --sample

  # 全市场沪深300多因子策略
  python picker_cli.py --pool hs300 --strategy multi_factor --no-sample

  # 并指定输出路径
  python picker_cli.py --pool zz500 --strategy pe_value --sample --send-qq
        """
    )

    # 股票池
    parser.add_argument(
        "--pool", "-p",
        choices=["hs300", "zz500", "zz1000", "all"],
        default="all",
        help="股票池选择 (默认: all)"
    )

    # 策略
    parser.add_argument(
        "--strategy", "-s",
        choices=list(STRATEGY_OPTIONS.values()),
        default="multi_factor",
        help="策略选择 (默认: multi_factor)"
    )

    # 采样模式
    parser.add_argument(
        "--sample", "-S",
        action="store_true",
        default=None,
        help="采样模式（快速，默认开启）"
    )
    parser.add_argument(
        "--no-sample",
        action="store_false",
        dest="sample",
        help="全市场模式（慢速）"
    )

    # 缓存
    parser.add_argument(
        "--use-cache",
        action="store_true",
        default=True,
        help="使用缓存加速（默认: 是）"
    )
    parser.add_argument(
        "--no-cache",
        action="store_false",
        dest="use_cache",
        help="不使用缓存"
    )

    # 回测
    parser.add_argument(
        "--backtest", "-b",
        action="store_true",
        default=False,
        help="运行回测验证"
    )

    # QQ推送
    parser.add_argument(
        "--send-qq", "-q",
        action="store_true",
        default=False,
        help="推送到QQ"
    )

    # 输出目录
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="报告输出目录（默认: reports/daily）"
    )

    # 采样大小
    parser.add_argument(
        "--sample-size",
        type=int,
        default=200,
        help="采样大小（默认200只）"
    )

    # 日志级别
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细日志"
    )

    return parser.parse_args()


# ============== 主函数 ==============

def main():
    """主入口"""
    args = parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 确定是否交互
    # 如果参数不全（只有默认值），则进入交互模式
    is_interactive = len(sys.argv) == 1

    if is_interactive:
        # 交互式收集
        config = collect_user_preferences()
        pool = config['pool']
        strategy = config['strategy']
        sample_size = config['sample_size'] if config['sample'] else None
        use_cache = config['use_cache']
        run_backtest = config['run_backtest']
        send_qq = config['send_qq']
    else:
        # 命令行参数模式
        pool = args.pool
        strategy = args.strategy
        sample_size = args.sample_size if args.sample else None
        use_cache = args.use_cache
        run_backtest = args.backtest
        send_qq = args.send_qq

        print("\n" + "=" * 60)
        print("📊 AI 智能选股助手（命令行模式）")
        print("=" * 60)
        print(f"股票池: {pool}")
        print(f"策略: {strategy}")
        print(f"模式: {'采样' if sample_size else '全市场'}")
        print(f"缓存: {'开启' if use_cache else '关闭'}")
        print(f"回测: {'开启' if run_backtest else '关闭'}")
        print(f"QQ推送: {'开启' if send_qq else '关闭'}")

    # 运行引擎
    try:
        engine = StockPickerEngine()

        result = engine.run(
            pool=pool,
            strategy_name=strategy,
            use_cache=use_cache,
            run_backtest=run_backtest,
            send_qq=send_qq,
            sample_size=sample_size,
            top_n=30
        )

        # 输出结果
        if "error" in result:
            print(f"\n❌ 运行失败: {result['error']}")
            sys.exit(1)

        selected = result['selected']
        stats = result['stats']

        print("\n" + "=" * 60)
        print("✅ 选股完成！")
        print("=" * 60)
        print(f"扫描股票: {stats['total_stocks']} 只")
        print(f"有效数据: {stats['data_fetched']} 只")
        print(f"推荐数量: {stats['selected']} 只")
        print(f"筛选比例: {stats['selection_ratio']:.1f}%")
        print(f"耗时: {result['elapsed_seconds']:.1f} 秒")

        if not selected.empty:
            print("\n🏆 Top 5 推荐：")
            for idx, row in selected.head(5).iterrows():
                code = row.get('代码', row.get('code', '-'))
                name = row.get('名称', row.get('name', '-'))
                score = row.get('总分', row.get('total_score', 0))
                rating = row.get('评级', '-')
                print(f"  {code} {name} | {score:.1f}分 | {rating}")

        print(f"\n📄 Markdown报告: {result.get('report_path', '控制台输出')}")
        print(f"📊 Excel文件: {result['excel_path']}")

        if send_qq and result.get('qq_sent'):
            print("✅ 已推送到QQ")

        print("\n" + "=" * 60)

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"运行失败: {e}")
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
