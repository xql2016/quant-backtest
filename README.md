# 📊 量化回测系统

一个功能强大的量化交易回测平台，支持多种市场、多种策略、多种时间周期的回测分析。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动应用
```bash
python -m streamlit run run_main.py
```

### 3. 访问应用
在浏览器中打开：http://localhost:8501

## 📁 项目结构

```
quant-backtest/
├── 📄 核心模块
│   ├── run_main.py              # Streamlit 主应用
│   ├── data_source.py           # 数据源模块（AKShare, YFinance, Tushare）
│   ├── strategy_backtest.py     # 策略和回测引擎
│   └── ssl_config.py            # SSL 配置模块
│
├── 📂 test/                     # 测试和诊断脚本
│   ├── README.md                # 测试脚本说明
│   ├── quick_test.py            # 快速系统测试 ⭐
│   ├── diagnose_network.py      # 网络诊断
│   ├── diagnose_akshare.py      # AKShare 诊断
│   ├── fix_ssl.py               # SSL 修复工具
│   ├── clear_cache.py           # 缓存清理工具
│   └── ... (其他测试脚本)
│
├── 📂 docs/                     # 项目文档
│   ├── README.md                # 文档目录
│   ├── SSL_ISSUE_README.md      # SSL 问题说明 ⭐
│   ├── DATASOURCE_ISSUE_SUMMARY.md  # 数据源问题总结 ⭐
│   ├── YFinance快速参考.md      # YFinance 使用指南
│   ├── 快速使用Tushare可转债.md  # 可转债使用指南
│   └── ... (其他文档)
│
└── 📄 requirements.txt          # 项目依赖
```

## ✨ 主要功能

### 支持的数据源
- 🇨🇳 **Tushare** - A股、可转债（推荐，最稳定）
- 🇨🇳 **AKShare** - A股、港股、美股
- 🌐 **YFinance** - 美股、港股、加密货币

### 支持的市场
- A股（日线）
- 港股（日线）
- 美股（日线）
- 可转债（日线）
- 加密货币（日线、4小时线、1小时线）

### 内置策略
- MACD 趋势策略
- 双均线策略 (SMA)
- RSI 超买超卖
- 布林带突破
- 波段策略
- 多重底入场策略

## 📊 使用示例

### 示例 1：A股回测（Tushare）
```
数据源：Tushare (A股/可转债)
市场：A股
代码：000001（平安银行）或 600519（贵州茅台）
日期：2024-01-01 至 2024-12-31
策略：双均线策略
```

### 示例 2：加密货币 4小时线回测
```
数据源：YFinance (全球市场/加密货币)
市场：加密货币
代码：BTC-USD（比特币）
时间粒度：4小时线
日期：2024-01-01 至 2024-12-31
策略：MACD 趋势策略
```

### 示例 3：可转债回测
```
数据源：Tushare (A股/可转债)
市场：可转债
代码：127035 或 113050
日期：2024-01-01 至 2024-12-31
策略：RSI 超买超卖
```

## 🔧 常见问题

### Q: 数据获取失败？
查看 [docs/DATASOURCE_ISSUE_SUMMARY.md](docs/DATASOURCE_ISSUE_SUMMARY.md)

### Q: SSL 证书错误？
查看 [docs/SSL_ISSUE_README.md](docs/SSL_ISSUE_README.md)

### Q: 如何验证系统正常？
```bash
python test/quick_test.py
```

### Q: 哪个数据源最稳定？
**推荐使用 Tushare**，数据质量高且稳定可靠。

## 📚 完整文档

- [测试脚本说明](test/README.md)
- [文档目录](docs/README.md)
- [SSL 问题说明](docs/SSL_ISSUE_README.md)
- [数据源问题总结](docs/DATASOURCE_ISSUE_SUMMARY.md)

## 🛠️ 快速诊断工具

### 验证系统
```bash
python test/quick_test.py
```

### 诊断网络问题
```bash
python test/diagnose_network.py
```

### 清理缓存
```bash
python test/clear_cache.py
```

## 💡 使用建议

1. **新手入门**
   - 使用 Tushare 数据源
   - 选择 A股 市场
   - 从双均线策略开始
   - 使用较短的回测区间（如 1 个月）

2. **进阶使用**
   - 尝试不同策略参数
   - 对比不同市场表现
   - 使用小时线数据（加密货币）
   - 测试可转债策略

3. **问题排查**
   - 先运行 `python test/quick_test.py`
   - 查看对应的文档说明
   - 运行诊断工具
   - 查看终端输出的详细错误

## 🎯 核心优势

- ✅ **多数据源**：支持 3 种主流数据源
- ✅ **多市场**：A股、港股、美股、可转债、加密货币
- ✅ **多周期**：日线、4小时线、1小时线
- ✅ **灵活策略**：6 种内置策略，参数可调
- ✅ **完善文档**：详细的使用说明和问题诊断
- ✅ **可视化**：直观的图表展示和交易日志

## 🔗 相关链接

- [Streamlit 官网](https://streamlit.io/)
- [AKShare 文档](https://akshare.akfamily.xyz/)
- [YFinance 文档](https://pypi.org/project/yfinance/)
- [Tushare 官网](https://tushare.pro/)

## 📄 许可证

本项目仅供学习和研究使用。

---

**版本：** 1.0.0  
**最后更新：** 2026-02-08  
**状态：** ✅ 生产就绪
