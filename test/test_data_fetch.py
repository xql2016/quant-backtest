"""
数据获取测试脚本
用于测试不同数据源能否正常获取数据
"""

import datetime
import sys

print("=" * 60)
print("🔍 数据获取测试脚本")
print("=" * 60)

# 测试1：测试YFinance港股数据
print("\n【测试1】YFinance - 港股 0700.HK (腾讯)")
print("-" * 60)
try:
    import yfinance as yf
    print("✅ yfinance 导入成功")
    
    # 获取最近30天的数据
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    print(f"📅 测试日期范围: {start_date} 至 {end_date}")
    
    ticker = yf.Ticker("0700.HK")
    print("📊 正在获取数据...")
    
    df = ticker.history(start=start_date, end=end_date)
    
    if df.empty:
        print("❌ 数据为空！")
        print("💡 可能原因：")
        print("   1. 网络连接问题")
        print("   2. Yahoo Finance API限制")
        print("   3. 代码格式错误")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print("\n前5条数据：")
        print(df.head())
        print("\n数据列：", df.columns.tolist())
        
except ImportError as e:
    print(f"❌ yfinance 未安装: {e}")
    print("💡 安装命令: pip install yfinance")
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2：测试AKShare A股数据
print("\n" + "=" * 60)
print("【测试2】AKShare - A股 000001 (平安银行)")
print("-" * 60)
try:
    import akshare as ak
    print("✅ akshare 导入成功")
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
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
        print("\n数据列：", df.columns.tolist())
        
except ImportError as e:
    print(f"❌ akshare 未安装: {e}")
    print("💡 安装命令: pip install akshare")
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3：测试Tushare数据
print("\n" + "=" * 60)
print("【测试3】Tushare - A股 000001.SZ (平安银行)")
print("-" * 60)
try:
    import tushare as ts
    print("✅ tushare 导入成功")
    
    # 使用内置的token
    token = "9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"
    pro = ts.pro_api(token)
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    print(f"📅 测试日期范围: {start_str} 至 {end_str}")
    print("📊 正在获取数据...")
    
    df = pro.daily(ts_code='000001.SZ', start_date=start_str, end_date=end_str)
    
    if df is None or df.empty:
        print("❌ 数据为空！")
        print("💡 可能原因：")
        print("   1. Token无效")
        print("   2. 网络连接问题")
        print("   3. API积分不足")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print("\n前5条数据：")
        print(df.head())
        print("\n数据列：", df.columns.tolist())
        
except ImportError as e:
    print(f"❌ tushare 未安装: {e}")
    print("💡 安装命令: pip install tushare")
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4：测试YFinance美股数据
print("\n" + "=" * 60)
print("【测试4】YFinance - 美股 AAPL (苹果)")
print("-" * 60)
try:
    import yfinance as yf
    print("✅ yfinance 已加载")
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    print(f"📅 测试日期范围: {start_date} 至 {end_date}")
    
    ticker = yf.Ticker("AAPL")
    print("📊 正在获取数据...")
    
    df = ticker.history(start=start_date, end=end_date)
    
    if df.empty:
        print("❌ 数据为空！")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print("\n前5条数据：")
        print(df.head())
        
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

# 测试5：测试YFinance加密货币数据
print("\n" + "=" * 60)
print("【测试5】YFinance - 加密货币 BTC-USD (比特币)")
print("-" * 60)
try:
    import yfinance as yf
    print("✅ yfinance 已加载")
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)  # 只测试7天
    
    print(f"📅 测试日期范围: {start_date} 至 {end_date}")
    
    ticker = yf.Ticker("BTC-USD")
    print("📊 正在获取数据...")
    
    df = ticker.history(start=start_date, end=end_date, interval='1d')
    
    if df.empty:
        print("❌ 数据为空！")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print("\n前5条数据：")
        print(df.head())
        
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ 测试完成！")
print("=" * 60)
print("\n💡 使用建议：")
print("   1. 如果YFinance失败，可能是网络问题或Yahoo Finance API限制")
print("   2. 如果AKShare失败，尝试升级: pip install --upgrade akshare")
print("   3. 如果Tushare失败，检查Token是否有效")
print("   4. 推荐使用Tushare数据源，数据质量最稳定")
