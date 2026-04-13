#!/usr/bin/env python3
"""
Excel导出模块 - 完整版
整合自 finance-ai-project 的Excel生成逻辑

功能：将筛选结果导出为带中文字段的Excel文件

Author: Simon (with AI Agent)
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ExcelWriter:
    """Excel文件写入器"""

    def __init__(self, output_dir: str = "reports/daily"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_stock_pool(self,
                         selected_stocks: pd.DataFrame,
                         pool: str,
                         strategy: str,
                         timestamp: Optional[datetime] = None
                         ) -> str:
        """
        写入股票池到Excel

        Args:
            selected_stocks: 筛选结果DataFrame
            pool: 股票池名称
            strategy: 策略名称
            timestamp: 时间戳

        Returns:
            文件路径
        """
        if timestamp is None:
            timestamp = datetime.now()

        timestamp_str = timestamp.strftime("%Y%m%d_%H%M")
        filename = f"stock_pool_{timestamp_str}.xlsx"
        filepath = self.output_dir / filename

        # 准备导出数据（中文字段）
        export_df = selected_stocks.copy()

        # 字段名映射（标准化）
        field_mapping = {
            '代码': '代码',
            'code': '代码',
            '名称': '名称',
            'name': '名称',
            'PE': 'PE',
            'PB': 'PB',
            '收盘价': '收盘价',
            'close': '收盘价',
            '总市值': '总市值（亿元）',
            'market_cap': '总市值（亿元）',
            'ROE': 'ROE(%)',
            '营收增长率': '营收增长率(%)',
            '利润增长率': '净利润增长率(%)',
        }

        # 重命名列
        export_df.rename(columns=field_mapping, inplace=True, errors='ignore')

        # 选择要导出的列（按顺序）
        export_columns = [
            '代码', '名称', 'PE', 'PB', '收盘价',
            '总市值（亿元）', 'ROE(%)', '营收增长率(%)', '净利润增长率(%)',
            '估值分', '盈利分', '规模分',
            '估值分_归一化', '盈利分_归一化', '规模分_归一化',
            '综合分', '总分', '评级'
        ]

        # 只保留存在的列
        available_cols = [c for c in export_columns if c in export_df.columns]
        export_df = export_df[available_cols]

        # 写入Excel
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name='推荐股票池', index=False)

                # 添加汇总sheet
                summary_df = self._generate_summary_sheet(selected_stocks, pool, strategy, timestamp)
                summary_df.to_excel(writer, sheet_name='汇总统计', index=False)

            logger.info(f"✅ Excel导出成功: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"❌ Excel导出失败: {e}")
            raise

    def _generate_summary_sheet(self,
                               selected_stocks: pd.DataFrame,
                               pool: str,
                               strategy: str,
                               timestamp: datetime
                               ) -> pd.DataFrame:
        """生成汇总统计表"""
        summary_data = {
            '项目': [
                '生成时间',
                '股票池',
                '策略',
                '推荐数量',
                '平均PE',
                '平均PB',
                '平均ROE(%)',
                '平均综合分',
                '最高分',
                '最低分',
            ],
            '数值': [
                timestamp.strftime('%Y-%m-%d %H:%M'),
                pool,
                strategy,
                len(selected_stocks),
                f"{selected_stocks['PE'].mean():.1f}" if 'PE' in selected_stocks.columns else '-',
                f"{selected_stocks['PB'].mean():.1f}" if 'PB' in selected_stocks.columns else '-',
                f"{selected_stocks['ROE'].mean():.1f}" if 'ROE' in selected_stocks.columns else '-',
                f"{selected_stocks['总分'].mean():.1f}" if '总分' in selected_stocks.columns else '-',
                f"{selected_stocks['总分'].max():.1f}" if '总分' in selected_stocks.columns else '-',
                f"{selected_stocks['总分'].min():.1f}" if '总分' in selected_stocks.columns else '-',
            ]
        }

        return pd.DataFrame(summary_data)

    def write_detailed_report(self,
                              all_data: pd.DataFrame,
                              pool: str,
                              strategy: str,
                              timestamp: Optional[datetime] = None
                              ) -> str:
        """
        写入详细报告（包含全部扫描数据，不仅是筛选结果）

        Returns:
            文件路径
        """
        if timestamp is None:
            timestamp = datetime.now()

        timestamp_str = timestamp.strftime("%Y%m%d_%H%M")
        filename = f"full_scan_{timestamp_str}.xlsx"
        filepath = self.output_dir / filename

        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 全部数据
                all_data.to_excel(writer, sheet_name='全部股票', index=False)

                # 筛选结果
                if 'signal' in all_data.columns:
                    selected = all_data[all_data['signal'] == 1]
                    selected.to_excel(writer, sheet_name='筛选结果', index=False)

                # 各因子分表
                if 'pe_score_norm' in all_data.columns:
                    factor_cols = ['代码', '名称', 'pe_score_norm', 'roe_score_norm', 'growth_score_norm', 'total_score']
                    available = [c for c in factor_cols if c in all_data.columns]
                    all_data[available].to_excel(writer, sheet_name='因子得分', index=False)

            logger.info(f"✅ 详细报告导出成功: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"❌ 详细报告导出失败: {e}")
            raise


if __name__ == "__main__":
    # 测试
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("📊 Excel导出模块测试")
    print("=" * 60)

    # 模拟数据
    mock_data = pd.DataFrame({
        '代码': ['600519', '000858', '600036'],
        '名称': ['贵州茅台', '五粮液', '招商银行'],
        'PE': [25.5, 18.2, 8.5],
        'PB': [8.2, 5.1, 1.2],
        '收盘价': [1680.5, 156.3, 42.1],
        'ROE': [32.1, 28.5, 16.2],
        '营收增长率': [12.3, 15.6, 8.9],
        '估值分_归一化': [85, 90, 70],
        '盈利分_归一化': [80, 85, 75],
        '规模分_归一化': [75, 80, 70],
        '综合分': [82.5, 85.2, 68.4],
        '评级': ['🟢 推荐', '🟢 推荐', '🟡 观望']
    })

    writer = ExcelWriter()
    path = writer.write_stock_pool(mock_data, "沪深300", "多因子策略")
    print(f"\n✅ 文件已生成: {path}")

    print("\n" + "=" * 60)
    print("✅ Excel导出模块测试完成")
    print("=" * 60)
