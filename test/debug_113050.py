"""
调试 113050 数据获取问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_source import TushareDataSource
import datetime

def debug_113050():
    """调试 113050 获取问题"""
    
    print("=" * 60)
    print("🔍 调试 113050 (南银转债) 数据获取")
    print("=" * 60)
    
    # 初始化 Tushare
    token = "9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"
    ts_source = TushareDataSource(token=token)
    
    # 测试不同的时间范围
    test_cases = [
        ("2026-01-01", "2026-02-08", "2026年1月至2月（用户选择的范围）"),
        ("2025-02-01", "2025-12-31", "2025年2月至年底"),
        ("2025-01-01", "2025-12-31", "2025年全年"),
        ("2024-01-01", "2024-12-31", "2024年全年"),
    ]
    
    for start_str, end_str, desc in test_cases:
        print(f"\n{'='*60}")
        print(f"📅 测试: {desc}")
        print(f"    时间范围: {start_str} ~ {end_str}")
        print(f"{'='*60}")
        
        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
        
        try:
            df = ts_source.fetch_data(
                code="113050",
                start_date=start_date,
                end_date=end_date,
                market='可转债'
            )
            
            if df is not None and not df.empty:
                print(f"✅ 成功获取数据！")
                print(f"   数据条数: {len(df)}")
                print(f"   日期范围: {df.index[0].date()} 至 {df.index[-1].date()}")
                print(f"   最新价格: {df['close'].iloc[-1]:.2f} 元")
                
                # 显示最后几条数据
                print(f"\n📊 最后5条数据:")
                print(df.tail())
                
            else:
                print(f"❌ 未获取到数据")
                print(f"💡 可能原因:")
                print(f"   1. 该时间范围内可转债未上市或已退市")
                print(f"   2. Tushare数据更新延迟（未来日期无数据）")
                
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 检查113050的基本信息
    print(f"\n{'='*60}")
    print(f"📋 查询 113050 基本信息")
    print(f"{'='*60}")
    
    if ts_source._init_tushare():
        try:
            bond_info = ts_source.pro.cb_basic(ts_code='113050.SH')
            if bond_info is not None and not bond_info.empty:
                print(f"\n✅ 可转债信息:")
                print(f"   代码: {bond_info['ts_code'].iloc[0]}")
                print(f"   名称: {bond_info['bond_short_name'].iloc[0]}")
                print(f"   上市日期: {bond_info['list_date'].iloc[0]}")
                if 'delist_date' in bond_info.columns and bond_info['delist_date'].iloc[0]:
                    print(f"   退市日期: {bond_info['delist_date'].iloc[0]}")
                else:
                    print(f"   退市日期: 未退市 ✅")
                print(f"   到期日期: {bond_info['maturity_date'].iloc[0]}")
            else:
                print(f"❌ 未找到可转债信息")
        except Exception as e:
            print(f"❌ 查询失败: {e}")
    
    print(f"\n{'='*60}")
    print(f"💡 建议")
    print(f"{'='*60}")
    print(f"1. 如果是未来日期（如2026年），Tushare数据库中还没有数据")
    print(f"2. 请使用历史日期进行测试，如：2025-01-01 至 2025-12-31")
    print(f"3. 或使用最近的日期：2025-01-01 至今天")
    print(f"4. Tushare数据通常T+1更新，最新数据可能是昨天的")

if __name__ == "__main__":
    debug_113050()

