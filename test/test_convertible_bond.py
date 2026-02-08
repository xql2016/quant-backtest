#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可转债数据获取功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
from data_source import get_stock_data

def test_convertible_bond_data():
    """测试可转债数据获取"""
    print("=" * 60)
    print("测试：可转债数据获取功能")
    print("=" * 60)
    
    # 测试几个常见的可转债
    test_bonds = [
        ("128039", "国光转债"),
        ("113050", "南银转债"),
        ("127045", "海亮转债")
    ]
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=90)  # 最近90天
    
    print(f"\n📅 测试时间范围：{start_date} 至 {end_date}")
    print("-" * 60)
    
    results = []
    
    for code, name in test_bonds:
        print(f"\n[测试] {code} - {name}")
        
        try:
            df = get_stock_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                market='可转债',
                source_type='akshare'
            )
            
            if df is not None and not df.empty:
                print(f"  ✅ 成功获取 {len(df)} 条数据")
                print(f"  📊 价格范围：{df['low'].min():.2f} - {df['high'].max():.2f} 元")
                print(f"  💰 最新收盘价：{df['close'].iloc[-1]:.2f} 元")
                print(f"  📈 区间涨跌幅：{(df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100:.2f}%")
                
                # 检查数据完整性
                missing = df.isnull().sum().sum()
                print(f"  🔍 缺失值：{missing} 个")
                
                results.append({
                    'code': code,
                    'name': name,
                    'status': '✅ 成功',
                    'data_count': len(df),
                    'latest_price': df['close'].iloc[-1]
                })
            else:
                print(f"  ❌ 数据获取失败")
                results.append({
                    'code': code,
                    'name': name,
                    'status': '❌ 失败',
                    'data_count': 0,
                    'latest_price': None
                })
                
        except Exception as e:
            print(f"  ❌ 错误：{e}")
            results.append({
                'code': code,
                'name': name,
                'status': f'❌ 错误: {str(e)[:30]}',
                'data_count': 0,
                'latest_price': None
            })
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    success_count = sum(1 for r in results if '成功' in r['status'])
    print(f"\n成功：{success_count}/{len(test_bonds)}")
    
    print("\n详细结果：")
    print(f"{'代码':<10} {'名称':<15} {'状态':<15} {'数据量':<10} {'最新价':<10}")
    print("-" * 60)
    for r in results:
        price_str = f"{r['latest_price']:.2f}" if r['latest_price'] else "N/A"
        print(f"{r['code']:<10} {r['name']:<15} {r['status']:<15} {r['data_count']:<10} {price_str:<10}")
    
    return success_count == len(test_bonds)

