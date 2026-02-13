# 缓存优化工具使用指南

本目录包含三个缓存优化工具，用于管理和优化缓存数据。

## 工具列表

### 1. merge_continuous_caches.py - 连续缓存合并工具

**功能**：判断两个缓存是否完全连续，如果是则合并并删除原缓存。

**使用方法**：

```bash
# 预览模式（不实际执行）
python tools/merge_continuous_caches.py \
  tushare/a_stock/000001_20250101_20250708.parquet \
  tushare/a_stock/000001_20250709_20260101.parquet \
  --dry-run

# 执行合并
python tools/merge_continuous_caches.py \
  tushare/a_stock/000001_20250101_20250708.parquet \
  tushare/a_stock/000001_20250709_20260101.parquet
```

**判断逻辑**：
- ✅ **完全连续**：A缓存到2025-07-08，B缓存从2025-07-09开始（gap=1天）
- ✅ **边界重叠**：A缓存到2025-07-08，B缓存从2025-07-08开始（gap=0，重叠1天）
- ✅ **多天重叠**：A缓存到2025-07-15，B缓存从2025-07-10开始（重叠6天，使用B的数据）
- ❌ **存在缺口**：A缓存到2025-07-08，B缓存从2025-07-10开始（gap=2天，有缺口）

**处理策略**：
- 对于重叠部分，使用后一个缓存（B）的数据（认为更新）
- 合并后自动更新 `cache_index.json`
- 自动删除原始的两个缓存文件

---

### 2. check_cache_overlap.py - 缓存覆盖判断工具

**功能**：判断一个缓存是否完全覆盖另一个，如果是则删除被覆盖的缓存。

**使用方法**：

```bash
# 预览模式
python tools/check_cache_overlap.py \
  tushare/a_stock/000001_20240101_20260101.parquet \
  tushare/a_stock/000001_20250101_20260101.parquet \
  --dry-run

# 执行清理
python tools/check_cache_overlap.py \
  tushare/a_stock/000001_20240101_20260101.parquet \
  tushare/a_stock/000001_20250101_20260101.parquet
```

**判断逻辑**：
- ✅ **完全覆盖**：A缓存(2024-01-01 ~ 2026-01-01) 完全覆盖 B缓存(2025-01-01 ~ 2026-01-01)
- ⚠️ **部分覆盖**：两个缓存有重叠但无完全覆盖关系（不删除）
- ✅ **无覆盖**：两个缓存无重叠（不删除）

**处理策略**：
- 保留覆盖范围更大的缓存
- 删除被完全覆盖的缓存
- 自动更新 `cache_index.json`
- 显示释放的磁盘空间

---

### 3. auto_optimize_cache.py - 自动优化工具 ⭐

**功能**：遍历所有缓存，自动执行合并和清理操作。

**使用方法**：

```bash
# 生成优化报告（只分析，不执行）
python tools/auto_optimize_cache.py --report

# 预览模式（显示将要执行的操作）
python tools/auto_optimize_cache.py

# 执行优化
python tools/auto_optimize_cache.py --execute
```

**自动化流程**：

1. **扫描阶段**：遍历 `cache/data/` 目录，按资产分组
   - 资产分组键：`{data_source}_{market}_{code}_{interval}`
   - 例如：`tushare_a_stock_000001_1d`

2. **清理阶段**：删除被覆盖的缓存
   - 检查同一资产的所有缓存
   - 找出完全覆盖关系
   - 删除被覆盖的缓存文件

3. **合并阶段**：合并连续的缓存
   - 检查同一资产的相邻缓存
   - 判断是否连续（gap ≤ 1天）
   - 合并连续缓存

4. **总结报告**：显示优化效果
   - 删除的冗余缓存数量
   - 合并的缓存对数量
   - 释放的磁盘空间

---

## 使用场景

### 场景1：手动合并两个连续缓存

```bash
# 你有两个缓存：
# - 000001_20250101_20250630.parquet
# - 000001_20250701_20251231.parquet

python tools/merge_continuous_caches.py \
  tushare/a_stock/000001_20250101_20250630.parquet \
  tushare/a_stock/000001_20250701_20251231.parquet
```

### 场景2：清理被覆盖的旧缓存

```bash
# 你有两个缓存：
# - 000001_20240101_20260101.parquet（大范围）
# - 000001_20250101_20250630.parquet（小范围，被覆盖）

python tools/check_cache_overlap.py \
  tushare/a_stock/000001_20240101_20260101.parquet \
  tushare/a_stock/000001_20250101_20250630.parquet
```

### 场景3：一键优化所有缓存 ⭐

```bash
# 先查看报告
python tools/auto_optimize_cache.py --report

# 确认后执行
python tools/auto_optimize_cache.py --execute
```

---

## 安全提示

### 1. 预览模式

所有工具都支持 `--dry-run` 或预览模式：
- 只检查和分析，不执行实际操作
- 显示将要执行的操作
- 帮助你确认操作是否符合预期

