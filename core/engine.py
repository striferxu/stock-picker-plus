#!/usr/bin/env python3
"""
主引擎 - 选股系统核心
整合数据获取、策略评分、报告生成全流程

设计：
1. 初始化各模块
2. 执行流程（数据 → 评分 → 筛选 → 报告）
3. 支持缓存、批量、回测

Author: Simon (with AI Agent)
"""

import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from .data_fetcher import DataFetcher
from .scorer import calculate_comprehensive_score
from .strategies import get_strategy, BaseStrategy
from .backtest import BacktestEngine, quick_backtest
from .indicators import add_all_indicators, calculate_momentum
from .cache_manager import CacheManager
from output.reporter import MarkdownReporter
from output.excel_writer import ExcelWriter
from output.qq_notifier import QQNotifier

logger = logging.getLogger(__name__)


class StockPickerEngine:
    """
    选股引擎 - 核心协调器

    使用示例：
    ```python
    engine = StockPickerEngine()
    result = engine.run(
        pool="all",              # 股票池：all/hs300/zz500/zz1000
        strategy_name="multi_factor",  # 策略名
        use_cache=True,          # 使用缓存
        send_qq=False            # 是否QQ推送
    )
    ```
    """

    def __init__(self,
                 config_path: str = "config/",
                 cache_dir: str = "data/cache",
                 reports_dir: str = "reports/daily"):
        """
        初始化引擎

        Args:
            config_path: 配置文件目录
            cache_dir: 缓存目录
            reports_dir: 报告输出目录
        """
        logger.info("初始化选股引擎...")

        # 初始化模块
        self.fetcher = DataFetcher(config_path)
        self.cache = CacheManager(cache_dir)
        self.reporter = MarkdownReporter()
        self.excel_writer = ExcelWriter(reports_dir)
        self.qq_notifier = QQNotifier()

        # 策略注册表（在 strategies.py 中已定义）
        from .strategies import STRATEGY_REGISTRY
        self.strategies = STRATEGY_REGISTRY

        # 回测引擎
        self.backtest_engine = BacktestEngine()

        logger.info("✅ 引擎初始化完成")

    def run(self,
            pool: str = "all",
            strategy_name: str = "multi_factor",
            strategy_params: Optional[Dict] = None,
            use_cache: bool = True,
            run_backtest: bool = False,
            send_qq: bool = False,
            top_n: int = 30,
            sample_size: Optional[int] = None
            ) -> Dict[str, Any]:
        """
        执行完整选股流程

        Args:
            pool: 股票池 ("all", "hs300", "zz500", "zz1000")
            strategy_name: 策略名称
            strategy_params: 策略参数（覆盖默认）
            use_cache: 是否使用缓存
            run_backtest: 是否运行回测
            send_qq: 是否QQ推送
            top_n: 最终推荐数量
            sample_size: 采样大小（None=全市场，int=采样N只用于测试）

        Returns:
            结果字典（包含selected, report, excel_path, stats）
        """
        start_time = datetime.now()
        logger.info(f"=" * 60)
        logger.info(f"🚀 开始运行 | 池: {pool} | 策略: {strategy_name}")
        logger.info(f"=" * 60)

        # ========== Step 1: 获取股票池 ==========
        logger.info("【Step 1】获取股票列表...")
        if use_cache:
            stock_list_df = self.cache.get_stock_list_cache()
            if stock_list_df is None:
                stock_list_df = self.fetcher.get_stock_basic()
                self.cache.set_stock_list_cache(stock_list_df)
        else:
            stock_list_df = self.fetcher.get_stock_basic()

        if stock_list_df.empty:
            raise ValueError("无法获取股票列表")

        # 根据池筛选
        stock_codes = self._filter_stock_pool(stock_list_df, pool)
        logger.info(f"股票池: {len(stock_codes)} 只")

        # 采样（可选，用于快速测试）
        if sample_size and sample_size < len(stock_codes):
            import random
            random.seed(42)
            stock_codes = random.sample(stock_codes, sample_size)
            logger.info(f"采样模式: {len(stock_codes)} 只")

        # ========== Step 2: 批量获取数据 ==========
        logger.info("【Step 2】批量获取数据（多线程）...")
        data_df = self.fetcher.fetch_batch(
            stock_codes,
            fields=['basic', 'valuation', 'financials'],
            use_cache=use_cache,
            max_workers=10
        )
        logger.info(f"数据获取完成: {len(data_df)} 只")

        if data_df.empty:
            logger.warning("未获取到有效数据")
            return {"error": "无有效数据"}

        # ========== Step 3: 计算技术指标 ==========
        logger.info("【Step 3】计算技术指标...")
        # 为每只股票获取历史行情并计算指标（简化：只取最近250天）
        # 注意：这会增加查询量，实际可选择性计算
        # 暂时跳过，按需计算

        # ========== Step 4: 策略评分 ==========
        logger.info("【Step 4】应用策略评分...")
        strategy = self._get_strategy(strategy_name, strategy_params)
        scored_df = strategy.generate_signals(data_df)
        logger.info("评分完成")

        # ========== Step 5: 筛选 ==========
        logger.info("【Step 5】筛选推荐股票...")
        selected = strategy.select_stocks(scored_df, top_n=top_n)
        logger.info(f"筛选结果: {len(selected)} 只")

        if selected.empty:
            logger.warning("未筛选出符合条件的股票")
            return {"selected": pd.DataFrame(), "stats": {"selected": 0}}

        # ========== Step 6: 回测（可选） ==========
        backtest_result = None
        if run_backtest and hasattr(strategy, 'backtest'):
            logger.info("【Step 6】运行回测...")
            # 需要历史日线数据，暂时跳过
            # backtest_result = quick_backtest(strategy, data_df)
            logger.info("回测暂未实现")

        # ========== Step 7: 生成报告 ==========
        logger.info("【Step 7】生成报告...")
        timestamp = datetime.now()
        stats = {
            "total_stocks": len(stock_codes),
            "data_fetched": len(data_df),
            "selected": len(selected),
            "selection_ratio": len(selected) / len(data_df) * 100 if len(data_df) > 0 else 0,
        }

        report_md = self.reporter.generate(
            selected_stocks=selected,
            pool=self._pool_name(pool),
            strategy=strategy.name,
            backtest_result=backtest_result,
            stats=stats,
            timestamp=timestamp
        )

        # ========== Step 8: 导出Excel ==========
        logger.info("【Step 8】导出Excel...")
        excel_path = self.excel_writer.write_stock_pool(
            selected_stocks=selected,
            pool=self._pool_name(pool),
            strategy=strategy.name,
            timestamp=timestamp
        )

        # ========== Step 9: QQ推送（可选） ==========
        qq_sent = False
        if send_qq:
            logger.info("【Step 9】QQ推送...")
            try:
                qq_sent = self.qq_notifier.send(report_md, excel_path)
            except Exception as e:
                logger.warning(f"QQ推送失败: {e}")

        # ========== 完成 ==========
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ 运行完成 | 耗时: {elapsed:.1f}秒 | 推荐: {len(selected)} 只")

        return {
            "selected": selected,
            "report_md": report_md,
            "excel_path": excel_path,
            "stats": stats,
            "qq_sent": qq_sent,
            "elapsed_seconds": elapsed,
            "timestamp": timestamp,
        }

    def _filter_stock_pool(self, stock_df: pd.DataFrame, pool: str) -> List[str]:
        """
        根据股票池筛选代码列表

        Args:
            stock_df: 股票基本信息DataFrame
            pool: 池名称 ("all", "hs300", "zz500", "zz1000")

        Returns:
            股票代码列表（如 ['600519', '000858', ...]）
        """
        if pool == "all":
            # 全市场：排除指数、基金、债券等
            df = stock_df.copy()
            # 过滤：仅保留A股（sh. 或 sz.）
            df = df[df['code'].str.startswith(('sh.', 'sz.'))]
            # 排除ST
            df = df[~df['code_name'].str.contains('ST|退市', na=False)]
            codes = df['code'].tolist()
        else:
            # 指数成分股（需从 Baostock 查询）
            # 简化：调用 fetcher 的指数成分获取
            codes = self.fetcher.get_index_components(pool)

        return codes

    def _pool_name(self, pool: str) -> str:
        """池代码转中文名"""
        names = {
            "all": "全A股",
            "hs300": "沪深300",
            "zz500": "中证500",
            "zz1000": "中证1000"
        }
        return names.get(pool, pool)

    def _get_strategy(self, name: str, params: Optional[Dict]) -> BaseStrategy:
        """获取策略实例"""
        if params:
            return get_strategy(name, **params)
        else:
            # 默认参数
            defaults = {
                "multi_factor": {"min_score": 60, "min_market_cap": 50},
                "pe_value": {"pe_threshold": 20, "roe_threshold": 15},
            }
            return get_strategy(name, **(defaults.get(name, {})))


