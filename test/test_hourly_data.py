#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试加密货币1小时线数据获取
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
from data_source import get_stock_data

def test_hourly_crypto_data():
    """测试加密货币1小时线数据"""
    print("=" * 60)
    print("测试：加密货币1小时线数据获取")
    print("=" * 60)
    
    # 测试比特币1小时线（最近7天）
    code = 'BTC-USD'
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)
    
    print(f"\n正在获取 {code} 的1小时线数据...")
    print(f"时间范围：{start_date} 至 {end_date}")
    
    # 获取1小时线数据
    df_1h = get_stock_data(
        code=code,
        start_date=start_date,
        end_date=end_date,
        market='加密货币',
        source_type='yfinance',
        interval='1h'
    )
    
    if df_1h is not None and not df_1h.empty:
        print(f"\n✅ 成功获取数据！")
        print(f"数据条数：{len(df_1h)} 条")
        print(f"时间范围：{df_1h.index[0]} 至 {df_1h.index[-1]}")
        print(f"\n前5条数据：")
        print(df_1h.head())
        print(f"\n最新价格：${df_1h['close'].iloc[-1]:,.2f}")
        
        # 验证是否是1小时间隔
        if len(df_1h) > 1:
            time_diff = df_1h.index[1] - df_1h.index[0]
            print(f"\n数据间隔：{time_diff}")
            
    else:
        print("❌ 获取数据失败！")
        return False
    
    print("\n" + "=" * 60)
    print("测试：日线数据对比")
    print("=" * 60)
    
    # 对比日线数据
    df_1d = get_stock_data(
        code=code,
        start_date=start_date,
        end_date=end_date,
        market='加密货币',
        source_type='yfinance',
        interval='1d'
    )
    
    if df_1d is not None and not df_1d.empty:
        print(f"\n✅ 日线数据获取成功！")
        print(f"数据条数：{len(df_1d)} 条")
        print(f"\n对比：")
        print(f"  - 1小时线：{len(df_1h)} 条数据")
        print(f"  - 日线：{len(df_1d)} 条数据")
        print(f"  - 比例：{len(df_1h) / len(df_1d):.1f}:1")
        
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    
    return True

def test_stock_fallback():
    """测试股票市场回退到日线"""
    print("\n" + "=" * 60)
    print("测试：股票市场使用日线（interval参数被忽略）")
    print("=" * 60)
    
    code = 'AAPL'
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    print(f"\n正在获取 {code} 的数据...")
    
    # 即使传入1h参数，YFinance对美股也只返回可用数据
    df = get_stock_data(
        code=code,
        start_date=start_date,
        end_date=end_date,
        market='美股',
        source_type='yfinance',
        interval='1d'  # 美股使用日线
    )
    
    if df is not None and not df.empty:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print(f"最新收盘价：${df['close'].iloc[-1]:.2f}")
    else:
        print("❌ 获取数据失败！")
    
    return True

if __name__ == '__main__':
    try:
        # 测试加密货币1小时线
        test_hourly_crypto_data()
        
        # 测试股票市场
        test_stock_fallback()
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误：{e}")
        import traceback
        traceback.print_exc()

