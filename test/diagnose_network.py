"""
网络和SSL诊断脚本
检查是否是SSL证书、代理或网络环境问题
"""

import datetime
import time
import sys

print("=" * 70)
print("🔍 网络和SSL环境诊断")
print("=" * 70)

# 检查1：Python SSL配置
print("\n【检查1】Python SSL 配置")
print("-" * 70)
try:
    import ssl
    print(f"✅ SSL模块可用")
    print(f"   OpenSSL版本: {ssl.OPENSSL_VERSION}")
    print(f"   默认证书路径: {ssl.get_default_verify_paths()}")
    
    # 检查是否有自定义证书设置
    context = ssl.create_default_context()
    print(f"   证书验证模式: {context.verify_mode}")
    print(f"   检查主机名: {context.check_hostname}")
except Exception as e:
    print(f"❌ SSL配置检查失败: {e}")

# 检查2：网络代理设置
print("\n【检查2】网络代理配置")
print("-" * 70)
import os
http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
no_proxy = os.environ.get('NO_PROXY') or os.environ.get('no_proxy')

if http_proxy or https_proxy:
    print(f"⚠️  检测到代理设置:")
    if http_proxy:
        print(f"   HTTP_PROXY: {http_proxy}")
    if https_proxy:
        print(f"   HTTPS_PROXY: {https_proxy}")
    if no_proxy:
        print(f"   NO_PROXY: {no_proxy}")
    print(f"\n💡 代理可能会导致SSL证书验证问题")
else:
    print(f"✅ 未检测到代理设置")

# 检查3：测试不同网站的连接
print("\n【检查3】测试网络连接")
print("-" * 70)

test_urls = [
    ("Yahoo Finance", "https://query1.finance.yahoo.com"),
    ("东方财富(AKShare)", "https://push2his.eastmoney.com"),
    ("Tushare", "https://api.tushare.pro"),
]

import urllib.request
import urllib.error

for name, url in test_urls:
    try:
        print(f"\n测试 {name}: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        print(f"   ✅ 连接成功 (状态码: {response.status})")
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print(f"   ❌ 连接失败: {e.reason}")
            if "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
                print(f"   💡 这是SSL证书验证问题！")
        else:
            print(f"   ❌ 连接失败: {e}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")

# 检查4：YFinance 详细测试（单次请求，避免频率限制）
print("\n" + "=" * 70)
print("【检查4】YFinance 单次测试（避免频率限制）")
print("-" * 70)

try:
    import yfinance as yf
    print("✅ yfinance 已导入")
    
    # 只请求一个简单的股票信息（不是历史数据）
    print("\n正在测试获取股票基本信息（不会触发频率限制）...")
    ticker = yf.Ticker("AAPL")
    
    # 尝试获取info（这个请求比较轻量）
    try:
        info = ticker.info
        if info and 'symbol' in info:
            print(f"✅ YFinance API 工作正常！")
            print(f"   股票: {info.get('longName', 'N/A')}")
            print(f"   交易所: {info.get('exchange', 'N/A')}")
            print(f"\n💡 结论: YFinance 本身没问题，之前的错误是频率限制")
        else:
            print(f"⚠️  获取到数据但格式异常")
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        if "CERTIFICATE" in str(e).upper() or "SSL" in str(e).upper():
            print(f"💡 这是SSL证书问题！")
        elif "Rate limit" in str(e) or "Too Many Requests" in str(e):
            print(f"💡 这是频率限制问题，需要等待")
        
except ImportError:
    print("❌ yfinance 未安装")
except Exception as e:
    print(f"❌ 测试失败: {e}")

# 检查5：证书文件位置
print("\n" + "=" * 70)
print("【检查5】系统证书配置")
print("-" * 70)

try:
    import certifi
    print(f"✅ certifi 已安装")
    print(f"   证书包路径: {certifi.where()}")
    
    # 检查证书文件是否存在
    import os
    cert_path = certifi.where()
    if os.path.exists(cert_path):
        file_size = os.path.getsize(cert_path) / 1024
        print(f"   证书文件大小: {file_size:.1f} KB")
        print(f"   ✅ 证书文件存在")
    else:
        print(f"   ❌ 证书文件不存在！")
except ImportError:
    print(f"⚠️  certifi 未安装（可选依赖）")
    print(f"   安装: pip install certifi")

# 总结
print("\n" + "=" * 70)
print("📋 诊断总结")
print("=" * 70)

print("""
根据诊断结果，问题可能是：

1️⃣ 如果 YFinance 显示 "Rate limited"（频率限制）:
   ✅ 这不是SSL问题，是正常的API限制
   💡 解决方案：
      - 等待几分钟后再试
      - 减少请求频率
      - 使用缓存机制（@st.cache_data）

2️⃣ 如果 AKShare 显示 "CERTIFICATE_VERIFY_FAILED":
   ❌ 这是SSL证书验证问题
   💡 可能原因：
      - 公司网络有代理/防火墙
      - SSL证书被拦截或替换
      - Python证书配置问题
   💡 解决方案：
      - 方案A: 使用Tushare数据源（推荐）
      - 方案B: 在代码中禁用SSL验证（仅用于测试）
      - 方案C: 配置正确的企业证书

3️⃣ 推荐的使用方式：
   ⭐ 优先使用 Tushare 数据源（最稳定）
   ⭐ YFinance 需要控制请求频率
   ⭐ AKShare 在某些网络环境下有SSL问题
""")

print("\n💡 建议操作：")
print("   1. 使用 Tushare 数据源（已测试可用）")
print("   2. 如需使用 YFinance，每次请求间隔3-5秒")
print("   3. 如在公司网络，联系IT部门配置SSL证书")
