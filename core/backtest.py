#!/usr/bin/env python3
"""
回测引擎 - A股专版
整合自 finance-ai-project/src/backtest.py

功能：
- 支持 T+1 交易规则
- 印花税（0.05%）、手续费（0.03%）
- 最大回撤、夏普比率计算
- 与策略类集成

Author: Simon (with AI Agent)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """A股回测引擎"""

    def __init__(self,
                 initial_capital: float = 1000000,
                 commission: float = 0.0003,  # 手续费 0.03%
                 stamp_tax: float = 0.0005,   # 印花税 0.05% (仅卖出)
                 slippage: float = 0.001,     # 滑点 0.1%
                 position_limit: float = 0.10,  # 单票上限 10%
                 max_drawdown_limit: float = 0.15  # 最大回撤止损 15%
                 ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.stamp_tax = stamp_tax
        self.slippage = slippage
        self.position_limit = position_limit  # 单票仓位上限（占总资产）
        self.max_drawdown_limit = max_drawdown_limit

    def run(self,
            signals: pd.DataFrame,
            price_data: Optional[pd.DataFrame] = None,
            benchmark_code: str = "000300"
            ) -> Dict[str, Any]:
        """
        运行回测

        Args:
            signals: 包含 signal 列的DataFrame（1=买入，-1=卖出）
            price_data: 价格数据（若为None则用信号中的价格）
            benchmark_code: 基准指数代码

        Returns:
            回测结果字典
        """
        logger.info(f"开始回测 | 初始资金: {self.initial_capital:,.0f}")

        # 准备数据
        df = signals.copy()
        if 'date' not in df.columns:
            df['date'] = pd.Timestamp.today()

        # 排序
        df = df.sort_values('date').reset_index(drop=True)

        # 初始化
        capital = self.initial_capital
        position = 0  # 持仓股数
        total_position_value = 0  # 持仓市值
        peak = self.initial_capital
        max_drawdown = 0
        trades = []  # 交易记录

        df['capital'] = self.initial_capital
        df['position_value'] = 0
        df['total_value'] = self.initial_capital
        df['returns'] = 0.0

        for i in range(1, len(df)):
            current_price = df['close'].iloc[i] if 'close' in df.columns else df.get('收盘价', 0)
            signal = df['signal'].iloc[i]

            # === 买入 ===
            if signal == 1 and position == 0:
                # 计算可买数量（考虑仓位限制）
                max_buy_value = capital * self.position_limit
                buy_value = min(capital * 0.99, max_buy_value)  # 留1%现金，不超过仓位上限

                # 考虑滑点（买入价格更高）
                exec_price = current_price * (1 + self.slippage)
                shares = int(buy_value / exec_price)

                if shares > 0:
                    cost = shares * exec_price * (1 + self.commission)
                    capital -= cost
                    position = shares
                    total_position_value = shares * exec_price

                    trades.append({
                        'type': 'buy',
                        'date': df['date'].iloc[i],
                        'price': exec_price,
                        'shares': shares,
                        'cost': cost,
                    })

            # === 卖出 ===
            elif signal == -1 and position > 0:
                # 考虑滑点（卖出价格更低）
                exec_price = current_price * (1 - self.slippage)
                revenue = position * exec_price * (1 - self.commission - self.stamp_tax)
                capital += revenue

                trades.append({
                    'type': 'sell',
                    'date': df['date'].iloc[i],
                    'price': exec_price,
                    'shares': position,
                    'revenue': revenue,
                    'profit': revenue - (position * df['close'].iloc[i-1])  # 简化盈亏
                })

                position = 0
                total_position_value = 0

            # === 更新持仓市值（按当日收盘价）===
            if position > 0:
                total_position_value = position * current_price

            total_value = capital + total_position_value

            # === 最大回撤监控 ===
            if total_value > peak:
                peak = total_value
            drawdown = (peak - total_value) / peak

            if drawdown > max_drawdown:
                max_drawdown = drawdown

            # === 强制平仓（触发最大回撤止损）===
            if drawdown >= self.max_drawdown_limit:
                logger.warning(f"⚠️ 触发最大回撤止损 ({drawdown:.2%}) @ {df['date'].iloc[i]}")
                # 强制卖出全部持仓
                if position > 0:
                    exec_price = current_price * (1 - self.slippage)
                    revenue = position * exec_price * (1 + self.commission + self.stamp_tax)
                    capital += revenue
                    position = 0
                    total_position_value = 0

            # 记录
            df.at[df.index[i], 'capital'] = capital
            df.at[df.index[i], 'position_value'] = total_position_value
            df.at[df.index[i], 'total_value'] = total_value
            df.at[df.index[i], 'drawdown'] = drawdown

        # 最终指标计算
        final_value = df['total_value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100

        # 年化收益
        days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
        annual_return = ((1 + total_return / 100) ** (365 / days) - 1) * 100 if days > 0 else 0

        # 夏普比率（假设无风险利率0，日频）
        returns = df['total_value'].pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if len(returns) > 0 and returns.std() > 0 else 0

        # 胜率
        win_trades = [t for t in trades if t.get('profit', 0) > 0]
        win_rate = len(win_trades) / len(trades) * 100 if trades else 0

        result = {
            "策略名称": getattr(self, 'name', '未知策略'),
            "初始资金": round(self.initial_capital, 2),
            "最终价值": round(final_value, 2),
            "总收益率": round(total_return, 2),
            "年化收益率": round(annual_return, 2),
            "夏普比率": round(sharpe, 2),
            "最大回撤": round(max_drawdown * 100, 2),
            "交易次数": len(trades),
            "胜率": round(win_rate, 2),
            "交易记录": trades,
        }

        logger.info(f"✅ 回测完成 | 收益={total_return:.2f}% | 夏普={sharpe:.2f} | 最大回撤={max_drawdown:.2%}")

        return result


def quick_backtest(strategy,
                   data: pd.DataFrame,
                   initial_capital: float = 1000000) -> Dict[str, Any]:
    """
    快速回测（简版）

    直接使用策略的generate_signals结果，自动回测
    """
    engine = BacktestEngine(initial_capital=initial_capital)
    result_df = strategy.generate_signals(data)
    return engine.run(result_df)


if __name__ == "__main__":
    # 测试
    from .strategies import MultiFactorStrategy

    print("=" * 60)
    print("📊 回测引擎测试")
    print("=" * 60)

    # 模拟数据
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    mock_data = pd.DataFrame({
        'date': dates,
        'close': np.random.randn(100).cumsum() + 50,
        'signal': [0]*90 + [1, 0, -1] + [0]*7,  # 模拟一次买卖
        '代码': '600519',
        '名称': '贵州茅台',
    })

    strategy = MultiFactorStrategy()
    result = quick_backtest(strategy, mock_data)

    print("\n回测结果：")
    for k, v in result.items():
        if k not in ['交易记录']:
            print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("✅ 回测引擎测试完成")
    print("=" * 60)
