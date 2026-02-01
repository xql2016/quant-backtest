# Streamlit Cloud 部署指南

## 🎯 为什么选择 Streamlit Cloud？

✅ **优势：**
- 完全免费（社区版）
- 无需服务器，无需运维
- 自动部署，代码更新即生效
- 获得一个公开网址，任何人都可以访问
- 支持 Python 应用，完美适配 Streamlit

❌ **限制：**
- 代码需要公开（除非升级付费版）
- 有资源限制（CPU、内存）
- 需要 GitHub 账号

---

## 🚀 部署步骤（约 15 分钟）

### 步骤 1：准备 GitHub 仓库

#### 1.1 确保有 GitHub 账号

访问 https://github.com 注册或登录

#### 1.2 创建新仓库

1. 点击右上角 "+" → "New repository"
2. 仓库名称：`quant-backtest`（或任意名称）
3. 描述：`量化回测工作台 - 支持A股/港股/美股多策略回测`
4. 选择：
   - ✅ Public（公开，免费部署）
   - ⭕ Private（私有，需付费部署）
5. ✅ 勾选 "Add a README file"
6. 点击 "Create repository"

#### 1.3 上传代码到 GitHub

**方法 A：使用 Git 命令（推荐）**

在项目目录打开终端：

```bash
# 如果还没初始化 Git（你已经初始化过了，可以跳过）
# git init

# 查看当前远程仓库
git remote -v

# 如果没有远程仓库，添加
git remote add origin https://github.com/你的用户名/quant-backtest.git

# 添加所有文件
git add .

# 提交
git commit -m "准备部署到 Streamlit Cloud"

# 推送到 GitHub
git push -u origin main
```

**方法 B：使用 GitHub 网页上传**

1. 在 GitHub 仓库页面点击 "Add file" → "Upload files"
2. 拖拽以下文件：
   - `多策略可视化回测_小红书20260117.py`
   - `requirements.txt`
   - `README.txt`（可选）
3. 点击 "Commit changes"

---

### 步骤 2：部署到 Streamlit Cloud

#### 2.1 访问 Streamlit Cloud

打开 https://share.streamlit.io/

#### 2.2 登录

点击 "Sign in" → 选择 "Continue with GitHub"
授权 Streamlit 访问你的 GitHub

#### 2.3 创建新应用

1. 点击 "New app" 或 "Deploy an app"

2. 填写配置：
   ```
   Repository: 你的用户名/quant-backtest
   Branch: main
   Main file path: 多策略可视化回测_小红书20260117.py
   ```

3. 点击 "Deploy!"

#### 2.4 等待部署

- 首次部署需要 3-5 分钟
- Streamlit 会自动安装 requirements.txt 中的依赖
- 可以看到实时日志

#### 2.5 完成！

部署成功后，你会获得一个网址：
```
https://你的用户名-quant-backtest-xxx.streamlit.app
```

---

### 步骤 3：测试应用

1. 点击获得的网址
2. 测试各项功能：
   - 选择市场（A股/港股/美股）
   - 输入股票代码
   - 选择策略
   - 运行回测

---

## 🔧 常见问题

### Q1: 部署失败，提示找不到模块

**原因：** requirements.txt 不完整

**解决：** 确保 requirements.txt 包含所有依赖：
```txt
streamlit
pandas
numpy
matplotlib
akshare
yfinance
```

### Q2: 应用运行很慢

**原因：** 免费版资源有限

**解决方案：**
- 优化代码，减少计算量
- 使用缓存 `@st.cache_data`（已使用）
- 升级到付费版（更多资源）

### Q3: 想更新代码怎么办？

**非常简单！** 只需：
1. 在本地修改代码
2. 提交到 GitHub：
   ```bash
   git add .
   git commit -m "更新功能"
   git push
   ```
3. Streamlit Cloud 会自动重新部署（约 1-2 分钟）

### Q4: 想让应用私有怎么办？

**选项 1：** 升级到 Streamlit Cloud Teams 或 Enterprise（付费）

**选项 2：** 使用其他部署方式：
- Heroku（免费额度已取消）
- AWS/Azure/GCP（需要配置）
- 自己的服务器

### Q5: 数据获取失败

**原因：** 可能是网络限制或 API 限制

**解决：**
- AkShare 和 yfinance 都是通过网络获取数据
- Streamlit Cloud 在美国，访问国内数据源可能较慢
- 可以考虑缓存数据或使用其他数据源

---

## 🎨 优化建议

### 1. 添加 .streamlit/config.toml

创建配置文件优化显示：

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
```

### 2. 添加 README.md

让 GitHub 仓库更专业：

```markdown
# 量化回测工作台

支持 A股、港股、美股的多策略量化回测系统。

## 在线演示

访问：https://你的网址.streamlit.app

## 功能特性

- 🌍 支持三大市场：A股、港股、美股
- 📊 6种交易策略
- 📈 专业的可视化回测报告
```

### 3. 添加 .gitignore

避免上传不必要的文件：

```gitignore
__pycache__/
*.pyc
.DS_Store
.env
```

---

## 📊 部署后的优势

### 对用户：
✅ 无需安装任何软件
✅ 打开网址即可使用
✅ 支持手机、平板、电脑
✅ 随时随地访问

### 对开发者（你）：
✅ 代码更新自动生效
✅ 无需打包成 exe
✅ 无需维护服务器
✅ 可以收集用户反馈

---

## 🔐 安全提示

### 如果代码包含敏感信息：

1. **不要** 在代码中硬编码 API 密钥
2. 使用 Streamlit Secrets 管理敏感信息：
   - 在 Streamlit Cloud 控制台
   - Settings → Secrets
   - 添加键值对

3. 代码中读取 secrets：
   ```python
   import streamlit as st
   api_key = st.secrets["api_key"]
   ```

---

## 📈 使用限制（免费版）

| 资源 | 限制 |
|------|------|
| 应用数量 | 无限制 |
| 并发用户 | 建议 < 100 |
| CPU | 1 核心 |
| 内存 | 1 GB |
| 存储 | 代码托管在 GitHub |

---

## 🎯 下一步

部署成功后，你可以：

1. 📤 **分享网址**
   - 给同事、客户、朋友
   - 发布到社交媒体
   - 添加到个人简历/作品集

2. 🔗 **自定义域名**（付费功能）
   - 例如：backtest.yourname.com

3. 📊 **查看分析**
   - Streamlit Cloud 提供访问统计
   - 了解有多少人在使用

4. 💬 **收集反馈**
   - 在应用中添加反馈表单
   - 持续改进

---

## ✅ 快速检查清单

部署前确认：

- [ ] GitHub 账号已创建
- [ ] 代码已推送到 GitHub
- [ ] requirements.txt 包含所有依赖
- [ ] 本地测试应用可以正常运行
- [ ] 准备好 Streamlit Cloud 账号

---

## 🆘 需要帮助？

- Streamlit 官方文档：https://docs.streamlit.io/
- Streamlit 社区论坛：https://discuss.streamlit.io/
- GitHub Issues：在你的仓库提出问题

---

## 🎉 恭喜！

完成部署后，你就拥有了一个专业的在线量化回测系统！

分享你的网址，让更多人体验你的作品吧！🚀

