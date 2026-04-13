# A股智能选股系统 - 测试套件

运行所有测试：

```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_data_fetcher.py -v
```

## 测试模块

- `test_data_fetcher.py` - 数据获取测试
- `test_strategies.py` - 策略逻辑测试
- `test_scorer.py` - 评分算法测试
- `test_backtest.py` - 回测引擎测试
