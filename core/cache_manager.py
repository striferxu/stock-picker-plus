#!/usr/bin/env python3
"""
缓存管理器 - 减少重复查询
缓存内容：股票列表、估值数据、财务数据

设计：
- 按日期缓存（每天只查一次）
- 文件缓存（JSON/CSV）
- 内存缓存（字典）

Author: Simon (with AI Agent)
"""

import pandas as pd
import json
import os
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = {}  # 内存缓存

    def _get_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        param_str = json.dumps(params, sort_keys=True, default=str)
        hash_val = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"{prefix}_{hash_val}"

    def _get_date_suffix(self) -> str:
        """日期后缀（每天一个文件）"""
        return date.today().strftime("%Y%m%d")

    def get(self, cache_type: str, params: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        获取缓存数据

        Args:
            cache_type: 缓存类型 ('stock_list', 'valuation', 'financials')
            params: 参数字典

        Returns:
            DataFrame 或 None（无缓存）
        """
        key = self._get_cache_key(cache_type, params)
        date_suffix = self._get_date_suffix()
        cache_file = self.cache_dir / f"{key}_{date_suffix}.pkl"

        # 检查内存缓存
        if key in self.memory_cache:
            logger.debug(f"缓存命中（内存）: {key}")
            return self.memory_cache[key]

        # 检查文件缓存
        if cache_file.exists():
            try:
                df = pd.read_pickle(cache_file)
                self.memory_cache[key] = df  # 载入内存
                logger.debug(f"缓存命中（文件）: {cache_file.name}")
                return df
            except Exception as e:
                logger.warning(f"缓存读取失败: {e}")

        return None

    def set(self, cache_type: str, params: Dict[str, Any], data: pd.DataFrame):
        """
        写入缓存

        Args:
            cache_type: 缓存类型
            params: 参数
            data: 要缓存的数据
        """
        if data.empty:
            return

        key = self._get_cache_key(cache_type, params)
        date_suffix = self._get_date_suffix()
        cache_file = self.cache_dir / f"{key}_{date_suffix}.pkl"

        try:
            data.to_pickle(cache_file)
            self.memory_cache[key] = data
            logger.debug(f"缓存写入: {cache_file.name} ({len(data)} 条)")
        except Exception as e:
            logger.warning(f"缓存写入失败: {e}")

    def clear(self, older_than_days: int = 7):
        """
        清理旧缓存

        Args:
            older_than_days: 清理多少天前的缓存
        """
        cutoff = date.today().toordinal() - older_than_days
        cleared = 0

        for file in self.cache_dir.glob("*.pkl"):
            # 从文件名提取日期（假设格式为 *_YYYYMMDD.pkl）
            try:
                date_str = file.stem.split('_')[-1]
                file_date = datetime.strptime(date_str, "%Y%m%d").date()
                if file_date.toordinal() < cutoff:
                    file.unlink()
                    cleared += 1
            except:
                continue

        logger.info(f"清理缓存: 删除 {cleared} 个旧文件")

    def get_stock_list_cache(self) -> Optional[pd.DataFrame]:
        """获取股票列表缓存"""
        return self.get("stock_list", {"source": "baostock"})

    def set_stock_list_cache(self, df: pd.DataFrame):
        """写入股票列表缓存"""
        self.set("stock_list", {"source": "baostock"}, df)

    def get_valuation_cache(self, date: str) -> Optional[pd.DataFrame]:
        """获取某日估值数据缓存"""
        return self.get("valuation", {"date": date})

    def set_valuation_cache(self, date: str, df: pd.DataFrame):
        """写入估值数据缓存"""
        self.set("valuation", {"date": date}, df)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.DEBUG)

    cache = CacheManager()

    # 测试股票列表缓存
    test_df = pd.DataFrame({
        'code': ['sh.600519', 'sz.000858'],
        'name': ['贵州茅台', '五粮液'],
        'PE': [25.5, 18.2]
    })

    print("写入缓存...")
    cache.set_stock_list_cache(test_df)

    print("读取缓存...")
    cached = cache.get_stock_list_cache()
    print(cached)

    print("✅ 缓存管理器测试完成")
