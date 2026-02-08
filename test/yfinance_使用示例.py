#!/usr/bin/env python3
"""
YFinance数据源使用示例
支持美股、港股、加密货币的数据获取和分析
"""

import datetime
import pandas as pd
from data_source import get_stock_data, YFinanceDataSource, DataSourceFactory

print("=" * 80)
print("YFinance 数据源使用示例")
print("=" * 80)


def example1_us_stocks():
    """示例1：获取美股数据"""
    print("\n" + "=" * 80)
    print("示例1：美股数据获取")
    print("=" * 80)
    
    # 定义要分析的美股
    us_stocks = [
        ('AAPL', '苹果'),
        ('TSLA', '特斯拉'),
        ('MSFT', '微软'),
        ('GOOGL', '谷歌'),
        ('NVDA', '英伟达')
    ]
    
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 2, 7)
    
    print(f"\n数据范围: {start_date} 至 {end_date}\n")
    
    for code, name in us_stocks[:2]:  # 只获取前2个以节省时间
        print(f"\n📊 获取 {name} ({code}) 数据...")
        
        try:
            df = get_stock_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                source_type='yfinance'
            )
            
            if df is not None and not df.empty:
                print(f"✅ 成功获取 {len(df)} 天的数据")
                print(f"   价格区间: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
                print(f"   最新收盘价: ${df['close'].iloc[-1]:.2f}")
                
                # 计算收益率
                returns = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
                print(f"   期间收益: {returns:+.2f}%")
            else:
                print(f"❌ 数据获取失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")


def example2_hk_stocks():
    """示例2：获取港股数据"""
    print("\n" + "=" * 80)
    print("示例2：港股数据获取")
    print("=" * 80)
    
    # 港股代码需要加 .HK 后缀
    hk_stocks = [
        ('0700.HK', '腾讯控股'),
        ('9988.HK', '阿里巴巴'),
        ('1810.HK', '小米集团'),
        ('3690.HK', '美团'),
        ('2318.HK', '中国平安')
    ]
    
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 2, 7)
    
    print(f"\n数据范围: {start_date} 至 {end_date}")
    print("💡 提示: 港股代码需要加 .HK 后缀\n")
    
    for code, name in hk_stocks[:2]:  # 只获取前2个
        print(f"\n📊 获取 {name} ({code}) 数据...")
        
        try:
            df = get_stock_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                source_type='yfinance'
            )
            
            if df is not None and not df.empty:
                print(f"✅ 成功获取 {len(df)} 天的数据")
                print(f"   价格区间: HK${df['close'].min():.2f} - HK${df['close'].max():.2f}")
                print(f"   最新收盘价: HK${df['close'].iloc[-1]:.2f}")
                
                # 计算收益率
                returns = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
                print(f"   期间收益: {returns:+.2f}%")
            else:
                print(f"❌ 数据获取失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")


def example3_crypto():
    """示例3：获取加密货币数据"""
    print("\n" + "=" * 80)
    print("示例3：加密货币数据获取")
    print("=" * 80)
    
    # 加密货币代码格式: XXX-USD
    cryptos = [
        ('BTC-USD', '比特币'),
        ('ETH-USD', '以太坊'),
        ('BNB-USD', '币安币'),
        ('SOL-USD', 'Solana'),
        ('ADA-USD', 'Cardano')
    ]
    
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 2, 7)
    
    print(f"\n数据范围: {start_date} 至 {end_date}")
    print("💡 提示: 加密货币代码格式为 XXX-USD\n")
    
    for code, name in cryptos[:2]:  # 只获取前2个
        print(f"\n📊 获取 {name} ({code}) 数据...")
        
        try:
            df = get_stock_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                source_type='yfinance',
                asset_type='crypto'
            )
            
            if df is not None and not df.empty:
                print(f"✅ 成功获取 {len(df)} 天的数据")
                print(f"   价格区间: ${df['close'].min():,.2f} - ${df['close'].max():,.2f}")
                print(f"   最新价格: ${df['close'].iloc[-1]:,.2f}")
                
                # 计算收益率
                returns = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
                print(f"   期间收益: {returns:+.2f}%")
                
                # 计算波动率
                volatility = df['close'].pct_change().std() * (252 ** 0.5) * 100
                print(f"   年化波动率: {volatility:.2f}%")
            else:
                print(f"❌ 数据获取失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")


