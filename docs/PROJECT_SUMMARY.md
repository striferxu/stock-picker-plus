---
layout: null
title: Project Summary
---

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
| **高性能查询** | 10线程批量查询 + 智能缓存（全市场15分钟 → 缓存2秒） |
| **双格式输出** | Markdown报告（简洁） + Excel（12个中文字段） |
| **自动推送** | QQ消息 + Excel附件自动发送 |
| **回测引擎** | A股规则（T+1、印花税、手续费） |
| **技术指标** | MA、MACD、RSI、KDJ、布林带（ta库） |
| **完整文档** | README + QUICKSTART + API文档 |

---

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 快速采样（20秒）
```bash
python cli/picker_cli.py --sample
```

### 全市场扫描（15分钟）
```bash
python cli/picker_cli.py --no-sample
```

---

## 📊 输出示例

每次运行生成：

```
reports/daily/
├── report_20260413_0900.md         # Markdown报告
└── stock_pool_20260413_0900.xlsx  # Excel数据（12字段）
```

**Excel字段**：代码、名称、PE、PB、收盘价、总市值、ROE、营收增长率、估值分、盈利分、规模分、综合分、评级

---

## ⚙️ 配置调整

编辑 `config/strategies.yaml` 即可调整策略参数：

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

## 📈 策略对比

| 策略 | 适用场景 | 特点 |
|------|---------|------|
| 多因子策略 | 全市场平衡 | 推荐，稳健 |
| 低PE价值 | 寻找低估 | 高风险低估值 |
| 三维评分 | 综合选股 | 需情绪API |

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE.html) 文件。
