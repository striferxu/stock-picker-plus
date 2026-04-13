# Stock Picker Plus 文档

欢迎访问 Stock Picker Plus 的官方文档站点。

Stock Picker Plus 是一个专为A股市场设计的智能选股系统，整合了多因子策略、三维评分、10线程批量查询、双格式输出（Markdown+Excel）和自动推送功能。

---

## 📖 文档导航

### 快速开始
- **[项目简介](PROJECT_SUMMARY.html)** - 项目概览与核心特性
- **[快速上手](QUICKSTART.html)** - 5分钟快速上手指南
- **[完整文档](README.html)** - 详细使用说明与API参考

### 开发文档
- **[数据获取模块](DATA_FETCHER.html)** - Baostock数据层API文档
- **[策略开发指南](STRATEGIES.html)** - 如何编写自定义策略
- **[回测引擎使用](BACKTEST.html)** - 回测功能详解

### 项目信息
- **[合并报告](MERGE_REPORT.html)** - 项目合并详情与架构说明
- **[CHANGELOG](CHANGELOG.html)** - 版本更新日志
- **[LICENSE](LICENSE.html)** - GNU General Public License v3.0

---

## 🎯 项目简介

**Stock Picker Plus** 是一个专为A股市场设计的智能选股系统，整合了多因子策略、三维评分、10线程批量查询、双格式输出（Markdown+Excel）和自动推送功能。

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **多因子策略** | 估值40% + 盈利30% + 规模30% 加权评分 |
| **三维评分** | 基本面40% + 技术面35% + 情绪面25%（集成Tavily） |
| **高性能查询** | 10线程并发 + 智能缓存（全市场15分钟 → 缓存2秒） |
| **双格式输出** | Markdown报告（简洁） + Excel（12个中文字段） |
| **自动推送** | QQ消息 + Excel附件自动发送 |
| **回测引擎** | A股规则（T+1、印花税、手续费） |
| **技术指标** | MA、MACD、RSI、KDJ、布林带（ta库） |
| **完整文档** | README + QUICKSTART + API参考 |

### 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/striferxu/stock-picker-plus.git
cd stock-picker-plus

# 安装依赖
pip install -r requirements.txt

# 快速采样（20秒出结果）
python cli/picker_cli.py --sample

# 全市场扫描（15分钟）
python cli/picker_cli.py --no-sample
```

### 📊 输出文件

每次运行生成：

```
reports/daily/
├── report_20260413_0900.md         # Markdown简洁报告
└── stock_pool_20260413_0900.xlsx  # Excel详细数据（12字段）
```

**Excel字段**：代码、名称、PE、PB、收盘价、总市值、ROE、营收增长率、估值分、盈利分、规模分、综合分、评级

---

## 🚀 快速命令

```bash
# 安装依赖
pip install -r requirements.txt

# 快速采样（20秒）
python cli/picker_cli.py --sample

# 全市场扫描（15分钟）
python cli/picker_cli.py --no-sample

# 运行测试
python tests/integration_test.py
```

---

## 📊 输出示例

```
reports/daily/
├── report_20260413_0900.md         # Markdown报告
└── stock_pool_20260413_0900.xlsx  # Excel数据（12字段）
```

---

## 🔗 相关链接

- **GitHub仓库**: https://github.com/striferxu/stock-picker-plus
- **问题反馈**: https://github.com/striferxu/stock-picker-plus/issues
- **更新日志**: [CHANGELOG](CHANGELOG.html)

---

**文档版本**: v1.0.0 | **更新日期**: 2026-04-13
