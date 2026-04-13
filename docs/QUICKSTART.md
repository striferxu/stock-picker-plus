---
layout: null
title: Quick Start Guide
---

# ⚡ 5分钟快速上手

本指南帮助你在5分钟内运行第一次选股扫描。

---

## 📋 前置要求

✅ **Python 3.10+**（推荐 3.11）  
✅ **pip**（Python包管理器）  
✅ **Git**（可选，用于克隆仓库）

---

## 🚀 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/striferxu/stock-picker-plus.git
cd stock-picker-plus
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖清单**：
- pandas >= 2.0.0
- numpy >= 1.24.0
- baostock >= 0.8.9
- matplotlib >= 3.5.0
- ta >= 0.10.0
- openpyxl >= 3.1.0
- pyyaml >= 6.0
- rich >= 13.0.0

### 3. 验证安装

```bash
python --version   # 应显示 3.10+
pip list | grep -E "pandas|numpy|baostock"
```

---

## 🎯 首次运行

### 快速模式（推荐新手）

采样200只股票，20-30秒出结果：

```bash
python cli/picker_cli.py --sample
```

**输出**：
```
✅ 查询完成: 200只股票
✅ 评分完成
🏆 Top 5 推荐:
  600519 贵州茅台 | 综合分:78.2
  000858 五粮液   | 综合分:75.1
  ...
📄 报告: reports/daily/stock_pool_20260413_1320.xlsx
```

### 全市场模式（需要15-20分钟）

扫描全部8687只A股：

```bash
python cli/picker_cli.py --no-sample
```

---

## 📂 输出文件

运行完成后，查看 `reports/daily/` 目录：

```
reports/daily/
├── report_YYYYMMDD_HHMM.md      # Markdown简洁报告
└── stock_pool_YYYYMMDD_HHMM.xlsx # Excel详细数据
```

**Excel打开方式**：
- Microsoft Excel
- WPS Office
- LibreOffice Calc
- 或在线查看（Google Sheets / 腾讯文档）

**Excel字段说明**：
| 字段 | 说明 |
|------|------|
| 代码 | 6位股票代码 |
| 名称 | 公司名称 |
| PE | 市盈率（越小越好） |
| PB | 市净率（越小越好） |
| 收盘价 | 最新收盘价 |
| 总市值 | 亿元 |
| ROE | 净资产收益率（%） |
| 营收增长率 | 同比增长率（%） |
| 估值分 | 0-100分（越高越优） |
| 盈利分 | 0-100分 |
| 规模分 | 0-100分 |
| 综合分 | 总分（加权） |
| 评级 | AAA/AA/A/BBB/BB/B |

---

## ⚙️ 常用参数

```bash
# 指定策略
python cli/picker_cli.py --strategy multi_factor   # 多因子（默认）
python cli/picker_cli.py --strategy pe             # 低PE价值
python cli/picker_cli.py --strategy three_d        # 三维评分

# 指定股票池
python cli/picker_cli.py --pool hs300     # 沪深300
python cli/picker_cli.py --pool zz500     # 中证500
python cli/picker_cli.py --pool all       # 全市场（默认）

# 采样数量
python cli/picker_cli.py --sample --sample-size 100

# 启用缓存
python cli/picker_cli.py --use-cache

# 发送QQ推送
python cli/picker_cli.py --send-qq

# 详细日志
python cli/picker_cli.py --verbose
```

---

## 🎯 策略说明

### 多因子策略（推荐）
```
综合分 = 估值分×40% + 盈利分×30% + 规模分×30%
```
适用：全市场平衡型选股，稳健性强。

### 低PE价值策略
```
筛选条件: PE < 20 AND ROE > 15% AND 营收增长 > 5%
```
适用：寻找低估值的蓝筹股。

### 三维评分策略
```
总分 = 基本面×40% + 技术面×35% + 情绪面×25%
```
适用：综合选股（需配置Tavily API Key）。

---

## 🔧 配置文件

所有参数可在 `config/` 目录调整：

- **data_sources.yaml** - 数据源开关（Baostock/AKShare）
- **strategies.yaml** - 策略权重和筛选条件
- **pools.yaml** - 股票池定义
- **scoring_weights.yaml** - 因子归一化参数

修改后下次运行自动生效，无需重启。

---

## 🧪 运行测试

验证系统是否正常工作：

```bash
python tests/integration_test.py
```

预期输出：
```
📊 集成测试 - 核心流程验证
【Step 1】初始化数据模块... ✅
【Step 2】获取股票列表... ✅ (8687只)
【Step 3】批量查询... ✅ (20只)
【Step 4】策略评分... ✅
【Step 5】引擎测试... ✅
✅ 所有测试通过！系统已就绪。
```

---

## ⚠️ 注意事项

1. **数据延迟**：Baostock 为 T+1 数据（当日收盘后更新）
2. **频率限制**：约 300ms/次查询，已通过多线程优化
3. **缓存机制**：按日期缓存，次日自动刷新
4. **QQ推送**：需在OpenClaw环境中运行
5. **风险提示**：仅供学习研究，不构成投资建议

---

## 📚 进阶使用

### 使用脚本直接运行

```bash
# 快速扫描
python scripts/fast_scan.py

# 全市场扫描
python scripts/full_scan.py

# 每日自动任务（需配置cron）
python scripts/daily_auto.py
```

### 使用Python API

```python
from core.engine import StockPickerEngine

engine = StockPickerEngine()
result = engine.run(
    pool="all",
    strategy_name="multi_factor",
    sample_size=200,
    use_cache=True
)
print(result['selected'])
```

---

## 🆘 获取帮助

- 📖 **完整文档**：阅读 [README.md](README.html)
- 🐛 **问题反馈**：https://github.com/striferxu/stock-picker-plus/issues
- 💬 **交流讨论**：欢迎提交Issue

---

**祝你使用愉快！** 🎉
