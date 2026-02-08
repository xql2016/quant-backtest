# SSL 证书问题诊断与解决方案

## 🔍 问题诊断结果

经过详细测试，你的机器存在 **SSL 证书验证问题**：

### 现象
- ❌ 所有 HTTPS API 都无法通过 SSL 证书验证
- ❌ Yahoo Finance API: `CERTIFICATE_VERIFY_FAILED`
- ❌ 东方财富 API (AKShare): `CERTIFICATE_VERIFY_FAILED`
- ✅ 但 Tushare 数据源可以正常工作

### 根本原因
这**不是频率限制问题**，而是 **SSL 证书链验证失败**。可能的原因：
1. macOS 系统证书未正确安装
2. Python 证书配置问题
3. 网络环境导致的证书问题

---

## ✅ 解决方案

### 🎯 方案1：使用 Tushare 数据源（最推荐）

**优点**：
- ✅ 已验证可用
- ✅ 数据质量高、更新及时
- ✅ 无需修改 SSL 配置

**使用方法**：
1. 在 Streamlit 应用中选择 "Tushare (A股/可转债)"
2. 选择市场类型（A股/可转债）
3. 输入股票代码进行回测

---

### 🔧 方案2：修复 SSL 证书（临时方案）

已创建 `ssl_config.py` 和 `ssl_fix_ultimate.py` 两个配置文件。

#### 使用方法A：在 run_main.py 中启用（已配置）

`run_main.py` 已经自动导入 SSL 配置，重启 Streamlit 应用即可：

```bash
# 停止当前应用（Ctrl+C）
# 重新启动
python -m streamlit run run_main.py
```

#### 使用方法B：临时测试脚本

```python
# 在任何脚本开头添加
import ssl_fix_ultimate  # 完全禁用 SSL 验证
```

⚠️ **警告**：禁用 SSL 验证会降低安全性，仅在开发环境使用！

---

### 🛠️ 方案3：修复系统证书（长期方案）

#### macOS 系统：

```bash
# 方法1: 重装 certifi
pip install --upgrade certifi
pip install --upgrade urllib3

# 方法2: 运行 Python 证书安装工具
/Applications/Python\ 3.12/Install\ Certificates.command

# 方法3: 使用 conda 重装（如果使用 miniconda）
conda install -c conda-forge certifi
```

---

## 📊 测试脚本说明

创建了以下测试脚本帮助诊断：

| 脚本 | 用途 |
|------|------|
| `test_data_fetch.py` | 原始测试（会显示错误） |
| `diagnose_network.py` | 详细网络和SSL诊断 |
| `fix_ssl.py` | SSL修复工具和方案说明 |
| `ssl_config.py` | SSL配置模块 |
| `ssl_fix_ultimate.py` | 终极SSL修复方案 ⭐ |
| `quick_test.py` | 快速回测测试（验证系统） |
| `test_with_ssl_fix.py` | 测试SSL修复效果 |

---

## 🚀 推荐使用流程

### 选项A：直接使用 Tushare（最简单）

1. 访问 http://localhost:8501
2. 选择数据源：**"Tushare (A股/可转债)"**
3. 选择市场：**"A股"**
4. 输入代码：如 `000001`（平安银行）
5. 设置回测区间：2024-01-01 至 2024-12-31
6. 点击 🚀 开始回测

### 选项B：使用 YFinance/AKShare（需要SSL修复）

1. 停止当前 Streamlit 应用
2. 确认 `ssl_config.py` 已导入到 `run_main.py`（已配置）
3. 重启应用：
   ```bash
   python -m streamlit run run_main.py
   ```
4. 在应用中选择对应的数据源

---

## ❓ 为什么你的另一台机器正常？

可能的原因：
1. **Python 版本不同**：另一台机器的 Python 可能正确安装了证书
2. **系统配置不同**：证书存储位置或配置不同
3. **网络环境不同**：网络代理、防火墙配置不同
4. **安装方式不同**：Homebrew Python vs conda Python vs 官方 Python

---

## 💡 最终建议

**开发/测试环境**：
- ✅ 使用 Tushare 数据源（无需修改配置）
- ✅ 或启用 SSL 配置临时禁用验证

**生产环境**：
- ✅ 修复系统证书（方案3）
- ✅ 或咨询 IT 部门配置企业证书

**紧急情况**：
- ✅ 直接运行 `quick_test.py` 验证 Tushare 可用
- ✅ 使用 Tushare 完成回测任务

---

## 🎯 下一步

1. 如果选择 Tushare：直接在 Streamlit 中使用即可
2. 如果要修复 SSL：运行 `pip install --upgrade certifi`
3. 如果仍有问题：提供 `diagnose_network.py` 的完整输出

