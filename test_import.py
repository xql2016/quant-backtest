#!/usr/bin/env python3
"""测试akshare导入是否正常"""

print("=" * 60)
print("测试 AKShare 和 py_mini_racer 导入")
print("=" * 60)

try:
    print("\n1. 测试 py_mini_racer 导入...")
    import py_mini_racer
    print("   ✅ py_mini_racer 导入成功")
    print(f"   版本: {py_mini_racer.__version__ if hasattr(py_mini_racer, '__version__') else '未知'}")
except Exception as e:
    print(f"   ❌ py_mini_racer 导入失败: {e}")
    exit(1)

try:
    print("\n2. 测试 akshare 导入...")
    import akshare as ak
    print("   ✅ akshare 导入成功")
    print(f"   版本: {ak.__version__}")
except Exception as e:
    print(f"   ❌ akshare 导入失败: {e}")
    exit(1)

try:
    print("\n3. 测试数据源模块导入...")
    from data_source import get_stock_data, AKShareDataSource
    print("   ✅ 数据源模块导入成功")
except Exception as e:
    print(f"   ❌ 数据源模块导入失败: {e}")
    exit(1)

try:
    print("\n4. 测试创建AKShareDataSource实例...")
    ds = AKShareDataSource()
    print("   ✅ AKShareDataSource 实例创建成功")
    print(f"   ak属性: {ds.ak}")
    print(f"   yf属性: {ds.yf}")
except Exception as e:
    print(f"   ❌ 创建实例失败: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ 所有测试通过！模块可以正常使用。")
print("=" * 60)
print("\n💡 建议：在浏览器中刷新Streamlit页面（Ctrl+R 或 Cmd+R）")

