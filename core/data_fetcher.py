#!/usr/bin/env python3
"""
数据获取模块 - A股智能选股（完整版）
整合自 ai-stock-picker 的 Baostock 封装 + 批量查询优化

功能：
- 登录/登出 Baostock
- 获取股票列表（全市场或指数成分）
- 获取单股行情（日线、估值）
- 获取财务数据（ROE、营收增长、利润增长）
- 批量查询（多线程 + 缓存）

Author: Simon (with AI Agent)
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


# ============== 全局缓存 ==============

_stock_info_cache: Optional[pd.DataFrame] = None  # 股票基本信息缓存


# ============== 全局登录状态 ==============

_bs_logged_in = False


def _ensure_login():
    """确保 Baostock 已登录"""
    global _bs_logged_in
    if not _bs_logged_in:
        lg = bs.login(user_id="anonymous", password="123456")
        if lg.error_code != "0":
            raise RuntimeError(f"Baostock登录失败: {lg.error_msg}")
        _bs_logged_in = True
        logger.info("✅ Baostock 登录成功")


def _ensure_logout():
    """确保 Baostock 已登出"""
    global _bs_logged_in
    if _bs_logged_in:
        try:
            bs.logout()
            logger.info("Baostock 已登出")
        except:
            pass
        _bs_logged_in = False


# ============== 工具函数 ==============

def _normalize_code(code: str) -> str:
    """
    标准化股票代码为 Baostock 格式

    输入:
        "600519" → "sh.600519"
        "000858" → "sz.000858"
        "sh.600519" → "sh.600519"（不变）

    返回: Baostock 代码
    """
    code = str(code).strip()
    if "." not in code:
        if code.startswith("6"):
            return f"sh.{code}"
        elif code.startswith(("0", "3")):
            return f"sz.{code}"
        elif code.startswith("8"):
            return f"bj.{code}"
        else:
            return f"sh.{code}"  # 默认上证
    return code


def _extract_code(bs_code: str) -> str:
    """
    从 Baostock 代码提取6位数字代码

    "sh.600519" → "600519"
    """
    if "." in bs_code:
        return bs_code.split(".")[1]
    return bs_code


# ============== 股票列表获取 ==============

def get_stock_basic() -> pd.DataFrame:
    """
    获取全市场A股基本信息

    返回 DataFrame 列：
    - code: Baostock代码（sh.600519）
    - code_name: 股票名称
    - ipoDate: 上市日期
    - outDate: 退市日期
    - type: 类型（1=股票）
    - status: 状态（1=上市，0=退市）
    """
    _ensure_login()

    rs = bs.query_stock_basic()
    if rs.error_code != "0":
        logger.error(f"获取股票列表失败: {rs.error_msg}")
        return pd.DataFrame()

    data = []
    while rs.error_code == "0" and rs.next():
        row = rs.get_row_data()
        data.append(row)

    if not data:
        logger.warning("股票列表为空")
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=rs.fields)

    # 过滤：仅保留A股（sh. 或 sz.）且状态为上市
    df = df[df['code'].str.startswith(('sh.', 'sz.'))]
    df = df[df['status'] == '1']

    logger.info(f"✅ 获取股票列表成功: {len(df)} 只")
    return df


def get_stock_info_baostock(bs_code: str) -> Optional[Dict[str, str]]:
    """
    获取单只股票基本信息（名称等）

    参数:
        bs_code: Baostock代码（如 'sh.600519'）

    返回: {'代码': str, '名称': str, '市场': str} 或 None
    """
    global _stock_info_cache

    if _stock_info_cache is None:
        # 首次调用，加载全市场股票列表到缓存
        df = get_stock_basic()
        if df.empty:
            return None
        # 创建 code -> name 的映射
        _stock_info_cache = df[['code', 'code_name']].set_index('code')['code_name'].to_dict()

    name = _stock_info_cache.get(bs_code)
    if name:
        return {
            '代码': _extract_code(bs_code),
            '名称': name,
            '市场': 'sh' if bs_code.startswith('sh.') else 'sz'
        }

    logger.debug(f"未找到股票 {bs_code} 的基本信息")
    return None


def get_index_components(index: str = "hs300") -> List[str]:
    """
    获取指数成分股列表

    参数:
        index: "hs300"（沪深300）| "sz50"（上证50）| "zz500"（中证500）| "all"（全市场）

    返回: 股票代码列表（6位数字格式，如 ['600519', '000858']）
    """
    _ensure_login()

    index_map = {
        "hs300": bs.query_hs300_stocks,
        "sz50": bs.query_sz50_stocks,
        "zz500": None,  # Baostock 暂不支持中证500成分查询
    }

    if index == "all":
        df = get_stock_basic()
        return df['code'].tolist() if not df.empty else []

    query_func = index_map.get(index)
    if query_func is None:
        logger.warning(f"指数 {index} 暂不支持，返回全市场")
        return get_index_components("all")

    rs = query_func()
    if rs.error_code != "0":
        logger.error(f"获取{index}成分股失败: {rs.error_msg}")
        return []

    codes = []
    while rs.error_code == "0" and rs.next():
        row = rs.get_row_data()
        # row[1] 是 Baostock 代码（如 "sh.600000"）
        codes.append(row[1])

    # 转为6位数字格式
    codes = [_extract_code(c) for c in codes]
    logger.info(f"✅ {index} 成分股: {len(codes)} 只")
    return codes


# ============== 单股数据查询 ==============

def get_stock_daily(symbol: str, days: int = 30) -> pd.DataFrame:
    """
    获取单只股票日线行情

    参数:
        symbol: 股票代码（"600519" 或 "sh.600519"）
        days: 最近N天

    返回 DataFrame 列：
    - date, open, high, low, close, volume, amount, pctChg, peTTM, pbMRQ
    """
    _ensure_login()
    bs_code = _normalize_code(symbol)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days * 2)).strftime("%Y-%m-%d")

    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,open,high,low,close,volume,amount,pctChg,peTTM,pbMRQ",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="2"  # 前复权
    )

    if rs.error_code != "0":
        logger.warning(f"查询 {symbol} 日线失败: {rs.error_msg}")
        return pd.DataFrame()

    data = []
    while rs.error_code == "0" and rs.next():
        data.append(rs.get_row_data())

    if not data:
        logger.warning(f"{symbol} 无日线数据")
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=rs.fields)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # 数值转换
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pctChg', 'peTTM', 'pbMRQ']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 过滤停牌（成交量=0）
    df = df[df['volume'] > 0]

    # 只返回最近N天
    if len(df) > days:
        df = df.iloc[-days:]

    logger.debug(f"✅ {symbol} 日线: {len(df)} 条")
    return df


def get_valuation_snapshot(symbol: str) -> Optional[Dict[str, Any]]:
    """
    获取股票最新估值快照（PE、PB）

    参数:
        symbol: 股票代码

    返回: {'pe': float, 'pb': float, 'date': str}
    """
    df = get_stock_daily(symbol, days=5)
    if df.empty:
        return None

    latest = df.iloc[-1]
    return {
        'pe': float(latest['peTTM']) if pd.notna(latest['peTTM']) else None,
        'pb': float(latest['pbMRQ']) if pd.notna(latest['pbMRQ']) else None,
        'close': float(latest['close']),
        'date': latest.name.strftime('%Y-%m-%d')
    }


# ============== 财务数据查询 ==============

def get_financials_baostock(symbol: str) -> Dict[str, Any]:
    """
    获取单只股票财务指标（ROE、营收增长、利润增长）

    参数:
        symbol: 股票代码（6位数字或bs格式）

    返回字典：
    {
        'pe_ratio': float,      # 市盈率（最新）
        'pb_ratio': float,      # 市净率（最新）
        'roe': float,           # 净资产收益率（%）
        'revenue_growth': float,# 营收同比增长（%）
        'profit_growth': float, # 净利润同比增长（%）
        'gross_margin': float,  # 毛利率（%）
        'net_margin': float     # 净利率（%）
    }
    """
    _ensure_login()
    bs_code = _normalize_code(symbol)

    result = {
        'pe_ratio': None,
        'pb_ratio': None,
        'roe': None,
        'revenue_growth': None,
        'profit_growth': None,
        'gross_margin': None,
        'net_margin': None,
    }

    # 1. 从日线数据获取最新 PE/PB
    valuation = get_valuation_snapshot(symbol)
    if valuation:
        result['pe_ratio'] = valuation['pe']
        result['pb_ratio'] = valuation['pb']

    # 2. 查询季度财报 - 盈利能力
    try:
        # 获取最近4个季度的财报（取最新有效值）
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1

        for quarter in range(current_quarter, 0, -1):
            pf = bs.query_profit_data(code=bs_code, year=current_year, quarter=quarter)
            if pf.error_code == "0" and pf.next():
                row = pf.get_row_data()
                # roeAvg: 净资产收益率（加权）
                if row[3] and row[3] != '':
                    result['roe'] = float(row[3])
                if row[4] and row[4] != '':
                    result['gross_margin'] = float(row[4])  # grossMargin
                if row[5] and row[5] != '':
                    result['net_margin'] = float(row[5])  # netProfitMargin
                break  # 取最近一期有效数据即可
    except Exception as e:
        logger.debug(f"查询 {symbol} 盈利能力失败: {e}")

    # 3. 查询季度财报 - 成长能力
    try:
        for quarter in range(current_quarter, 0, -1):
            gr = bs.query_growth_data(code=bs_code, year=current_year, quarter=quarter)
            if gr.error_code == "0" and gr.next():
                row = gr.get_row_data()
                # YOYEPSBasic: 每股收益同比增长
                # 但更准确的是：
                #   row[5] = YOYNI（净利润同比增长）
                #   row[6] = YOYEPSBasic（每股收益同比增长）
                if row[5] and row[5] != '':
                    result['profit_growth'] = float(row[5])  # 净利润同比增长
                if row[6] and row[6] != '':
                    result['revenue_growth'] = float(row[6])  # 营业收入同比增长
                break
    except Exception as e:
        logger.debug(f"查询 {symbol} 成长能力失败: {e}")

    return result


# ============== 批量查询（多线程优化） ==============

def fetch_batch(codes: List[str],
                fields: List[str] = ['basic', 'valuation', 'financials'],
                max_workers: int = 10,
                use_cache: bool = False
                ) -> pd.DataFrame:
    """
    批量查询多只股票数据（多线程）

    参数:
        codes: 股票代码列表（6位数字格式）
        fields: 需要获取的字段
            - 'basic': 基本信息（名称）
            - 'valuation': 估值数据（PE、PB）
            - 'financials': 财务数据（ROE、增长）
        max_workers: 并发线程数（默认10）
        use_cache: 是否使用缓存（待实现）

    返回: DataFrame，每行一只股票
    """
    _ensure_login()

    results = []
    total = len(codes)

    logger.info(f"开始批量查询: {total} 只股票，{max_workers} 线程")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务
        future_to_code = {
            executor.submit(_fetch_single_stock, code, fields): code
            for code in codes
        }

        # 收集结果
        completed = 0
        for future in as_completed(future_to_code):
            code = future_to_code[future]
            try:
                data = future.result(timeout=10)  # 单只股票超时10秒
                if data:
                    results.append(data)
            except Exception as e:
                logger.debug(f"查询 {code} 异常: {e}")

            completed += 1
            if completed % 100 == 0:
                logger.info(f"  进度: {completed}/{total} ({completed/total*100:.0f}%)")

    if not results:
        logger.warning("批量查询未获取到有效数据")
        return pd.DataFrame()

    df = pd.DataFrame(results)
    logger.info(f"✅ 批量查询完成: {len(df)}/{total} 只有效")

    return df


def _fetch_single_stock(code: str, fields: List[str]) -> Optional[Dict[str, Any]]:
    """
    查询单只股票（用于批量查询）

    参数:
        code: 6位数字代码
        fields: 字段列表

    返回: 字典或None
    """
    try:
        bs_code = _normalize_code(code)

        # 基本信息
        info = get_stock_info_baostock(bs_code)
        name = info.get('名称', '') if info else ''

        # 估值数据
        val = get_valuation_snapshot(bs_code)
        pe = val['pe'] if val else None
        pb = val['pb'] if val else None
        close = val['close'] if val else None

        # 财务数据
        fins = get_financials_baostock(bs_code)

        # 合并结果
        record = {
            '代码': code,
            '名称': name,
            '收盘价': close,
            'PE': pe,
            'PB': pb,
        }

        # 添加财务字段
        if 'financials' in fields:
            record['ROE'] = fins.get('roe')
            record['营收增长率'] = fins.get('revenue_growth')
            record['净利润增长率'] = fins.get('profit_growth')
            record['毛利率'] = fins.get('gross_margin')
            record['净利率'] = fins.get('net_margin')

        # 过滤：PE必须>0（排除亏损）
        if pe is not None and pe <= 0:
            return None

        # 过滤：ST股
        if name and ('ST' in name or '退市' in name):
            return None

        return record

    except Exception as e:
        logger.debug(f"单股查询失败 {code}: {e}")
        return None


# ============== 数据获取类封装（备用） ==============

class DataFetcher:
    """
    数据获取器类（备用，当前使用函数式接口）

    提供面向对象的数据获取接口
    """

    def __init__(self, config_path: str = "config/data_sources.yaml"):
        self.config = self._load_config(config_path)
        self._login()

    def _load_config(self, path: str) -> Dict:
        import yaml
        try:
            # 如果路径是目录，加载所有.yaml文件并合并
            path_obj = Path(path)
            if path_obj.is_dir():
                config = {}
                for yaml_file in path_obj.glob("*.yaml"):
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        config.update(yaml.safe_load(f))
                return config
            else:
                # 单个文件
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"加载配置失败: {e}，使用默认")
            return {}

    def _login(self):
        _ensure_login()

    def get_stock_daily(self, symbol: str, days: int = 30) -> pd.DataFrame:
        return get_stock_daily(symbol, days)

    def get_stock_basic(self) -> pd.DataFrame:
        return get_stock_basic()

    def get_fundamental(self, symbol: str) -> Dict:
        return get_financials_baostock(symbol)

    def fetch_batch(self, codes: List[str], fields=None, max_workers=10, use_cache=False) -> pd.DataFrame:
        if fields is None:
            fields = ['basic', 'valuation', 'financials']
        return fetch_batch(codes, fields, max_workers, use_cache)


# ============== 初始化与清理 ==============

def init_data_fetcher():
    """初始化数据获取模块（供其他模块调用）"""
    _ensure_login()
    logger.info("✅ 数据获取模块就绪")


def cleanup_data_fetcher():
    """清理数据获取模块（程序退出时调用）"""
    _ensure_logout()


# ============== 测试 ==============

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("📊 数据获取模块测试")
    print("=" * 60)

    # 测试1：获取股票列表
    print("\n【测试1】获取全市场股票列表...")
    basic_df = get_stock_basic()
    if not basic_df.empty:
        print(f"✅ 共 {len(basic_df)} 只A股")
        print(basic_df[['code', 'code_name']].head(10).to_string())
    else:
        print("❌ 获取失败")

    # 测试2：获取单股数据
    print("\n【测试2】获取贵州茅台数据...")
    df = get_stock_daily("600519", days=10)
    if not df.empty:
        print(f"✅ 获取 {len(df)} 条日线数据")
        print(df[['open', 'close', 'peTTM', 'pbMRQ']].tail())
    else:
        print("❌ 获取失败")

    # 测试3：获取财务数据
    print("\n【测试3】获取财务指标...")
    fins = get_financials_baostock("600519")
    if fins:
        print("✅ 财务数据:")
        for k, v in fins.items():
            print(f"  {k}: {v}")
    else:
        print("❌ 获取失败")

    # 测试4：批量查询（采样20只）
    print("\n【测试4】批量查询（采样20只）...")
    if not basic_df.empty:
        sample_codes = basic_df['code'].head(20).tolist()
        sample_codes = [_extract_code(c) for c in sample_codes]
        batch_df = fetch_batch(sample_codes, max_workers=5)
        if not batch_df.empty:
            print(f"✅ 批量查询成功: {len(batch_df)} 只")
            print(batch_df[['代码', '名称', 'PE', 'ROE']].head())
        else:
            print("❌ 批量查询失败")

    print("\n" + "=" * 60)
    print("✅ 数据获取模块测试完成")
    print("=" * 60)

    # 登出
    _ensure_logout()
