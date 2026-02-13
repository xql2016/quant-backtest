#!/bin/bash
# Excel导出功能依赖安装脚本

echo "📦 安装 openpyxl 库..."
pip3 install openpyxl

echo ""
echo "✅ 安装完成！"
echo ""
echo "📖 使用说明："
echo "1. 运行应用：streamlit run run_main.py"
echo "2. 选择批量回测模式"
echo "3. 点击下载按钮，将生成 .xlsx 格式文件"
echo "4. 用 Excel 打开，中文将正常显示"
echo ""
echo "💡 提示：如果已在虚拟环境中，请在虚拟环境激活状态下运行此脚本"
