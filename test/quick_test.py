"""
快速测试脚本 - 验证 Tushare 数据源
直接测试回测系统是否能正常工作
"""

import datetime
from data_source import get_stock_data
from strategy_backtest import StrategyFactory, BacktestEngine

print("=" * 60)
print("🚀 快速回测测试")
print("=" * 60)

# 配置
stock_code = "000001"  # 平安银行
start_date = datetime.date(2024, 1, 1)
end_date = datetime.date(2024, 12, 31)
market_type = "A股"
source_type = "tushare"
token = "9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"

print(f"\n📊 测试参数：")
print(f"   股票代码: {stock_code}")
print(f"   回测区间: {start_date} 至 {end_date}")
print(f"   数据源: {source_type}")
print(f"   市场: {market_type}")

# 1. 获取数据
print(f"\n⏳ 正在从 Tushare 获取数据...")
df = get_stock_data(
    code=stock_code,
    start_date=start_date,
    end_date=end_date,
    market=market_type,
    source_type=source_type,
    token=token
)

if df is None or df.empty:
    print("❌ 数据获取失败！")
    exit(1)

print(f"✅ 成功获取 {len(df)} 条数据")
print(f"\n数据示例（前5行）：")
print(df.head())

# 2. 创建策略并回测
print(f"\n⏳ 开始回测（双均线策略）...")

strategy_params = {
    'short': 5,
    'long': 20
}

strategy = StrategyFactory.create_strategy("双均线策略(SMA)", strategy_params)
engine = BacktestEngine(
    initial_cash=100000,
    buy_commission=0.0003,
    sell_commission=0.0003,
    allow_fractional=True
)

result = engine.run(df, strategy)

# 3. 显示结果
print(f"\n" + "=" * 60)
print(f"📈 回测结果")
print(f"=" * 60)
print(f"   初始资金: ¥100,000")
print(f"   最终资产: ¥{result.df['equity'].iloc[-1]:,.2f}")
print(f"   策略收益率: {result.total_return*100:.2f}%")
print(f"   基准收益率: {result.benchmark_return*100:.2f}%")
print(f"   交易次数: {result.total_trades}")
print(f"   胜率: {result.win_rate*100:.1f}%")

if result.total_return > result.benchmark_return:
    print(f"\n🎉 策略跑赢基准 {(result.total_return - result.benchmark_return)*100:.2f}%！")
else:
    print(f"\n📉 策略跑输基准 {(result.benchmark_return - result.total_return)*100:.2f}%")

print(f"\n✅ 回测系统工作正常！")
print(f"💡 现在可以在 Streamlit 应用中使用 Tushare 数据源进行回测了")
