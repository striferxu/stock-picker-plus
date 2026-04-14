#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from core.data_fetcher import _ensure_login, get_stock_daily, get_valuation_snapshot

# 登录
_ensure_login()
print("登录成功\n")

# 测试获取单只股票日线
code = '600519'
print(f"测试股票: {code}")
df = get_stock_daily(code, days=5)
print(f"日线数据行数: {len(df)}")
if not df.empty:
    print(f"列: {df.columns.tolist()}")
    print(f"最后一行:\n{df.iloc[-1]}")
    print(f"peTTM: {df.iloc[-1].get('peTTM')}")
    print(f"pbMRQ: {df.iloc[-1].get('pbMRQ')}")
else:
    print("日线数据为空！")

print("\n---\n")

# 测试估值快照
val = get_valuation_snapshot(code)
print(f"估值快照结果: {val}")
