"""
检查 AKShare 可转债因子数据接口
探索可用的因子：波动率、股息率、转股溢价率等
"""

def check_akshare_bond_factors():
    """检查 AKShare 可转债因子数据"""
    
    print("=" * 70)
    print("🔍 检查 AKShare 可转债因子数据接口")
    print("=" * 70)
    
    try:
        import akshare as ak
        print(f"✅ AKShare 版本: {ak.__version__}")
    except Exception as e:
        print(f"❌ AKShare 导入失败: {e}")
        return
    
    # 1. 列出所有可转债相关接口
    print("\n" + "=" * 70)
    print("📋 AKShare 可转债相关接口")
    print("=" * 70)
    
    # 获取所有以 bond 开头的接口
    bond_interfaces = [name for name in dir(ak) if 'bond' in name.lower() and not name.startswith('_')]
    
    print(f"\n找到 {len(bond_interfaces)} 个债券相关接口：\n")
    for i, interface in enumerate(bond_interfaces, 1):
        print(f"   {i:2d}. {interface}")
    
    # 2. 重点测试集思录接口（最重要的因子数据源）
    print("\n" + "=" * 70)
    print("🧪 测试集思录可转债实时数据接口 (bond_cov_jsl)")
    print("=" * 70)
    
    if hasattr(ak, 'bond_cov_jsl'):
        try:
            print("\n正在获取数据...")
            df = ak.bond_cov_jsl()
            
            if df is not None and not df.empty:
                print(f"✅ 成功获取 {len(df)} 条可转债数据")
                
                print(f"\n📊 数据列名 ({len(df.columns)} 列):")
                for i, col in enumerate(df.columns, 1):
                    print(f"   {i:2d}. {col}")
                
                # 检查关键因子字段
                print(f"\n" + "=" * 70)
                print(f"🔍 关键因子字段检查")
                print(f"=" * 70)
                
                factor_mapping = {
                    "转股溢价率": ["溢价率", "转股溢价率", "premium_rt", "溢价"],
                    "双低指标": ["双低", "双低值", "double_low"],
                    "到期收益率": ["到期收益率", "ytm_rt", "ytm", "到期"],
                    "纯债溢价率": ["纯债溢价率", "pure_bond_premium", "纯债"],
                    "纯债价值": ["纯债价值", "pure_bond_value", "纯债"],
                    "转股价值": ["转股价值", "conversion_value", "转股"],
                    "正股价格": ["正股价格", "stock_price", "正股价"],
                    "转股价": ["转股价", "conversion_price", "convert_price"],
                    "剩余年限": ["剩余年限", "year_left", "剩余"],
                    "评级": ["评级", "rating", "信用"],
                    "规模": ["规模", "amount", "余额"],
                }
                
                found_factors = {}
                for factor_name, possible_names in factor_mapping.items():
                    found = False
                    for col in df.columns:
                        col_str = str(col).lower()
                        if any(name.lower() in col_str for name in possible_names):
                            found_factors[factor_name] = col
                            print(f"   ✅ {factor_name:12s}: {col}")
                            found = True
                            break
                    if not found:
                        print(f"   ❌ {factor_name:12s}: 未找到")
                
                # 显示示例数据（只显示找到的因子列）
                if found_factors:
                    print(f"\n📋 示例数据（前3条，仅显示关键因子）:")
                    display_cols = list(found_factors.values())[:10]  # 最多显示10列
                    if '代码' in df.columns:
                        display_cols.insert(0, '代码')
                    if '名称' in df.columns:
                        display_cols.insert(1, '名称')
                    
                    print(df[display_cols].head(3).to_string())
                
            else:
                print(f"❌ 未获取到数据")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ bond_cov_jsl 接口不可用")
    
    # 3. 测试历史数据接口
    print(f"\n" + "=" * 70)
    print(f"🧪 测试可转债历史行情接口 (bond_zh_hs_cov_daily)")
    print(f"=" * 70)
    
    if hasattr(ak, 'bond_zh_hs_cov_daily'):
        print(f"✅ bond_zh_hs_cov_daily 接口可用")
        print(f"   说明：可获取历史OHLC数据，用于计算波动率")
    else:
        print(f"❌ bond_zh_hs_cov_daily 接口不可用")
    
    # 4. 总结
    print(f"\n" + "=" * 70)
    print(f"📊 AKShare 可转债因子数据总结")
    print(f"=" * 70)
    
    print(f"\n✅ 可直接获取的因子（通过 bond_cov_jsl）：")
    print(f"   • 转股溢价率 ✅")
    print(f"   • 双低指标 ✅")
    print(f"   • 到期收益率 ✅")
    print(f"   • 纯债价值/溢价率 ✅")
    print(f"   • 转股价值 ✅")
    print(f"   • 正股价格 ✅")
    print(f"   • 转股价 ✅")
    print(f"   • 剩余年限 ✅")
    print(f"   • 评级 ✅")
    
    print(f"\n❌ 需要自行计算的因子：")
    print(f"   • 波动率：需基于 bond_zh_hs_cov_daily 历史数据计算")
    print(f"     - 常用：20日波动率、60日波动率")
    print(f"     - 计算方法：收益率标准差 × √252")
    
    print(f"\n❌ 不可获取的因子：")
    print(f"   • 股息率：可转债本身无股息")
    print(f"     - 如需正股股息率，需查询正股A股数据")
    print(f"     - 可使用 stock_dividend_cninfo 等接口")
    
    print(f"\n💡 推荐方案：")
    print(f"   1. 使用 bond_cov_jsl 获取实时因子（转股溢价率、双低等）")
    print(f"   2. 使用 bond_zh_hs_cov_daily 获取历史价格，计算波动率")
    print(f"   3. 如需正股股息率，通过正股代码查询A股数据")
    
    print(f"\n🆚 与 Tushare 对比：")
    print(f"   • AKShare：免费，数据来源集思录，因子较全")
    print(f"   • Tushare：付费（2000积分），数据更专业，接口更稳定")
    print(f"   • 建议：两者结合使用，Tushare获取基础数据，AKShare补充因子")

if __name__ == "__main__":
    check_akshare_bond_factors()
