# 数据源问题总结与解决方案

## 🔍 问题诊断结果

### 测试结果对比

| 数据源 | 命令行测试 | Streamlit 测试 | 状态 |
|--------|-----------|---------------|------|
| Tushare | ✅ 成功 | ✅ 成功 | 完全可用 |
| AKShare | ✅ 成功 | ❌ JSON错误 | 命令行可用 |
| YFinance | ⚠️ 频率限制 | ⚠️ 频率限制 | 需要等待 |

### 根本原因

1. **SSL 证书问题**（已解决）
   - 所有 HTTPS 连接都有证书验证失败
   - 已通过 `ssl_config.py` 修复

2. **AKShare 在 Streamlit 中的问题**
   - 命令行测试：✅ 正常工作
   - Streamlit 中：❌ JSON 解析错误
   - 可能原因：
     - Streamlit 缓存机制
     - 请求被拦截或修改
     - API 响应不一致

3. **YFinance 频率限制**
   - Yahoo Finance API 有请求频率限制
   - 短时间内多次请求会被限流
   - 需要等待几分钟后重试

---

## ✅ 推荐解决方案

### 🎯 方案1：使用 Tushare（最推荐）

**优点：**
- ✅ 命令行和 Streamlit 中都完全可用
- ✅ 数据质量高、更新及时
- ✅ 支持 A股 和 可转债
- ✅ 无需任何额外配置

**使用步骤：**
1. 启动应用：`python -m streamlit run run_main.py`
2. 数据源选择：`Tushare (A股/可转债)`
3. 市场选择：`A股` 或 `可转债`
4. 输入代码：
   - A股：`000001`（平安银行）、`600519`（贵州茅台）
   - 可转债：`127035`、`113050`
5. 日期范围：`2024-01-01` 至 `2024-12-31`
6. 点击 `🚀 开始回测`

---

### ⚙️ 方案2：修复 AKShare（如果必须使用）

**步骤：**

1. **清理缓存**
   ```bash
   python clear_cache.py
   ```

2. **重启 Streamlit**
   ```bash
   pkill -f "streamlit run"
   python -m streamlit run run_main.py
   ```

3. **在应用中清除缓存**
   - 打开 Streamlit 应用
   - 按键盘 `C` 键
   - 选择 "Clear cache"
   - 重新运行回测

4. **如果仍然失败**
   - 使用较小的日期范围（如最近1个月）
   - 或切换到 Tushare 数据源

---

### 🌐 方案3：使用 YFinance（国际市场）

**适用于：**
- 美股：`AAPL`、`TSLA`、`MSFT`
- 港股：`0700.HK`、`9988.HK`
- 加密货币：`BTC-USD`、`ETH-USD`

**注意事项：**
- ⚠️ 有频率限制，短时间内多次请求会失败
- ⚠️ 需要等待 5-10 分钟后重试
- ⚠️ 建议使用 `@st.cache_data` 缓存数据

**使用建议：**
- 每次回测间隔至少 30 秒
- 如遇频率限制，等待 10 分钟后重试
- 使用较小的日期范围

---

## 📁 已创建的工具文件

| 文件 | 用途 |
|------|------|
| `ssl_config.py` | SSL 配置模块（已自动加载）|
| `diagnose_network.py` | 网络和 SSL 诊断 |
| `diagnose_akshare.py` | AKShare 详细诊断 |
| `clear_cache.py` | 清理缓存工具 |
| `quick_test.py` | 快速回测测试 |
| `test_ssl_fixed.py` | 测试 SSL 修复效果 |
| `SSL_ISSUE_README.md` | SSL 问题详细说明 |
| `DATASOURCE_ISSUE_SUMMARY.md` | 本文件 |

---

## 🚀 快速启动指南

### 方案A：直接使用（推荐）

```bash
# 1. 启动应用
python -m streamlit run run_main.py

# 2. 在浏览器中访问 http://localhost:8501

# 3. 配置参数
#    - 数据源：Tushare (A股/可转债)
#    - 市场：A股
#    - 代码：000001
#    - 日期：2024-01-01 至 2024-12-31
#    - 策略：任选

# 4. 点击 🚀 开始回测
```

### 方案B：清理后重启

```bash
# 1. 停止现有进程
pkill -f "streamlit run"

# 2. 清理缓存
python clear_cache.py

# 3. 重新启动
python -m streamlit run run_main.py
```

---

## 🧪 测试命令

### 测试所有数据源
```bash
python test_ssl_fixed.py
```

### 诊断 AKShare
```bash
python diagnose_akshare.py
```

### 快速回测测试
```bash
python quick_test.py
```

---

## ❓ 常见问题

### Q1: AKShare 在 Streamlit 中失败但命令行成功？
**A**: 这是已知问题。推荐切换到 Tushare 数据源。如必须使用 AKShare：
1. 清理缓存（`python clear_cache.py`）
2. 重启应用
3. 在应用中按 `C` 清除缓存

### Q2: YFinance 显示 "Rate limited"？
**A**: 这是 Yahoo Finance API 的频率限制，正常现象。
- 等待 10 分钟后重试
- 或切换到其他数据源

### Q3: SSL 证书错误？
**A**: 已通过 `ssl_config.py` 修复。确保 `run_main.py` 中导入了该模块。

### Q4: 哪个数据源最稳定？
**A**: Tushare 数据源最稳定可靠：
- ✅ 数据质量高
- ✅ API 稳定
- ✅ 支持 A股 和 可转债
- ✅ 无频率限制（合理使用）

---

## 💡 最终建议

**生产环境：**
- ✅ 优先使用 Tushare
- ✅ 提前测试数据源可用性
- ✅ 实现数据缓存机制

**开发环境：**
- ✅ 使用 Tushare 进行主要开发
- ⚠️ AKShare 仅在需要时使用
- ⚠️ YFinance 用于国际市场

**调试建议：**
- 使用 `python quick_test.py` 快速验证
- 使用 `python diagnose_akshare.py` 诊断问题
- 查看终端输出的详细错误信息

---

**最后更新：** 2026-02-08
**状态：** ✅ Tushare 完全可用
