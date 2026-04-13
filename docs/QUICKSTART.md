# ⚡ 5分钟快速上手 - A股智能选股

本指南帮助你在 **5分钟内** 运行第一次选股扫描。

---

## 📋 前置要求

- ✅ Python 3.10+ 已安装
- ✅ pip 包管理器可用
- ✅ 互联网连接（Baostock数据源）

---

## 🚀 四步启动

### 第1步：解压并进入项目目录（10秒）

```bash
# 解压
tar -xzf stock-picker-plus.tar.gz

# 进入目录
cd stock-picker-plus
```

---

### 第2步：安装依赖（1分钟）

```bash
# 创建虚拟环境（可选但推荐）
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

**依赖列表**：
- `baostock` - A股数据
- `pandas` - 数据处理
- `numpy` - 数值计算
- `ta` - 技术指标
- `openpyxl` - Excel导出
- `pyyaml` - 配置解析

---

### 第3步：测试数据连接（30秒）

```bash
python -c "import baostock; print('✅ Baostock 可用')"
```

预期输出：
```
✅ Baostock 可用
```

如果报错，请检查：
1. 网络连接（Baostock服务器在国内）
2. Python版本（需3.10+）
3. 依赖是否完整安装

---

### 第4步：运行第一次扫描（2-3分钟）

**推荐：快速采样模式**（200只股票，20-30秒）

```bash
python cli/picker_cli.py --sample
```

**或直接运行脚本**：

```bash
python scripts/fast_scan.py
```

---

## 🎯 交互式流程（首次运行推荐）

如果使用 `python cli/picker_cli.py`（无参数），会进入交互模式：

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
  1. 快速采样（约30秒，采样200只）— 适合快速预览
  2. 全市场扫描（约15-20分钟）— 正式报告

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

---

## 📊 查看结果

运行完成后，输出类似：

```
✅ 扫描完成！
总耗时: 25.3 秒
推荐股票: 8 只
筛选比例: 4.0%
Excel报告: reports/daily/stock_pool_20260413_1430.xlsx

🏆 Top 5 推荐:
  600519 贵州茅台 | 综合分:82.5 | PE:25.5
  000858 五粮液 | 综合分:85.2 | PE:18.2
  600036 招商银行 | 综合分:68.4 | PE:8.5
  ...
```

---

## 📁 打开Excel报告

```bash
# 列出最新报告
ls -lt reports/daily/*.xlsx | head -5

# 用系统默认程序打开（Linux/Mac）
xdg-open reports/daily/stock_pool_*.xlsx

# Windows
start reports/daily/stock_pool_*.xlsx
```

Excel包含完整字段：
- 代码、名称、PE、PB、收盘价
- ROE、营收增长率
- 估值分、盈利分、规模分、综合分
- 评级（推荐/观望/回避）

---

## 🔧 常用命令速查

| 目标 | 命令 |
|------|------|
| 快速采样（默认） | `python cli/picker_cli.py --sample` |
| 全市场扫描 | `python cli/picker_cli.py --no-sample` |
| 指定股票池 | `python cli/picker_cli.py --pool hs300` |
| 指定策略 | `python cli/picker_cli.py --strategy pe_value` |
| 开启详细日志 | `python cli/picker_cli.py --verbose` |
| 直接运行脚本 | `python scripts/fast_scan.py` |
| 查看帮助 | `python cli/picker_cli.py --help` |

---

## ⚠️ 常见问题

### Q: 报错 "No module named 'baostock'"

**A**: 依赖未安装完整。运行：
```bash
pip install -r requirements.txt
```

---

### Q: 全市场扫描太慢，有没有更快的方法？

**A**:
1. 日常使用 **采样模式**（200只，20秒）
2. 开启 **缓存**（`--use-cache`，默认开启）
3. 收盘后批量运行（避免盘中网络拥堵）

---

### Q: 如何修改策略参数？

**A**: 编辑 `config/strategies.yaml`，例如提高多因子策略的估值权重：

```yaml
multi_factor:
  weights:
    valuation: 0.50   # 从40%提高到50%
```

保存后下次运行自动生效。

---

### Q: 报告文件在哪里？

**A**: `reports/daily/` 目录下，文件名包含时间戳：
- `report_YYYYMMDD_HHMM.md` - Markdown版
- `stock_pool_YYYYMMDD_HHMM.xlsx` - Excel版

---

## 🎓 下一步

✅ 你已经完成了第一次扫描！

接下来可以：
1. **阅读完整文档**：`README.md`
2. **尝试全市场扫描**：`python cli/picker_cli.py --no-sample`
3. **配置QQ推送**：设置 `send_qq=True`，每天自动接收报告
4. **自定义策略**：继承 `BaseStrategy` 创建自己的因子组合
5. **设置定时任务**：每天08:00自动运行（cron）

---

## 📚 更多资源

- **详细文档**：`README.md`
- **API参考**：`docs/` 目录
- **策略开发**：`core/strategies.py` 注释
- **问题反馈**：提交 GitHub Issue

---

**恭喜！你已经成功运行了 A股智能选股系统！** 🎉

*有任何问题，查看 `README.md` 或提交 Issue。*
