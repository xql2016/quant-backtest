# 数据缓存目录

此目录用于存储本地缓存的数据文件。

## 📁 目录结构

```
cache/
├── config.json              # 缓存配置文件
├── data/                    # 数据文件存储（自动生成）
│   ├── akshare/            # AKShare 数据源
│   ├── yfinance/           # YFinance 数据源
│   └── tushare/            # Tushare 数据源
├── metadata/               # 元数据
│   └── cache_index.json   # 缓存索引（自动生成）
└── logs/                   # 日志文件（自动生成）
```

## 📖 文档

详细文档请查看：

- **快速开始**: [../docs/数据缓存快速开始.md](../docs/数据缓存快速开始.md)
- **使用指南**: [../docs/数据缓存使用指南.md](../docs/数据缓存使用指南.md)
- **技术说明**: [../docs/缓存模块技术说明.md](../docs/缓存模块技术说明.md)
- **实现总结**: [../docs/缓存系统实现总结.md](../docs/缓存系统实现总结.md)
- **检查清单**: [../docs/缓存功能检查清单.md](../docs/缓存功能检查清单.md)

## 🔧 配置

编辑 `config.json` 可以调整缓存设置：

- `max_size_mb`: 最大缓存容量
- `ttl_rules`: TTL过期规则
- `cleanup_policy`: 清理策略
- `storage_format`: 存储格式

## 🛠️ 管理缓存

使用命令行工具管理缓存：

```bash
python test/cache_tool.py
```

## ⚠️ 注意

- `data/`, `logs/`, `metadata/cache_index.json` 已被 git 忽略
- 缓存文件会自动创建，无需手动创建
- 定期清理缓存以节省磁盘空间
