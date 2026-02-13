#!/usr/bin/env python3
"""
详细调试：检查文件扫描和解析问题
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("🔍 详细调试：缓存扫描")
print("=" * 80)

# 1. 检查目录
data_dir = Path("cache/data")
print(f"\n1. 检查目录:")
print(f"   data_dir: {data_dir}")
print(f"   存在: {data_dir.exists()}")
print(f"   绝对路径: {data_dir.absolute()}")

# 2. 列出所有 parquet 文件
print(f"\n2. 列出所有 parquet 文件:")
parquet_files = list(data_dir.rglob("*.parquet"))
print(f"   找到 {len(parquet_files)} 个文件")

for file_path in parquet_files:
    print(f"   - {file_path}")

# 3. 尝试解析每个文件
print(f"\n3. 尝试解析每个文件:")

for file_path in parquet_files:
    print(f"\n   文件: {file_path}")
    
    try:
        # 相对路径
        rel_path = file_path.relative_to(data_dir)
        print(f"   相对路径: {rel_path}")
        
        parts = rel_path.parts
        print(f"   路径部分: {parts}")
        
        if len(parts) < 3:
            print(f"   ❌ 路径部分少于3个")
            continue
        
        data_source = parts[0]
        market = parts[1]
        filename = parts[-1]
        
        print(f"   data_source: {data_source}")
        print(f"   market: {market}")
        print(f"   filename: {filename}")
        
        # 解析文件名
        name_parts = filename.split('_')
        print(f"   文件名部分: {name_parts}")
        
        if len(name_parts) < 3:
            print(f"   ❌ 文件名部分少于3个")
            continue
        
        # 移除 .parquet 后缀
        last_part = name_parts[-1].replace('.parquet', '')
        name_parts[-1] = last_part
        
        print(f"   处理后的文件名部分: {name_parts}")
        
        code = name_parts[0]
        start_date_str = name_parts[1]
        end_date_str = name_parts[2]
        interval = name_parts[3] if len(name_parts) > 3 else '1d'
        
        print(f"   code: {code}")
        print(f"   start_date_str: {start_date_str}")
        print(f"   end_date_str: {end_date_str}")
        print(f"   interval: {interval}")
        
        # 转换日期
        start_date = datetime.strptime(start_date_str, '%Y%m%d').date()
        end_date = datetime.strptime(end_date_str, '%Y%m%d').date()
        
        print(f"   start_date: {start_date}")
        print(f"   end_date: {end_date}")
        
        # 文件大小
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"   file_size_mb: {file_size_mb:.2f}")
        
        print(f"   ✅ 解析成功")
        
    except Exception as e:
        print(f"   ❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
