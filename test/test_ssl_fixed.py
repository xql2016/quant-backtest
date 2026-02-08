"""
测试修复后的 SSL 配置
"""

# 测试导入
print("测试 SSL 配置...")

from ssl_config import disable_ssl_verification

# 启用 SSL 配置
disable_ssl_verification()

# 测试数据获取
print("\n测试数据获取...")

import datetime
from data_source import get_stock_data

# 测试 Tushare
print("\n【测试 Tushare】")
try:
    df = get_stock_data(
        code="000001",
        start_date=datetime.date(2024, 12, 1),
        end_date=datetime.date(2024, 12, 31),
        market="A股",
        source_type="tushare",
        token="9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"
    )
    
    if df is not None and not df.empty:
        print(f"✅ Tushare 成功获取 {len(df)} 条数据")
    else:
        print("❌ Tushare 数据为空")
except Exception as e:
    print(f"❌ Tushare 失败: {e}")

# 测试 AKShare
print("\n【测试 AKShare】")
try:
    df = get_stock_data(
        code="000001",
        start_date=datetime.date(2024, 12, 1),
        end_date=datetime.date(2024, 12, 31),
        market="A股",
        source_type="akshare"
    )
    
    if df is not None and not df.empty:
        print(f"✅ AKShare 成功获取 {len(df)} 条数据")
    else:
        print("❌ AKShare 数据为空")
except Exception as e:
    print(f"❌ AKShare 失败: {e}")

print("\n✅ 测试完成！")
print("\n💡 结论：")
print("   - 如果没有报错，说明 SSL 配置修复成功")
print("   - Tushare 应该始终可用")
print("   - AKShare 可能仍需要等待或有其他限制")
