"""
测试缓存智能日期匹配功能
验证：大范围缓存能覆盖小范围查询
"""

import sys
from pathlib import Path
import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from cached_data_source import create_cached_data_source


def test_smart_date_matching():
    """测试智能日期匹配"""
    print("=" * 80)
    print("测试：智能日期范围匹配")
    print("=" * 80)
    
    data_source = create_cached_data_source('tushare', cache_enabled=True, 
                                           token='9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4')
    
    code = '000001'
    
    # 场景1：先缓存大范围数据
    print("\n【场景1】缓存大范围数据：2024-01-01 ~ 2024-12-31")
    print("-" * 80)
    
    df_large = data_source.fetch_data(
        code,
        datetime.date(2024, 1, 1),
        datetime.date(2024, 12, 31),
        market='A股'
    )
    
    if df_large is not None and not df_large.empty:
        print(f"✅ 大范围数据获取成功: {len(df_large)} 条记录")
        print(f"   日期范围: {df_large.index[0].date()} ~ {df_large.index[-1].date()}")
    else:
        print("❌ 大范围数据获取失败")
        return
    
    # 场景2：查询小范围数据（应该从大缓存中获取）
    print("\n【场景2】查询小范围数据：2024-03-01 ~ 2024-06-30")
    print("期望：从大缓存中过滤，不创建新缓存")
    print("-" * 80)
    
    df_small = data_source.fetch_data(
        code,
        datetime.date(2024, 3, 1),
        datetime.date(2024, 6, 30),
        market='A股'
    )
    
    if df_small is not None and not df_small.empty:
        print(f"✅ 小范围数据获取成功: {len(df_small)} 条记录")
        print(f"   日期范围: {df_small.index[0].date()} ~ {df_small.index[-1].date()}")
        
        # 验证日期范围
        if (df_small.index[0].date() >= datetime.date(2024, 3, 1) and
            df_small.index[-1].date() <= datetime.date(2024, 6, 30)):
            print("✅ 日期范围正确过滤")
        else:
            print("⚠️  日期范围过滤不正确")
    else:
        print("❌ 小范围数据获取失败")
        return
    
    # 场景3：查看缓存文件
    print("\n【场景3】检查缓存文件")
    print("-" * 80)
    
    cache_dir = Path("cache/data/tushare/a_stock")
    if cache_dir.exists():
        files = list(cache_dir.glob("000001_*.parquet"))
        print(f"缓存文件数量: {len(files)} 个")
        for f in files:
            size_kb = f.stat().st_size / 1024
            print(f"   - {f.name} ({size_kb:.2f} KB)")
        
        # 验证：应该只有1个大范围的缓存文件
        large_cache = [f for f in files if '20240101_20241231' in f.name]
        small_cache = [f for f in files if '20240301_20240630' in f.name]
        
        if large_cache and not small_cache:
            print("\n✅ 优化成功！只有大范围缓存，没有创建小范围缓存")
        elif large_cache and small_cache:
            print("\n⚠️  存在重复缓存：同时有大范围和小范围缓存")
        else:
            print("\n❌ 缓存文件不符合预期")
    
    # 场景4：多次查询不同小范围（都应该使用同一个大缓存）
    print("\n【场景4】多次查询不同小范围")
    print("-" * 80)
    
    test_ranges = [
        (datetime.date(2024, 1, 1), datetime.date(2024, 2, 28), "1-2月"),
        (datetime.date(2024, 4, 1), datetime.date(2024, 5, 31), "4-5月"),
        (datetime.date(2024, 7, 1), datetime.date(2024, 9, 30), "7-9月"),
    ]
    
    for start, end, label in test_ranges:
        df = data_source.fetch_data(code, start, end, market='A股')
        if df is not None and not df_empty:
            print(f"✅ {label}: {len(df)} 条记录 ({df.index[0].date()} ~ {df.index[-1].date()})")
        else:
            print(f"❌ {label}: 获取失败")
    
    # 场景5：查看缓存统计
    print("\n【场景5】缓存统计")
    print("-" * 80)
    
    from cache_manager import CacheManager
    cache_manager = CacheManager()
    stats = cache_manager.get_statistics()
    
    print(f"缓存总数: {stats['total_entries']} 个")
    print(f"缓存大小: {stats['total_size_mb']:.2f} MB")
    
    # 列出所有 000001 的缓存
    entries = cache_manager.index.get_all_entries()
    code_caches = [k for k in entries.keys() if '000001' in k]
    
    print(f"\n000001 的缓存:")
    for key in code_caches:
        entry = entries[key]
        print(f"   - {entry['start_date']} ~ {entry['end_date']}")
        print(f"     访问次数: {entry.get('access_count', 0)}")
        print(f"     大小: {entry.get('file_size_kb', 0):.2f} KB")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == '__main__':
    test_smart_date_matching()
