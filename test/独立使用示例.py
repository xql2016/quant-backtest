"""
独立使用示例：不依赖Streamlit界面，直接使用模块进行回测
"""

import datetime
import pandas as pd
import matplotlib.pyplot as plt

# 导入自定义模块
from data_source import get_stock_data, DataSourceFactory
from strategy_backtest import StrategyFactory, BacktestEngine

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False


def example1_basic_backtest():
    """示例1：基本回测流程"""
    print("=" * 60)
    print("示例1：基本回测流程 - MACD策略")
    print("=" * 60)
    
    # 1. 获取数据
    print("\n步骤1：获取数据...")
    df = get_stock_data(
        code='000001',
        start_date=datetime.date(2023, 1, 1),
        end_date=datetime.date(2024, 1, 1),
        market='A股',
        source_type='akshare'
    )
    
    if df is None or df.empty:
        print("❌ 数据获取失败")
        return
    
    print(f"✅ 成功获取 {len(df)} 天的数据")
    print(f"数据范围: {df.index[0]} 至 {df.index[-1]}")
    
    # 2. 创建策略
    print("\n步骤2：创建策略...")
    params = {
        'fast': 12,
        'slow': 26,
        'signal': 9
    }
    strategy = StrategyFactory.create_strategy("MACD趋势策略", params)
    print(f"✅ 策略创建成功: {strategy.get_strategy_name()}")
    
    # 3. 运行回测
    print("\n步骤3：运行回测...")
    engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
    result = engine.run(df, strategy)
    print("✅ 回测完成")
    
    # 4. 输出结果
    print("\n" + "=" * 60)
    print("回测结果")
    print("=" * 60)
    print(f"初始资金: ¥{result.initial_cash:,.2f}")
    print(f"最终资产: ¥{result.final_equity:,.2f}")
    print(f"总收益率: {result.total_return:.2%}")
    print(f"基准收益率: {result.benchmark_return:.2%}")
    print(f"超额收益: {(result.total_return - result.benchmark_return):.2%}")
    print(f"交易次数: {result.total_trades}")
    print(f"胜率: {result.win_rate:.2%}")
    print("=" * 60)
    
    # 5. 显示交易日志
    if result.trade_log:
        print("\n交易日志（前5条）:")
        for i, trade in enumerate(result.trade_log[:5]):
            print(f"{i+1}. {trade['日期'].strftime('%Y-%m-%d')} | {trade['操作']} | 价格: ¥{trade['价格']:.2f} | 资产: ¥{trade['资产']:,.2f}")
        if len(result.trade_log) > 5:
            print(f"... 共 {len(result.trade_log)} 条交易记录")
    
    return result


def example2_compare_strategies():
    """示例2：对比多个策略"""
    print("\n" + "=" * 60)
    print("示例2：多策略对比")
    print("=" * 60)
    
    # 获取数据
    print("\n获取数据...")
    df = get_stock_data(
        code='000001',
        start_date=datetime.date(2023, 1, 1),
        end_date=datetime.date(2024, 1, 1),
        market='A股',
        source_type='akshare'
    )
    
    if df is None or df.empty:
        print("❌ 数据获取失败")
        return
    
    print(f"✅ 数据获取成功")
    
    # 定义要测试的策略
    strategies_to_test = [
        ("MACD趋势策略", {'fast': 12, 'slow': 26, 'signal': 9}),
        ("双均线策略(SMA)", {'short': 5, 'long': 20}),
        ("RSI超买超卖", {'period': 14, 'lower': 30, 'upper': 70}),
        ("布林带突破", {'period': 20, 'std': 2.0})
    ]
    
    # 回测引擎
    engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
    
    # 存储结果
    results = []
    
    print("\n开始回测...")
    for strategy_name, params in strategies_to_test:
        print(f"\n测试策略: {strategy_name}")
        try:
            strategy = StrategyFactory.create_strategy(strategy_name, params)
            result = engine.run(df.copy(), strategy)
            results.append({
                '策略': strategy_name,
                '总收益率': result.total_return,
                '基准收益率': result.benchmark_return,
                '超额收益': result.total_return - result.benchmark_return,
                '交易次数': result.total_trades,
                '胜率': result.win_rate,
                '最终资产': result.final_equity
            })
            print(f"  ✅ 完成 | 收益率: {result.total_return:.2%} | 交易次数: {result.total_trades}")
        except Exception as e:
            print(f"  ❌ 失败: {e}")
    
    # 创建对比表格
    print("\n" + "=" * 100)
    print("策略对比结果")
    print("=" * 100)
    
    comparison_df = pd.DataFrame(results)
    comparison_df = comparison_df.sort_values('总收益率', ascending=False)
    
    print(comparison_df.to_string(index=False, float_format=lambda x: f'{x:.4f}' if abs(x) < 1 else f'{x:,.2f}'))
    print("=" * 100)
    
    return comparison_df


