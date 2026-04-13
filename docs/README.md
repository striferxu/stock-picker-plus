---
layout: null
title: Stock Picker Plus - A股智能选股系统完整版
---

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
| 策略引擎 | ✅ 完成 | 多因子/低PE/三维评分 |
| 回测系统 | ✅ 完成 | A股规则（T+1、印花税、手续费） |
| 技术指标 | ✅ 完成 | MA/MACD/RSI/KDJ/布林带 |
| 输出模块 | ✅ 完成 | Markdown + Excel（中文字段） |
| QQ推送 | ✅ 完成 | 格式化消息 + 文件附件 |
| 缓存机制 | ✅ 完成 | 文件+内存，按日期失效 |
| 文档 | ✅ 完成 | README + QUICKSTART + API |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/striferxu/stock-picker-plus.git
cd stock-picker-plus
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 首次运行

**快速采样**（20秒，推荐新手）：
```bash
python cli/picker_cli.py --sample
```

**全市场扫描**（15-20分钟）：
```bash
python cli/picker_cli.py --no-sample
```

---

## 🛠️ 配置指南

### 策略配置

编辑 `config/strategies.yaml`：

```yaml
multi_factor:
  weights:
    valuation: 0.40     # 估值权重 (0-1)
    profitability: 0.30 # 盈利权重
    scale: 0.30        # 规模权重
  filters:
    min_score: 60      # 最低总分（0-100）
    min_market_cap: 50 # 最低市值（亿元）
    max_pe: 100        # 最高PE
```

### 数据源配置

`config/data_sources.yaml`：

```yaml
baostock:
  enabled: true
  cache_days: 1        # 缓存天数
  max_workers: 10      # 并发线程数
```

### 股票池配置

`config/pools.yaml`：

```yaml
all:
  name: "全市场A股"
  count: 8687

hs300:
  name: "沪深300"
  index: "sh.000300"

zz500:
  name: "中证500"
  index: "sh.000905"
```

---

## 📊 输出说明

### 报告文件结构

```
reports/daily/
├── report_20260413_0900.md       # Markdown报告（可读性强）
│   ├── 运行概况
│   ├── 推荐股票表格
│   ├── 行业分布统计
│   └── 风险提示
│
└── stock_pool_20260413_0900.xlsx  # Excel详细数据
    ├── 代码
    ├── 名称
    ├── PE/PB/收盘价/总市值
    ├── ROE/营收增长率
    ├── 估值分/盈利分/规模分
    ├── 综合分
    └── 评级（AAA/AA/A/BBB/BB/B）
```

---

## 🔧 高级用法

### 命令行参数

```bash
# 策略选择
--strategy multi_factor   # 多因子（默认）
--strategy pe             # 低PE价值
--strategy three_d        # 三维评分

# 股票池
--pool all               # 全市场
--pool hs300             # 沪深300
--pool zz500             # 中证500

# 采样控制
--sample                 # 启用采样（默认200只）
--sample-size 500        # 自定义采样数

# 缓存
--use-cache              # 启用缓存
--no-cache               # 禁用缓存

# QQ推送
--send-qq                # 发送到QQ

# 调试
--verbose                # 详细日志
--debug                  # 调试模式
```

### Python API

```python
from core.engine import StockPickerEngine

# 初始化引擎
engine = StockPickerEngine()

# 运行选股
result = engine.run(
    pool="all",              # 全市场
    strategy_name="multi_factor",
    sample_size=200,         # 采样200只（快速）
    use_cache=True,          # 使用缓存
    send_qq=False            # 不发QQ
)

# 查看结果
selected = result['selected']
print(f"推荐 {len(selected)} 只股票：")
print(selected[['代码', '名称', 'PE', '总分']].to_string())

# 输出文件
print(f"Excel报告: {result['excel_path']}")
```

---

## 🧪 测试与验证

### 集成测试

```bash
python tests/integration_test.py
```

测试覆盖：
1. Baostock 登录
2. 股票列表获取
3. 批量查询（多线程）
4. 策略评分
5. 完整引擎流程

### 性能基准

| 模式 | 股票数 | 耗时 | 内存 |
|------|--------|------|------|
| 快速采样 | 200只 | 20-30秒 | <100MB |
| 全市场扫描 | 8687只 | 15-20分钟 | ~500MB |
| 缓存命中 | - | 2-5秒 | <50MB |

---

## 📈 策略详解

### 1. 多因子策略

```
综合分 = 估值分×40% + 盈利分×30% + 规模分×30%
```

**估值分计算**：
- PE归一化（反向，越小越好）
- PB归一化（反向）
- 规模分（总市值越大越好）

**盈利分计算**：
- ROE得分（越高越好）
- 营收增长得分
- 利润增长得分

### 2. 低PE价值策略

```
条件: PE < 20 AND ROE > 15% AND 营收增长率 > 5%
```

适合：寻找低估蓝筹股

### 3. 三维评分策略

```
总分 = 基本面×40% + 技术面×35% + 情绪面×25%
```

- 基本面：PE/PB/ROE/营收/利润
- 技术面：MA/MACD/RSI/KDJ/布林带（需实现）
- 情绪面：Tavily新闻评分（需API Key）

---

## 🔄 数据更新

### 数据来源

**主数据源**：Baostock（免费、稳定、无需token）
- 日线数据：T+1更新（当日收盘后）
- 财务数据：季度报表
- 频率限制：约300ms/次（已通过多线程优化）

### 缓存策略

```
data/cache/
├── stock_basic_20260413.pkl    # 股票列表（按日期）
├── daily_20260413.pkl          # 日线数据
└── financial_20260413.pkl      # 财务数据
```

缓存按日期自动失效，次日重新查询。

---

## ⚠️ 风险提示

本项目**仅供学习研究使用**，不构成任何投资建议。请注意：

1. **数据延迟**：使用T+1数据，非实时
2. **策略未回测**：未经过充分历史验证
3. **市场风险**：股市有风险，投资需谨慎
4. **性能限制**：Baostock有频率限制，全市场扫描需15-20分钟
5. **情绪API**：三维策略的情绪面需要Tavily API Key（需自行申请）

---

## 📚 相关文档

- [快速上手](QUICKSTART.html) - 5分钟上手
- [API参考](API_REFERENCE.html) - 完整API文档
- [数据获取模块](DATA_FETCHER.html) - Baostock封装详解
- [策略开发指南](STRATEGIES.html) - 自定义策略
- [回测引擎使用](BACKTEST.html) - 回测功能
- [合并报告](MERGE_REPORT.html) - 项目合并详情
- [更新日志](CHANGELOG.html) - 版本历史

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

GNU General Public License v3.0 - 详见 [LICENSE](LICENSE.html) 文件。

---

**Built with ❤️ by striferxu | GitHub: [@striferxu](https://github.com/striferxu)**