def example4_asset_info():
    """示例4：获取资产信息"""
    print("\n" + "=" * 80)
    print("示例4：获取资产详细信息")
    print("=" * 80)
    
    # 创建YFinance数据源
    yf_source = YFinanceDataSource()
    
    assets = [
        ('AAPL', '苹果'),
        ('0700.HK', '腾讯'),
        ('BTC-USD', '比特币')
    ]
    
    print("\n获取资产基本信息:\n")
    
    for code, name in assets:
        print(f"📌 {name} ({code})")
        info = yf_source.get_info(code)
        
        if 'error' not in info:
            print(f"   名称: {info.get('name', 'N/A')}")
            print(f"   市场: {info.get('market', 'N/A')}")
            print(f"   币种: {info.get('currency', 'N/A')}")
            print(f"   交易所: {info.get('exchange', 'N/A')}")
            print(f"   类型: {info.get('type', 'N/A')}")
        else:
            print(f"   ❌ 获取失败: {info['error']}")
        print()


def example5_comparison():
    """示例5：多资产对比分析"""
    print("\n" + "=" * 80)
    print("示例5：多资产收益对比")
    print("=" * 80)
    
    # 对比不同市场的代表性资产
    assets = [
        ('SPY', '标普500ETF', '美股'),
        ('0700.HK', '腾讯', '港股'),
        ('BTC-USD', '比特币', '加密货币')
    ]
    
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 2, 7)
    
    print(f"\n数据范围: {start_date} 至 {end_date}\n")
    print(f"{'资产':<15} {'市场':<10} {'期初价格':<12} {'期末价格':<12} {'收益率':<10}")
    print("-" * 70)
    
    results = []
    
    for code, name, market in assets:
        try:
            df = get_stock_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                source_type='yfinance'
            )
            
            if df is not None and not df.empty:
                start_price = df['close'].iloc[0]
                end_price = df['close'].iloc[-1]
                returns = (end_price - start_price) / start_price * 100
                
                print(f"{name:<15} {market:<10} ${start_price:>10,.2f} ${end_price:>10,.2f} {returns:>8.2f}%")
                results.append((name, returns))
            else:
                print(f"{name:<15} {market:<10} {'数据获取失败':>40}")
                
        except Exception as e:
            print(f"{name:<15} {market:<10} 错误: {e}")
    
    if results:
        print("\n" + "=" * 70)
        best = max(results, key=lambda x: x[1])
        print(f"🏆 最佳表现: {best[0]} ({best[1]:+.2f}%)")


def example6_factory_usage():
    """示例6：使用工厂模式创建数据源"""
    print("\n" + "=" * 80)
    print("示例6：使用DataSourceFactory")
    print("=" * 80)
    
    print("\n使用工厂模式创建不同类型的数据源:\n")
    
    # 创建yfinance数据源
    yf_source = DataSourceFactory.create_data_source('yfinance')
    print(f"✅ 创建 YFinance 数据源: {type(yf_source).__name__}")
    
    # 获取数据
    code = 'AAPL'
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 1, 31)
    
    print(f"\n使用工厂创建的数据源获取 {code} 数据...")
    df = yf_source.fetch_data(code, start_date, end_date)
    
    if df is not None and not df.empty:
        print(f"✅ 成功获取 {len(df)} 天的数据")
        print(f"\n数据预览:")
        print(df.head())
    else:
        print("❌ 数据获取失败")


if __name__ == "__main__":
    print("\n🚀 YFinance 数据源功能演示\n")
    
    try:
        # 运行所有示例
        example1_us_stocks()      # 美股
        example2_hk_stocks()      # 港股
        example3_crypto()         # 加密货币
        example4_asset_info()     # 资产信息
        example5_comparison()     # 多资产对比
        example6_factory_usage()  # 工厂模式
        
        print("\n" + "=" * 80)
        print("✅ 所有示例运行完成！")
        print("=" * 80)
        
        print("\n💡 使用提示:")
        print("   1. 美股代码: 直接使用代码，如 AAPL, TSLA")
        print("   2. 港股代码: 需要加 .HK 后缀，如 0700.HK, 9988.HK")
        print("   3. 加密货币: 使用 XXX-USD 格式，如 BTC-USD, ETH-USD")
        print("   4. 支持获取资产详细信息")
        print("   5. 支持不同时间间隔（1d, 1h等）")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()

