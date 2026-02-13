"""
简单测试：验证工具基本功能
"""

from pathlib import Path

# 测试导入
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from tools.merge_continuous_caches import CacheMergeTool
    from tools.check_cache_overlap import CacheOverlapTool
    from tools.auto_optimize_cache import CacheAutoOptimizer
    
    print("✅ 所有工具导入成功")
    
    # 测试初始化
    merge_tool = CacheMergeTool()
    print(f"✅ CacheMergeTool 初始化成功")
    print(f"   - cache_root: {merge_tool.cache_root}")
    print(f"   - data_dir: {merge_tool.data_dir}")
    
    overlap_tool = CacheOverlapTool()
    print(f"✅ CacheOverlapTool 初始化成功")
    
    optimizer = CacheAutoOptimizer()
    print(f"✅ CacheAutoOptimizer 初始化成功")
    
    # 扫描缓存
    print("\n扫描缓存文件...")
    cache_groups = optimizer._scan_caches()
    print(f"✅ 找到 {len(cache_groups)} 个资产组")
    
    for group_key, caches in cache_groups.items():
        print(f"\n资产组: {group_key}")
        print(f"  缓存数量: {len(caches)}")
        for cache in caches:
            print(f"  - {cache['filename']} ({cache['start_date']} ~ {cache['end_date']})")
    
    print("\n✅ 测试完成！工具运行正常")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
