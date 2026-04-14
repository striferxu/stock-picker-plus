#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from core.data_fetcher import _ensure_login, _fetch_single_stock

_ensure_login()
print("登录成功\n")

# 测试几只股票
test_codes = ['600519', '000858', '600066', '600160']
for code in test_codes:
    print(f"\n=== 测试 {code} ===")
    result = _fetch_single_stock(code, ['basic', 'valuation', 'financials'])
    print(f"结果: {result}")
