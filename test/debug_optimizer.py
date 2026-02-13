#!/usr/bin/env python3
"""
调试脚本：检查为什么没有发现覆盖关系
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.auto_optimize_cache import CacheAutoOptimizer

# 创建优化器
optimizer = CacheAutoOptimizer()

# 扫描缓存
print("=" * 80)
print("🔍 扫描缓存文件")
print("=" * 80)

cache_groups = optimizer._scan_caches()

print(f"\n找到 {len(cache_groups)} 个资产组\n")

# 详细打印每个资产组
for group_key, caches in cache_groups.items():
    print(f"资产组: {group_key}")
    print(f"缓存数量: {len(caches)}")
    
    for i, cache in enumerate(caches):
        print(f"  [{i}] {cache['filename']}")
        print(f"      开始: {cache['start_date']}")
        print(f"      结束: {cache['end_date']}")
        print(f"      大小: {cache['file_size_mb']:.2f} MB")
    
    # 检查覆盖关系
    print(f"\n  覆盖关系检查:")
    found_coverage = False
    
    for i, cache_i in enumerate(caches):
        for j, cache_j in enumerate(caches):
            if i == j:
                continue
            
            # 检查 cache_i 是否覆盖 cache_j
            if (cache_i['start_date'] <= cache_j['start_date'] and
                cache_i['end_date'] >= cache_j['end_date']):
                print(f"    ✓ [{i}] {cache_i['filename']}")
                print(f"      覆盖 [{j}] {cache_j['filename']}")
                found_coverage = True
    
    if not found_coverage:
        print(f"    ✗ 未发现覆盖关系")
    
    print()
