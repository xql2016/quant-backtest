#!/usr/bin/env python3
"""
超详细调试：逐步检查 _scan_caches 方法
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.auto_optimize_cache import CacheAutoOptimizer

print("=" * 80)
print("🔍 超详细调试：_scan_caches 方法")
print("=" * 80)

# 创建优化器
optimizer = CacheAutoOptimizer()

print(f"\n1. 优化器初始化:")
print(f"   cache_root: {optimizer.cache_root}")
print(f"   data_dir: {optimizer.data_dir}")
print(f"   data_dir 存在: {optimizer.data_dir.exists()}")
print(f"   data_dir 绝对路径: {optimizer.data_dir.absolute()}")

print(f"\n2. 使用 rglob 查找 parquet 文件:")
parquet_files = list(optimizer.data_dir.rglob("*.parquet"))
print(f"   找到 {len(parquet_files)} 个文件")
for file_path in parquet_files:
    print(f"   - {file_path}")

print(f"\n3. 调用 _parse_cache_file 解析每个文件:")
cache_groups = {}

for file_path in parquet_files:
    print(f"\n   文件: {file_path}")
    
    # 直接调用 _parse_cache_file
    info = optimizer._parse_cache_file(file_path)
    
    if info:
        print(f"   ✅ 解析成功")
        print(f"      data_source: {info['data_source']}")
        print(f"      market: {info['market']}")
        print(f"      code: {info['code']}")
        print(f"      start_date: {info['start_date']}")
        print(f"      end_date: {info['end_date']}")
        print(f"      interval: {info['interval']}")
        
        # 生成分组键
        group_key = f"{info['data_source']}_{info['market']}_{info['code']}_{info['interval']}"
        print(f"      group_key: {group_key}")
        
        if group_key not in cache_groups:
            cache_groups[group_key] = []
        cache_groups[group_key].append(info)
    else:
        print(f"   ❌ 解析失败 (返回 None)")

print(f"\n4. 分组结果:")
print(f"   找到 {len(cache_groups)} 个资产组")

for group_key, caches in cache_groups.items():
    print(f"\n   资产组: {group_key}")
    print(f"   缓存数量: {len(caches)}")
    for cache in caches:
        print(f"     - {cache['filename']} ({cache['start_date']} ~ {cache['end_date']})")

print(f"\n5. 对比：直接调用 _scan_caches():")
result = optimizer._scan_caches()
print(f"   返回的资产组数: {len(result)}")

print("\n" + "=" * 80)
