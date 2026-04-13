#!/usr/bin/env python3
"""
策略库 - A股智能选股（合并版）
包含：多因子策略、PE价值策略、三维评分策略

整合来源：
- finance-ai-project/src/strategies.py (多因子 + PE策略)
- ai-stock-picker/stock_picker/scorer.py (三维评分)

Author: Simon (with AI Agent)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

from .scorer import calculate_comprehensive_score, score_fundamental, score_technical, score_sentiment

logger = logging.getLogger(__name__)


# ============== 策略基类 ==============

class BaseStrategy(ABC):
    """策略基类 - 所有策略必须继承此类"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """生成交易信号（1=买入，-1=卖出，0=持有）"""
        pass

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算策略所需指标"""
        pass

    def select_stocks(self, data: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
        """
        筛选股票（通用方法）

        Args:
            data: 包含评分的数据
            top_n: 选择前N只

        Returns:
            筛选后的股票列表
        """
        if '总分' in data.columns:
            ranked = data.sort_values('总分', ascending=False).head(top_n)
        elif 'total_score' in data.columns:
            ranked = data.sort_values('total_score', ascending=False).head(top_n)
        else:
            ranked = data.head(top_n)

        return ranked


# ============== 多因子策略（来自 finance-ai-project） ==============

class MultiFactorStrategy(BaseStrategy):
    """
    A股多因子模型策略
    因子：估值 + 盈利 + 规模 + 动量
    权重：估值40% + 盈利30% + 规模30%（动量可选）
    """

    def __init__(self,
                 pe_weight: float = -0.3,      # PE越低越好（负权重）
                 roe_weight: float = 0.4,      # ROE越高越好
                 growth_weight: float = 0.3,   # 成长性
                 momentum_weight: float = 0.2, # 动量
                 min_score: float = 60,        # 最低综合得分
                 min_market_cap: float = 50):  # 最小市值50亿
        super().__init__(
            name="A股多因子策略",
            description=f"综合{abs(pe_weight)*100:.0f}%估值+{roe_weight*100:.0f}%盈利+{growth_weight*100:.0f}%成长+{momentum_weight*100:.0f}%动量"
        )
        self.pe_weight = pe_weight
        self.roe_weight = roe_weight
        self.growth_weight = growth_weight
        self.momentum_weight = momentum_weight
        self.min_score = min_score
        self.min_market_cap = min_market_cap  # 单位：亿元

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算多因子所需指标"""
        df = data.copy()

        # 1. 估值因子（PE倒数，越小越好）
        df['pe_score'] = 1 / df['PE'].clip(lower=0.1)

        # 2. 盈利因子（ROE，越高越好）
        df['roe_score'] = df['ROE']

        # 3. 成长因子（营收增长率，越高越好）
        df['growth_score'] = df['营收增长率']

        # 4. 动量因子（20日涨幅，适中）
        if 'momentum_20d' not in df.columns:
            df['momentum_score'] = 0
        else:
            df['momentum_score'] = df['momentum_20d'].clip(-10, 20)

        return df

    def generate_signals(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        生成多因子买入信号

        步骤：
        1. 计算各因子得分
        2. 归一化到0-100
        3. 加权求和得到综合分
        4. 筛选：综合分>=min_score，市值>=50亿，PE>0，非ST
        """
        logger.info(f"生成多因子信号: {self.name}")

        df = self.calculate_indicators(data)

        # 归一化（去极值）
        for col in ['pe_score', 'roe_score', 'growth_score', 'momentum_score']:
            if col in df.columns:
                min_val = df[col].quantile(0.05)
                max_val = df[col].quantile(0.95)
                df[f'{col}_norm'] = ((df[col] - min_val) / (max_val - min_val + 1e-8) * 100).clip(0, 100)

        # 加权综合得分
        df['total_score'] = (
            df.get('pe_score_norm', 0) * abs(self.pe_weight) * 100 +
            df.get('roe_score_norm', 0) * self.roe_weight * 100 +
            df.get('growth_score_norm', 0) * self.growth_weight * 100 +
            df.get('momentum_score_norm', 0) * self.momentum_weight * 100
        )

        # 筛选条件
        cond_score = df['total_score'] >= self.min_score
        cond_marketcap = df['总市值'] >= self.min_market_cap * 100000000  # 亿元→元
        cond_pe = df['PE'] > 0
        cond_no_st = ~df['名称'].str.contains('ST|退市', na=False)

        df['signal'] = 0
        df.loc[cond_score & cond_marketcap & cond_pe & cond_no_st, 'signal'] = 1

        buy_count = (df['signal'] == 1).sum()
        logger.info(f"✅ 多因子筛选出 {buy_count} 只A股符合条件")

        return df


# ============== PE价值策略（来自 finance-ai-project） ==============

class PEStrategy(BaseStrategy):
    """低PE选股策略 - 基本面策略"""

    def __init__(self,
                 pe_threshold: float = 20,
                 roe_threshold: float = 15,
                 revenue_growth: float = 5,
                 min_market_cap: float = 10):
        super().__init__(
            name="低PE价值策略",
            description=f"PE<{pe_threshold} + ROE>{roe_threshold}% + 营收增长>{revenue_growth}%"
        )
        self.pe_threshold = pe_threshold
        self.roe_threshold = roe_threshold
        self.revenue_growth = revenue_growth
        self.min_market_cap = min_market_cap

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算指标（PE、ROE等已在数据中）"""
        return data

    def generate_signals(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df = data.copy()

        cond_pe = df['PE'] < self.pe_threshold
        cond_roe = df['ROE'] > self.roe_threshold
        cond_growth = df['营收增长率'] > self.revenue_growth
        cond_marketcap = df['总市值'] > self.min_market_cap * 100000000

        buy_cond = cond_pe & cond_roe & cond_growth & cond_marketcap

        df['signal'] = 0
        df.loc[buy_cond, 'signal'] = 1

        buy_count = buy_cond.sum()
        logger.info(f"✅ PE策略筛选出 {buy_count} 只股票")

        return df


# ============== 三维评分策略（来自 ai-stock-picker） ==============

class ThreeDimensionalStrategy(BaseStrategy):
    """
    三维评分策略：基本面 + 技术面 + 情绪面
    适合：综合选股，兼顾价值、时机、热度
    """

    def __init__(self,
                 strategy: str = "moderate",
                 weights: Optional[Dict[str, float]] = None):
        super().__init__(
            name="三维评分策略",
            description=f"基本面40% + 技术面35% + 情绪面25% ({strategy})"
        )
        self.strategy = strategy
        self.weights = weights or {
            "fundamental": 0.40,
            "technical": 0.35,
            "sentiment": 0.25,
        }

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算三维评分

        需要的数据：
        - financials: PE, ROE, 营收增长, 利润增长
        - price_data: 价格序列（用于技术指标）
        - sentiment: 情绪数据字典
        """
        df = data.copy()

        # 计算各维度分（已在 scorer.py 实现，此处调用）
        # 实际计算在 generate_signals 中逐行处理
        return df

    def generate_signals(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        为每只股票计算三维评分并生成信号

        输入数据需包含：
        - financials 列（字典类型，含 pe_ratio, roe, revenue_growth, profit_growth）
        - price_data 列（DataFrame 类型，历史行情）
        - sentiment 列（字典类型，含 score, news_count）
        """
        logger.info(f"生成三维评分信号: {self.name}")

        df = data.copy()

        # 逐行计算评分
        scores = []
        for idx, row in df.iterrows():
            financials = row.get('financials') if 'financials' in row else None
            price_data = row.get('price_data') if 'price_data' in row else None
            sentiment = row.get('sentiment') if 'sentiment' in row else {}

            score_result = calculate_comprehensive_score(
                financials,
                price_data,
                sentiment,
                strategy=self.strategy
            )
            scores.append(score_result)

        # 将评分展开到DataFrame
        score_df = pd.DataFrame(scores)
        df = pd.concat([df, score_df], axis=1)

        # 筛选：综合分 >= 60，非ST，PE > 0
        cond_score = df['总分'] >= 60
        cond_pe = df['PE'] > 0 if 'PE' in df.columns else True
        cond_no_st = ~df['名称'].str.contains('ST|退市', na=False) if '名称' in df.columns else True

        df['signal'] = 0
        df.loc[cond_score & cond_pe & cond_no_st, 'signal'] = 1

        buy_count = (df['signal'] == 1).sum()
        logger.info(f"✅ 三维评分筛选出 {buy_count} 只股票")

        return df


# ============== 策略工厂 ==============

STRATEGY_REGISTRY = {
    "multi_factor": MultiFactorStrategy,
    "pe_value": PEStrategy,
    "three_dimensional": ThreeDimensionalStrategy,
}


def get_strategy(name: str, **kwargs) -> BaseStrategy:
    """
    获取策略实例

    Args:
        name: 策略名称 ("multi_factor" / "pe_value" / "three_dimensional")
        **kwargs: 策略参数

    Returns:
        BaseStrategy 实例
    """
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"未知策略: {name}。可选: {list(STRATEGY_REGISTRY.keys())}")

    return STRATEGY_REGISTRY[name](**kwargs)


def list_strategies() -> Dict[str, str]:
    """列出所有可用策略"""
    return {
        name: cls().description
        for name, cls in STRATEGY_REGISTRY.items()
    }


# ============== 测试 ==============

if __name__ == "__main__":
    print("=" * 60)
    print("📊 策略库测试")
    print("=" * 60)

    # 列出策略
    print("\n可用策略：")
    for name, desc in list_strategies().items():
        print(f"  - {name}: {desc}")

    # 测试多因子策略
    print("\n【测试】多因子策略")
    mf = get_strategy("multi_factor")
    mock_data = pd.DataFrame({
        '代码': ['600519', '000858'],
        '名称': ['贵州茅台', '五粮液'],
        'PE': [25.5, 18.2],
        'ROE': [32.1, 28.5],
        '营收增长率': [12.3, 15.6],
        '总市值': [22000, 6500],
        'momentum_20d': [2.5, 5.2]
    })
    result = mf.generate_signals(mock_data)
    print(result[['代码', '名称', 'total_score', 'signal']])

    print("\n" + "=" * 60)
    print("✅ 策略库测试完成")
    print("=" * 60)
