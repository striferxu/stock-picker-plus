# 🏷️ 股票数据获取模块

核心数据获取层，基于 Baostock 实现 A 股数据查询。

---

## 📦 模块结构

```
core/
├── data_fetcher.py    # 数据获取（Baostock封装）
├── indicators.py      # 技术指标计算
├── cache_manager.py   # 缓存管理
└── ...
```

---

## 🔧 核心类

### `DataFetcher`

统一数据获取接口，支持：
- 单只股票日线行情
- 全市场股票列表
- 估值数据（PE/PB）
- 财务数据（ROE、营收增长等）

---

## 📊 主要函数

### `get_stock_daily(symbol, days)`

获取单只股票日K线数据。

**参数**:
- `symbol`: 股票代码（如 `"600519"` 或 `"sh.600519"`）
- `days`: 最近N天（默认30天）

**返回**: `pd.DataFrame`（开盘、收盘、最高、最低、成交量等）

**示例**:
```python
fetcher = DataFetcher()
df = fetcher.get_stock_daily("600519", days=10)
print(df[['date', 'open', 'close', 'volume']])
```

---

### `get_stock_basic()`

获取全A股股票基本信息（代码、名称、PE、PB等）。

**返回**: `pd.DataFrame`

**示例**:
```python
basic_df = fetcher.get_stock_basic()
print(f"共 {len(basic_df)} 只股票")
print(basic_df[['code', 'name', 'PE', 'PB']].head())
```

---

### `fetch_batch(codes, fields, use_cache)`

批量查询多只股票数据（多线程优化）。

**参数**:
- `codes`: 股票代码列表
- `fields`: 所需字段（`['basic', 'valuation', 'financials']`）
- `use_cache`: 是否使用缓存

**返回**: `pd.DataFrame`（合并后的数据）

---

## 🗃️ 数据字段说明

返回的DataFrame包含以下字段：

| 字段 | 说明 | 来源 |
|------|------|------|
| `code` | 股票代码（sh.600519） | 基本信息 |
| `名称` / `name` | 公司名称 | 基本信息 |
| `PE` / `pe_ratio` | 市盈率（TTM） | 估值数据 |
| `PB` / `pb_ratio` | 市净率 | 估值数据 |
| `ROE` | 净资产收益率（%） | 财务数据 |
| `营收增长率` | 营收同比增长（%） | 财务数据 |
| `利润增长率` | 净利润同比增长（%） | 财务数据 |
| `收盘价` / `close` | 最新收盘价 | 日线数据 |

---

## ⚡ 性能优化

### 缓存机制

`CacheManager` 提供两级缓存：
- **内存缓存**：进程内快速读取
- **文件缓存**：按日期持久化（`.pkl`格式）

**缓存命中**：
- 同一日内重复查询 → 直接读缓存（毫秒级）
- 跨日 → 自动失效，重新查询

**示例**:
```python
from core.cache_manager import CacheManager
cache = CacheManager()

# 尝试读取缓存
cached = cache.get_stock_list_cache()
if cached is not None:
    stock_list = cached
else:
    stock_list = fetcher.get_stock_basic()
    cache.set_stock_list_cache(stock_list)
```

### 多线程批量查询

`fetch_batch()` 内部使用 `ThreadPoolExecutor`（默认10并发）：
- 查询200只股票 → 约20秒（原需200秒）
- 查询8687只股票 → 约15分钟（原需数小时）

---

## 🚨 错误处理

所有数据查询均包含异常捕获，失败返回空DataFrame并记录日志。

**日志级别**:
- `INFO`: 成功获取数据
- `WARNING`: 单只股票查询失败（继续下一只）
- `ERROR`: 批量查询整体失败

查看日志：`tail -f logs/auto_daily.log`

---

## 🔄 数据更新策略

### 盘中实时数据

日线数据为 T+1 格式（当日收盘后更新）：
- 更新时间：15:30 - 次日09:00
- 盘中查询可能返回昨日数据

### 缓存清理

自动清理7天前的旧缓存：
```bash
# 手动清理
python -c "from core.cache_manager import CacheManager; CacheManager().clear(older_than_days=7)"
```

---

## 📈 数据源对比

| 数据源 | 状态 | 优点 | 缺点 |
|--------|------|------|------|
| Baostock | ✅ 主用 | 免费、稳定、财务数据全 | 频率限制（~300ms/次） |
| AKShare | ⚠️ 废弃 | A股接口丰富 | 不稳定，常超时 |
| Tushare | ⚠️ 备用 | 数据质量高 | 需token，有配额 |

---

## 🧪 测试

运行数据模块测试：
```bash
python src/data_fetcher.py
```

预期输出：
```
✅ Baostock登录成功
✅ 全市场: 8687 只股票
✅ 股票列表获取成功
...
```

---

## 🔗 依赖模块

- `core/strategies.py` - 策略计算依赖数据字段
- `core/indicators.py` - 技术指标依赖日线数据
- `output/excel_writer.py` - Excel导出依赖DataFrame结构

---

## 📝 注意事项

1. **Baostock 登录**：首次调用会自动登录，无需手动操作
2. **网络要求**：需要稳定的互联网连接（Baostock 服务器在国内）
3. **数据延迟**：日线数据为 T+1，非实时
4. **频率限制**：避免高频重复查询（建议使用缓存）
5. **字段兼容**：部分函数返回字段名可能不一致（如 `peTTM` vs `PE`），模块内部已做映射

---

*最后更新: 2026-04-13*
*维护者: Simon (with AI Agent)*
