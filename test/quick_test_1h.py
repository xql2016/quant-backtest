#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试1小时线数据获取
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
from data_source import get_stock_data

# 测试加密货币1小时线
print("测试：比特币1小时线数据")
print("=" * 50)

code = 'BTC-USD'
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=3)

print(f"代码：{code}")
print(f"时间范围：{start_date} 至 {end_date}")
print(f"时间粒度：1小时线")
print("\n正在获取数据...")

try:
    df = get_stock_data(
        code=code,
        start_date=start_date,
        end_date=end_date,
        market='加密货币',
        source_type='yfinance',
        interval='1h'
    )
    
    if df is not None and not df.empty:
        print(f"\n✅ 成功获取 {len(df)} 条数据！")
        print(f"\n数据预览：")
        print(df.head(10))
        print(f"\n最新数据：")
        print(df.tail(3))
        print(f"\n最新价格：${df['close'].iloc[-1]:,.2f}")
    else:
        print("\n❌ 获取数据失败，返回空数据")
        
except Exception as e:
    print(f"\n❌ 发生错误：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)

