#!/bin/bash

echo "=========================================="
echo "Streamlit Cloud 快速部署脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤 1: 检查 Git 状态
echo -e "${BLUE}[步骤 1/5]${NC} 检查 Git 状态..."
git status

echo ""
echo -e "${YELLOW}提示：${NC}"
echo "1. 首先需要在 GitHub 上创建一个新仓库"
echo "   访问: https://github.com/new"
echo "   仓库名建议: quant-backtest"
echo "   选择: Public (公开)"
echo ""
read -p "已创建 GitHub 仓库了吗？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "请先创建 GitHub 仓库，然后重新运行此脚本"
    exit 1
fi

# 步骤 2: 获取仓库地址
echo ""
echo -e "${BLUE}[步骤 2/5]${NC} 配置远程仓库..."
echo "请输入你的 GitHub 仓库地址"
echo "格式: https://github.com/用户名/仓库名.git"
read -p "仓库地址: " REPO_URL

# 检查是否已有远程仓库
if git remote | grep -q "origin"; then
    echo "检测到已有 origin，将更新地址..."
    git remote set-url origin $REPO_URL
else
    echo "添加远程仓库..."
    git remote add origin $REPO_URL
fi

echo -e "${GREEN}✓${NC} 远程仓库配置完成"

# 步骤 3: 添加并提交文件
echo ""
echo -e "${BLUE}[步骤 3/5]${NC} 准备提交代码..."
git add .

echo "请输入提交信息 (直接回车使用默认信息)"
read -p "提交信息 [部署到 Streamlit Cloud]: " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"部署到 Streamlit Cloud"}

git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✓${NC} 代码已提交"

# 步骤 4: 推送到 GitHub
echo ""
echo -e "${BLUE}[步骤 4/5]${NC} 推送到 GitHub..."
echo "正在推送... (可能需要输入 GitHub 用户名和密码)"
git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 推送成功！"
else
    echo "推送失败，可能需要配置 Git 凭据"
    echo ""
    echo "解决方案："
    echo "1. 使用 Personal Access Token 代替密码"
    echo "   生成地址: https://github.com/settings/tokens"
    echo "2. 或使用 SSH 密钥"
    exit 1
fi

# 步骤 5: 部署说明
echo ""
echo -e "${BLUE}[步骤 5/5]${NC} 部署到 Streamlit Cloud..."
echo ""
echo "=========================================="
echo -e "${GREEN}代码已成功推送到 GitHub！${NC}"
echo "=========================================="
echo ""
echo "下一步：部署到 Streamlit Cloud"
echo ""
echo "1. 访问: ${BLUE}https://share.streamlit.io/${NC}"
echo "2. 使用 GitHub 账号登录"
echo "3. 点击 'New app'"
echo "4. 填写配置:"
echo "   Repository: ${REPO_URL%.git}"
echo "   Branch: main"
echo "   Main file: 多策略可视化回测_小红书20260117.py"
echo "5. 点击 'Deploy!'"
echo ""
echo "等待 3-5 分钟，你的应用就上线了！"
echo ""
echo "详细说明请查看: Streamlit_Cloud_部署指南.md"
echo ""

