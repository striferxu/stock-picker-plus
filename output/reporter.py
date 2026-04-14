#!/usr/bin/env python3
"""
Markdown报告生成器 - 完整版
整合来源：
- ai-stock-picker/stock_picker/reporter.py (格式)
- finance-ai-project/src/report.py (详细字段)

输出：Markdown格式选股报告
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MarkdownReporter:
    """Markdown报告生成器"""

    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir

    def generate(self,
                 selected_stocks: pd.DataFrame,
                 pool: str,
                 strategy: str,
                 backtest_result: Optional[Dict[str, Any]] = None,
                 stats: Optional[Dict[str, Any]] = None,
                 timestamp: Optional[datetime] = None
                 ) -> str:
        """
        生成完整报告

        Args:
            selected_stocks: 筛选出的股票DataFrame
            pool: 股票池名称
            strategy: 策略名称
            backtest_result: 回测结果（可选）
            stats: 统计信息
            timestamp: 时间戳（默认当前时间）

        Returns:
            Markdown格式报告字符串
        """
        if timestamp is None:
            timestamp = datetime.now()

        # 报告头部
        report = self._generate_header(pool, strategy, timestamp, stats)

        # 选股结果摘要
        report += self._generate_summary(selected_stocks)

        # Top 20 表格
        report += self._generate_top20_table(selected_stocks)

        # 详细分析（每只股票）
        report += self._generate_detailed_analysis(selected_stocks)

        # 回测结果（如有）
        if backtest_result:
            report += self._generate_backtest_section(backtest_result)

        # 免责声明
        report += self._generate_disclaimer(timestamp)

        return report

    def _generate_header(self, pool: str, strategy: str, timestamp: datetime, stats: Optional[Dict]) -> str:
        """报告头部"""
        header = f"""# 📈 A股智能选股报告

**生成时间**: {timestamp.strftime('%Y-%m-%d %H:%M')}
**股票池**: {pool}
**策略**: {strategy}
"""

        if stats:
            header += f"""
**统计信息**:
- 扫描股票数: {stats.get('total_stocks', '-')} 只
- 有效数据: {stats.get('data_fetched', '-')} 只
- 筛选结果: {stats.get('selected', '-')} 只
- 筛选比例: {stats.get('selection_ratio', 0):.1f}%

---

"""

        return header

    def _generate_summary(self, selected_stocks: pd.DataFrame) -> str:
        """摘要统计"""
        if selected_stocks.empty:
            return "## ⚠️ 未找到符合条件的股票\n"

        avg_pe = selected_stocks['PE'].mean() if 'PE' in selected_stocks.columns else '-'
        avg_score = selected_stocks['总分'].mean() if '总分' in selected_stocks.columns else selected_stocks['total_score'].mean()

        summary = f"""## 📊 筛选结果摘要

| 指标 | 数值 |
|------|------|
| 推荐股票数 | {len(selected_stocks)} 只 |
| 平均PE | {avg_pe:.1f}  |
| 平均综合分 | {avg_score:.1f} 分 |
| 最高分 | {selected_stocks['总分'].max() if '总分' in selected_stocks.columns else selected_stocks['total_score'].max():.1f} 分 |

---

"""
        return summary

    def _generate_top20_table(self, selected_stocks: pd.DataFrame) -> str:
        """Top 20 表格"""
        if selected_stocks.empty:
            return ""

        top20 = selected_stocks.head(20)

        # 列名映射（确保中文列名）
        col_map = {
            '代码': '代码',
            'code': '代码',
            '名称': '名称',
            'name': '名称',
            'PE': 'PE',
            'PB': 'PB',
            '收盘价': '收盘价',
            'close': '收盘价',
            '总分': '综合分',
            'total_score': '综合分',
            '评级': '评级',
            '基本面': '基本面',
            '技术面': '技术面',
            '情绪面': '情绪面',
        }

        # 构建表头
        headers = ['排名', '代码', '名称', 'PE', 'PB', '收盘价', '综合分', '评级']
        table = "## 🏆 Top 20 推荐\n\n"
        table += "| " + " | ".join(headers) + " |\n"
        table += "|" + ":---|" * len(headers) + "\n"

        for idx, (_, row) in enumerate(top20.iterrows(), 1):
            code = row.get('代码', row.get('code', '-'))
            name = row.get('名称', row.get('name', '-'))
            pe = f"{row.get('PE', 0):.1f}" if pd.notna(row.get('PE', None)) else '-'
            pb = f"{row.get('PB', 0):.1f}" if pd.notna(row.get('PB', None)) else '-'
            close = f"{row.get('收盘价', row.get('close', 0)):.2f}"
            score = f"{row.get('总分', row.get('total_score', 0)):.1f}"
            rating = row.get('评级', '-')

            table += f"| {idx} | {code} | {name} | {pe} | {pb} | {close} | **{score}** | {rating} |\n"

        table += "\n"
        return table

    def _generate_detailed_analysis(self, selected_stocks: pd.DataFrame) -> str:
        """详细分析（每只股票）"""
        if selected_stocks.empty:
            return ""

        analysis = "## 📋 详细分析\n\n"

        top5 = selected_stocks.head(5)
        for idx, (_, row) in enumerate(top5.iterrows(), 1):
            code = row.get('代码', row.get('code', ''))
            name = row.get('名称', row.get('name', ''))
            score = row.get('总分', row.get('total_score', 0))
            rating = row.get('评级', '')

            analysis += f"### {idx}. {code} {name} — {rating}\n\n"
            analysis += f"**综合评分：** {score:.1f} / 100\n\n"

            # 各维度得分
            analysis += "| 维度 | 评分 | 关键指标 |\n|:---|:---:|:---|\n"
            analysis += f"| 基本面 | {row.get('基本面', '-'):.1f} | PE: {row.get('PE', '-'):.1f}, ROE: {row.get('ROE', '-'):.1f}% |\n"
            analysis += f"| 技术面 | {row.get('技术面', '-'):.1f} | 待补充 |\n"
            analysis += f"| 情绪面 | {row.get('情绪面', '-'):.1f} | 待补充 |\n\n"

        return analysis

    def _generate_backtest_section(self, backtest_result: Dict[str, Any]) -> str:
        """回测结果章节"""
        section = "## 📊 回测验证\n\n"
        section += "| 指标 | 数值 |\n|:---|:---|\n"
        section += f"| 初始资金 | ¥{backtest_result['初始资金']:,.0f} |\n"
        section += f"| 最终价值 | ¥{backtest_result['最终价值']:,.0f} |\n"
        section += f"| 总收益率 | {backtest_result['总收益率']:.2f}% |\n"
        section += f"| 年化收益 | {backtest_result['年化收益率']:.2f}% |\n"
        section += f"| 夏普比率 | {backtest_result['夏普比率']:.2f} |\n"
        section += f"| 最大回撤 | {backtest_result['最大回撤']:.2f}% |\n"
        section += f"| 交易次数 | {backtest_result['交易次数']} 次 |\n"

        if '胜率' in backtest_result:
            section += f"| 胜率 | {backtest_result['胜率']:.1f}% |\n"

        section += "\n"
        return section

    def _generate_disclaimer(self, timestamp: datetime) -> str:
        """免责声明"""
        return f"""---

