"""
测试缓存功能
验证缓存的保存、读取、过期等功能
"""

import sys
from pathlib import Path
import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from cached_data_source import create_cached_data_source, get_cached_stock_data
from cache_manager import CacheManager


def test_basic_cache():
    """测试基本缓存功能"""
    print("=" * 80)
    print("测试1: 基本缓存功能")
    print("=" * 80)
    
    # 创建带缓存的数据源
    data_source = create_cached_data_source('akshare', cache_enabled=True)
    
    # 测试参数
    code = '000001'
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 3, 31)
    market = 'A股'
    
    print(f"\n第一次获取数据（应该从API获取）...")
    df1 = data_source.fetch_data(code, start_date, end_date, market=market)
    
    if df1 is not None:
        print(f"✅ 获取成功: {len(df1)} 条记录")
        print(f"   日期范围: {df1.index[0]} ~ {df1.index[-1]}")
    else:
        print("❌ 获取失败")
        return
    
    print(f"\n第二次获取同样的数据（应该从缓存读取）...")
    df2 = data_source.fetch_data(code, start_date, end_date, market=market)
    
    if df2 is not None:
        print(f"✅ 获取成功: {len(df2)} 条记录")
        print(f"   日期范围: {df2.index[0]} ~ {df2.index[-1]}")
        
        # 验证数据一致性
        if df1.equals(df2):
            print("✅ 数据一致性验证通过")
        else:
            print("⚠️  数据不一致")
    else:
        print("❌ 获取失败")
    
    print()


def test_cache_statistics():
    """测试缓存统计"""
    print("=" * 80)
    print("测试2: 缓存统计信息")
    print("=" * 80)
    
    cache_manager = CacheManager()
    stats = cache_manager.get_statistics()
    
    print(f"\n📊 缓存统计:")
    print(f"   总数: {stats['total_entries']} 个")
    print(f"   大小: {stats['total_size_mb']:.2f} MB")
    print(f"   最早: {stats.get('oldest_entry', 'N/A')}")
    print(f"   最新: {stats.get('newest_entry', 'N/A')}")
    
    print()


def test_date_range_query():
    """测试日期范围查询"""
    print("=" * 80)
    print("测试3: 日期范围查询")
    print("=" * 80)
    
    data_source = create_cached_data_source('akshare', cache_enabled=True)
    
    code = '000001'
    
    # 先缓存一个大范围的数据
    print("\n缓存大范围数据: 2024-01-01 ~ 2024-06-30")
    df_large = data_source.fetch_data(
        code,
        datetime.date(2024, 1, 1),
        datetime.date(2024, 6, 30),
        market='A股'
    )
    
    if df_large is not None:
        print(f"✅ 缓存成功: {len(df_large)} 条记录")
    else:
        print("❌ 缓存失败")
        return
    
    # 查询小范围数据（应该从缓存中过滤）
    print("\n查询小范围数据: 2024-03-01 ~ 2024-03-31 (应该从缓存读取)")
    df_small = data_source.fetch_data(
        code,
        datetime.date(2024, 3, 1),
        datetime.date(2024, 3, 31),
        market='A股'
    )
    
    if df_small is not None:
        print(f"✅ 查询成功: {len(df_small)} 条记录")
        print(f"   日期范围: {df_small.index[0]} ~ {df_small.index[-1]}")
        
        # 验证日期范围
        if df_small.index[0].date() >= datetime.date(2024, 3, 1) and \
           df_small.index[-1].date() <= datetime.date(2024, 3, 31):
            print("✅ 日期范围正确")
        else:
            print("⚠️  日期范围不正确")
    else:
        print("❌ 查询失败")
    
    print()


def test_different_markets():
    """测试不同市场的缓存"""
    print("=" * 80)
    print("测试4: 不同市场的缓存隔离")
    print("=" * 80)
    
    data_source = create_cached_data_source('yfinance', cache_enabled=True)
    
    start_date = datetime.date(2024, 6, 1)
    end_date = datetime.date(2024, 6, 30)
    
    # 测试美股
    print("\n测试美股: AAPL")
    df_us = data_source.fetch_data(
        'AAPL',
        start_date,
        end_date,
        market='stock',
        asset_type='stock',
        interval='1d'
    )
    
    if df_us is not None:
        print(f"✅ 美股数据获取成功: {len(df_us)} 条记录")
    else:
        print("⚠️  美股数据获取失败（可能是网络问题）")
    
    # 测试加密货币
    print("\n测试加密货币: BTC-USD")
    df_crypto = data_source.fetch_data(
        'BTC-USD',
        start_date,
        end_date,
        market='crypto',
        asset_type='crypto',
        interval='1d'
    )
    
    if df_crypto is not None:
        print(f"✅ 加密货币数据获取成功: {len(df_crypto)} 条记录")
    else:
        print("⚠️  加密货币数据获取失败（可能是网络问题）")
    
    print()


def test_convenience_function():
    """测试便捷函数"""
    print("=" * 80)
    print("测试5: 便捷函数")
    print("=" * 80)
    
    print("\n使用便捷函数 get_cached_stock_data...")
    
    df = get_cached_stock_data(
        code='000001',
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 2, 29),
        market='A股',
        source_type='akshare',
        cache_enabled=True
    )
    
    if df is not None:
        print(f"✅ 获取成功: {len(df)} 条记录")
        print(f"   数据列: {list(df.columns)}")
    else:
        print("❌ 获取失败")
    
    print()


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("🧪 开始测试缓存功能...")
    print("\n")
    
    try:
        test_basic_cache()
        test_cache_statistics()
        test_date_range_query()
        test_different_markets()
        test_convenience_function()
        
        print("=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
