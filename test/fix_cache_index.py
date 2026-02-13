#!/usr/bin/env python3
"""
修复脚本：同步缓存索引和实际文件
"""

import json
from pathlib import Path

# 读取索引
index_file = Path("cache/metadata/cache_index.json")
with open(index_file, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

print("=" * 80)
print("🔧 同步缓存索引和实际文件")
print("=" * 80)

# 检查每个索引条目对应的文件是否存在
to_remove = []
for key, entry in index_data['entries'].items():
    file_path = Path(entry['file_path'])
    
    if not file_path.exists():
        print(f"\n❌ 发现孤立索引条目（文件不存在）:")
        print(f"   键: {key}")
        print(f"   文件: {entry['file_path']}")
        to_remove.append(key)
    else:
        print(f"\n✅ 索引和文件一致:")
        print(f"   键: {key}")
        print(f"   文件: {entry['file_path']}")

# 删除孤立条目
if to_remove:
    print(f"\n🗑️ 删除 {len(to_remove)} 个孤立索引条目...")
    
    for key in to_remove:
        del index_data['entries'][key]
    
    # 更新统计
    from datetime import datetime
    
    total_size = sum(e['file_size_kb'] for e in index_data['entries'].values()) / 1024
    
    index_data['statistics'] = {
        'total_entries': len(index_data['entries']),
        'total_size_mb': round(total_size, 2),
        'oldest_entry': min((e['created_at'] for e in index_data['entries'].values()), default=None),
        'newest_entry': max((e['created_at'] for e in index_data['entries'].values()), default=None)
    }
    
    index_data['last_update'] = datetime.now().isoformat()
    
    # 保存
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print("✅ 索引已更新")
    
    print(f"\n📊 新的统计信息:")
    print(f"   缓存数: {index_data['statistics']['total_entries']} 个")
    print(f"   大小: {index_data['statistics']['total_size_mb']:.2f} MB")
else:
    print(f"\n✅ 索引和文件完全一致，无需修复")

print("\n" + "=" * 80)
print("🎉 完成！刷新 Streamlit 页面查看更新")
print("=" * 80)