# ============== 便捷函数 ==============

def run_quick_scan(pool: str = "all", sample_size: int = 200, strategy: str = "multi_factor") -> Dict[str, Any]:
    """
    快速扫描（采样版）

    用途：快速测试、预览结果
    耗时：~20-30秒（采样200只）
    """
    engine = StockPickerEngine()
    return engine.run(
        pool=pool,
        strategy_name=strategy,
        sample_size=sample_size,
        use_cache=True
    )


def run_full_scan(pool: str = "all", strategy: str = "multi_factor") -> Dict[str, Any]:
    """
    全市场扫描

    用途：正式报告
    耗时：~15-20分钟（8687只）
    """
    engine = StockPickerEngine()
    return engine.run(
        pool=pool,
        strategy_name=strategy,
        use_cache=False,  # 全量查询不使用缓存（避免过期）
        run_backtest=False,  # 回测耗时长，可后续加
        top_n=50
    )


if __name__ == "__main__":
    # 直接运行测试
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("📊 主引擎测试（采样200只）")
    print("=" * 60)

    # 快速测试（采样）
    result = run_quick_scan(pool="all", sample_size=200, strategy="multi_factor")

    if "error" not in result:
        print(f"\n✅ 扫描完成！")
        print(f"   推荐数量: {len(result['selected'])} 只")
        print(f"   耗时: {result['elapsed_seconds']:.1f} 秒")
        print(f"   Excel: {result['excel_path']}")

        # 预览Top 5
        selected = result['selected']
        if not selected.empty:
            print("\nTop 5 推荐:")
            for idx, row in selected.head(5).iterrows():
                print(f"  {row.get('代码','-')} {row.get('名称','-')} | 综合分: {row.get('总分',0):.1f}")
    else:
        print(f"❌ 失败: {result['error']}")

    print("\n" + "=" * 60)
    print("✅ 主引擎测试完成")
    print("=" * 60)
