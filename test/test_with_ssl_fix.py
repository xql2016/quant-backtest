"""
测试 SSL 修复后的数据获取
"""

import datetime
import warnings
warnings.filterwarnings('ignore')

# 导入 SSL 配置
from ssl_config import disable_ssl_verification
disable_ssl_verification()

print("=" * 70)
print("🧪 测试 SSL 修复后的数据获取")
print("=" * 70)

# 测试 1: YFinance
print("\n【测试1】YFinance - 美股 AAPL")
print("-" * 70)
try:
    import yfinance as yf
    import time
    
    print("⏳ 等待5秒避免频率限制...")
    time.sleep(5)
    
    end_date = datetime.date(2024, 12, 31)
    start_date = datetime.date(2024, 12, 1)
    
    ticker = yf.Ticker("AAPL")
    df = ticker.history(start=start_date, end=end_date)
    
    if df.empty:
        print("❌ 数据为空")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print(df.head())
        print("\n✨ YFinance 工作正常！")
except Exception as e:
    print(f"❌ 失败: {e}")
    if "Rate limit" in str(e):
        print("💡 仍然是频率限制，需要等待更长时间")

# 测试 2: AKShare
print("\n" + "=" * 70)
print("【测试2】AKShare - A股 000001")
print("-" * 70)
try:
    import akshare as ak
    
    end_date = datetime.date(2024, 12, 31)
    start_date = datetime.date(2024, 12, 1)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    df = ak.stock_zh_a_hist(
        symbol="000001",
        period="daily",
        start_date=start_str,
        end_date=end_str,
        adjust="qfq"
    )
    
    if df.empty:
        print("❌ 数据为空")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print(df.head())
        print("\n✨ AKShare 工作正常！")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "=" * 70)
print("✅ 测试完成")
print("=" * 70)
print("\n💡 结论：")
print("   - 如果 YFinance/AKShare 现在能工作，说明是 SSL 证书问题")
print("   - 如果仍然失败，可能是其他网络限制")
print("   - Tushare 数据源始终可用（推荐）")
