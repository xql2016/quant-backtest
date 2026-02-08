"""
SSL 证书问题修复脚本
将此配置添加到项目中以解决 SSL 证书验证问题
"""

import ssl
import urllib.request
import certifi

print("=" * 70)
print("🔧 SSL 证书问题修复工具")
print("=" * 70)

# 方案1：尝试重新安装证书（Mac系统）
print("\n【方案1】检查 Python 证书安装")
print("-" * 70)

import sys
import os
import platform

if platform.system() == 'Darwin':  # macOS
    print("检测到 macOS 系统")
    print("\n可能需要安装 Python 证书，运行以下命令：")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # 检查可能的证书安装脚本位置
    possible_paths = [
        f"/Applications/Python {python_version}/Install Certificates.command",
        "/opt/homebrew/Caskroom/miniconda/base/bin/pip",
    ]
    
    print(f"\n1. 使用 pip 安装 certifi:")
    print(f"   pip install --upgrade certifi")
    
    print(f"\n2. 或运行 Python 自带的证书安装工具:")
    for path in possible_paths:
        if os.path.exists(path):
            print(f"   ✅ 找到: {path}")
    
    print(f"\n3. 手动运行证书安装命令:")
    print(f"   /Applications/Python\\ {python_version}/Install\\ Certificates.command")

# 方案2：创建一个配置文件，禁用 SSL 验证（仅用于开发/测试）
print("\n" + "=" * 70)
print("【方案2】创建 SSL 配置文件（开发环境临时方案）")
print("-" * 70)

config_code = '''"""
SSL 配置模块
在数据获取前导入此模块以禁用 SSL 验证（仅用于开发环境）
"""

import ssl
import urllib.request
import warnings

def disable_ssl_verification():
    """
    禁用 SSL 证书验证
    警告：这会降低安全性，仅在开发/测试环境使用！
    """
    # 创建不验证证书的 SSL 上下文
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # 禁用 SSL 警告
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    print("⚠️  已禁用 SSL 证书验证（仅用于开发环境）")

def enable_ssl_verification():
    """恢复 SSL 证书验证"""
    ssl._create_default_https_context = ssl.create_default_context
    print("✅ 已恢复 SSL 证书验证")
'''

# 写入配置文件
with open('ssl_config.py', 'w', encoding='utf-8') as f:
    f.write(config_code)

print("✅ 已创建 ssl_config.py")
print("\n使用方法：")
print("   在 run_main.py 开头添加:")
print("   ```python")
print("   from ssl_config import disable_ssl_verification")
print("   disable_ssl_verification()  # 仅开发环境使用")
print("   ```")

# 方案3：更新系统证书
print("\n" + "=" * 70)
print("【方案3】更新 certifi 证书包")
print("-" * 70)
print("运行以下命令更新证书：")
print("   pip install --upgrade certifi")
print("   pip install --upgrade urllib3")

# 方案4：测试禁用 SSL 后的效果
print("\n" + "=" * 70)
print("【方案4】测试禁用 SSL 验证后的效果")
print("-" * 70)

# 临时禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

test_urls = [
    ("Yahoo Finance", "https://query1.finance.yahoo.com"),
    ("东方财富", "https://push2his.eastmoney.com"),
]

print("\n禁用 SSL 验证后测试连接：")
for name, url in test_urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        print(f"   ✅ {name}: 连接成功！")
    except Exception as e:
        print(f"   ❌ {name}: {e}")

# 恢复 SSL 验证
ssl._create_default_https_context = ssl.create_default_context

print("\n" + "=" * 70)
print("💡 推荐方案")
print("=" * 70)
print("""
根据你的情况，推荐按以下顺序尝试：

1️⃣ 【最佳方案】更新证书并重装 certifi
   ```bash
   pip install --upgrade certifi
   python -m certifi  # 查看证书位置
   ```

2️⃣ 【临时方案】在代码中禁用 SSL 验证
   - 在 run_main.py 开头导入 ssl_config
   - 调用 disable_ssl_verification()
   - ⚠️  仅用于开发环境，生产环境不推荐

3️⃣ 【长期方案】配置系统证书
   - macOS: 运行 Python 证书安装工具
   - 或手动安装企业证书

4️⃣ 【替代方案】优先使用 Tushare 数据源
   - Tushare 在你的机器上可以正常工作
   - 数据质量和稳定性都很好
""")
