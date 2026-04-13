#!/usr/bin/env python3
"""
QQ推送模块 - A股智能选股
负责将报告推送到QQ（通过OpenClaw直接回复机制）

注意：在OpenClaw环境中，直接在回复文本中嵌入<qqfile>标签即可自动发送。
本模块负责格式化消息内容。

Author: Simon (with AI Agent)
"""

import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class QQNotifier:
    """QQ通知器"""

    def __init__(self):
        self.max_message_length = 5000  # QQ消息长度限制

    def format_report_message(self,
                              report_md: str,
                              excel_path: str,
                              stats: Optional[dict] = None
                              ) -> str:
        """
        格式化QQ消息（Markdown + 文件标签）

        Args:
            report_md: 完整Markdown报告
            excel_path: Excel文件路径
            stats: 统计信息

        Returns:
            格式化的QQ消息字符串（包含<qqfile>标签）
        """
        # 提取报告中的关键信息
        lines = report_md.split('\n')

        # 构建简洁消息（适合QQ）
        message_parts = []

        # 标题
        message_parts.append("📊 **A股智能选股报告**")
        message_parts.append(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        message_parts.append("")

        # 统计摘要
        if stats:
            message_parts.append("📈 本次筛选结果：")
            message_parts.append(f"• 扫描股票: {stats.get('total_stocks', '-')} 只")
            message_parts.append(f"• 有效数据: {stats.get('data_fetched', '-')} 只")
            message_parts.append(f"• 推荐数量: {stats.get('selected', '-')} 只")
            message_parts.append(f"• 筛选比例: {stats.get('selection_ratio', 0):.1f}%")
            message_parts.append("")

        # 提取Top 5表格（从Markdown中）
        top5_lines = []
        in_table = False
        table_count = 0
        for line in lines:
            if '| 排名 |' in line or '| 代码 |' in line:
                in_table = True
                top5_lines.append(line)
                continue
            if in_table and '|' in line:
                top5_lines.append(line)
                table_count += 1
                if table_count >= 6:  # 表头 + 5行数据
                    break

        if top5_lines:
            message_parts.append("🏆 Top 5 推荐：")
            message_parts.extend(top5_lines)
            message_parts.append("")

        # 附件
        excel_file = Path(excel_path)
        if excel_file.exists():
            message_parts.append(f"📎 完整数据: <qqfile>{excel_path}</qqfile>")
        else:
            message_parts.append(f"📎 Excel文件: {excel_path}")

        message_parts.append("")
        message_parts.append("⚠️ 风险提示：本报告仅供学习参考，不构成投资建议。股市有风险，决策需谨慎。")

        full_message = "\n".join(message_parts)

        # 长度检查
        if len(full_message) > self.max_message_length:
            logger.warning(f"消息过长({len(full_message)}字符)，将截断")
            full_message = full_message[:self.max_message_length - 100] + "\n...（消息过长，请查看完整报告）"

        return full_message

    def send(self, report_md: str, excel_path: str, stats: Optional[dict] = None) -> bool:
        """
        发送报告到QQ

        在OpenClaw环境中，此函数应返回消息文本，
        由调用者通过直接回复的方式发送（避免使用message工具）

        Args:
            report_md: Markdown报告全文
            excel_path: Excel文件路径
            stats: 统计信息

        Returns:
            True表示消息已准备就绪
        """
        try:
            message = self.format_report_message(report_md, excel_path, stats)
            logger.info(f"QQ消息已格式化，长度: {len(message)} 字符")
            # 注意：实际发送由调用者通过直接回复完成
            # 在OpenClaw中，只需在回复中包含<qqfile>标签即可
            return True
        except Exception as e:
            logger.error(f"QQ消息格式化失败: {e}")
            return False


# 便捷函数
def format_qq_report(report_md: str, excel_path: str, stats: Optional[dict] = None) -> str:
    """快速格式化QQ报告"""
    notifier = QQNotifier()
    return notifier.format_report_message(report_md, excel_path, stats)


if __name__ == "__main__":
    # 测试
    import sys
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("📊 QQ推送模块测试")
    print("=" * 60)

    # 模拟报告
    mock_report = """# 📈 A股智能选股报告

**生成时间**: 2026-04-13 16:00

## 📊 筛选结果摘要

| 指标 | 数值 |
|------|------|
| 推荐股票数 | 5 只 |
| 平均PE | 18.5 |
| 平均综合分 | 72.3 分 |

## 🏆 Top 20 推荐

| 排名 | 代码 | 名称 | PE | PB | 收盘价 | 综合分 | 评级 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 600519 | 贵州茅台 | 25.5 | 8.2 | 1680.5 | 82.5 | 🟢 推荐 |
| 2 | 000858 | 五粮液 | 18.2 | 5.1 | 156.3 | 85.2 | 🟢 推荐 |
"""

    mock_excel = "/root/.openclaw/workspace/stock-picker-plus/reports/daily/stock_pool_test.xlsx"

    notifier = QQNotifier()
    message = notifier.format_report_message(mock_report, mock_excel, {
        'total_stocks': 200,
        'data_fetched': 186,
        'selected': 5,
        'selection_ratio': 2.7
    })

    print("\n生成的QQ消息：")
    print("=" * 60)
    print(message)
    print("=" * 60)

    print("\n✅ QQ推送模块测试完成")