def example3_custom_data_source():
    """示例3：使用自定义数据源"""
    print("\n" + "=" * 60)
    print("示例3：扩展数据源示例")
    print("=" * 60)
    
    # 使用工厂模式创建数据源
    print("\n当前支持的数据源：")
    print("1. akshare - AKShare数据源（A股、港股、美股）")
    print("2. csv - CSV文件数据源（需要指定csv_dir参数）")
    print("3. database - 数据库数据源（需要实现连接逻辑）")
    
    # 示例：使用AKShare数据源
    print("\n使用AKShare数据源...")
    data_source = DataSourceFactory.create_data_source('akshare')
    df = data_source.fetch_data(
        '000001',
        datetime.date(2023, 1, 1),
        datetime.date(2023, 6, 30),
        market='A股'
    )
    
    if df is not None:
        print(f"✅ 成功获取 {len(df)} 天的数据")
        print(f"\n数据预览:")
        print(df.head())
    else:
        print("❌ 数据获取失败")


def example4_wave_strategy():
    """示例4：波段策略回测"""
    print("\n" + "=" * 60)
    print("示例4：波段策略回测")
    print("=" * 60)
    
    # 获取数据
    print("\n获取数据...")
    df = get_stock_data(
        code='000001',
        start_date=datetime.date(2023, 1, 1),
        end_date=datetime.date(2024, 1, 1),
        market='A股',
        source_type='akshare'
    )
    
    if df is None or df.empty:
        print("❌ 数据获取失败")
        return
    
    print(f"✅ 数据获取成功")
    
    # 创建波段策略（使用更激进的参数）
    params = {
        'first_position': 80,          # 首次建仓80%
        'first_add_drop': 5,            # 跌5%加仓
        'first_profit_target': 20,      # 涨20%止盈
        'first_profit_ma': 5,           # 5日均线
        'reentry_ma': 5,                # 突破5日均线重新入场
        'subsequent_position': 80,      # 后续建仓80%
        'subsequent_add_drop': 5,       # 后续跌5%加仓
        'subsequent_profit_target': 15, # 后续涨15%止盈
        'subsequent_profit_ma': 5       # 后续5日均线止盈
    }
    
    print("\n策略参数:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # 运行回测
    print("\n运行回测...")
    strategy = StrategyFactory.create_strategy("波段策略", params)
    engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
    result = engine.run(df, strategy)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("回测结果")
    print("=" * 60)
    print(f"总收益率: {result.total_return:.2%}")
    print(f"基准收益率: {result.benchmark_return:.2%}")
    print(f"交易次数: {result.total_trades}")
    print(f"胜率: {result.win_rate:.2%}")
    print("=" * 60)
    
    # 显示详细交易日志
    if result.trade_log:
        print("\n详细交易日志:")
        for i, trade in enumerate(result.trade_log):
            print(f"{i+1}. {trade['日期'].strftime('%Y-%m-%d')} | {trade['操作']:15s} | 价格: ¥{trade['价格']:7.2f} | 资产: ¥{trade['资产']:12,.2f}")


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("量化回测模块独立使用示例")
    print("🚀" * 30)
    
    # 运行示例
    try:
        # 示例1：基本回测
        example1_basic_backtest()
        
        # 示例2：多策略对比
        example2_compare_strategies()
        
        # 示例3：自定义数据源
        example3_custom_data_source()
        
        # 示例4：波段策略
        example4_wave_strategy()
        
        print("\n" + "✅" * 30)
        print("所有示例运行完成！")
        print("✅" * 30 + "\n")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()

