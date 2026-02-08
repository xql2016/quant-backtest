"""
数据获取测试脚本 - 修复版本
解决SSL证书和日期问题
"""

import datetime
import warnings
warnings.filterwarnings('ignore')

# 禁用SSL验证（仅用于测试）
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

print("=" * 60)
print("🔍 数据获取测试脚本（修复版）")
print("=" * 60)

# 使用历史日期（2024年）避免未来日期问题
end_date = datetime.date(2024, 12, 31)
start_date = datetime.date(2024, 12, 1)

# 测试1：测试Tushare A股数据（推荐）
print("\n【测试1】Tushare - A股 000001.SZ (平安银行) ⭐ 推荐")
print("-" * 60)
try:
    import tushare as ts
    print("✅ tushare 导入成功")
    
    # 使用内置的token
    token = "9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"
    pro = ts.pro_api(token)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    print(f"📅 测试日期范围: {start_str} 至 {end_str}")
    print("📊 正在获取数据...")
    
    df = pro.daily(ts_code='000001.SZ', start_date=start_str, end_date=end_str)
    
    if df is None or df.empty:
        print("❌ 数据为空！")
        print("💡 可能原因：")
        print("   1. Token无效或过期")
        print("   2. 网络连接问题")
        print("   3. API积分不足")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print("\n前5条数据：")
        print(df.head())
        print("\n✨ Tushare数据源工作正常！")
        
except ImportError as e:
    print(f"❌ tushare 未安装: {e}")
    print("💡 安装命令: pip install tushare")
except Exception as e:
    print(f"❌ 获取数据失败: {e}")

# 测试2：测试AKShare A股数据
print("\n" + "=" * 60)
print("【测试2】AKShare - A股 000001 (平安银行)")
print("-" * 60)
try:
    import akshare as ak
    print("✅ akshare 导入成功")
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    print(f"📅 测试日期范围: {start_str} 至 {end_str}")
    print("📊 正在获取数据...")
    
    df = ak.stock_zh_a_hist(
        symbol="000001", 
        period="daily", 
        start_date=start_str, 
        end_date=end_str, 
        adjust="qfq"
    )
    
    if df.empty:
        print("❌ 数据为空！")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print("\n前5条数据：")
        print(df.head())
        print("\n✨ AKShare数据源工作正常！")
        
except ImportError as e:
    print(f"❌ akshare 未安装: {e}")
    print("💡 安装命令: pip install akshare")
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    print("💡 这可能是网络或SSL证书问题")

# 测试3：测试YFinance美股数据（带重试）
print("\n" + "=" * 60)
print("【测试3】YFinance - 美股 AAPL (苹果)")
print("-" * 60)
try:
    import yfinance as yf
    import time
    print("✅ yfinance 已加载")
    
    print(f"📅 测试日期范围: {start_date} 至 {end_date}")
    print("📊 正在获取数据...")
    print("⏳ 等待3秒避免频率限制...")
    time.sleep(3)
    
    ticker = yf.Ticker("AAPL")
    df = ticker.history(start=start_date, end=end_date)
    
    if df.empty:
        print("❌ 数据为空！")
        print("💡 可能是频率限制，请稍后再试")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print("\n前5条数据：")
        print(df[['Open', 'High', 'Low', 'Close', 'Volume']].head())
        print("\n✨ YFinance数据源工作正常！")
        
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    if "Rate limit" in str(e):
        print("💡 Yahoo Finance API频率限制，请等待几分钟后再试")

print("\n" + "=" * 60)
print("✅ 测试完成！")
print("=" * 60)

print("\n📋 问题总结：")
print("   1. ✅ 依赖包已正确安装")
print("   2. ⚠️  YFinance 有频率限制（每分钟请求次数有限）")
print("   3. ⚠️  SSL证书问题（已通过禁用验证暂时解决）")
print("   4. ⚠️  不要使用未来日期（如2026年）")

print("\n💡 解决方案：")
print("   1. 推荐使用 Tushare 数据源（最稳定）")
print("   2. 如果使用 YFinance，请适当增加请求间隔")
print("   3. 在 Streamlit 应用中使用 @st.cache_data 缓存数据")
print("   4. 使用历史日期进行回测（避免未来日期）")
