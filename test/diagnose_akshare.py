"""
AKShare 详细诊断脚本
查看具体的 API 响应和错误
"""

import datetime
from ssl_config import disable_ssl_verification

# 禁用 SSL 验证
disable_ssl_verification()

print("=" * 70)
print("🔍 AKShare 详细诊断")
print("=" * 70)

# 测试 1: 直接测试 AKShare API
print("\n【测试1】直接调用 AKShare 获取 A股数据")
print("-" * 70)

try:
    import akshare as ak
    print("✅ akshare 导入成功")
    print(f"   版本: {ak.__version__ if hasattr(ak, '__version__') else '未知'}")
    
    # 测试不同的日期范围
    end_date = datetime.date(2024, 12, 31)
    start_date = datetime.date(2024, 12, 1)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    print(f"\n日期范围: {start_str} 至 {end_str}")
    print(f"股票代码: 000001")
    print(f"\n正在调用 ak.stock_zh_a_hist()...")
    
    # 详细捕获异常
    try:
        df = ak.stock_zh_a_hist(
            symbol="000001", 
            period="daily", 
            start_date=start_str, 
            end_date=end_str, 
            adjust="qfq"
        )
        
        if df is None:
            print("❌ 返回值为 None")
        elif df.empty:
            print("❌ 返回空 DataFrame")
        else:
            print(f"✅ 成功获取 {len(df)} 条数据")
            print(f"\n列名: {df.columns.tolist()}")
            print(f"\n前3行数据:")
            print(df.head(3))
            
    except Exception as e:
        print(f"❌ API 调用失败")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {e}")
        
        # 打印详细的异常栈
        import traceback
        print(f"\n详细错误栈:")
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ akshare 导入失败: {e}")
except Exception as e:
    print(f"❌ 测试失败: {e}")

# 测试 2: 测试其他 AKShare 接口
print("\n" + "=" * 70)
print("【测试2】测试 AKShare 其他接口")
print("-" * 70)

try:
    import akshare as ak
    
    # 测试获取股票列表（这个接口通常更稳定）
    print("\n正在获取 A股实时行情...")
    try:
        df_spot = ak.stock_zh_a_spot_em()
        if df_spot is not None and not df_spot.empty:
            print(f"✅ 成功获取 {len(df_spot)} 只股票的实时数据")
            print(f"   这说明 AKShare 基本功能正常")
        else:
            print("❌ 实时行情数据为空")
    except Exception as e:
        print(f"❌ 实时行情获取失败: {e}")
    
    # 测试历史数据接口（更简单的调用）
    print("\n正在测试历史数据接口（最近5天）...")
    try:
        recent_end = datetime.date.today() - datetime.timedelta(days=1)
        recent_start = recent_end - datetime.timedelta(days=7)
        
        recent_start_str = recent_start.strftime("%Y%m%d")
        recent_end_str = recent_end.strftime("%Y%m%d")
        
        print(f"日期: {recent_start_str} 至 {recent_end_str}")
        
        df_recent = ak.stock_zh_a_hist(
            symbol="000001",
            period="daily",
            start_date=recent_start_str,
            end_date=recent_end_str,
            adjust=""  # 不复权
        )
        
        if df_recent is not None and not df_recent.empty:
            print(f"✅ 成功获取 {len(df_recent)} 条最近数据")
        else:
            print("❌ 最近数据为空")
            
    except Exception as e:
        print(f"❌ 最近数据获取失败: {e}")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")

# 测试 3: 检查网络响应
print("\n" + "=" * 70)
print("【测试3】检查东方财富 API 原始响应")
print("-" * 70)

try:
    import requests
    
    # 构造 AKShare 使用的 API URL
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": "101",
        "fqt": "1",
        "secid": "0.000001",
        "beg": "20241201",
        "end": "20241231"
    }
    
    print(f"URL: {url}")
    print(f"参数: secid=0.000001, 日期=20241201-20241231")
    print(f"\n正在发送请求...")
    
    response = requests.get(url, params=params, timeout=10, verify=False)
    
    print(f"✅ 响应状态码: {response.status_code}")
    print(f"   响应头 Content-Type: {response.headers.get('Content-Type', '未知')}")
    print(f"   响应大小: {len(response.content)} 字节")
    print(f"\n前 500 字符的响应内容:")
    print(response.text[:500])
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n✅ JSON 解析成功")
            print(f"   返回键: {list(data.keys())}")
        except Exception as e:
            print(f"\n❌ JSON 解析失败: {e}")
            print(f"   这可能是 API 返回了 HTML 或其他非 JSON 内容")
    
except Exception as e:
    print(f"❌ 网络请求失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("💡 诊断建议")
print("=" * 70)
print("""
根据错误 "Expecting value: line 1 column 1 (char 0)"，可能的原因：

1. API 返回空内容或非 JSON 格式
   - 可能是 API 端点变化
   - 或者返回了 HTML 错误页面

2. 解决方案：
   ✅ 使用 Tushare 数据源（最稳定可靠）
   ⚠️  AKShare API 可能不稳定或被限制
   ⚠️  等待 AKShare 更新或尝试其他时间段

3. 临时方案：
   - 在 Streamlit 应用中选择 Tushare 数据源
   - Tushare 已验证完全可用
""")
