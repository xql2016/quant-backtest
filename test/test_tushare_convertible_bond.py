"""
测试 Tushare 可转债数据获取
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_source import TushareDataSource
import datetime

def test_tushare_convertible_bond():
    """测试 Tushare 可转债数据获取"""
    
    print("=" * 60)
    print("🧪 Tushare 可转债数据测试")
    print("=" * 60)
    
    # 初始化 Tushare
    token = "9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"
    ts_source = TushareDataSource(token=token)
    
    # 测试多个可转债代码
    test_codes = [
        ("128039", "国光转债 (深交所)"),
        ("113050", "南银转债 (上交所)"),
        ("127045", "海亮转债 (深交所)")
    ]
    
    # 设置测试日期范围（最近1年）
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    
    print(f"\n📅 测试日期范围: {start_date} 至 {end_date}\n")
    
    for code, name in test_codes:
        print(f"\n{'='*60}")
        print(f"📜 测试可转债: {name} ({code})")
        print(f"{'='*60}")
        
        try:
            # 获取数据
            df = ts_source.fetch_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                market='可转债'
            )
            
            if df is not None and not df.empty:
                print(f"✅ 数据获取成功！")
                print(f"\n📊 数据概览:")
                print(f"   - 数据条数: {len(df)} 条")
                print(f"   - 日期范围: {df.index[0].date()} 至 {df.index[-1].date()}")
                print(f"   - 列名: {df.columns.tolist()}")
                
                print(f"\n📈 价格统计:")
                print(f"   - 最高价: {df['high'].max():.2f} 元")
                print(f"   - 最低价: {df['low'].min():.2f} 元")
                print(f"   - 平均价: {df['close'].mean():.2f} 元")
                print(f"   - 最新价: {df['close'].iloc[-1]:.2f} 元")
                
                # 检查价格范围
                if df['close'].max() > 200:
                    print(f"   ⚠️  警告：最高价超过200元，可能存在异常")
                if df['close'].min() < 50:
                    print(f"   💡 提示：最低价低于50元，关注下修风险")
                
                print(f"\n📊 成交量统计:")
                print(f"   - 平均成交量: {df['volume'].mean():,.0f}")
                print(f"   - 最大成交量: {df['volume'].max():,.0f}")
                
                print(f"\n🔍 前5行数据:")
                print(df.head())
                
                print(f"\n🔍 最后5行数据:")
                print(df.tail())
                
                # 验证数据完整性
                print(f"\n✅ 数据质量检查:")
                null_counts = df.isnull().sum()
                if null_counts.sum() == 0:
                    print(f"   - 无缺失值")
                else:
                    print(f"   ⚠️  发现缺失值:")
                    for col, count in null_counts[null_counts > 0].items():
                        print(f"      - {col}: {count} 个")
                
                # 验证 OHLC 逻辑
                invalid_ohlc = df[(df['high'] < df['low']) | 
                                  (df['high'] < df['close']) | 
                                  (df['high'] < df['open']) |
                                  (df['low'] > df['close']) | 
                                  (df['low'] > df['open'])]
                
                if len(invalid_ohlc) == 0:
                    print(f"   - OHLC逻辑正确")
                else:
                    print(f"   ⚠️  发现 {len(invalid_ohlc)} 行OHLC数据异常")
                
            else:
                print(f"❌ 数据获取失败或为空")
                print(f"💡 可能原因:")
                print(f"   1. 该可转债在此日期范围内未上市或已退市")
                print(f"   2. Tushare积分不足（可转债数据需要2000积分）")
                print(f"   3. Token配置错误")
                print(f"   4. 网络连接问题")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("✅ Tushare可转债数据测试完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_tushare_convertible_bond()

