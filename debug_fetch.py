#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from core.data_fetcher import fetch_batch, _ensure_login

_ensure_login()
print("登录成功\n")

# 测试少量股票（5只）
codes = ['600519', '000858', '600066', '600160', '002666']

print(f"测试 {len(codes)} 只股票...")
df = fetch_batch(codes, fields=['basic', 'valuation'], max_workers=2)
print(f"\n结果: {len(df)} 行")
if not df.empty:
    print(df.to_string())
else:
    print("返回空DataFrame")
