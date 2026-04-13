# Stock Picker Plus - A股智能选股系统

![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> 专为A股市场设计的智能选股系统 - 多因子策略 · 三维评分 · 10线程批量查询 · 自动推送

---

## 🎯 功能亮点

| 特性 | 说明 |
|------|------|
| **多因子策略** | 估值40% + 盈利30% + 规模30% 加权评分 |
| **三维评分** | 基本面40% + 技术面35% + 情绪面25%（集成Tavily） |
| **高性能查询** | 10线程并发 + 智能缓存（15分钟 → 2秒） |
| **双格式输出** | Markdown报告（简洁） + Excel（12个中文字段） |
| **自动推送** | QQ消息 + Excel附件自动发送 |
| **回测引擎** | A股规则（T+1、印花税、手续费） |
| **技术指标** | MA、MACD、RSI、KDJ、布林带（ta库） |
| **完整文档** | README + QUICKSTART + API参考 |

---

## 📦 安装使用

### 快速开始（3步）

```bash
# 1. 克隆并进入
git clone https://github.com/striferxu/stock-picker-plus.git
cd stock-picker-plus

# 2. 安装依赖
pip install -r requirements.txt

# 3. 首次运行（采样200只，20秒）
python cli/picker_cli.py --sample
```

### 运行模式

| 命令 | 说明 | 耗时 | 股票数 |
|------|------|------|--------|
| `python cli/picker_cli.py --sample` | 快速采样 | 20-30秒 | 200只 |
| `python cli/picker_cli.py --no-sample` | 全市场扫描 | 15-20分钟 | 8687只 |
| `python scripts/fast_scan.py` | 快速脚本 | 20-30秒 | 200只 |
| `python scripts/full_scan.py` | 全量脚本 | 15-20分钟 | 8687只 |

---

## 📊 输出文件

每次运行生成：

```
reports/daily/
├── report_20260413_0900.md         # Markdown简洁报告
└── stock_pool_20260413_0900.xlsx  # Excel详细数据（12字段）
```

**Excel字段**：代码、名称、PE、PB、收盘价、总市值、ROE、营收增长率、估值分、盈利分、规模分、综合分、评级

---

## ⚙️ 配置调整

所有策略参数在 `config/strategies.yaml` 中配置：

```yaml
multi_factor:
  weights:
    valuation: 0.40     # 估值权重
    profitability: 0.30 # 盈利权重
    scale: 0.30        # 规模权重
  filters:
    min_score: 60      # 最低总分
    min_market_cap: 50 # 最低市值（亿元）
    max_pe: 100        # 最高PE
```

修改后下次运行自动生效。

---

## 🏗️ 项目结构

```
stock-picker-plus/
├── core/                    # 核心引擎
│   ├── data_fetcher.py      # Baostock数据获取（完整财务）
│   ├── scorer.py            # 三维评分算法
│   ├── strategies.py        # 策略库（3种）
│   ├── backtest.py          # 回测引擎
│   ├── indicators.py        # 技术指标
│   ├── cache_manager.py     # 缓存管理
│   └── engine.py            # 主协调器
├── cli/                     # 交互界面
├── output/                  # 输出模块（报告/Excel/QQ）
├── config/                  # YAML配置（4个文件）
├── scripts/                 # 工具脚本（快速/全量/自动）
├── docs/                    # API文档
└── tests/                   # 集成测试
```

---

## 📈 策略说明

### 1. 多因子策略（推荐）
```
综合分 = 估值分×40% + 盈利分×30% + 规模分×30%
```
适用：全市场平衡型选股，稳健性强。

### 2. 低PE价值策略
```
筛选条件: PE < 20 AND ROE > 15% AND 营收增长 > 5%
```
适用：寻找低估蓝筹股。

### 3. 三维评分策略
```
总分 = 基本面×40% + 技术面×35% + 情绪面×25%
```
适用：综合选股（需配置Tavily API Key）。

---

## 🔄 数据源

**主数据源**：Baostock（免费、稳定、无需token）
- 日线数据：T+1更新
- 财务数据：季度报表（ROE、营收、利润）
- 频率限制：约300ms/次（已通过多线程优化）

---

## ⚠️ 风险提示

本项目**仅供学习研究使用**，不构成任何投资建议。量化策略未经充分回测，市场有风险，决策需谨慎。

---

## 📚 文档

| 文档 | 链接 |
|------|------|
| 完整README | [README.md](README.md) |
| 快速上手 | [QUICKSTART.md](QUICKSTART.md) |
| 合并报告 | [MERGE_REPORT.md](MERGE_REPORT.md) |
| API文档 | [docs/DATA_FETCHER.md](docs/DATA_FETCHER.md) |

---

## 🤝 贡献

欢迎提交Issue、Feature Request或Pull Request！

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**Built with ❤️ by striferxu | GitHub: @striferxu**
