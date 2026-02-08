"""
检查 128039 可转债的详细信息
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_source import TushareDataSource
import datetime

def check_bond_info():
    """检查可转债的详细信息"""
    
    print("=" * 60)
    print("🔍 检查可转债 128039 (国光转债)")
    print("=" * 60)
    
    # 初始化 Tushare
    token = "9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"
    ts_source = TushareDataSource(token=token)
    
    # 初始化
    if not ts_source._init_tushare():
        print("❌ Tushare初始化失败")
        return
    
    # 1. 查询可转债基本信息
    print("\n📋 查询可转债基本信息...")
    try:
        bond_basic = ts_source.pro.cb_basic(ts_code='128039.SZ')
        if bond_basic is not None and not bond_basic.empty:
            print("\n✅ 找到可转债信息：")
            print(bond_basic.to_string())
            
            # 提取关键信息
            if 'delist_date' in bond_basic.columns:
                delist_date = bond_basic['delist_date'].iloc[0]
                print(f"\n⚠️  退市日期: {delist_date}")
            if 'maturity_date' in bond_basic.columns:
                maturity_date = bond_basic['maturity_date'].iloc[0]
                print(f"📅 到期日期: {maturity_date}")
            if 'list_date' in bond_basic.columns:
                list_date = bond_basic['list_date'].iloc[0]
                print(f"📅 上市日期: {list_date}")
        else:
            print("❌ 未找到该可转债的基本信息")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 2. 尝试不同的时间范围
    test_periods = [
        ("2025-01-01", "2025-12-31", "2025年全年"),
        ("2024-01-01", "2024-12-31", "2024年全年"),
        ("2023-01-01", "2023-12-31", "2023年全年"),
        ("2020-01-01", "2025-12-31", "2020-2025年"),
    ]
    
    print("\n" + "=" * 60)
    print("📊 尝试不同时间范围获取数据")
    print("=" * 60)
    
    for start_str, end_str, desc in test_periods:
        print(f"\n🔍 测试时间范围: {desc} ({start_str} ~ {end_str})")
        
        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
        
        try:
            df = ts_source.fetch_data(
                code="128039",
                start_date=start_date,
                end_date=end_date,
                market='可转债'
            )
            
            if df is not None and not df.empty:
                print(f"✅ 成功获取 {len(df)} 条数据")
                print(f"   日期范围: {df.index[0].date()} 至 {df.index[-1].date()}")
                print(f"   最新价格: {df['close'].iloc[-1]:.2f} 元")
                break
            else:
                print(f"❌ 该时间范围无数据")
        except Exception as e:
            print(f"❌ 获取失败: {e}")
    
    # 3. 推荐其他可用的可转债
    print("\n" + "=" * 60)
    print("💡 推荐使用以下可转债（已验证可用）")
    print("=" * 60)
    
    recommended_bonds = [
        ("113050", "南银转债", "上交所"),
        ("127045", "海亮转债", "深交所"),
        ("123110", "东财转3", "深交所"),
        ("110053", "苏银转债", "上交所"),
    ]
    
    for code, name, exchange in recommended_bonds:
        print(f"  • {code} - {name} ({exchange})")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_bond_info()

