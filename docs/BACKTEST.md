# 回测引擎使用指南

`core/backtest.py` 提供A股规则下的回测功能，支持印花税、手续费和T+1交易限制。

---

## 🎯 快速开始

```python
from core.backtest import AShareBacktest

# 1. 初始化回测引擎
bt = AShareBacktest(
    initial_capital=1000000,   # 初始资金100万
    commission=0.0003,         # 手续费0.03%（万3）
    stamp_tax=0.001,           # 印花税0.1%（卖出收）
    min_trade_unit=100,        # 最小交易单位（A股100股/手）
    max_position=0.30          # 单股最大仓位30%
)

# 2. 运行回测
results = bt.run(df, signals)

# 3. 查看结果
bt.print_stats()
bt.plot_equity_curve()
```

---

## 📊 参数说明

### 构造函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `initial_capital` | float | 1,000,000 | 初始资金（元） |
| `commission` | float | 0.0003 | 手续费率（买入+卖出） |
| `stamp_tax` | float | 0.001 | 印花税率（仅卖出） |
| `min_trade_unit` | int | 100 | 最小交易单位（股） |
| `max_position` | float | 0.10 | 单股最大仓位比例 |

### A股特有规则

1. **T+1交易**：当日买入的股票，下一交易日才能卖出
2. **印花税**：仅卖出时收取（0.1%）
3. **手数单位**：必须为100股的整数倍

---

## 📥 输入数据

### df（股票数据DataFrame）
必须包含以下字段：
```python
df.columns = ['code', 'name', 'date', 'open', 'high', 'low', 'close', 'volume']
```

### signals（交易信号DataFrame）
```python
signals.columns = ['code', 'date', 'signal']
# signal: 1=买入, -1=卖出, 0=持有
```

---

## 📈 输出结果

`bt.run()` 返回字典：

```python
{
    'initial_capital': 1000000.0,
    'final_value': 1250000.0,
    'total_return': 0.25,           # 总收益率25%
    'annual_return': 0.15,          # 年化收益率
    'max_drawdown': -0.12,          # 最大回撤-12%
    'sharpe_ratio': 1.35,           # 夏普比率
    'win_rate': 0.58,               # 胜率58%
    'trade_count': 45,              # 交易次数
    'equity_curve': pd.DataFrame(), # 每日净值曲线
    'positions': pd.DataFrame()     # 持仓记录
}
```

---

## 🧮 回测流程

```
1. 初始化账户（现金、持仓、交易记录）
2. 遍历每个交易日：
   a. 检查是否有交易信号
   b. 买入：计算可买数量（手数）→ 扣款 → 记录持仓
   c. 卖出：检查T+1限制 → 计算卖出金额 → 加款
   d. 计算当日净值
3. 生成统计报告
```

---

## 🔍 示例：完整回测流程

```python
import pandas as pd
from core.backtest import AShareBacktest
from core.strategies import get_strategy

# 1. 获取数据（假设已有历史数据df）
df = pd.read_csv('historical_data.csv')

# 2. 生成策略信号
strategy = get_strategy('multi_factor')
df_with_signals = strategy.generate_signals(df)

# 3. 提取信号
signals = df_with_signals[['code', 'date', 'signal']].copy()

# 4. 运行回测
bt = AShareBacktest(
    initial_capital=1000000,
    commission=0.0003,
    stamp_tax=0.001
)
results = bt.run(df, signals)

# 5. 输出结果
print(f"初始资金: {results['initial_capital']:,.2f}")
print(f"最终净值: {results['final_value']:,.2f}")
print(f"总收益率: {results['total_return']*100:.2f}%")
print(f"最大回撤: {results['max_drawdown']*100:.2f}%")
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
print(f"胜率: {results['win_rate']*100:.2f}%")

# 6. 绘制净值曲线
bt.plot_equity_curve()
```

---

## ⚠️ 注意事项

1. **数据完整性**：确保df包含完整的OHLCV数据
2. **信号频率**：建议每日生成一次信号，避免高频交易
3. **滑点**：当前未考虑滑点，实际交易需额外扣除
4. **流动性**：未考虑涨跌停限制，实际交易需检查
5. **费用模型**：可根据券商费率调整`commission`和`stamp_tax`

---

## 📈 性能指标说明

| 指标 | 公式 | 说明 |
|------|------|------|
| 总收益率 | (最终净值-初始资金)/初始资金 | 不考虑时间价值 |
| 年化收益率 | (1+总收益率)^(252/交易日数)-1 | 252个交易日/年 |
| 最大回撤 | min(净值/历史最大值-1) | 衡量风险 |
| 夏普比率 | (收益均值-无风险)/收益标准差 | 风险调整后收益 |
| 胜率 | 盈利交易次数/总交易次数 | >50%为佳 |

---

## 🛠️ 高级功能

### 自定义手续费
```python
bt = AShareBacktest(
    commission=0.0005,      # 万5（较高）
    stamp_tax=0.001,
    ...
)
```

### 限制单股仓位
```python
bt = AShareBacktest(
    max_position=0.20,      # 单股不超过20%
    ...
)
```

### 导出交易记录
```python
bt.positions.to_csv('backtest_positions.csv', index=False, encoding='utf-8-sig')
bt.equity_curve.to_csv('backtest_equity.csv', index=False, encoding='utf-8-sig')
```

---

## 📚 API 参考

### AShareBacktest类

#### `__init__(initial_capital, commission, stamp_tax, min_trade_unit, max_position)`
初始化回测引擎。

#### `run(df, signals)`
运行回测，返回结果字典。

#### `print_stats()`
打印统计报告到控制台。

#### `plot_equity_curve()`
绘制净值曲线图（需matplotlib）。

---

**提示**：回测结果仅供参考，实际市场表现可能不同。建议：
1. 先用历史数据验证策略稳定性
2. 使用多周期（牛市/熊市/震荡市）测试
3. 结合基本面分析综合判断
