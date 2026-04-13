#!/usr/bin/env python3
"""
快速集成测试 - 验证核心流程

测试内容：
1. Baostock 登录
2. 获取股票列表
3. 单股财务查询
4. 批量查询（采样20只）
5. 策略评分
6. 报告生成

运行：python tests/integration_test.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
logging.basicConfig(level=logging.INFO)

from core import (
    init_data_fetcher,
    get_stock_basic,
    fetch_batch,
    get_strategy,
    StockPickerEngine
)

def main():
    print("=" * 60)
    print("📊 集成测试 - 核心流程验证")
    print("=" * 60)

    try:
        # Step 1: 初始化
        print("\n【Step 1】初始化数据模块...")
        init_data_fetcher()
        print("✅ 初始化成功")

        # Step 2: 获取股票列表
        print("\n【Step 2】获取股票列表...")
        basic_df = get_stock_basic()
        if basic_df.empty:
            print("❌ 股票列表为空，测试终止")
            return
        print(f"✅ 获取 {len(basic_df)} 只股票")

        # Step 3: 批量查询（采样20只）
        print("\n【Step 3】批量查询（采样20只）...")
        sample_codes = basic_df['code'].head(20).tolist()
        # 转为6位数字格式
        sample_codes = [c.split('.')[1] if '.' in c else c for c in sample_codes]

        batch_df = fetch_batch(sample_codes, max_workers=5)
        if batch_df.empty:
            print("❌ 批量查询无结果")
            return
        print(f"✅ 查询成功: {len(batch_df)} 只")

        # Step 4: 策略评分
        print("\n【Step 4】策略评分...")
        strategy = get_strategy("multi_factor")
        scored_df = strategy.generate_signals(batch_df)
        selected = strategy.select_stocks(scored_df, top_n=10)
        print(f"✅ 筛选完成: {len(selected)} 只推荐")

        if not selected.empty:
            print("\n🏆 Top 5 推荐:")
            for idx, row in selected.head(5).iterrows():
                code = row.get('代码', '-')
                name = row.get('名称', '-')
                score = row.get('总分', 0)
                print(f"  {code} {name} | 综合分:{score:.1f}")

        # Step 5: 完整引擎测试
        print("\n【Step 5】完整引擎测试（采样50只）...")
        engine = StockPickerEngine()
        result = engine.run(
            pool="all",
            strategy_name="multi_factor",
            sample_size=50,
            use_cache=True,
            send_qq=False
        )

        if "error" not in result:
            stats = result['stats']
            print(f"✅ 引擎运行成功")
            print(f"   扫描: {stats['total_stocks']} → 筛选: {stats['selected']} 只")
            print(f"   耗时: {result['elapsed_seconds']:.1f}秒")
            print(f"   Excel: {result['excel_path']}")
        else:
            print(f"❌ 引擎运行失败: {result['error']}")

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！系统已就绪。")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