## ⚠️ 免责声明

1. 本报告由 AI 自动生成，仅供参考，**不构成投资建议**。
2. 股市有风险，投资需谨慎，决策前请自行判断。
3. 历史数据不代表未来表现，策略可能失效。
4. 报告基于 Baostock 数据源，数据有一定延迟。

*报告生成时间：{timestamp.strftime('%Y-%m-%d %H:%M')}*
*由 小跃（StepFun AI Agent）生成*
"""


# ============== 简化版报告生成（兼容旧代码） ==============

def generate_simple_report(selected: pd.DataFrame, pool: str, strategy: str) -> str:
    """
    生成简洁报告（用于快速预览）

    Returns:
        简短的Markdown文本
    """
    if selected.empty:
        return "😢 未找到符合条件的股票。"

    top5 = selected.head(5)
    lines = [
        f"# 📈 {pool} · {strategy} 选股结果",
        f"共选出 **{len(selected)}** 只股票，Top 5：",
        "",
        "| 排名 | 代码 | 名称 | 综合分 | 评级 |",
        "|:---:|:---:|:---:|:---:|:---:|",
    ]

    for idx, (_, row) in enumerate(top5.iterrows(), 1):
        code = row.get('代码', row.get('code', '-'))
        name = row.get('名称', row.get('name', '-'))
        score = f"{row.get('总分', row.get('total_score', 0)):.1f}"
        rating = row.get('评级', '-')
        lines.append(f"| {idx} | {code} | {name} | {score} | {rating} |")

    lines.append("")
    lines.append("详细报告请查看完整文档。")
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("📊 报告生成器测试")
    print("=" * 60)

    # 模拟数据
    mock_data = pd.DataFrame({
        '代码': ['600519', '000858', '600036', '000333', '002594'],
        '名称': ['贵州茅台', '五粮液', '招商银行', '美的集团', '比亚迪'],
        'PE': [25.5, 18.2, 8.5, 12.3, 30.2],
        'PB': [8.2, 5.1, 1.2, 2.8, 3.5],
        '收盘价': [1680.5, 156.3, 42.1, 58.2, 245.6],
        'ROE': [32.1, 28.5, 16.2, 22.1, 12.5],
        '营收增长率': [12.3, 15.6, 8.9, 9.8, 25.3],
        '基本面': [85, 90, 70, 75, 65],
        '技术面': [75, 80, 60, 70, 85],
        '情绪面': [80, 75, 65, 70, 90],
        '总分': [82.5, 85.2, 68.4, 72.1, 78.6],
        '评级': ['🟢 推荐', '🟢 推荐', '🟡 观望', '🟡 观望', '🟢 推荐']
    })

    reporter = MarkdownReporter()
    report = reporter.generate(
        selected_stocks=mock_data,
        pool="沪深300",
        strategy="多因子策略",
        stats={
            'total_stocks': 300,
            'data_fetched': 285,
            'selected': 5,
            'selection_ratio': 1.67
        }
    )

    print("\n生成的报告预览（前500字符）：")
    print(report[:500])
    print("...")

    # 保存到文件
    output_dir = Path("reports/daily")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = output_dir / f"report_combined_{timestamp}.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"\n✅ 完整报告已保存到: {report_path}")

    print("\n" + "=" * 60)
    print("✅ 报告生成器测试完成")
    print("=" * 60)
