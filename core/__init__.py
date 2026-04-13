# 核心模块统一导出

from .data_fetcher import (
    get_stock_basic,
    get_stock_daily,
    get_financials_baostock,
    fetch_batch,
    get_index_components,
    init_data_fetcher,
    cleanup_data_fetcher,
)

from .scorer import (
    calculate_comprehensive_score,
    score_fundamental,
    score_technical,
    score_sentiment,
    calculate综合评分,
)

from .strategies import (
    BaseStrategy,
    MultiFactorStrategy,
    PEStrategy,
    ThreeDimensionalStrategy,
    get_strategy,
    list_strategies,
    STRATEGY_REGISTRY,
)

from .backtest import BacktestEngine, quick_backtest

from .indicators import (
    add_all_indicators,
    calculate_momentum,
    check_ma_alignment,
    check_macd_crossover,
)

from .cache_manager import CacheManager

from .engine import StockPickerEngine, run_quick_scan, run_full_scan

__all__ = [
    # Data Fetcher
    'get_stock_basic',
    'get_stock_daily',
    'get_financials_baostock',
    'fetch_batch',
    'get_index_components',
    'init_data_fetcher',
    'cleanup_data_fetcher',

    # Scorer
    'calculate_comprehensive_score',
    'score_fundamental',
    'score_technical',
    'score_sentiment',
    'calculate综合评分',

    # Strategies
    'BaseStrategy',
    'MultiFactorStrategy',
    'PEStrategy',
    'ThreeDimensionalStrategy',
    'get_strategy',
    'list_strategies',
    'STRATEGY_REGISTRY',

    # Backtest
    'BacktestEngine',
    'quick_backtest',

    # Indicators
    'add_all_indicators',
    'calculate_momentum',
    'check_ma_alignment',
    'check_macd_crossover',

    # Cache
    'CacheManager',

    # Engine
    'StockPickerEngine',
    'run_quick_scan',
    'run_full_scan',
]