**建议**：第一次使用时，先用预览模式查看效果。

### 2. 备份

虽然工具会自动更新索引，但建议在大规模优化前备份：

```bash
# 备份索引文件
cp cache/metadata/cache_index.json cache/metadata/cache_index.json.backup

# 备份整个缓存目录（可选）
tar -czf cache_backup.tar.gz cache/
```

### 3. 幂等性

- ✅ 工具已实现幂等性：多次运行不会产生副作用
- ✅ 已删除的缓存不会重复删除
- ✅ 已合并的缓存不会重复合并

---

## 工作原理

### 文件名解析

工具通过文件名自动解析缓存信息：

```
文件路径: tushare/a_stock/000001_20250101_20251231_1d.parquet
          ^^^^^^^ ^^^^^^^ ^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^
          数据源  市场    代码   开始日期  结束日期  时间粒度

解析结果:
- data_source: tushare
- market: a_stock
- code: 000001
- start_date: 2025-01-01
- end_date: 2025-12-31
- interval: 1d
```

### 资产分组

同一资产的所有缓存会被分为一组，分组键不包含日期：

```
分组键: tushare_a_stock_000001_1d

该组包含:
- 000001_20240101_20241231.parquet
- 000001_20250101_20250630.parquet
- 000001_20250701_20251231.parquet
```

### 索引更新

操作完成后自动更新 `cache/metadata/cache_index.json`：
- 删除旧缓存的索引条目
- 添加新缓存的索引条目
- 更新 `last_update` 时间戳

---

## 常见问题

### Q1: 合并后的缓存文件名是什么？

A: 使用合并后的日期范围：

```
合并前:
- 000001_20250101_20250630.parquet
- 000001_20250701_20251231.parquet

合并后:
- 000001_20250101_20251231.parquet
```

### Q2: 重叠部分的数据如何处理？

A: 使用后一个缓存（时间上更靠后）的数据，认为是更新的数据。

### Q3: 如果两个缓存中间有缺口怎么办？

A: 不会合并。例如：
- A缓存: 2025-01-01 ~ 2025-06-30
- B缓存: 2025-07-02 ~ 2025-12-31
- 缺口: 2025-07-01（1天）

工具会报错提示存在缺口，不执行合并。

### Q4: 自动优化工具会不会误删数据？

A: 不会。工具只在以下情况删除：
1. 缓存被另一个更大范围的缓存**完全覆盖**
2. 两个缓存表示同一资产（数据源、市场、代码、时间粒度都相同）

### Q5: 可以撤销操作吗？

A: 工具本身不提供撤销功能，但建议：
1. 使用预览模式确认操作
2. 操作前备份索引文件
3. 如需恢复，可以重新获取数据

---

## 性能优化建议

### 定期优化

建议定期（如每周）运行自动优化：

```bash
# 添加到 crontab（每周日凌晨3点）
0 3 * * 0 cd /path/to/quant-backtest && python tools/auto_optimize_cache.py --execute
```

### 监控缓存大小

使用自动优化工具的报告功能监控缓存状态：

```bash
python tools/auto_optimize_cache.py --report
```

输出示例：

```
📊 优化潜力总结
================================================================================
可删除冗余缓存: 5 个
可合并连续缓存: 3 对
可释放空间: 125.45 MB
```

---

## 示例：完整优化流程

```bash
# 1. 查看当前缓存状态
python test/cache_tool.py --stats

# 2. 生成优化报告
python tools/auto_optimize_cache.py --report

# 3. 预览优化操作
python tools/auto_optimize_cache.py

# 4. 确认后执行优化
python tools/auto_optimize_cache.py --execute

# 5. 查看优化后的状态
python test/cache_tool.py --stats
```

---

## 技术实现

### 连续性判断算法

```python
gap = (cache2_start_date - cache1_end_date).days

if gap == 1:
    # 完全连续，无缺口无重叠
    # A: 2025-01-01 ~ 2025-06-30
    # B: 2025-07-01 ~ 2025-12-31
    return "continuous"

elif gap == 0:
    # 边界重叠1天
    # A: 2025-01-01 ~ 2025-06-30
    # B: 2025-06-30 ~ 2025-12-31
    return "overlap"

elif gap < 0:
    # 多天重叠
    # A: 2025-01-01 ~ 2025-07-15
    # B: 2025-07-01 ~ 2025-12-31
    return "overlap"

else:
    # 存在缺口
    # A: 2025-01-01 ~ 2025-06-30
    # B: 2025-07-05 ~ 2025-12-31
    return "gap"
```

### 覆盖关系判断

```python
def is_covering(cache_a, cache_b):
    """检查 cache_a 是否完全覆盖 cache_b"""
    return (cache_a.start_date <= cache_b.start_date and
            cache_a.end_date >= cache_b.end_date)
```

---

## 更新日志

- **2026-02-13**: 初始版本发布
  - 实现连续缓存合并工具
  - 实现缓存覆盖判断工具
  - 实现自动优化工具
  - 支持预览模式和报告生成
