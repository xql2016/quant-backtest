"""
缓存功能使用示例
演示如何使用数据缓存功能
"""

import datetime
from cached_data_source import create_cached_data_source, get_cached_stock_data


def example1_basic_usage():
    """示例1：基本使用 - 使用装饰器"""
    print("=" * 80)
    print("示例1：基本使用")
    print("=" * 80)
    
    # 创建带缓存的数据源
    data_source = create_cached_data_source('akshare', cache_enabled=True)
    
    # 获取数据
    code = '000001'
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 3, 31)
    
    print(f"\n获取数据: {code}, {start_date} ~ {end_date}")
    df = data_source.fetch_data(code, start_date, end_date, market='A股')
    
    if df is not None:
        print(f"✅ 成功获取 {len(df)} 条记录")
        print(f"   数据列: {list(df.columns)}")
        print(f"   日期范围: {df.index[0].date()} ~ {df.index[-1].date()}")
        print(f"\n前5条数据:")
        print(df.head())
    else:
        print("❌ 获取失败")
    
    print()


def example2_convenience_function():
    """示例2：使用便捷函数"""
    print("=" * 80)
    print("示例2：使用便捷函数（最简单）")
    print("=" * 80)
    
    print("\n使用 get_cached_stock_data 一行代码获取数据...")
    
    df = get_cached_stock_data(
        code='000001',
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 2, 29),
        market='A股',
        source_type='akshare',
        cache_enabled=True
    )
    
    if df is not None:
        print(f"✅ 成功获取 {len(df)} 条记录")
        print(f"   数据形状: {df.shape}")
    else:
        print("❌ 获取失败")
    
    print()


def example3_different_sources():
    """示例3：不同数据源"""
    print("=" * 80)
    print("示例3：使用不同数据源")
    print("=" * 80)
    
    # AKShare - A股
    print("\n1. AKShare - A股")
    ds_akshare = create_cached_data_source('akshare')
    df_a = ds_akshare.fetch_data(
        '000001',
        datetime.date(2024, 6, 1),
        datetime.date(2024, 6, 30),
        market='A股'
    )
    if df_a is not None:
        print(f"   ✅ A股数据: {len(df_a)} 条")
    
    # YFinance - 美股
    print("\n2. YFinance - 美股")
    ds_yfinance = create_cached_data_source('yfinance')
    df_us = ds_yfinance.fetch_data(
        'AAPL',
        datetime.date(2024, 6, 1),
        datetime.date(2024, 6, 30),
        market='stock',
        interval='1d'
    )
    if df_us is not None:
        print(f"   ✅ 美股数据: {len(df_us)} 条")
    else:
        print("   ⚠️  美股数据获取失败（可能是网络问题）")
    
    # YFinance - 加密货币
    print("\n3. YFinance - 加密货币")
    df_crypto = ds_yfinance.fetch_data(
        'BTC-USD',
        datetime.date(2024, 6, 1),
        datetime.date(2024, 6, 30),
        market='crypto',
        interval='1d'
    )
    if df_crypto is not None:
        print(f"   ✅ 加密货币数据: {len(df_crypto)} 条")
    else:
        print("   ⚠️  加密货币数据获取失败（可能是网络问题）")
    
    print()


def example4_cache_statistics():
    """示例4：查看缓存统计"""
    print("=" * 80)
    print("示例4：缓存统计")
    print("=" * 80)
    
    from cache_manager import CacheManager
    
    cache_manager = CacheManager()
    stats = cache_manager.get_statistics()
    
    print(f"\n📊 缓存统计信息:")
    print(f"   缓存总数: {stats['total_entries']} 个")
    print(f"   缓存大小: {stats['total_size_mb']:.2f} MB")
    print(f"   最早缓存: {stats.get('oldest_entry', 'N/A')}")
    print(f"   最新缓存: {stats.get('newest_entry', 'N/A')}")
    
    print()


def example5_date_range_filtering():
    """示例5：日期范围过滤"""
    print("=" * 80)
    print("示例5：日期范围过滤")
    print("=" * 80)
    
    data_source = create_cached_data_source('akshare')
    code = '000001'
    
    # 先获取大范围数据
    print("\n1. 获取大范围数据: 2024-01-01 ~ 2024-06-30")
    df_large = data_source.fetch_data(
        code,
        datetime.date(2024, 1, 1),
        datetime.date(2024, 6, 30),
        market='A股'
    )
    
    if df_large is not None:
        print(f"   ✅ 获取成功: {len(df_large)} 条记录")
    
    # 再获取小范围数据（应该从缓存读取）
    print("\n2. 获取小范围数据: 2024-03-01 ~ 2024-03-31 (从缓存过滤)")
    df_small = data_source.fetch_data(
        code,
        datetime.date(2024, 3, 1),
        datetime.date(2024, 3, 31),
        market='A股'
    )
    
    if df_small is not None:
        print(f"   ✅ 获取成功: {len(df_small)} 条记录")
        print(f"   日期范围: {df_small.index[0].date()} ~ {df_small.index[-1].date()}")
    
    print()


def example6_disable_cache():
    """示例6：禁用缓存"""
    print("=" * 80)
    print("示例6：禁用缓存（需要实时数据时）")
    print("=" * 80)
    
    # 创建不带缓存的数据源
    data_source = create_cached_data_source('akshare', cache_enabled=False)
    
    print("\n获取数据（不使用缓存）...")
    df = data_source.fetch_data(
        '000001',
        datetime.date(2024, 1, 1),
        datetime.date(2024, 1, 31),
        market='A股'
    )
    
    if df is not None:
        print(f"✅ 获取成功: {len(df)} 条记录（未缓存）")
    
    print()


def main():
    """运行所有示例"""
    print("\n")
    print("🎯 数据缓存功能使用示例")
    print("\n")
    
    try:
        # 运行示例
        example1_basic_usage()
        example2_convenience_function()
        example3_different_sources()
        example4_cache_statistics()
        example5_date_range_filtering()
        example6_disable_cache()
        
        print("=" * 80)
        print("✅ 所有示例运行完成！")
        print("=" * 80)
        print()
        print("💡 提示:")
        print("   - 第一次运行会从API获取数据（较慢）")
        print("   - 第二次运行会从缓存读取数据（极快）")
        print("   - 使用 'python test/cache_tool.py' 查看和管理缓存")
        print()
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
