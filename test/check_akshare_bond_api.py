#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查AKShare可转债接口
"""

import sys

print("=" * 60)
print("检查 AKShare 可转债接口")
print("=" * 60)

# 1. 导入AKShare
print("\n[1] 导入AKShare...")
try:
    import akshare as ak
    print(f"✅ AKShare版本: {ak.__version__}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 2. 查找可转债相关接口
print("\n[2] 查找可转债相关接口...")
bond_apis = [attr for attr in dir(ak) if 'bond' in attr.lower() and 'cov' in attr.lower()]
print(f"找到 {len(bond_apis)} 个相关接口:")
for api in bond_apis:
    print(f"  - {api}")

# 3. 测试常见接口
print("\n[3] 测试可转债接口...")

test_apis = [
    'bond_zh_cov',           # 可转债实时行情
    'bond_cov_jsl',          # 集思录可转债
    'bond_zh_hs_cov_daily',  # 可转债日线（如果存在）
    'bond_zh_cov_daily',     # 可转债日线（旧版本）
]

for api_name in test_apis:
    if hasattr(ak, api_name):
        print(f"\n  ✅ {api_name} 存在")
        try:
            func = getattr(ak, api_name)
            # 尝试获取数据
            if api_name == 'bond_zh_cov' or api_name == 'bond_cov_jsl':
                df = func()
                print(f"     获取数据成功：{len(df)} 条记录")
                print(f"     列名：{df.columns.tolist()}")
                if len(df) > 0:
                    print(f"     示例代码：{df.iloc[0]['代码'] if '代码' in df.columns else 'N/A'}")
            elif 'daily' in api_name:
                # 尝试用一个测试代码
                test_code = "128039"
                print(f"     尝试获取 {test_code} 的历史数据...")
                df = func(symbol=test_code)
                print(f"     ✅ 成功获取：{len(df)} 条记录")
                print(f"     列名：{df.columns.tolist()}")
        except Exception as e:
            print(f"     ⚠️  调用失败: {str(e)[:100]}")
    else:
        print(f"  ❌ {api_name} 不存在")

# 4. 结论和建议
print("\n" + "=" * 60)
print("结论")
print("=" * 60)

if hasattr(ak, 'bond_zh_cov') or hasattr(ak, 'bond_cov_jsl'):
    print("\n✅ AKShare 支持可转债实时行情查询")
    print("   接口：bond_zh_cov() 或 bond_cov_jsl()")
else:
    print("\n❌ 未找到可转债实时行情接口")

if hasattr(ak, 'bond_zh_hs_cov_daily') or hasattr(ak, 'bond_zh_cov_daily'):
    print("\n✅ AKShare 支持可转债历史K线查询")
else:
    print("\n❌ AKShare 不支持可转债历史K线查询")
    print("   💡 建议：")
    print("   1. 使用 Tushare 或其他数据源获取可转债历史数据")
    print("   2. 本系统主要支持 A股、港股、美股、加密货币回测")
    print("   3. 可转债功能受限于数据源支持")

print("\n" + "=" * 60)

