#!/usr/bin/env python3
"""
综合评分算法 - A股专版（三维评分：基本面+技术面+情绪面）
整合自 ai-stock-picker/scorer.py

Author: Simon (with AI Agent)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .indicators import calculate_technical_indicators

# 评分权重配置（可调整）
SCORING_WEIGHTS = {
    "fundamental": 0.40,   # 基本面 40%
    "technical": 0.35,     # 技术面 35%
    "sentiment": 0.25,     # 情绪面 25%
}

# 策略参数（保守/平衡/激进）
STRATEGY_PARAMS = {
    "strict": {
        "pe_range": (0, 30),
        "roe_min": 12,
        "revenue_growth_min": 10,
        "profit_growth_min": 5,
    },
    "moderate": {
        "pe_range": (0, 50),
        "roe_min": 8,
        "revenue_growth_min": 5,
        "profit_growth_min": 0,
    },
    "loose": {
        "pe_range": (-50, 100),
        "roe_min": 3,
        "revenue_growth_min": 0,
        "profit_growth_min": -10,
    },
}


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """将数值归一化到 0~1"""
    if max_val == min_val:
        return 0.5
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def score_fundamental(financials: Optional[Dict[str, Any]], strategy: str = "moderate") -> float:
    """
    基本面评分（0~100）
    指标：PE、ROE、营收增长率、净利润增长率
    """
    if not financials:
        return 30.0  # 无数据给基础分

    params = STRATEGY_PARAMS[strategy]
    pe_min, pe_max = params["pe_range"]
    roe_min = params["roe_min"]
    rev_min = params["revenue_growth_min"]
    profit_min = params["profit_growth_min"]

    score = 0.0

    # 1. PE评分（越低越好）
    pe = financials.get("pe_ratio")
    if pe is not None and not np.isnan(pe):
        if pe_min <= pe <= pe_max:
            score += 25 * (1 - (pe - pe_min) / (pe_max - pe_min))
        elif pe < 0:  # 亏损
            # 若有高增长，给部分分
            if financials.get("revenue_growth", 0) > 0.2:
                score += 15
            else:
                score += 5
        # else PE超出上限，不加分

    # 2. ROE评分（越高越好）
    roe = financials.get("roe")
    if roe is not None and not np.isnan(roe):
        score += 25 * normalize_score(roe * 100, roe_min, 40)

    # 3. 营收增长评分
    rev_growth = financials.get("revenue_growth")
    if rev_growth is not None and not np.isnan(rev_growth):
        score += 25 * normalize_score(rev_growth * 100, rev_min, 50)

    # 4. 净利润增长评分
    profit_growth = financials.get("profit_growth")
    if profit_growth is not None and not np.isnan(profit_growth):
        score += 25 * normalize_score(profit_growth * 100, profit_min, 100)

    return min(100.0, max(0.0, score))


def score_technical(price_data: Optional[pd.DataFrame], strategy: str = "moderate") -> float:
    """
    技术面评分（0~100）
    指标：均线多头、MACD金叉、成交量放大
    """
    if price_data is None or price_data.empty or len(price_data) < 60:
        return 30.0

    try:
        close = price_data["Close"] if "Close" in price_data.columns else price_data["收盘"]
        vol_col = "Volume" if "Volume" in price_data.columns else "成交量"

        # 计算均线
        ma5 = close.rolling(window=5).mean()
        ma20 = close.rolling(window=20).mean()
        ma60 = close.rolling(window=60).mean()

        latest = close.iloc[-1]
        score = 0.0

        # 1. 均线多头排列（价格 > MA20 > MA60）
        if latest > ma20.iloc[-1] > ma60.iloc[-1]:
            score += 35
            alignment_strength = (latest / ma60.iloc[-1] - 1) * 10
            score += min(15, alignment_strength)
        elif latest > ma20.iloc[-1]:
            score += 15

        # 2. MACD金叉
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        if len(macd) >= 2:
            if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
                score += 25  # 金叉
            elif macd.iloc[-1] > signal.iloc[-1]:
                score += 15  # 正值但未金叉

        # 3. 成交量配合
        if vol_col in price_data.columns:
            avg_vol = price_data[vol_col].rolling(20).mean()
            current_vol = price_data[vol_col].iloc[-1]
            if avg_vol.iloc[-1] > 0 and current_vol > avg_vol.iloc[-1] * 1.2:
                score += 25  # 放大20%以上
            elif avg_vol.iloc[-1] > 0 and current_vol > avg_vol.iloc[-1]:
                score += 15  # 放量
            else:
                score += 5   # 不足

        return min(100.0, max(0.0, score))

    except Exception as e:
        return 30.0


def score_sentiment(sentiment_data: Dict[str, Any]) -> float:
    """
    情绪面评分（0~100）
    基于 Tavily 新闻情绪分析
    """
    if not sentiment_data or "error" in sentiment_data:
        return 50.0  # 无情绪数据给平均分

    base_score = sentiment_data.get("score", 0.5) * 100
    news_count = sentiment_data.get("news_count", 0)

    # 新闻数量加成（最多10分）
    count_bonus = min(10, news_count * 2)

    return min(100.0, max(0.0, base_score + count_bonus))


def calculate_comprehensive_score(
    financials: Optional[Dict[str, Any]],
    price_data: Optional[pd.DataFrame],
    sentiment_data: Dict[str, Any],
    strategy: str = "moderate"
) -> Dict[str, Any]:
    """
    计算综合评分（三维加权）

    Returns:
        {
            "总分": 75.5,
            "基本面": 80.0,
            "技术面": 70.0,
            "情绪面": 60.0,
            "评级": "🟢 推荐"
        }
    """
    fund_score = score_fundamental(financials, strategy)
    tech_score = score_technical(price_data, strategy)
    sent_score = score_sentiment(sentiment_data)

    total = (
        fund_score * SCORING_WEIGHTS["fundamental"] +
        tech_score * SCORING_WEIGHTS["technical"] +
        sent_score * SCORING_WEIGHTS["sentiment"]
    )

    # 评级
    if total >= 75:
        rating = "🟢 强烈推荐"
    elif total >= 60:
        rating = "🟢 推荐"
    elif total >= 45:
        rating = "🟡 观望"
    else:
        rating = "🔴 回避"

    return {
        "总分": round(total, 1),
        "基本面": round(fund_score, 1),
        "技术面": round(tech_score, 1),
        "情绪面": round(sent_score, 1),
        "评级": rating,
    }


# 为了兼容性，保留原名
calculate综合评分 = calculate_comprehensive_score
