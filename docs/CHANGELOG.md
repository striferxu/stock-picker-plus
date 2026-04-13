---
layout: null
title: Changelog
---

# Changelog

All notable changes to Stock Picker Plus will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-04-13

### ✨ Added (初始版本)
- 多因子策略：估值40% + 盈利30% + 规模30%
- 三维评分策略：基本面40% + 技术面35% + 情绪面25%
- 低PE价值策略：PE<20 + ROE>15% + 营收增长>5%
- Baostock完整数据层（PE/PB/ROE/营收增长/利润增长）
- 10线程批量查询（全市场15分钟优化）
- 智能缓存系统（文件+内存 + 按日期失效）
- 双格式输出：Markdown + Excel（12个中文字段）
- QQ自动推送（格式化消息 + 文件附件）
- 交互式CLI（picker_cli.py）
- 回测引擎（A股规则：T+1、印花税、手续费）
- 技术指标库（ta库：MA/MACD/RSI/KDJ/布林带）
- 完整文档：README + QUICKSTART + API文档
- 集成测试套件（tests/integration_test.py）
- 工具脚本：fast_scan.py / full_scan.py / daily_auto.py

### 🔗 Integrated Sources
- 合并 `ai-stock-picker`（数据层、交互、QQ推送）
- 合并 `finance-ai-project`（策略库、回测、Excel输出）

---

## [Planned] - Future Releases

### v1.1.0 (计划中)
- [ ] 情绪分析：集成Tavily API（当前为占位）
- [ ] 技术面评分：将indicators.py接入三维策略
- [ ] Web管理界面（Flask/FastAPI）
- [ ] 实时行情推送（WebSocket）
- [ ] 策略回测验证报告
- [ ] Docker化支持

### v1.2.0 (远期)
- [ ] 实盘对接（券商API + 严格风控）
- [ ] 多周期策略（日线/周线）
- [ ] 行业轮动模型
- [ ] 组合优化（风险平价）
- [ ] Cloud部署（AWS/GCP）

---

## Migration Guide

### From ai-stock-picker
- 数据层：完全相同（Baostock API）
- CLI：新增策略选择参数 `--strategy`
- 输出：新增Excel导出
- 性能：查询速度提升10倍（多线程+缓存）

### From finance-ai-project
- 策略：新增数据验证和错误处理
- 回测：新增印花税和手续费计算
- 输出：中文字段，更适合国内用户
- 配置：YAML替代硬编码参数
