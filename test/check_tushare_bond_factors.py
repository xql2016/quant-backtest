"""
检查 Tushare 可转债因子接口
探索是否有转股溢价率、双低指标等
"""

def check_tushare_bond_factors():
    """检查 Tushare 可转债因子数据"""
    
    print("=" * 70)
    print("🔍 检查 Tushare 可转债因子接口")
    print("=" * 70)
    
    try:
        import tushare as ts
        print(f"✅ Tushare 导入成功")
    except Exception as e:
        print(f"❌ Tushare 导入失败: {e}")
        return
    
    # 初始化
    token = "9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"
    pro = ts.pro_api(token)
    
    print("\n" + "=" * 70)
    print("📋 Tushare 可转债相关接口")
    print("=" * 70)
    
    interfaces = {
        "cb_basic": "可转债基本信息",
        "cb_issue": "可转债发行信息",
        "cb_daily": "可转债日线行情",
        "cb_share": "可转债转股结果",
        "cb_call": "可转债回售信息",
        "cb_redeem": "可转债赎回信息",
        "cb_rate": "可转债利率信息",
    }
    
    print("\nTushare 可转债接口列表：")
    for i, (interface, desc) in enumerate(interfaces.items(), 1):
        print(f"   {i}. {interface:15s} - {desc}")
    
    # 测试 cb_basic 接口（最重要）
    print("\n" + "=" * 70)
    print("🧪 测试 cb_basic 接口（可转债基本信息）")
    print("=" * 70)
    
    try:
        print("\n正在获取数据...")
        df = pro.cb_basic(fields='ts_code,bond_short_name,list_date,delist_date,conv_start_date,conv_price,maturity_date')
        
        if df is not None and not df.empty:
            print(f"✅ 成功获取 {len(df)} 条可转债基本信息")
            print(f"\n📊 cb_basic 包含的字段：")
            
            # 获取完整字段列表
            df_full = pro.cb_basic()
            for i, col in enumerate(df_full.columns, 1):
                print(f"   {i:2d}. {col}")
            
            print(f"\n📋 示例数据（前3条）:")
            print(df.head(3).to_string())
        else:
            print(f"❌ 未获取到数据")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试 cb_daily 接口
    print("\n" + "=" * 70)
    print("🧪 测试 cb_daily 接口（可转债日线行情）")
    print("=" * 70)
    
    try:
        print("\n正在获取数据（127045.SZ 最近5天）...")
        df = pro.cb_daily(ts_code='127045.SZ', start_date='20250201', end_date='20250210')
        
        if df is not None and not df.empty:
            print(f"✅ 成功获取 {len(df)} 条数据")
            print(f"\n📊 cb_daily 包含的字段：")
            for i, col in enumerate(df.columns, 1):
                print(f"   {i:2d}. {col}")
            
            print(f"\n📋 示例数据:")
            print(df.to_string())
        else:
            print(f"❌ 未获取到数据")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 关键因子检查
    print("\n" + "=" * 70)
    print("🔍 关键因子检查")
    print("=" * 70)
    
    print("\n❓ Tushare 是否提供以下因子：")
    
    factors = {
        "转股溢价率": "❌ 不提供（需自行计算）",
        "双低指标": "❌ 不提供（需自行计算）",
        "到期收益率": "⚠️  不直接提供（可通过利率和剩余期限计算）",
        "转股价值": "❌ 不提供（需用正股价格/转股价计算）",
        "纯债价值": "❌ 不提供（需通过票面利率折现计算）",
        "正股价格": "⚠️  不在可转债接口，需查询对应A股",
        "剩余年限": "✅ 提供（list_date, maturity_date）",
        "转股价": "✅ 提供（conv_price）",
        "票面利率": "✅ 提供（cb_rate接口）",
    }
    
    for factor, status in factors.items():
        print(f"   • {factor:12s}: {status}")
    
    # 计算说明
    print("\n" + "=" * 70)
    print("💡 如何获取转股溢价率等因子")
    print("=" * 70)
    
    print("\n如需转股溢价率、双低等因子，需要：")
    print("\n1️⃣ 转股溢价率计算公式：")
    print("   转股溢价率 = (可转债价格 - 转股价值) / 转股价值")
    print("   其中：转股价值 = 正股价格 / 转股价 × 100")
    
    print("\n2️⃣ 双低指标计算：")
    print("   双低 = 可转债价格 + 转股溢价率")
    print("   （价格和溢价率都越低越好）")
    
    print("\n3️⃣ 所需数据：")
    print("   • 可转债价格：cb_daily 接口")
    print("   • 转股价：cb_basic 接口")
    print("   • 正股价格：daily 接口（A股日线）")
    
    print("\n4️⃣ 实现难度：")
    print("   ⭐ 简单 - 只需要关联3个数据表")
    print("   ⭐ 可以实现实时计算")
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 总结")
    print("=" * 70)
    
    print("\n✅ Tushare 提供的基础数据：")
    print("   • 可转债基本信息（代码、转股价、期限等）")
    print("   • 可转债日线行情（OHLC、成交量）")
    print("   • 可转债利率信息")
    print("   • A股日线行情（正股价格）")
    
    print("\n❌ Tushare 不直接提供的因子：")
    print("   • 转股溢价率")
    print("   • 双低指标")
    print("   • 转股价值")
    print("   • 纯债价值")
    
    print("\n💡 建议方案：")
    print("   方案1：使用 AKShare bond_cov_jsl 获取集思录因子（免费）")
    print("   方案2：基于 Tushare 数据自行计算（更准确）")
    print("   方案3：两者结合 - Tushare历史数据 + AKShare实时因子")
    
    print("\n🎯 最佳实践：")
    print("   • 回测：使用 Tushare 数据自行计算（保证数据一致性）")
    print("   • 实盘：使用 AKShare 集思录数据（更新及时）")

if __name__ == "__main__":
    check_tushare_bond_factors()

