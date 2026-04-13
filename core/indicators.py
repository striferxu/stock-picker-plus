#!/usr/bin/env python3
"""
技术指标计算模块 - A股专版
整合自 finance-ai-project/src/indicators.py

使用 ta 库计算常用技术指标
"""

import pandas as pd
import numpy as np
import ta  # pip install ta
from typing import Dict, Any

logger = logging.getLogger(__name__)


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    为DataFrame添加所有常用技术指标

    Args:
        df: 需包含列 ['open', 'high', 'low', 'close', 'volume']

    Returns:
        添加了技术指标的DataFrame
    """
    df = df.copy()

    # 价格和成交量
    close = df['close'] if 'close' in df.columns else df['收盘']
    high = df['high'] if 'high' in df.columns else df['最高']
    low = df['low'] if 'low' in df.columns else df['最低']
    volume = df['volume'] if 'volume' in df.columns else df['成交量']

    # --- 趋势指标 ---
    # SMA均线
    df['ma5'] = ta.trend.sma_indicator(close, window=5)
    df['ma10'] = ta.trend.sma_indicator(close, window=10)
    df['ma20'] = ta.trend.sma_indicator(close, window=20)
    df['ma60'] = ta.trend.sma_indicator(close, window=60)

    # EMA指数均线
    df['ema12'] = ta.trend.ema_indicator(close, window=12)
    df['ema26'] = ta.trend.ema_indicator(close, window=26)

    # --- 震荡指标 ---
    # RSI相对强弱指数
    df['rsi_14'] = ta.momentum.rsi(close, window=14)

    # MACD
    macd = ta.trend.MACD(close)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()

    # KDJ（ stochastic）
    stoch = ta.momentum.StochasticOscillator(high, low, close)
    df['k'] = stoch.stoch()
    df['d'] = stoch.stoch_signal()
    df['j'] = 3 * df['k'] - 2 * df['d']

    # --- 波动率 ---
    # Bollinger Bands 布林带
    bollinger = ta.volatility.BollingerBands(close)
    df['bb_upper'] = bollinger.bollinger_hband()
    df['bb_middle'] = bollinger.bollinger_mband()
    df['bb_lower'] = bollinger.bollinger_lband()
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

    # ATR平均真实波幅
    df['atr_14'] = ta.volatility.average_true_range(high, low, close, window=14)

    # --- 成交量 ---
    # OBV能量潮
    df['obv'] = ta.volume.on_balance_volume(close, volume)

    # 成交量均线
    df['volume_ma5'] = ta.volume.volume_sma_indicator(volume, window=5)
    df['volume_ma20'] = ta.volume.volume_sma_indicator(volume, window=20)

    # --- 其他 ---
    # 价格变动百分比
    df['returns'] = close.pct_change()
    df['returns_5d'] = close.pct_change(5)

    return df


def calculate_momentum(df: pd.DataFrame, windows: list = [5, 10, 20]) -> Dict[str, float]:
    """
    计算动量指标（多周期涨幅）

    Returns:
        {'momentum_5d': 2.5, 'momentum_20d': 5.2, ...}
    """
    close = df['close'] if 'close' in df.columns else df['收盘']
    momentum = {}

    for w in windows:
        if len(close) > w:
            ret = (close.iloc[-1] / close.iloc[-w-1] - 1) * 100
            momentum[f'momentum_{w}d'] = round(ret, 2)
        else:
            momentum[f'momentum_{w}d'] = 0

    return momentum


def check_ma_alignment(df: pd.DataFrame) -> Dict[str, Any]:
    """
    检查均线多头排列状态

    Returns:
        {
            'is_bullish': True/False,
            'alignment': '多头排列' / '空头排列' / '混乱',
            'strength': 0-100  # 排列强度
        }
    """
    if len(df) < 60:
        return {"is_bullish": False, "alignment": "数据不足", "strength": 0}

    ma5 = df['ma5'].iloc[-1] if 'ma5' in df.columns else ta.trend.sma_indicator(df['close'], 5).iloc[-1]
    ma20 = df['ma20'].iloc[-1] if 'ma20' in df.columns else ta.trend.sma_indicator(df['close'], 20).iloc[-1]
    ma60 = df['ma60'].iloc[-1] if 'ma60' in df.columns else ta.trend.sma_indicator(df['close'], 60).iloc[-1]

    # 多头排列：MA5 > MA20 > MA60 且价格>MA5
    close = df['close'].iloc[-1]
    bullish = (close > ma5) and (ma5 > ma20) and (ma20 > ma60)

    # 空头排列：MA5 < MA20 < MA60 且价格<MA5
    bearish = (close < ma5) and (ma5 < ma20) and (ma20 < ma60)

    if bullish:
        alignment = "多头排列"
        strength = min(100, (close / ma60 - 1) * 100 * 2)  # 相对60线涨幅
    elif bearish:
        alignment = "空头排列"
        strength = min(100, (ma60 / close - 1) * 100 * 2)
    else:
        alignment = "混乱"
        strength = 50

    return {
        "is_bullish": bullish,
        "alignment": alignment,
        "strength": round(strength, 1)
    }


def check_macd_crossover(df: pd.DataFrame) -> Dict[str, Any]:
    """
    检查MACD金叉/死叉

    Returns:
        {'signal': 'golden'/'death'/'none', 'strength': 0-100}
    """
    if len(df) < 2 or 'macd' not in df.columns or 'macd_signal' not in df.columns:
        return {"signal": "none", "strength": 0}

    macd = df['macd'].iloc[-2:]
    signal = df['macd_signal'].iloc[-2:]

    # 金叉：MACD上穿信号线
    if macd.iloc[0] <= signal.iloc[0] and macd.iloc[1] > signal.iloc[1]:
        strength = min(100, abs(macd.iloc[1] - signal.iloc[1]) * 100)
        return {"signal": "golden", "strength": round(strength, 1)}

    # 死叉：MACD下穿信号线
    elif macd.iloc[0] >= signal.iloc[0] and macd.iloc[1] < signal.iloc[1]:
        strength = min(100, abs(macd.iloc[1] - signal.iloc[1]) * 100)
        return {"signal": "death", "strength": round(strength, 1)}

    else:
        return {"signal": "none", "strength": 0}


# 为兼容性，保留旧函数名
calculate_technical_indicators = add_all_indicators


if __name__ == "__main__":
    # 测试
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    print("=" * 60)
    print("📊 技术指标模块测试")
    print("=" * 60)

    # 生成测试数据
    dates = pd.date_range("2026-01-01", periods=100, freq="B")
    close = 50 + np.random.randn(100).cumsum()
    high = close * 1.02
    low = close * 0.98
    volume = np.random.randint(1000, 10000, 100)

    df = pd.DataFrame({
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    })

    print("\n原始数据：")
    print(df.head())

    # 计算指标
    df_with_indicators = add_all_indicators(df)
    print("\n指标列：")
    print(df_with_indicators.columns.tolist())

    # 检查均线排列
    alignment = check_ma_alignment(df_with_indicators)
    print(f"\n均线状态: {alignment}")

    # 检查MACD
    macd_signal = check_macd_crossover(df_with_indicators)
    print(f"MACD信号: {macd_signal}")

    # 计算动量
    momentum = calculate_momentum(df_with_indicators)
    print(f"动量: {momentum}")

    print("\n" + "=" * 60)
    print("✅ 技术指标模块测试完成")
    print("=" * 60)
