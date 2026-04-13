---
layout: null
title: Strategy Development Guide
---

# 策略开发指南

本文档说明如何开发自定义选股策略。

---

## 📖 策略基类

所有策略继承自 `BaseStrategy`（位于 `core/strategies.py`）：

```python
from core.strategies import BaseStrategy

class MyStrategy(BaseStrategy):
    name = "my_strategy"
    description = "我的自定义策略"

    def generate_signals(self, df):
        """
        输入：包含所有因子的DataFrame
        输出：添加了信号列的DataFrame
        """
        # 你的策略逻辑
        df['signal'] = ...
        return df

    def select_stocks(self, df, top_n=10):
        """
        从信号DataFrame中筛选top_n只股票
        """
        df = df.sort_values('signal', ascending=False)
        return df.head(top_n)
```

---

## 🎯 内置策略

### 1. 多因子策略 (MultiFactorStrategy)

**权重配置**（`config/strategies.yaml`）：
```yaml
multi_factor:
  weights:
    valuation: 0.40    # 估值分权重
    profitability: 0.30  # 盈利分权重
    scale: 0.30        # 规模分权重
  filters:
    min_score: 60      # 最低总分
    min_market_cap: 50 # 最低市值（亿元）
    max_pe: 100        # 最高PE
```

**计算方式**：
```
估值分 = 归一化(PE) + 归一化(PB) + 规模分
盈利分 = ROE得分 + 营收增长得分 + 利润增长得分
规模分 = 总市值排名（越大越好）
综合分 = 估值分×40% + 盈利分×30% + 规模分×30%
```

### 2. 低PE价值策略 (PEStrategy)

**筛选条件**：
```python
PE < 20 AND ROE > 15% AND 营收增长率 > 5%
```

**适用场景**：寻找低估值的蓝筹股。

### 3. 三维评分策略 (ThreeDimensionalStrategy)

**权重配置**：
```yaml
three_dimensional:
  weights:
    fundamental: 0.40  # 基本面
    technical: 0.35    # 技术面
    sentiment: 0.25    # 情绪面
```

**数据需求**：
- 基本面：PE、PB、ROE（来自Baostock）
- 技术面：MA、MACD、RSI（来自`indicators.py`）
- 情绪面：Tavily新闻评分（需配置API Key）

---

## 🔧 开发自定义策略

### 步骤1：创建策略类

在 `core/strategies.py` 中添加：

```python
class MyCustomStrategy(BaseStrategy):
    name = "my_custom"
    description = "我的自定义策略描述"

    def generate_signals(self, df):
        # 输入df包含以下字段（示例）：
        # code, name, PE, PB, ROE, revenue_growth, profit_growth, close, market_cap

        # 示例：修改PE筛选 + 动量因子
        df['valuation_score'] = self._calc_valuation(df)
        df['momentum_score'] = self._calc_momentum(df)
        df['signal'] = df['valuation_score'] * 0.6 + df['momentum_score'] * 0.4

        return df

    def _calc_valuation(self, df):
        # PE/PB归一化（越小越好）
        pe_rank = (df['PE'] < 30).astype(int)  # PE<30得1分
        pb_rank = (df['PB'] < 2).astype(int)   # PB<2得1分
        return pe_rank + pb_rank

    def _calc_momentum(self, df):
        # 20日收益率
        return df['close'].pct_change(20)
```

### 步骤2：注册策略

在 `strategies.py` 底部 `get_strategy()` 函数中添加：

```python
def get_strategy(name: str, **kwargs):
    strategies = {
        "multi_factor": MultiFactorStrategy,
        "pe": PEStrategy,
        "three_d": ThreeDimensionalStrategy,
        "my_custom": MyCustomStrategy,  # 新增
    }
    return strategies[name]()
```

### 步骤3：添加配置

在 `config/strategies.yaml` 中：

```yaml
my_custom:
  param1: value1
  param2: value2
```

### 步骤4：运行测试

```bash
python cli/picker_cli.py --strategy my_custom --sample
```

---

## 📊 因子归一化

策略中常用的归一化方法（`core/scorer.py`）：

```python
def min_max_normalize(series, reverse=False):
    """
    Min-Max归一化到0-1
    reverse=True: 越小越好（如PE）
    reverse=False: 越大越好（如ROE）
    """
    if reverse:
        return (series.max() - series) / (series.max() - series.min())
    else:
        return (series - series.min()) / (series.max() - series.min())
```

---

## 🔍 调试技巧

### 查看中间数据
```python
# 在generate_signals中添加
print(df[['code', 'name', 'PE', 'signal']].head(10))
```

### 保存中间结果
```python
df.to_csv('debug_signals.csv', index=False, encoding='utf-8-sig')
```

### 使用集成测试
```bash
python tests/integration_test.py
```

---

## 📈 性能优化

1. **向量化计算**：使用pandas向量操作，避免循环
2. **缓存因子**：`cache_manager.py` 自动缓存查询结果
3. **分批处理**：大数据集使用 `df.groupby()` 分组计算
4. **并行化**：查询阶段已优化，策略计算通常很快

---

## 🧪 回测验证

新策略开发完成后，建议使用 `core/backtest.py` 进行历史回测：

```python
from core.backtest import AShareBacktest

bt = AShareBacktest(
    initial_capital=1000000,
    commission=0.0003,
    stamp_tax=0.001
)
results = bt.run(df, signals)
bt.print_stats()
bt.plot_equity_curve()
```

---

## 📝 提交规范

提交新策略时，请更新：
1. `core/strategies.py` - 策略类
2. `config/strategies.yaml` - 策略配置
3. `README.md` - 说明新策略
4. `CHANGELOG.md` - 记录版本变更

---

**祝开发愉快！** 🎉
