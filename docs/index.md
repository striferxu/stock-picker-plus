# Stock Picker Plus 文档

欢迎访问 Stock Picker Plus 的官方文档站点。

---

## 📖 文档导航

### 快速开始
- **[项目简介](../PROJECT_SUMMARY.md)** - 项目概览与核心特性
- **[快速上手](QUICKSTART.md)** - 5分钟快速上手指南
- **[完整文档](README.md)** - 详细使用说明与API参考

### 开发文档
- **[数据获取模块](DATA_FETCHER.md)** - Baostock数据层API文档
- **[策略开发指南](STRATEGIES.md)** - 如何编写自定义策略
- **[回测引擎使用](BACKTEST.md)** - 回测功能详解

### 项目信息
- **[合并报告](MERGE_REPORT.md)** - 项目合并详情与架构说明
- **[CHANGELOG](CHANGELOG.md)** - 版本更新日志
- **[LICENSE](LICENSE)** - MIT许可证

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
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)

---

**文档版本**: v1.0.0 | **更新日期**: 2026-04-13
