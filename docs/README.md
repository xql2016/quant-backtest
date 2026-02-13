# 缓存系统文档索引

## 📚 完整文档列表

### 用户指南

1. **[数据缓存快速开始](数据缓存快速开始.md)** ⭐
   - 5分钟快速上手
   - 基本使用示例
   - 最佳实践

2. **[数据缓存使用指南](数据缓存使用指南.md)**
   - 详细的功能说明
   - 配置选项说明
   - 高级用法

3. **[缓存优化工具快速指南](缓存优化工具快速指南.md)** ⭐
   - 缓存优化工具快速入门
   - 常用命令
   - 工作流推荐

4. **[工具详细使用指南](../tools/README.md)**
   - 三个优化工具的完整说明
   - 详细的使用场景
   - 技术实现细节

### 技术文档

5. **[缓存模块技术说明](缓存模块技术说明.md)**
   - 架构设计
   - 核心模块说明
   - API 参考

6. **[缓存系统实现总结](缓存系统实现总结.md)**
   - 系统概览
   - 核心功能
   - 性能指标

7. **[缓存优化工具实现总结](缓存优化工具实现总结.md)**
   - 工具实现细节
   - 算法说明
   - 未来改进方向

8. **[缓存智能日期匹配优化](缓存智能日期匹配优化.md)**
   - 智能匹配机制
   - 优化原理
   - 测试验证

### 集成说明

9. **[Streamlit应用缓存集成说明](Streamlit应用缓存集成说明.md)**
   - Streamlit 集成步骤
   - UI 功能说明
   - 验证方法

10. **[缓存功能检查清单](缓存功能检查清单.md)**
    - 功能完整性检查
    - 故障排查
    - 测试清单

### 分析文档

11. **[多缓存合并可行性分析](多缓存合并可行性分析.md)**
    - 合并场景分析
    - 可行性评估
    - 潜在问题

---

## 🚀 快速导航

### 我是新手，想快速上手
👉 从这里开始：
1. [数据缓存快速开始](数据缓存快速开始.md)
2. [缓存优化工具快速指南](缓存优化工具快速指南.md)

### 我想了解详细功能
👉 阅读这些：
1. [数据缓存使用指南](数据缓存使用指南.md)
2. [工具详细使用指南](../tools/README.md)

### 我想了解技术实现
👉 查看这些：
1. [缓存模块技术说明](缓存模块技术说明.md)
2. [缓存系统实现总结](缓存系统实现总结.md)
3. [缓存优化工具实现总结](缓存优化工具实现总结.md)

### 我在集成到 Streamlit
👉 参考这个：
1. [Streamlit应用缓存集成说明](Streamlit应用缓存集成说明.md)

### 我遇到问题了
👉 先检查这些：
1. [缓存功能检查清单](缓存功能检查清单.md)
2. 运行诊断工具：`python test/diagnose_cache.py`

---

## 📂 文件结构

```
quant-backtest/
├── cache/                           # 缓存目录
│   ├── config.json                  # 配置文件
│   ├── data/                        # 缓存数据
│   ├── metadata/                    # 元数据
│   └── logs/                        # 日志
│
├── cache_manager.py                 # 缓存管理核心模块
├── cached_data_source.py            # 缓存数据源包装器
│
├── tools/                           # 缓存优化工具
│   ├── README.md                    # 工具使用指南
│   ├── merge_continuous_caches.py   # 连续缓存合并
│   ├── check_cache_overlap.py       # 覆盖判断
│   └── auto_optimize_cache.py       # 自动优化
│
├── test/                            # 测试和工具
│   ├── cache_tool.py                # 缓存管理命令行工具
│   ├── diagnose_cache.py            # 诊断工具
│   ├── test_cache.py                # 基础测试
│   └── test_smart_cache.py          # 智能匹配测试
│
└── docs/                            # 文档目录
    ├── README.md                    # 本文档（索引）
    ├── 数据缓存快速开始.md           # 快速开始
    ├── 数据缓存使用指南.md           # 使用指南
    ├── 缓存优化工具快速指南.md       # 优化工具快速指南
    ├── 缓存模块技术说明.md           # 技术说明
    ├── 缓存系统实现总结.md           # 实现总结
    ├── 缓存优化工具实现总结.md       # 工具实现总结
    ├── 缓存智能日期匹配优化.md       # 智能匹配
    ├── Streamlit应用缓存集成说明.md # Streamlit集成
    ├── 缓存功能检查清单.md           # 检查清单
    └── 多缓存合并可行性分析.md       # 可行性分析
```

