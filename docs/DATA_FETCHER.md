---
layout: null
title: Data Fetcher Module - Baostock API
---

# 🏷️ 股票数据获取模块

核心数据获取层，基于 Baostock 实现 A 股数据查询。

---

## 📦 模块结构

```
core/
├── data_fetcher.py    # 主模块
├── cache_manager.py   # 缓存管理
└── indicators.py      # 技术指标
```

---

## 🚀 快速使用

```python
from core.data_fetcher import init_data_fetcher, get_stock_basic, fetch_batch

# 1. 初始化
init_data_fetcher()

# 2. 获取股票列表
basic_df = get_stock_basic()
print(f"Total stocks: {len(basic_df)}")

# 3. 批量查询
codes = basic_df['code'].head(100).tolist()
df = fetch_batch(codes)
print(df[['code', 'PE', 'PB']].head())
```

---

## 🔧 核心API

### `init_data_fetcher()`

初始化Baostock连接。

```python
def init_data_fetcher() -> bool:
    """登录Baostock，返回是否成功"""
```

### `get_stock_basic(use_cache=True)`

获取全市场股票基本信息。

**参数**：
- `use_cache` (bool): 是否使用缓存（默认True）

**返回**：pandas.DataFrame
- `code`: 股票代码（如 sh.600519）
- `name`: 股票名称
- `industry`: 所属行业
- `market`: 市场类型（主板/创业板/科创板）

**示例**：
```python
df = get_stock_basic()
print(df.head())
```

### `fetch_batch(codes, max_workers=10, use_cache=True)`

批量查询股票日线数据和财务指标。

**参数**：
- `codes`: 股票代码列表（6位数字或带市场前缀）
- `max_workers`: 并发线程数（默认10）
- `use_cache`: 是否使用缓存（默认True）

**返回**：DataFrame包含字段：
- `code`, `name`, `date`, `open`, `high`, `low`, `close`, `volume`
- `PE`, `PB`, `ROE`, `revenue_growth`, `profit_growth`
- `market_cap`（总市值）

**示例**：
```python
codes = ['600519', '000858', '002594']
df = fetch_batch(codes)
```

---

## 📊 数据字段说明

### 日线数据

| 字段 | 类型 | 说明 |
|------|------|------|
| code | str | 股票代码（sh.600519） |
| name | str | 股票名称 |
| date | str | 交易日期（YYYY-MM-DD） |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | int | 成交量（手） |

### 财务数据

| 字段 | 类型 | 说明 |
|------|------|------|
| PE | float | 市盈率（动态） |
| PB | float | 市净率 |
| ROE | float | 净资产收益率（%） |
| revenue_growth | float | 营收同比增长率（%） |
| profit_growth | float | 利润同比增长率（%） |
| market_cap | float | 总市值（亿元） |

---

## ⚙️ 配置选项

### 数据源开关

编辑 `config/data_sources.yaml`：

```yaml
baostock:
  enabled: true
  cache_days: 1
  max_workers: 10

akshare:
  enabled: false  # 已禁用
```

### 缓存设置

缓存文件保存在 `data/cache/` 目录：

```
data/cache/
├── stock_basic_20260413.pkl   # 股票列表
├── daily_20260413.pkl         # 日线数据
├── financial_20260413.pkl     # 财务数据
└── indicators_20260413.pkl    # 技术指标
```

缓存按日期自动失效，次日重新下载。

---

## 🔍 查询逻辑

### 获取股票列表

1. 检查缓存文件是否存在且有效（当天）
2. 若缓存有效，直接加载
3. 否则调用 `bs.query_stock_basic()` 获取全市场列表
4. 保存到缓存并返回

### 批量查询流程

```python
for code in codes:
    1. 查询日线数据 (query_history_k_data_plus)
    2. 查询PE/PB (query_profit_data)
    3. 查询ROE (query_growth_data)
    4. 合并为单行记录
    5. 保存到缓存
```

多线程优化：使用 `ThreadPoolExecutor` 并发查询，速度提升10倍。

---

## ⚠️ 注意事项

1. **频率限制**：Baostock 约 300ms/次，多线程仍需控制
2. **数据延迟**：T+1 数据，当日收盘后更新
3. **缓存位置**：`data/cache/` 自动创建，无需手动管理
4. **错误处理**：网络失败自动重试3次
5. **内存占用**：全市场数据约500MB，建议分批次查询

---

## 🐛 调试

### 启用日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 清除缓存

```bash
rm -rf data/cache/*
```

### 测试连接

```python
from core.data_fetcher import test_connection
success = test_connection()
print(f"Baostock连接: {'✅' if success else '❌'}")
```

---

## 📚 API参考

完整API请查看源代码：`core/data_fetcher.py`

**主要函数**：
- `init_data_fetcher()`
- `logout_data_fetcher()`
- `get_stock_basic(use_cache)`
- `fetch_batch(codes, max_workers, use_cache)`
- `get_stock_daily(code, start_date, end_date)`
- `get_pe_pb(code)`
- `get_financial_data(code)`

---

**下一步**：阅读 [策略开发指南](STRATEGIES.html) 了解如何使用获取的数据进行选股。
