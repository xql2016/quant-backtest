#!/usr/bin/env python3
"""
调试：检查覆盖关系检测
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.auto_optimize_cache import CacheAutoOptimizer

print("=" * 80)
print("🔍 调试：覆盖关系检测")
print("=" * 80)

# 创建优化器
optimizer = CacheAutoOptimizer()

# 扫描缓存
cache_groups = optimizer._scan_caches()

print(f"\n找到 {len(cache_groups)} 个资产组\n")

# 检查每个资产组的覆盖关系
for group_key, caches in cache_groups.items():
    print(f"资产组: {group_key}")
    print(f"缓存数量: {len(caches)}")
    
    for i, cache in enumerate(caches):
        print(f"\n  [{i}] {cache['filename']}")
        print(f"      {cache['start_date']} ~ {cache['end_date']}")
        print(f"      大小: {cache.get('file_size_mb', 0):.2f} MB")
    
    print(f"\n  开始检测覆盖关系...")
    
    # 模拟 _remove_covered_caches 的逻辑
    to_remove = []
    for i, cache_i in enumerate(caches):
        if cache_i in to_remove:
            print(f"  [{i}] 已在删除列表，跳过")
            continue
        
        for j, cache_j in enumerate(caches):
            if i == j:
                continue
            if cache_j in to_remove:
                print(f"  [{j}] 已在删除列表，跳过")
                continue
            
            # 检查覆盖关系
            print(f"\n  检查: [{i}] 是否覆盖 [{j}]")
            print(f"    [{i}] start: {cache_i['start_date']}, end: {cache_i['end_date']}")
            print(f"    [{j}] start: {cache_j['start_date']}, end: {cache_j['end_date']}")
            
            if (cache_i['start_date'] <= cache_j['start_date'] and
                cache_i['end_date'] >= cache_j['end_date']):
                print(f"    ✅ [{i}] 覆盖 [{j}]")
                to_remove.append(cache_j)
            else:
                print(f"    ❌ 不覆盖")
                if cache_i['start_date'] > cache_j['start_date']:
                    print(f"       原因: [{i}].start ({cache_i['start_date']}) > [{j}].start ({cache_j['start_date']})")
                if cache_i['end_date'] < cache_j['end_date']:
                    print(f"       原因: [{i}].end ({cache_i['end_date']}) < [{j}].end ({cache_j['end_date']})")
    
    print(f"\n  结果:")
    if to_remove:
        print(f"    需要删除 {len(to_remove)} 个缓存:")
        for cache in to_remove:
            print(f"      - {cache['filename']}")
    else:
        print(f"    未发现需要删除的缓存")

print("\n" + "=" * 80)