---

## 🎯 核心功能概览

### 数据缓存系统
- ✅ 三层缓存架构（内存 → 本地文件 → 远程API）
- ✅ 智能日期匹配（自动使用已有缓存）
- ✅ 灵活的过期策略（TTL）
- ✅ Parquet 高效存储
- ✅ 自动索引管理

### 缓存优化工具
- ✅ 自动合并连续缓存
- ✅ 自动清理被覆盖缓存
- ✅ 一键优化所有缓存
- ✅ 预览模式和报告生成
- ✅ 幂等性和安全性保障

---

## 🔧 常用命令

### 数据获取（自动缓存）
```python
from cached_data_source import get_cached_stock_data

df = get_cached_stock_data(
    code='000001',
    start_date=date(2025, 1, 1),
    end_date=date(2025, 12, 31),
    market='A股',
    source_type='tushare'
)
```

### 缓存管理
```bash
# 查看缓存统计
python test/cache_tool.py --stats

# 列出所有缓存
python test/cache_tool.py --list

# 清理过期缓存
python test/cache_tool.py --clean
```

### 缓存优化
```bash
# 生成优化报告
python tools/auto_optimize_cache.py --report

# 执行自动优化
python tools/auto_optimize_cache.py --execute
```

### 故障诊断
```bash
# 运行诊断工具
python test/diagnose_cache.py

# 运行测试
python test/test_cache.py
python test/test_smart_cache.py
```

---

## 📊 性能指标

### 缓存命中率
- 首次获取：需访问远程API（慢）
- 再次获取：使用本地缓存（快 100-1000 倍）

### 存储效率
- Parquet 格式：高压缩比，快速读写
- 典型压缩比：3-5倍
- 100万条数据约 20-30 MB

### 优化效果
- 自动优化可减少 30-50% 的冗余缓存
- 典型场景可释放 100-500 MB 空间

---

## 🌟 最佳实践

1. **使用 `get_cached_stock_data` 获取数据**
   - 自动处理缓存逻辑
   - 透明的 API 调用

2. **定期运行自动优化**
   - 每周一次：`python tools/auto_optimize_cache.py --execute`
   - 或添加到 crontab

3. **监控缓存大小**
   - 定期检查：`python test/cache_tool.py --stats`
   - 根据需要调整 `max_size_mb`

4. **合理配置 TTL**
   - 历史数据：永久缓存
   - 近期数据：7天
   - 实时数据：1小时

---

## 📞 支持

如有问题：
1. 查看相关文档
2. 运行诊断工具：`python test/diagnose_cache.py`
3. 查看日志：`cache/logs/cache_access.log`
4. 检查索引：`cache/metadata/cache_index.json`

---

## 📝 更新日志

### 2026-02-13
- ✅ 实现缓存优化工具（合并、清理、自动优化）
- ✅ 添加预览模式和报告生成
- ✅ 创建完整文档体系

### 2025-xx-xx
- ✅ 实现智能日期匹配优化
- ✅ 集成到 Streamlit 应用
- ✅ 添加幂等性保障

### 2025-xx-xx
- ✅ 初始版本
- ✅ 三层缓存架构
- ✅ Parquet 存储
- ✅ TTL 过期策略
