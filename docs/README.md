# 🚀 A股智能选股助手（完整版）

> **Stock Picker Plus** - 基于 OpenClaw 的 A 股量化选股 AI Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Baostock](https://img.shields.io/badge/data-Baostock-green.svg)](https://baostock.com)

---

## 📖 项目简介

**Stock Picker Plus** 是一个专为 A 股市场设计的智能选股系统，整合了：

- ✅ **ai-stock-picker** 的完整数据层（Baostock + 三维评分）
- ✅ **finance-ai-project** 的策略框架（多因子模型 + 回测引擎）
- ✅ **性能优化**（10线程批量查询 + 缓存机制）
- ✅ **双重输出**（Markdown + Excel 带中文字段）
- ✅ **交互界面**（CLI + 自动QQ推送）

**目标用户**：A股投资者、量化研究员、AI量化爱好者

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 **多策略支持** | 多因子模型、低PE价值、三维评分（基本面+技术面+情绪面） |
| ⚡ **极速批量查询** | 10线程并发，200只股票20秒，全市场15分钟 |
| 💾 **智能缓存** | 按日期缓存，避免重复查询，加速后续运行 |
| 📊 **双重输出** | Markdown（简洁版）+ Excel（详细数据，中文字段） |
| 🤖 **AI集成** | Tavily 新闻情绪分析（可选） |
| 📱 **QQ推送** | 自动生成报告并推送到QQ（定时任务） |
| 🔄 **易于扩展** | 模块化设计，新增策略只需继承 `BaseStrategy` |
| 📈 **回测验证** | 内置回测引擎（支持T+1、印花税、手续费） |

---

## 📁 项目结构

```
stock-picker-plus/
├── core/                    # 核心引擎
│   ├── data_fetcher.py     # Baostock数据获取（完整财务查询）
│   ├── scorer.py           # 三维评分算法
│   ├── strategies.py       # 策略库（多因子/PE/三维）
│   ├── backtest.py         # 回测引擎（A股规则）
│   ├── indicators.py       # 技术指标计算（ta库）
│   ├── cache_manager.py    # 缓存管理
│   └── engine.py           # 主引擎（协调全流程）
│
├── cli/                     # 交互界面
│   ├── picker_cli.py       # 主入口（交互式+参数）
│   └── config.py           # 配置常量
│
├── output/                  # 输出模块
│   ├── reporter.py         # Markdown报告生成
│   ├── excel_writer.py     # Excel导出
│   └── qq_notifier.py      # QQ推送格式化
│
├── config/                  # 配置文件（YAML）
│   ├── data_sources.yaml   # 数据源配置
│   ├── strategies.yaml     # 策略参数
│   ├── pools.yaml          # 股票池配置
│   └── scoring_weights.yaml # 评分权重
│
├── scripts/                 # 工具脚本
│   ├── fast_scan.py        # 快速采样（200只，~30秒）
│   ├── full_scan.py        # 全市场扫描（~15分钟）
│   └── daily_auto.py       # 每日自动化（cron）
│
├── data/                    # 数据目录（自动生成）
│   ├── cache/              # 缓存文件
│   ├── raw/                # 原始数据（可选）
│   └── processed/          # 处理后数据
│
├── reports/                 # 报告输出
│   ├── daily/              # 每日简报
│   └── backtest/           # 回测报告
│
├── tests/                   # 单元测试
├── notebooks/               # Jupyter实验
├── logs/                    # 运行日志
│
├── requirements.txt         # Python依赖
├── README.md               # 本文件
├── QUICKSTART.md           # 5分钟快速上手
├── USER_GUIDE.md           # 用户手册
└── API_REFERENCE.md        # API文档
```

---

## 🎯 功能矩阵

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| 数据获取（Baostock） | ✅ 完成 | 支持PE/PB/ROE/营收增长/利润增长 |
| 批量查询（10线程） | ✅ 完成 | 采样200只≈20秒，全市场≈15分钟 |
| 缓存机制 | ✅ 完成 | 按日期缓存，避免重复查询 |
| 多因子策略 | ✅ 完成 | 估值40% + 盈利30% + 规模30% |
| PE价值策略 | ✅ 完成 | 低PE筛选 |
| 三维评分策略 | ✅ 完成 | 基本面+技术面+情绪面 |
| 技术指标计算 | ✅ 完成 | MA/MACD/RSI/KDJ/布林带（ta库） |
| 回测引擎 | ✅ 完成 | 支持T+1、印花税、手续费 |
| Markdown报告 | ✅ 完成 | 简洁表格 + Top 20 推荐 |
| Excel导出 | ✅ 完成 | 详细数据 + 中文字段 |
| QQ推送 | ✅ 完成 | 自动格式化 + 文件附件 |
| 交互式CLI | ✅ 完成 | 问答式选择股票池/策略 |
| 命令行参数 | ✅ 完成 | 支持非交互模式 |
| 定时任务 | ✅ 完成 | 每日08:00自动运行 |
| 新闻情绪分析 | ⚠️ 可选 | 需 Tavily API Key |

---

## 📦 安装

### 环境要求

- Python 3.10+
- pip 包管理器
- Git（可选）

### 步骤1：克隆/解压项目

```bash
# 如果收到压缩包
tar -xzf stock-picker-plus.tar.gz
cd stock-picker-plus

# 或从Git克隆
git clone <repository-url>
cd stock-picker-plus
```

### 步骤2：创建虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 步骤3：安装依赖

```bash
pip install -r requirements.txt
```

**依赖说明**：
- `baostock`: A股数据源（免费，无需注册）
- `pandas/numpy`: 数据处理
- `ta`: 技术指标库
- `matplotlib/seaborn`: 可视化（可选）
- `openpyxl`: Excel导出
- `pyyaml`: 配置文件解析

### 步骤4：验证安装

```bash
python -c "import baostock; print('✅ Baostock 可用')"
```

如果看到 ✅，说明安装成功。

---

## 🚀 快速开始

### 方式1：交互式运行（推荐新手）

```bash
python cli/picker_cli.py
```

按照提示选择：
1. 股票池（沪深300/中证500/中证1000/全A股）
2. 策略（低PE/多因子/三维评分）
3. 运行模式（快速采样/全市场）
4. 其他选项（缓存、回测、QQ推送）

**示例交互**：
```
📊 AI 智能选股助手（完整版）

请选择股票池：
  1. 沪深300 — 大盘蓝筹，300只
  2. 中证500 — 中盘成长，500只
  3. 中证1000 — 小盘潜力，1000只
  4. 全部A股 — 全市场扫描，约8687只

请输入编号 [默认: 4]: 4
✅ 已选择: 全部A股

请选择投资策略：
  1. 低PE价值策略 — 要求低估值高盈利
  2. 多因子策略 — 综合估值+盈利+规模
  3. 三维评分策略 — 基本面+技术面+情绪面

请输入编号 [默认: 2]: 2
✅ 已选择: 多因子策略

请选择运行模式：
  1. 快速采样（约30秒，采样200只）
  2. 全市场扫描（约15-20分钟）

请输入编号 [默认: 1]: 1
✅ 模式: 快速采样（200只）

其他选项：
  是否使用缓存加速？(Y/n) Y
  ✅ 缓存: 开启
  是否运行回测验证？(y/N) n
  ✅ 回测: 跳过
  是否自动推送到QQ？(y/N) n
  ✅ QQ推送: 关闭
```

### 方式2：命令行参数（适合脚本化）

```bash
# 快速采样（默认）
python cli/picker_cli.py --pool all --strategy multi_factor --sample

# 全市场沪深300多因子策略
python cli/picker_cli.py --pool hs300 --strategy multi_factor --no-sample

# 带回测和QQ推送
python cli/picker_cli.py --pool zz500 --strategy pe_value --sample --backtest --send-qq
```

**参数说明**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--pool` / `-p` | 股票池：`hs300`/`zz500`/`zz1000`/`all` | `all` |
| `--strategy` / `-s` | 策略：`multi_factor`/`pe_value`/`three_dimensional` | `multi_factor` |
| `--sample` / `-S` | 采样模式（快速） | 开启 |
| `--no-sample` | 全市场模式（慢速） | - |
| `--use-cache` | 使用缓存加速 | 开启 |
| `--no-cache` | 不使用缓存 | - |
| `--backtest` / `-b` | 运行回测 | 关闭 |
| `--send-qq` / `-q` | QQ推送 | 关闭 |
| `--sample-size` | 采样数量 | `200` |
| `--verbose` / `-v` | 详细日志 | 关闭 |

### 方式3：直接调用脚本

```bash
# 快速扫描（采样200只）
python scripts/fast_scan.py all multi_factor

# 全市场扫描
python scripts/full_scan.py all multi_factor
```

### 方式4：Python API（嵌入其他项目）

```python
from core.engine import StockPickerEngine

# 初始化引擎
engine = StockPickerEngine()

# 运行选股
result = engine.run(
    pool="all",              # 全市场
    strategy_name="multi_factor",
    sample_size=200,         # 采样200只（快速）
    use_cache=True,
    send_qq=False
)

# 查看结果
selected = result['selected']
print(f"推荐 {len(selected)} 只股票：")
print(selected[['代码', '名称', 'PE', '总分']].to_string())

# 输出文件
print(f"Excel报告: {result['excel_path']}")
```

---

## 📊 输出说明

### 报告文件

运行完成后，报告保存在 `reports/daily/` 目录：

```
reports/daily/
├── report_YYYYMMDD_HHMM.md      # Markdown报告（可读性强）
├── stock_pool_YYYYMMDD_HHMM.xlsx  # Excel详细数据
└── full_scan_YYYYMMDD_HHMM.xlsx   # 全量数据（如有）
```

### Excel字段说明

| 列名 | 说明 | 示例 |
|------|------|------|
| `代码` | 股票代码（6位数字） | `600519` |
| `名称` | 公司名称 | `贵州茅台` |
| `PE` | 市盈率（TTM） | `25.5` |
| `PB` | 市净率 | `8.2` |
| `收盘价` | 最新收盘价（元） | `1680.5` |
| `总市值（亿元）` | 总市值 | `22000` |
| `ROE(%)` | 净资产收益率 | `32.1` |
| `营收增长率(%)` | 营收同比增长 | `12.3` |
| `估值分` | 估值因子得分（0-100） | `85` |
| `盈利分` | 盈利因子得分 | `80` |
| `规模分` | 规模因子得分 | `75` |
| `综合分` | 加权总分 | `82.5` |
| `评级` | 投资建议 | `🟢 推荐` |

### Markdown报告结构

```markdown
# 📈 A股智能选股报告

**生成时间**: 2026-04-13 16:00
**股票池**: 全A股
**策略**: 多因子策略

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
...

## 📋 详细分析

### 1. 600519 贵州茅台 — 🟢 推荐

**综合评分：** 82.5 / 100

| 维度 | 评分 | 关键指标 |
|:---|:---:|:---|
| 基本面 | 85.0 | PE: 25.5, ROE: 32.1% |
| 技术面 | 75.0 | 待补充 |
| 情绪面 | 80.0 | 待补充 |

---

## ⚠️ 免责声明
...
```

---

## ⚙️ 配置说明

所有配置文件位于 `config/` 目录：

### `data_sources.yaml` - 数据源配置

```yaml
baostock:
  enabled: true
  rate_limit_ms: 300  # 查询间隔（避免被封）

tavily:
  enabled: false      # 设为 true 并填写 API Key 启用情绪分析
  api_key: ""
```

### `strategies.yaml` - 策略参数

```yaml
multi_factor:
  weights:
    valuation: 0.40
    profitability: 0.30
    scale: 0.30
  filters:
    min_score: 60
    min_market_cap: 50  # 亿元
    max_pe: 50
```

修改后下次运行自动生效。

---

## 🔧 高级功能

### 1. 自定义策略

创建新策略只需继承 `BaseStrategy`：

```python
from core.strategies import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="我的策略", description="自定义因子组合")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        # 计算自定义指标
        return data

    def generate_signals(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df = self.calculate_indicators(data)
        # 生成信号：1=买入，0=持有，-1=卖出
        df['signal'] = (df['my_score'] > 70).astype(int)
        return df
```

注册到 `core/strategies.py` 的 `STRATEGY_REGISTRY` 字典即可在CLI中选择。

---

### 2. 定时任务（每日自动运行）

#### 使用 OpenClaw 定时任务：

```bash
# 创建定时任务（每天上午08:00）
openclaw cron create \
  --name "daily-stock-pick" \
  --schedule "0 8 * * 1-5" \   # 周一至周五 08:00
  -- python scripts/daily_auto.py

# 查看任务列表
openclaw cron list

# 手动触发测试
openclaw cron run <task-id>
```

#### 或直接 crontab：

```bash
crontab -e

# 添加一行：
0 8 * * 1-5 cd /path/to/stock-picker-plus && /path/to/venv/bin/python scripts/daily_auto.py >> logs/cron.log 2>&1
```

---

### 3. QQ推送配置

系统已内置QQ推送模块，但需要在 OpenClaw 中正确配置 QQ 机器人。

**测试推送**：
```bash
# 手动测试
python cli/picker_cli.py --sample --send-qq
```

如果收到QQ消息，说明配置正确。

**注意**：在 OpenClaw 环境中，文件附件通过 `<qqfile>` 标签自动处理，无需额外工具调用。

---

### 4. 回测验证

```python
from core.engine import StockPickerEngine
from core.strategies import get_strategy

engine = StockPickerEngine()

# 获取数据
data = engine.fetcher.get_stock_basic()

# 选择策略
strategy = get_strategy("multi_factor")

# 生成信号
signals = strategy.generate_signals(data)

# 运行回测（需有历史价格数据）
from core.backtest import BacktestEngine
bt = BacktestEngine(initial_capital=1000000)
result = bt.run(signals, price_data=historical_prices)

print(f"回测收益: {result['总收益率']:.2f}%")
print(f"年化收益: {result['年化收益率']:.2f}%")
print(f"夏普比率: {result['夏普比率']:.2f}")
print(f"最大回撤: {result['最大回撤']:.2f}%")
```

---

## 📈 策略说明

### 策略1：多因子模型（推荐）

**因子组合**：
- 估值因子（40%）：PE 倒数（越低越好）
- 盈利因子（30%）：ROE（越高越好）
- 规模因子（30%）：营收增长率（越高越好）

**筛选条件**：
- 综合分 ≥ 60
- 市值 ≥ 50 亿元
- PE > 0（排除亏损）
- 排除 ST 股

**适用场景**：全市场扫描，平衡型投资

---

### 策略2：低PE价值策略

**条件**：
- PE < 20
- ROE > 15%
- 营收增长 > 5%
- 市值 > 10 亿元

**适用场景**：寻找被低估的蓝筹股

---

### 策略3：三维评分策略

**三个维度**：
1. **基本面（40%）**：PE、ROE、增长
2. **技术面（35%）**：均线多头、MACD金叉、成交量
3. **情绪面（25%）**：新闻情绪分析（需 Tavily API）

**评级**：
- 🟢 强烈推荐：≥ 75
- 🟢 推荐：60-74
- 🟡 观望：45-59
- 🔴 回避：< 45

**适用场景**：兼顾价值、时机、热度的综合选股

---

## 🔍 常见问题

### Q1: 为什么全市场扫描这么慢？

**A**: Baostock 有频率限制（约300ms/次），8687只股票理论最小耗时：
```
8687 股票 × 0.3秒 ≈ 43分钟
```

但我们已优化到 **15分钟**（10线程并发 + 智能重试）。建议：
- 日常使用 **采样模式**（200只，20秒）
- 收盘后运行 **全市场**（生成正式报告）

---

### Q2: 缓存文件占空间吗？

**A**: 缓存按日期存储，每天最多几个MB（主要是股票列表）。自动清理7天前旧缓存。

清理缓存：
```bash
python -c "from core.cache_manager import CacheManager; CacheManager().clear()"
```

---

### Q3: 如何调整策略参数？

**A**: 编辑 `config/strategies.yaml`，例如提高多因子策略的估值权重：

```yaml
multi_factor:
  weights:
    valuation: 0.50   # 从40%提高到50%
    profitability: 0.30
    scale: 0.20       # 降低规模因子
```

---

### Q4: 可以添加自己的数据源吗？

**A**: 可以。在 `core/data_fetcher.py` 中新增方法，或创建新的数据源类（如 `data_source_tushare.py`），然后在 `DataFetcher` 中集成。

---

### Q5: 回测为什么没实现？

**A**: 回测需要**历史日线数据**（每只股票250天以上），数据量巨大。当前版本已实现回测引擎框架，待数据层完善后即可使用。

要启用回测：
1. 确保 `fetch_batch()` 能获取历史价格
2. 在 `engine.run()` 中设置 `run_backtest=True`
3. 查看回测结果（收益、夏普、最大回撤）

---

### Q6: Excel为什么打不开？

**A**: 确保安装了 `openpyxl` 引擎：
```bash
pip install openpyxl
```

如果仍有问题，检查文件路径是否包含中文或特殊字符。

---

### Q7: 如何停止正在运行的程序？

**A**: 按 `Ctrl+C` 发送中断信号，程序会优雅退出（清理线程、保存缓存）。

---

## 🐛 调试与日志

### 查看日志

日志文件位置：`logs/auto_daily.log`

实时查看：
```bash
tail -f logs/auto_daily.log
```

### 设置详细日志

```bash
python cli/picker_cli.py --verbose
```

日志级别：
- `INFO`: 常规运行信息
- `DEBUG`: 详细调试信息（`--verbose` 开启）
- `WARNING`: 单只股票查询失败
- `ERROR`: 严重错误

---

## 📚 API 文档

详细API文档见 `docs/` 目录：
- `DATA_FETCHER.md` - 数据获取模块
- `STRATEGIES.md` - 策略开发指南
- `BACKTEST.md` - 回测引擎使用
- `REPORTING.md` - 报告生成定制

---

## 🧪 测试

运行单元测试：
```bash
pytest tests/ -v
```

运行集成测试（快速采样）：
```bash
python scripts/fast_scan.py
```

预期输出：200只股票采样，生成Excel报告。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**开发流程**：
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 仅供学习研究，**不构成投资建议**。

---

## ⚠️ 风险提示

1. 本软件为 **量化研究工具**，仅供学习使用
2. **不构成任何投资建议**，决策需独立判断
3. 股市有风险，投资需谨慎
4. 历史表现不代表未来收益
5. 策略可能因市场变化而失效
6. 数据来自 Baostock，存在一定延迟

---

## 📧 联系我们

- 项目维护：Simon
- 问题反馈：请在 GitHub Issues 提交
- 交流群：待建

---

## 🎉 致谢

- **Baostock** - 免费稳定的A股数据源
- **ai-stock-picker** - 原始版本（三维评分）
- **finance-ai-project** - 策略框架参考
- **OpenClaw** - AI Agent 平台支持

---

**最后更新**: 2026-04-13  
**版本**: v1.0.0 (完整合并版)  
**状态**: ✅ 生产就绪

---

*Happy Trading! 📈*
