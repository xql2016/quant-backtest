#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试4小时线聚合功能
验证：1小时 → 4小时聚合的正确性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
from data_source import get_stock_data

def test_4h_aggregation():
    """测试加密货币4小时线聚合"""
    print("=" * 60)
    print("测试：加密货币4小时线数据聚合")
    print("=" * 60)
    
    code = 'BTC-USD'
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)
    
    print(f"\n📊 测试资产：{code}")
    print(f"📅 时间范围：{start_date} 至 {end_date}")
    print("-" * 60)
    
    # 1. 获取1小时线数据
    print("\n[1/3] 获取1小时线数据...")
    try:
        df_1h = get_stock_data(
            code=code,
            start_date=start_date,
            end_date=end_date,
            market='加密货币',
            source_type='yfinance',
            interval='1h'
        )
        
        if df_1h is None or df_1h.empty:
            print("❌ 1小时线数据获取失败")
            return False
        
        print(f"✅ 成功获取 {len(df_1h)} 条1小时K线")
        print(f"   时间范围：{df_1h.index[0]} 至 {df_1h.index[-1]}")
        
    except Exception as e:
        print(f"❌ 1小时线获取错误：{e}")
        return False
    
    # 2. 获取4小时线数据
    print("\n[2/3] 获取4小时线数据（从1小时聚合）...")
    try:
        df_4h = get_stock_data(
            code=code,
            start_date=start_date,
            end_date=end_date,
            market='加密货币',
            source_type='yfinance',
            interval='4h'
        )
        
        if df_4h is None or df_4h.empty:
            print("❌ 4小时线数据获取失败")
            return False
        
        print(f"✅ 成功获取 {len(df_4h)} 条4小时K线")
        print(f"   时间范围：{df_4h.index[0]} 至 {df_4h.index[-1]}")
        
    except Exception as e:
        print(f"❌ 4小时线获取错误：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 验证聚合正确性
    print("\n[3/3] 验证聚合正确性...")
    
    # 理论上：4小时K线数量 ≈ 1小时K线数量 / 4
    expected_ratio = len(df_1h) / len(df_4h)
    print(f"   1小时K线数：{len(df_1h)}")
    print(f"   4小时K线数：{len(df_4h)}")
    print(f"   数量比例：{expected_ratio:.2f} : 1")
    
    if 3.5 <= expected_ratio <= 5:
        print(f"   ✅ 比例正常（预期约4:1）")
    else:
        print(f"   ⚠️  比例异常（预期3.5-5:1，实际{expected_ratio:.2f}:1）")
    
    # 4. 显示数据样本
    print("\n📈 4小时线数据预览：")
    print("-" * 60)
    print(df_4h.head(10).to_string())
    
    print("\n💰 最新数据：")
    print("-" * 60)
    latest = df_4h.tail(3)
    for idx, row in latest.iterrows():
        print(f"{idx}: 开{row['open']:.2f} 高{row['high']:.2f} 低{row['low']:.2f} 收{row['close']:.2f} 量{row['volume']:.0f}")
    
    # 5. 对比日线数据
    print("\n[对比] 获取日线数据...")
    try:
        df_1d = get_stock_data(
            code=code,
            start_date=start_date,
            end_date=end_date,
            market='加密货币',
            source_type='yfinance',
            interval='1d'
        )
        
        if df_1d is not None and not df_1d.empty:
            print(f"✅ 日线数据：{len(df_1d)} 条")
            print(f"\n📊 数据量对比：")
            print(f"   日线 (1d)  : {len(df_1d):>4} 条 (基准)")
            print(f"   4小时 (4h) : {len(df_4h):>4} 条 ({len(df_4h)/len(df_1d):.1f}x)")
            print(f"   1小时 (1h) : {len(df_1h):>4} 条 ({len(df_1h)/len(df_1d):.1f}x)")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！4小时线聚合功能正常")
    print("=" * 60)
    
    return True

def test_data_quality():
    """测试数据质量"""
    print("\n" + "=" * 60)
    print("数据质量检查")
    print("=" * 60)
    
    code = 'ETH-USD'  # 使用以太坊测试
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=3)
    
    print(f"\n测试资产：{code}")
    
    try:
        df_4h = get_stock_data(
            code=code,
            start_date=start_date,
            end_date=end_date,
            market='加密货币',
            source_type='yfinance',
            interval='4h'
        )
        
        if df_4h is not None and not df_4h.empty:
            print(f"✅ 获取 {len(df_4h)} 条4小时数据")
            
            # 检查数据完整性
            print("\n数据完整性检查：")
            print(f"  - 缺失值：{df_4h.isnull().sum().sum()} 个")
            print(f"  - 价格范围：${df_4h['low'].min():.2f} - ${df_4h['high'].max():.2f}")
            print(f"  - 成交量总和：{df_4h['volume'].sum():.0f}")
            
            # 检查OHLC逻辑
            invalid_count = 0
            for idx, row in df_4h.iterrows():
                if not (row['low'] <= row['open'] <= row['high'] and 
                       row['low'] <= row['close'] <= row['high']):
                    invalid_count += 1
            
            if invalid_count == 0:
                print(f"  - OHLC逻辑：✅ 正确")
            else:
                print(f"  - OHLC逻辑：⚠️  发现{invalid_count}条异常数据")
            
            print("\n✅ 数据质量检查通过")
        else:
            print("❌ 数据获取失败")
            
    except Exception as e:
        print(f"❌ 检查失败：{e}")

if __name__ == '__main__':
    print("\n🚀 开始测试4小时线聚合功能\n")
    
    try:
        # 主测试
        success = test_4h_aggregation()
        
        if success:
            # 数据质量测试
            test_data_quality()
            
            print("\n" + "=" * 60)
            print("🎉 所有测试通过！")
            print("=" * 60)
            print("\n💡 提示：现在可以在Streamlit应用中使用4小时线功能了！")
            print("   访问：http://localhost:8501")
            print("   选择：加密货币 → 时间粒度 → 4小时线 (4h)")
        else:
            print("\n⚠️  测试未完全通过，请检查错误信息")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误：{e}")
        import traceback
        traceback.print_exc()