def test_data_quality():
    """测试数据质量"""
    print("\n" + "=" * 60)
    print("数据质量详细检查")
    print("=" * 60)
    
    code = "128039"  # 国光转债
    name = "国光转债"
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    print(f"\n测试标的：{code} - {name}")
    print(f"时间范围：{start_date} 至 {end_date}")
    
    try:
        df = get_stock_data(
            code=code,
            start_date=start_date,
            end_date=end_date,
            market='可转债',
            source_type='akshare'
        )
        
        if df is not None and not df.empty:
            print(f"\n✅ 数据获取成功：{len(df)} 条")
            
            # 1. 数据完整性
            print("\n[1] 数据完整性检查：")
            print(f"  - 总行数：{len(df)}")
            print(f"  - 缺失值：{df.isnull().sum().sum()} 个")
            print(f"  - 时间跨度：{df.index[0]} 至 {df.index[-1]}")
            
            # 2. OHLC逻辑检查
            print("\n[2] OHLC逻辑检查：")
            invalid_count = 0
            for idx, row in df.iterrows():
                if not (row['low'] <= row['open'] <= row['high'] and 
                       row['low'] <= row['close'] <= row['high']):
                    invalid_count += 1
                    if invalid_count <= 3:  # 只显示前3个
                        print(f"  ⚠️  {idx}: O={row['open']}, H={row['high']}, L={row['low']}, C={row['close']}")
            
            if invalid_count == 0:
                print(f"  ✅ 所有数据符合OHLC逻辑")
            else:
                print(f"  ⚠️  发现 {invalid_count} 条异常数据")
            
            # 3. 价格统计
            print("\n[3] 价格统计：")
            print(f"  - 最高价：{df['high'].max():.2f} 元")
            print(f"  - 最低价：{df['low'].min():.2f} 元")
            print(f"  - 平均收盘价：{df['close'].mean():.2f} 元")
            print(f"  - 最新收盘价：{df['close'].iloc[-1]:.2f} 元")
            
            # 4. 波动性分析
            print("\n[4] 波动性分析：")
            daily_return = df['close'].pct_change()
            print(f"  - 日均涨跌幅：{daily_return.mean() * 100:.2f}%")
            print(f"  - 最大单日涨幅：{daily_return.max() * 100:.2f}%")
            print(f"  - 最大单日跌幅：{daily_return.min() * 100:.2f}%")
            print(f"  - 波动率（标准差）：{daily_return.std() * 100:.2f}%")
            
            # 5. 成交量统计
            print("\n[5] 成交量统计：")
            print(f"  - 平均成交量：{df['volume'].mean():.0f}")
            print(f"  - 最大成交量：{df['volume'].max():.0f}")
            print(f"  - 最小成交量：{df['volume'].min():.0f}")
            
            # 6. 数据预览
            print("\n[6] 数据预览（最近5天）：")
            print(df.tail(5).to_string())
            
            print("\n✅ 数据质量检查完成")
            return True
        else:
            print("\n❌ 数据获取失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 检查失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def test_common_bonds():
    """测试常见可转债列表"""
    print("\n" + "=" * 60)
    print("常见可转债代码参考")
    print("=" * 60)
    
    common_bonds = [
        ("128039", "国光转债", "国光股份"),
        ("113050", "南银转债", "南京银行"),
        ("127045", "海亮转债", "海亮股份"),
        ("123107", "温氏转债", "温氏股份"),
        ("113616", "韦尔转债", "韦尔股份"),
        ("128136", "立讯转债", "立讯精密"),
        ("110053", "苏银转债", "苏州银行"),
    ]
    
    print(f"\n{'代码':<10} {'名称':<15} {'正股':<15}")
    print("-" * 60)
    for code, name, stock in common_bonds:
        print(f"{code:<10} {name:<15} {stock:<15}")
    
    print("\n💡 提示：")
    print("  1. 可转债代码为6位数字")
    print("  2. 交易单位：10张起（1000元面值）")
    print("  3. 价格单位：元（如100.50表示100.50元）")
    print("  4. 回测时使用T+1交易规则（实际可转债是T+0）")

if __name__ == '__main__':
    print("\n🚀 开始测试可转债数据获取功能\n")
    
    try:
        # 1. 基本功能测试
        success = test_convertible_bond_data()
        
        if success:
            # 2. 数据质量测试
            test_data_quality()
            
            # 3. 显示常见可转债
            test_common_bonds()
            
            print("\n" + "=" * 60)
            print("🎉 所有测试通过！")
            print("=" * 60)
            print("\n💡 提示：现在可以在Streamlit应用中使用可转债回测了！")
            print("   访问：http://localhost:8501")
            print("   选择：数据源 → AKShare → 市场 → 可转债")
            print("   代码：128039, 113050, 127045 等")
        else:
            print("\n⚠️  部分测试未通过，请检查错误信息")
            print("💡 常见问题：")
            print("   1. 检查网络连接")
            print("   2. 确认AKShare版本：pip install --upgrade akshare")
            print("   3. 某些可转债可能已退市或代码错误")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误：{e}")
        import traceback
        traceback.print_exc()

