"""
模块测试脚本：验证数据源和策略模块是否正常工作
"""

import datetime
import sys

def test_data_source():
    """测试数据源模块"""
    print("=" * 60)
    print("测试1: 数据源模块")
    print("=" * 60)
    
    try:
        from data_source import get_stock_data, DataSourceFactory, AKShareDataSource
        print("✅ 模块导入成功")
        
        # 测试工厂模式
        print("\n测试工厂模式...")
        data_source = DataSourceFactory.create_data_source('akshare')
        print(f"✅ 创建数据源成功: {type(data_source).__name__}")
        
        # 测试数据获取
        print("\n测试数据获取（获取少量数据以加快速度）...")
        df = get_stock_data(
            code='000001',
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),
            market='A股',
            source_type='akshare'
        )
        
        if df is not None and not df.empty:
            print(f"✅ 数据获取成功: {len(df)} 天")
            print(f"   列: {list(df.columns)}")
            print(f"   索引类型: {type(df.index).__name__}")
            
            # 验证数据格式
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"❌ 缺少必需列: {missing_cols}")
                return False
            else:
                print(f"✅ 数据格式验证通过")
        else:
            print("❌ 数据获取失败")
            return False
        
        print("\n✅ 数据源模块测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据源模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy():
    """测试策略模块"""
    print("\n" + "=" * 60)
    print("测试2: 策略模块")
    print("=" * 60)
    
    try:
        from strategy_backtest import (
            StrategyFactory, 
            BacktestEngine, 
            MACDStrategy,
            DoubleSMAStrategy,
            RSIStrategy,
            BollingerBandsStrategy
        )
        print("✅ 模块导入成功")
        
        # 测试策略工厂
        print("\n测试策略工厂...")
        strategies_to_test = [
            ("MACD趋势策略", {'fast': 12, 'slow': 26, 'signal': 9}),
            ("双均线策略(SMA)", {'short': 5, 'long': 20}),
            ("RSI超买超卖", {'period': 14, 'lower': 30, 'upper': 70}),
            ("布林带突破", {'period': 20, 'std': 2.0})
        ]
        
        for strategy_name, params in strategies_to_test:
            strategy = StrategyFactory.create_strategy(strategy_name, params)
            print(f"✅ 创建策略成功: {strategy.get_strategy_name()}")
        
        # 测试回测引擎
        print("\n测试回测引擎...")
        engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
        print(f"✅ 创建回测引擎成功")
        print(f"   初始资金: ¥{engine.initial_cash:,.2f}")
        print(f"   手续费率: {engine.commission_rate:.4f}")
        
        print("\n✅ 策略模块测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 策略模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """测试集成（完整回测流程）"""
    print("\n" + "=" * 60)
    print("测试3: 集成测试（完整回测流程）")
    print("=" * 60)
    
    try:
        from data_source import get_stock_data
        from strategy_backtest import StrategyFactory, BacktestEngine
        
        # 获取数据
        print("\n步骤1: 获取测试数据...")
        df = get_stock_data(
            code='000001',
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),
            market='A股',
            source_type='akshare'
        )
        
        if df is None or df.empty:
            print("❌ 数据获取失败")
            return False
        
        print(f"✅ 数据获取成功: {len(df)} 天")
        
        # 创建策略
        print("\n步骤2: 创建策略...")
        params = {'fast': 12, 'slow': 26, 'signal': 9}
        strategy = StrategyFactory.create_strategy("MACD趋势策略", params)
        print(f"✅ 策略创建成功: {strategy.get_strategy_name()}")
        
        # 运行回测
        print("\n步骤3: 运行回测...")
        engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
        result = engine.run(df, strategy)
        print("✅ 回测完成")
        
        # 验证结果
        print("\n步骤4: 验证结果...")
        print(f"   总收益率: {result.total_return:.2%}")
        print(f"   基准收益率: {result.benchmark_return:.2%}")
        print(f"   交易次数: {result.total_trades}")
        print(f"   胜率: {result.win_rate:.2%}")
        print(f"   最终资产: ¥{result.final_equity:,.2f}")
        
        # 验证结果对象
        if result.df is None or result.df.empty:
            print("❌ 结果DataFrame为空")
            return False
        
        if 'equity' not in result.df.columns:
            print("❌ 结果缺少equity列")
            return False
        
        if 'signal' not in result.df.columns:
            print("❌ 结果缺少signal列")
            return False
        
        print("✅ 结果验证通过")
        print("\n✅ 集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "🧪" * 30)
    print("模块测试开始")
    print("🧪" * 30 + "\n")
    
    results = []
    
    # 运行所有测试
    results.append(("数据源模块", test_data_source()))
    results.append(("策略模块", test_strategy()))
    results.append(("集成测试", test_integration()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20s}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 所有测试通过！模块工作正常。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

