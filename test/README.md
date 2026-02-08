# 📁 测试和诊断脚本

本目录包含所有用于测试、诊断和工具的 Python 脚本。

## 🧪 核心测试脚本

### 快速测试
- **`quick_test.py`** ⭐ 推荐
  - 快速验证回测系统是否正常工作
  - 测试 Tushare 数据源
  - 运行简单的双均线策略回测
  - 使用：`python test/quick_test.py`

### SSL 相关测试
- **`test_ssl_fixed.py`**
  - 测试 SSL 修复后的数据获取
  - 验证 Tushare 和 AKShare 是否可用
  - 使用：`python test/test_ssl_fixed.py`

- **`test_with_ssl_fix.py`**
  - 测试禁用 SSL 验证后的效果
  - 包含等待时间避免频率限制
  - 使用：`python test/test_with_ssl_fix.py`

### 数据源测试
- **`test_data_fetch.py`**
  - 原始数据获取测试（会显示 SSL 错误）
  - 测试所有数据源
  - 使用：`python test/test_data_fetch.py`

- **`test_data_fix.py`**
  - 修复版数据获取测试
  - 使用历史日期避免未来日期问题
  - 使用：`python test/test_data_fix.py`

## 🔍 诊断工具

### 网络诊断
- **`diagnose_network.py`**
  - 完整的网络和 SSL 环境诊断
  - 检查 SSL 配置、代理设置
  - 测试各个 API 端点连接
  - 使用：`python test/diagnose_network.py`

- **`diagnose_akshare.py`**
  - AKShare 专项诊断
  - 查看 API 原始响应
  - 测试不同接口
  - 使用：`python test/diagnose_akshare.py`

## 🛠️ 修复工具

### SSL 修复
- **`fix_ssl.py`**
  - SSL 证书问题修复工具
  - 显示多种修复方案
  - 创建 SSL 配置文件
  - 使用：`python test/fix_ssl.py`

- **`ssl_fix_ultimate.py`**
  - 终极 SSL 修复方案
  - 完全禁用 SSL 验证（仅开发环境）
  - 使用：`import ssl_fix_ultimate`

### 缓存清理
- **`clear_cache.py`**
  - 清理 Python 和 Streamlit 缓存
  - 解决缓存导致的问题
  - 使用：`python test/clear_cache.py`

## 📊 专项功能测试

### 时间周期测试
- **`test_4h_aggregation.py`**
  - 测试 4小时线数据聚合
  - 验证 1小时数据到 4小时数据的转换
  
- **`test_hourly_data.py`**
  - 测试 1小时线数据获取
  - 验证小时级数据回测

- **`quick_test_1h.py`**
  - 快速测试 1小时线回测
  - 使用加密货币数据

### 可转债测试
- **`test_convertible_bond.py`**
  - 测试可转债数据获取和回测
  - 使用 AKShare 数据源

- **`test_tushare_convertible_bond.py`**
  - 测试 Tushare 可转债数据
  - 推荐使用此版本

- **`check_akshare_bond_api.py`**
  - 检查 AKShare 可转债 API

- **`check_akshare_bond_factors.py`**
  - 检查可转债因子数据

- **`check_tushare_bond_factors.py`**
  - 检查 Tushare 可转债因子

- **`check_bond_128039.py`**
  - 检查特定可转债数据（128039）

- **`debug_113050.py`**
  - 调试可转债 113050 数据问题

## 🎯 快速使用指南

### 1. 验证系统是否正常
```bash
python test/quick_test.py
```

### 2. 诊断网络和 SSL 问题
```bash
python test/diagnose_network.py
```

### 3. 修复 SSL 证书问题
```bash
python test/fix_ssl.py
```

### 4. 清理缓存
```bash
python test/clear_cache.py
```

### 5. 测试特定数据源
```bash
# 测试 AKShare
python test/diagnose_akshare.py

# 测试 Tushare
python test/test_tushare.py
```

## 📝 其他文件

- **`test_modules.py`** - 模块导入测试
- **`test_import.py`** - 依赖导入测试
- **`test_tushare.py`** - Tushare 数据源测试
- **`run_app.py`** - 独立运行应用

## 💡 常见使用场景

### 场景1：首次安装后验证
```bash
python test/quick_test.py
```

### 场景2：数据获取失败
```bash
# 先诊断
python test/diagnose_network.py

# 如果是 SSL 问题
python test/fix_ssl.py

# 测试修复效果
python test/test_ssl_fixed.py
```

### 场景3：AKShare 在 Streamlit 中失败
```bash
# 诊断 AKShare
python test/diagnose_akshare.py

# 清理缓存
python test/clear_cache.py

# 重启应用
pkill -f "streamlit run"
python -m streamlit run run_main.py
```

### 场景4：测试新功能
```bash
# 测试 4小时线
python test/test_4h_aggregation.py

# 测试可转债
python test/test_tushare_convertible_bond.py
```

## ⚠️ 注意事项

1. **运行环境**
   - 所有脚本应从项目根目录运行
   - 确保已安装所有依赖：`pip install -r requirements.txt`

2. **SSL 配置**
   - SSL 修复仅用于开发环境
   - 生产环境应修复系统证书

3. **频率限制**
   - YFinance 有频率限制，注意请求间隔
   - 测试时避免短时间内多次运行

4. **数据源选择**
   - 优先使用 Tushare（最稳定）
   - AKShare 在某些环境下可能不稳定
   - YFinance 适合国际市场

## 🔗 相关文档

- [SSL 问题说明](../docs/SSL_ISSUE_README.md)
- [数据源问题总结](../docs/DATASOURCE_ISSUE_SUMMARY.md)
- [项目主文档](../docs/README.md)

---

**最后更新：** 2026-02-08
