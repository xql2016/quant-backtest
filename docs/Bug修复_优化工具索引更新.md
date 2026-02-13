# Bug 修复报告：优化工具索引更新问题

## 🐛 问题描述

**问题**：使用缓存优化工具删除被覆盖的缓存后，Streamlit 界面仍显示旧的缓存数量。

**现象**：
- 实际文件系统：只有 1 个缓存文件
- Streamlit 界面：显示 2 个缓存
- 索引文件：包含 2 个条目，但统计信息未更新

**根本原因**：
优化工具删除缓存时，虽然删除了索引条目（`entries`），但**未重新计算统计信息**（`statistics`），导致 `total_entries` 和 `total_size_mb` 仍保持旧值。

---

## 🔧 修复方案

### 修复的文件

1. **tools/check_cache_overlap.py** - `_delete_cache` 方法
2. **tools/merge_continuous_caches.py** - `_update_index_after_merge` 方法

### 修复内容

在删除索引条目后，**重新计算统计信息**：

```python
# 删除旧条目
for key in to_remove:
    del index_data['entries'][key]

# ✅ 新增：重新计算统计信息
if index_data['entries']:
    total_size = sum(e.get('file_size_kb', 0) for e in index_data['entries'].values()) / 1024
    created_times = [e['created_at'] for e in index_data['entries'].values() if 'created_at' in e]
    
    index_data['statistics'] = {
        'total_entries': len(index_data['entries']),
        'total_size_mb': round(total_size, 2),
        'oldest_entry': min(created_times) if created_times else None,
        'newest_entry': max(created_times) if created_times else None
    }
else:
    # 如果没有缓存了，清空统计
    index_data['statistics'] = {
        'total_entries': 0,
        'total_size_mb': 0.0,
        'oldest_entry': None,
        'newest_entry': None
    }
```

---

## 🛠️ 修复工具

创建了修复脚本 `test/fix_cache_index.py`，用于：
- 检测索引和实际文件的不一致
- 删除孤立的索引条目（文件不存在）
- 重新计算统计信息
- 同步索引状态

**使用方法**：
```bash
python test/fix_cache_index.py
```

---

## ✅ 验证结果

### 修复前
```json
{
  "entries": {
    "tushare_a_stock_000001_20240101_20260101_1d": {...},  // 文件已删除
    "tushare_a_stock_000001_20230214_20260213_1d": {...}   // 文件存在
  },
  "statistics": {
    "total_entries": 2,    // ❌ 错误
    "total_size_mb": 0.06  // ❌ 错误
  }
}
```

### 修复后
```json
{
  "entries": {
    "tushare_a_stock_000001_20230214_20260213_1d": {...}   // 只保留存在的文件
  },
  "statistics": {
    "total_entries": 1,    // ✅ 正确
    "total_size_mb": 0.03  // ✅ 正确
  }
}
```

### Streamlit 界面
- **修复前**：缓存数 2 个，大小 0.1 MB
- **修复后**：缓存数 1 个，大小 0.03 MB ✅

---

## 📋 影响范围

### 受影响的工具
1. `tools/auto_optimize_cache.py` - 通过调用 `overlap_tool._delete_cache()`
2. `tools/check_cache_overlap.py` - 直接删除缓存
3. `tools/merge_continuous_caches.py` - 合并后删除旧缓存

### 影响的功能
- 缓存优化（删除被覆盖的缓存）
- 缓存合并（合并连续缓存）
- Streamlit 缓存统计显示

---

## 🎯 测试建议

### 测试场景1：删除被覆盖的缓存
```bash
# 1. 创建两个有覆盖关系的缓存
# 2. 运行优化
python tools/auto_optimize_cache.py --execute

# 3. 验证索引
cat cache/metadata/cache_index.json | grep "total_entries"

# 4. 验证 Streamlit 界面
# 刷新页面，检查缓存数是否正确
```

### 测试场景2：合并连续缓存
```bash
# 1. 创建两个连续的缓存
# 2. 运行合并
python tools/merge_continuous_caches.py file1 file2

# 3. 验证索引和文件数量一致
```

### 测试场景3：修复工具
```bash
# 1. 手动删除一个缓存文件（不更新索引）
rm cache/data/tushare/a_stock/xxx.parquet

# 2. 运行修复工具
python test/fix_cache_index.py

# 3. 验证索引和文件同步
```

---

## 📝 相关文件

- `tools/check_cache_overlap.py` - 已修复
- `tools/merge_continuous_caches.py` - 已修复
- `test/fix_cache_index.py` - 新增修复工具
- `cache/metadata/cache_index.json` - 已修复

---

## 🎉 总结

**问题**：删除缓存后统计信息未更新
**原因**：只删除了索引条目，未重新计算 `statistics`
**修复**：在删除后重新计算所有统计信息
**工具**：提供修复脚本同步索引和文件

现在优化工具能够正确更新索引，Streamlit 界面也能显示准确的缓存统计信息了！
