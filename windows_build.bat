@echo off
chcp 65001 >nul
echo ========================================
echo 量化回测工作台 - Windows 打包脚本
echo ========================================
echo.

echo [1/4] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误：未找到 Python！
    echo 请先安装 Python 3.9 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python 已安装
echo.

echo [2/4] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误：依赖安装失败！
    pause
    exit /b 1
)
echo ✓ 依赖安装完成
echo.

echo [3/4] 安装 PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo 错误：PyInstaller 安装失败！
    pause
    exit /b 1
)
echo ✓ PyInstaller 已安装
echo.

echo [4/4] 开始打包...
echo 这可能需要 5-10 分钟，请耐心等待...
pyinstaller build_spec.spec
if errorlevel 1 (
    echo 错误：打包失败！
    echo 请查看错误信息
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✓ 打包完成！
echo ========================================
echo.
echo 可执行文件位置：
echo   dist\量化回测工作台\量化回测工作台.exe
echo.
echo 可以将整个 "dist\量化回测工作台" 文件夹压缩分发
echo.
pause

