import tushare as ts

# 设置你的token（替换为你自己的）
ts.set_token('9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4')
pro = ts.pro_api()

# 测试：获取可转债列表
try:
    df = pro.cb_basic(fields='ts_code,bond_short_name,stk_code,stk_short_name')
    print(f"✅ Token有效！获取到 {len(df)} 只可转债")
    print("\n前5只可转债：")
    print(df.head())
except Exception as e:
    print(f"❌ 错误：{e}")