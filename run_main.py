import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

# SSL 配置（解决证书验证问题）
try:
    from ssl_config import disable_ssl_verification
    # 仅在开发环境禁用 SSL 验证
    disable_ssl_verification()
except ImportError:
    pass  # 如果没有 ssl_config.py，继续正常运行

# 导入自定义模块
from data_source import get_stock_data
from cached_data_source import get_cached_stock_data  # 带缓存的数据获取
from strategy_backtest import StrategyFactory, BacktestEngine

# ===========================
# 0. 全局配置
# ===========================
st.set_page_config(
    page_title="全能量化回测工作台", 
    page_icon="📈", 
    layout="wide"
)

# 绘图字体适配（解决中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False

# ===========================
# 1. 侧边栏：控制面板
# ===========================
st.sidebar.title("🎛️ 策略控制面板")

# --- A. 基础设置 ---
st.sidebar.markdown("### 1. 基础回测设置")

# 数据源选择
data_source = st.sidebar.selectbox(
    "📊 数据源",
    ["Tushare (A股/可转债)", "AKShare (A股/港股)", "YFinance (全球市场/加密货币)"],
    help="选择数据获取来源"
)

# 根据数据源确定实际使用的source_type
if "Tushare" in data_source:
    source_type = "tushare"
    market_options = ["A股", "可转债"]
    
    # Tushare Token 内置配置（不在UI显示）
    tushare_token = "9d1b233c81c719297da330bc01f946fa1d88040946cb8d85ed02e9a4"
    
elif "AKShare" in data_source:
    source_type = "akshare"
    market_options = ["A股", "港股", "美股"]  # 移除可转债选项
    tushare_token = None
else:  # YFinance
    source_type = "yfinance"
    market_options = ["美股", "港股", "加密货币"]
    tushare_token = None

# 市场选择
market_type = st.sidebar.selectbox(
    "🌍 选择市场",
    market_options,
    help="选择要回测的市场类型"
)

# 回测模式选择
st.sidebar.markdown("---")
batch_mode = st.sidebar.radio(
    "📋 回测模式",
    ["单只股票", "批量回测"],
    help="选择单只股票回测或批量回测多只股票"
)

# 根据数据源和市场类型显示不同的股票代码输入提示
if batch_mode == "单只股票":
    if source_type == "tushare":
        # Tushare数据源
        if market_type == "A股":
            stock_code = st.sidebar.text_input(
                "股票代码", 
                value="000001", 
                help="请输入6位A股代码，如 600519、000858"
            )
        elif market_type == "可转债":
            stock_code = st.sidebar.text_input(
                "可转债代码", 
                value="127035", 
                help="请输入6位可转债代码，如 128039(国光转债)、113050(南银转债)、127045(海亮转债)"
            )
    elif source_type == "akshare":
        # AKShare数据源
        if market_type == "A股":
            stock_code = st.sidebar.text_input(
                "股票代码", 
                value="000001", 
                help="请输入6位A股代码，如 600519、000858"
            )
        elif market_type == "港股":
            stock_code = st.sidebar.text_input(
                "股票代码", 
                value="00700", 
                help="请输入5位港股代码，如 00700(腾讯)、09988(阿里)、01810(小米)"
            )
        elif market_type == "美股":
            stock_code = st.sidebar.text_input(
                "股票代码", 
                value="AAPL", 
                help="请输入美股代码，如 AAPL(苹果)、TSLA(特斯拉)、MSFT(微软)"
            )
    else:
        # YFinance数据源
        if market_type == "美股":
            stock_code = st.sidebar.text_input(
                "股票代码", 
                value="AAPL", 
                help="美股代码示例：AAPL(苹果)、TSLA(特斯拉)、MSFT(微软)、NVDA(英伟达)"
            )
        elif market_type == "港股":
            stock_code = st.sidebar.text_input(
                "股票代码", 
                value="0700.HK", 
                help="港股代码需加.HK后缀，如 0700.HK(腾讯)、9988.HK(阿里)、1810.HK(小米)"
            )
        elif market_type == "加密货币":
            stock_code = st.sidebar.text_input(
                "加密货币代码", 
                value="BTC-USD", 
                help="加密货币代码示例：BTC-USD(比特币)、ETH-USD(以太坊)、BNB-USD(币安币)"
            )
    stock_codes = [stock_code]  # 转换为列表格式统一处理
else:
    # 批量回测模式
    stock_codes_input = st.sidebar.text_area(
        "股票代码列表",
        value="000001\n000002\n600519",
        height=150,
        help="每行输入一个股票代码，支持批量回测。示例：\n000001\n000002\n600519"
    )
    # 解析输入的代码列表
    stock_codes = [code.strip() for code in stock_codes_input.split('\n') if code.strip()]
    
    if stock_codes:
        st.sidebar.success(f"✅ 已输入 {len(stock_codes)} 只股票")
    else:
        st.sidebar.error("❌ 请输入至少一个股票代码")

# 默认回测最近3年（需要先定义，供后续使用）
default_start = datetime.date.today() - datetime.timedelta(days=365*3)
default_end = datetime.date.today()
date_range = st.sidebar.date_input("回测区间", [default_start, default_end])

# 时间粒度选择（只有加密货币支持小时线）
if source_type == "yfinance" and market_type == "加密货币":
    time_interval = st.sidebar.selectbox(
        "⏰ 时间粒度",
        ["日线 (1d)", "4小时线 (4h)", "1小时线 (1h)"],
        help="加密货币支持小时级数据，4小时线和1小时线最多回溯约730天"
    )
    # 提取实际的interval参数
    if "1h" in time_interval:
        interval = "1h"
        # 1小时线最多支持730天
        max_days = 730
        if len(date_range) == 2:
            days_diff = (date_range[1] - date_range[0]).days
            if days_diff > max_days:
                st.sidebar.warning(f"⚠️ 1小时线最多支持{max_days}天数据，建议缩短回测区间")
    elif "4h" in time_interval:
        interval = "4h"
        # 4小时线最多支持730天（基于1小时数据聚合）
        max_days = 730
        if len(date_range) == 2:
            days_diff = (date_range[1] - date_range[0]).days
            if days_diff > max_days:
                st.sidebar.warning(f"⚠️ 4小时线最多支持{max_days}天数据，建议缩短回测区间")
    else:
        interval = "1d"
else:
    # 其他市场只支持日线
    interval = "1d"
    if source_type == "yfinance" and market_type != "加密货币":
        st.sidebar.info("ℹ️ 当前市场仅支持日线数据")

initial_cash = st.sidebar.number_input("初始资金 (元)", value=100000, step=10000)

# 手续费设置
st.sidebar.markdown("**💰 手续费设置**")
buy_commission = st.sidebar.number_input(
    "买入手续费率", 
    value=0.0003, 
    format="%.4f",
    help="买入时的手续费率，如0.0003表示万三"
)
sell_commission = st.sidebar.number_input(
    "卖出手续费率", 
    value=0.0003, 
    format="%.4f",
    help="卖出时的手续费率，如0.0003表示万三"
)

# --- 异常检查：日期 ---
if len(date_range) == 2:
    start_date, end_date = date_range
    if start_date > end_date:
        st.sidebar.error("❌ 错误：开始日期不能晚于结束日期")
        st.stop()
else:
    st.sidebar.warning("⚠️ 请选择完整的开始和结束日期")
    st.stop()

# --- B. 策略选择与参数 ---
st.sidebar.markdown("### 2. 策略与参数")
strategy_list = ["MACD趋势策略", "双均线策略(SMA)", "RSI超买超卖", "布林带突破", "波段策略", "多重底入场策略"]
selected_strategy = st.sidebar.selectbox("选择交易策略", strategy_list)

# 动态参数容器
params = {}

if selected_strategy == "MACD趋势策略":
    st.sidebar.caption("逻辑：DIF上穿DEA买入(金叉)，下穿卖出(死叉)")
    params['fast'] = st.sidebar.slider("快线周期 (Fast)", 2, 60, 12)
    params['slow'] = st.sidebar.slider("慢线周期 (Slow)", 10, 100, 26)
    params['signal'] = st.sidebar.slider("信号周期 (Signal)", 2, 60, 9)
    # 异常检查
    if params['fast'] >= params['slow']:
        st.sidebar.error("❌ 错误：快线周期必须小于慢线周期！")
        st.stop()

elif selected_strategy == "双均线策略(SMA)":
    st.sidebar.caption("逻辑：短线上穿长线买入，下穿卖出")
    params['short'] = st.sidebar.slider("短期均线", 2, 60, 5)
    params['long'] = st.sidebar.slider("长期均线", 10, 250, 20)
    # 异常检查
    if params['short'] >= params['long']:
        st.sidebar.error("❌ 错误：短期均线必须小于长期均线！")
        st.stop()

elif selected_strategy == "RSI超买超卖":
    st.sidebar.caption("逻辑：RSI < 下轨买入(抄底)，RSI > 上轨卖出(逃顶)")
    params['period'] = st.sidebar.slider("RSI周期", 2, 30, 14)
    params['lower'] = st.sidebar.slider("超卖阈值 (下轨)", 10, 40, 30)
    params['upper'] = st.sidebar.slider("超买阈值 (上轨)", 60, 90, 70)
    # 异常检查
    if params['lower'] >= params['upper']:
        st.sidebar.error("❌ 错误：下轨阈值必须小于上轨阈值！")
        st.stop()

elif selected_strategy == "布林带突破":
    st.sidebar.caption("逻辑：跌破下轨买入(回归)，突破上轨卖出")
    params['period'] = st.sidebar.slider("均线周期", 5, 60, 20)
    params['std'] = st.sidebar.slider("标准差倍数", 1.0, 3.0, 2.0, step=0.1)

elif selected_strategy == "波段策略":
    st.sidebar.caption("逻辑：首次和后续建仓使用不同参数，灵活控制每个波段")
    
    # 首次建仓参数
    st.sidebar.markdown("#### 🎯 首次建仓参数")
    params['first_position'] = st.sidebar.slider("首次建仓比例 (%)", 50, 100, 80)
    params['first_add_drop'] = st.sidebar.slider("首次加仓跌幅 (%)", 3, 10, 5)
    params['first_profit_target'] = st.sidebar.slider("首次止盈涨幅 (%)", 10, 50, 20)
    params['first_profit_ma'] = st.sidebar.slider("首次止盈均线周期", 3, 20, 5)
    
    # 后续入场参数
    st.sidebar.markdown("#### 🔄 后续入场参数")
    params['reentry_ma'] = st.sidebar.slider("突破均线周期（重新买入）", 3, 20, 5)
    params['subsequent_position'] = st.sidebar.slider("后续建仓比例 (%)", 50, 100, 80)
    params['subsequent_add_drop'] = st.sidebar.slider("后续加仓跌幅 (%)", 3, 10, 5)
    params['subsequent_profit_target'] = st.sidebar.slider("后续止盈涨幅 (%)", 0, 30, 15)
    params['subsequent_profit_ma'] = st.sidebar.slider("后续止盈均线周期", 3, 20, 5)

elif selected_strategy == "多重底入场策略":
    st.sidebar.caption("逻辑：价格创新低但MACD柱不创新低（底背离），形成多重底入场")
    params['fast'] = st.sidebar.slider("MACD快线周期", 5, 30, 12)
    params['slow'] = st.sidebar.slider("MACD慢线周期", 15, 60, 26)
    params['signal'] = st.sidebar.slider("MACD信号周期", 5, 20, 9)
    params['lookback'] = st.sidebar.slider("价格新低回溯期", 20, 60, 30, help="判断价格新低的天数")
    params['divergence_count'] = st.sidebar.slider("底背离次数", 2, 4, 2, help="形成几重底（2=双重底，3=三重底）")
    params['zero_threshold'] = st.sidebar.slider("0轴阈值", 0.0, 1.0, 0.3, step=0.1, help="MACD回到0轴附近的容忍度")
    params['profit_pct'] = st.sidebar.slider("止盈百分比 (%)", 5, 30, 15)
    # 异常检查
    if params['fast'] >= params['slow']:
        st.sidebar.error("❌ 错误：快线周期必须小于慢线周期！")
        st.stop()

# --- C. 启动按钮 ---
run_btn = st.sidebar.button("🚀 开始回测", type="primary")

# ===========================
# 2. 核心逻辑处理
# ===========================

# 初始化 session_state 用于保存批量回测结果
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None
if 'batch_trades' not in st.session_state:
    st.session_state.batch_trades = None
if 'batch_failed' not in st.session_state:
    st.session_state.batch_failed = None
if 'batch_metadata' not in st.session_state:
    st.session_state.batch_metadata = None

if run_btn:
    # 定义通用变量（批量和单股都需要）
    data_source_names = {"akshare": "AKShare", "yfinance": "YFinance", "tushare": "Tushare"}
    data_source_name = data_source_names.get(source_type, "未知")
    market_flags = {"A股": "🇨🇳", "港股": "🇭🇰", "美股": "🇺🇸", "加密货币": "💎", "可转债": "📜"}
    market_flag = market_flags.get(market_type, "")
    interval_names = {"1h": "1小时线", "4h": "4小时线", "1d": "日线"}
    interval_name = interval_names.get(interval, "日线")
    
    # 批量回测模式
    if batch_mode == "批量回测" and len(stock_codes) > 1:
        st.title("📊 批量回测报告")
        st.caption(f"数据源：{data_source_name} | 市场：{market_type} | 策略：{selected_strategy}")
        
        # 创建结果容器
        results = []
        failed_codes = []
        all_trades = []  # 存储所有交易记录
        
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 逐个股票回测
        for idx, stock_code in enumerate(stock_codes):
            try:
                status_text.text(f"正在回测 {stock_code} ({idx+1}/{len(stock_codes)})...")
                
                # 获取数据
                if source_type == "yfinance":
                    df = get_cached_stock_data(stock_code, start_date, end_date, market=market_type, source_type=source_type, interval=interval, cache_enabled=True)
                elif source_type == "tushare":
                    df = get_cached_stock_data(stock_code, start_date, end_date, market=market_type, source_type=source_type, token=tushare_token, cache_enabled=True)
                else:
                    df = get_cached_stock_data(stock_code, start_date, end_date, market=market_type, source_type=source_type, cache_enabled=True)
                
                if df is None or df.empty:
                    failed_codes.append((stock_code, "无法获取数据"))
                    continue
                
                # 执行回测
                strategy = StrategyFactory.create_strategy(selected_strategy, params)
                engine = BacktestEngine(
                    initial_cash=initial_cash, 
                    buy_commission=buy_commission,
                    sell_commission=sell_commission,
                    allow_fractional=True,
                    min_trade_value=0
                )
                result = engine.run(df, strategy)
                
                # 记录结果
                results.append({
                    'code': stock_code,
                    'total_return': result.total_return,
                    'benchmark_return': result.benchmark_return,
                    'win_rate': result.win_rate,
                    'total_trades': result.total_trades,
                    'final_equity': result.df['equity'].iloc[-1],
                    'max_drawdown': result.max_drawdown if hasattr(result, 'max_drawdown') else 0,
                    'sharpe_ratio': result.sharpe_ratio if hasattr(result, 'sharpe_ratio') else 0
                })
                
                # 收集交易记录
                if result.trade_log:
                    for trade in result.trade_log:
                        trade_record = trade.copy()
                        trade_record['股票代码'] = stock_code
                        all_trades.append(trade_record)
                
            except Exception as e:
                failed_codes.append((stock_code, str(e)))
            
            # 更新进度
            progress_bar.progress((idx + 1) / len(stock_codes))
        
        status_text.empty()
        progress_bar.empty()
        
        # 保存结果到 session_state
        st.session_state.batch_results = results
        st.session_state.batch_trades = all_trades
        st.session_state.batch_failed = failed_codes
        st.session_state.batch_metadata = {
            'data_source': data_source_name,
            'market': market_type,
            'strategy': selected_strategy
        }
    
    # 单只股票回测模式
    else:
        stock_code = stock_codes[0]  # 取第一个（唯一的）代码
        
        st.title(f"📊 量化回测报告：{market_flag} {stock_code}")
        st.caption(f"数据源：{data_source_name} | 市场：{market_type} | 时间粒度：{interval_name}")
        
        with st.spinner(f'正在从 {data_source_name} 拉取数据并进行量化计算...'):
            # 显示缓存信息
            cache_info_placeholder = st.empty()
            
            # 1. 获取数据（使用带缓存的数据源）
            # 如果是YFinance且支持interval参数，则传入
            if source_type == "yfinance":
                df = get_cached_stock_data(stock_code, start_date, end_date, market=market_type, source_type=source_type, interval=interval, cache_enabled=True)
            elif source_type == "tushare":
                df = get_cached_stock_data(stock_code, start_date, end_date, market=market_type, source_type=source_type, token=tushare_token, cache_enabled=True)
            else:
                df = get_cached_stock_data(stock_code, start_date, end_date, market=market_type, source_type=source_type, cache_enabled=True)
            
            # 清除缓存信息占位符
            cache_info_placeholder.empty()
            
            if df is None or df.empty:
                st.error(f"❌ 无法获取代码 {stock_code} 的数据，请检查代码是否正确，或该股在区间内已退市。")
                st.stop()

            # 2. 创建策略和回测引擎
            try:
                strategy = StrategyFactory.create_strategy(selected_strategy, params)
            
                # 创建回测引擎（支持小数股交易，最大化资金利用率）
                engine = BacktestEngine(
                    initial_cash=initial_cash, 
                    buy_commission=buy_commission,    # 买入手续费率
                    sell_commission=sell_commission,  # 卖出手续费率
                    allow_fractional=True,            # 允许小数股交易
                    min_trade_value=0                 # 无最小交易金额限制
                )
            
                # 3. 运行回测
                result = engine.run(df, strategy)
            
                # 将结果赋值给df和trade_log，以便后续绘图使用
                df = result.df
                trade_log = result.trade_log
                total_ret = result.total_return
                bench_ret = result.benchmark_return
                win_rate = result.win_rate
                sell_count = result.total_trades
            
                # 记录开始价格（用于波段策略绘图）
                start_price = df['close'].iloc[0]
            
            except Exception as e:
                st.error(f"❌ 回测过程中出现错误: {e}")
                st.stop()
        

            # ===========================
            # 3. 仪表盘展示
            # ===========================
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("最终资产", f"{df['equity'].iloc[-1]:,.0f}", delta=f"{total_ret*100:.2f}%")
            col2.metric("基准收益", f"{bench_ret*100:.2f}%", delta_color="off")
            col3.metric("交易次数", f"{sell_count}", help="指完成买卖闭环的次数")
            col4.metric("策略胜率", f"{win_rate*100:.1f}%")

            # --- 图表区 ---
            st.subheader("📈 资金曲线与技术指标")
        
            # 根据策略类型决定子图数量
            if selected_strategy == "多重底入场策略":
                fig = plt.figure(figsize=(12, 14))
                # 主图：股价 + 买卖点
                ax1 = fig.add_subplot(311)
            else:
                fig = plt.figure(figsize=(12, 10))
                # 主图：股价 + 买卖点
                ax1 = fig.add_subplot(211)
        
            ax1.plot(df.index, df['close'], label='收盘价', color='#333', alpha=0.6)
        
            # 如果有布林带，画轨道
            if selected_strategy == "布林带突破":
                ax1.plot(df.index, df['upper'], color='green', linestyle='--', alpha=0.3, label='上轨')
                ax1.plot(df.index, df['lower'], color='red', linestyle='--', alpha=0.3, label='下轨')
                ax1.fill_between(df.index, df['upper'], df['lower'], color='gray', alpha=0.1)
            # 如果是均线策略，画均线
            elif selected_strategy == "双均线策略(SMA)":
                ax1.plot(df.index, df['sma_short'], color='#ff7f0e', alpha=0.6, label='短期均线')
                ax1.plot(df.index, df['sma_long'], color='#1f77b4', alpha=0.6, label='长期均线')
            # 如果是波段策略，画多条均线和参考线
            elif selected_strategy == "波段策略":
                # 画三条MA线
                ax1.plot(df.index, df['first_profit_ma'], color='#ff7f0e', alpha=0.5, linewidth=1.5, 
                        label=f'首次止盈MA{params["first_profit_ma"]}', linestyle='-')
                ax1.plot(df.index, df['reentry_ma'], color='#2ca02c', alpha=0.5, linewidth=1.5, 
                        label=f'后续入场MA{params["reentry_ma"]}', linestyle='--')
                ax1.plot(df.index, df['subsequent_profit_ma'], color='#d62728', alpha=0.5, linewidth=1.5, 
                        label=f'后续止盈MA{params["subsequent_profit_ma"]}', linestyle='-.')
                # 首波段参考线
                ax1.axhline(y=start_price, color='blue', linestyle='--', alpha=0.3, label='首波段价格')
                ax1.axhline(y=start_price * (1 - params['first_add_drop']/100), color='orange', 
                           linestyle=':', alpha=0.3, label=f'首次加仓(-{params["first_add_drop"]}%)')
                ax1.axhline(y=start_price * (1 + params['first_profit_target']/100), color='green', 
                           linestyle=':', alpha=0.3, label=f'首次止盈(+{params["first_profit_target"]}%)')
            # 如果是多重底策略，显示MACD低点
            elif selected_strategy == "多重底入场策略":
                # 标记MACD低点
                macd_troughs = df[df['is_macd_trough'] == True]
                if len(macd_troughs) > 0:
                    ax1.scatter(macd_troughs.index, macd_troughs['close'], 
                               marker='o', c='purple', s=50, alpha=0.5, label='MACD低点', zorder=4)

            # 标记买卖点
            buys = df[df['signal'] == 1]
            sells = df[df['signal'] == -1]
            ax1.scatter(buys.index, buys['close'], marker='^', c='r', s=80, label='买入', zorder=5)
            ax1.scatter(sells.index, sells['close'], marker='v', c='g', s=80, label='卖出', zorder=5)
            ax1.legend(loc='upper left')
            ax1.set_title(f"{stock_code} 价格走势与交易信号")
            ax1.grid(True, alpha=0.2)

            # 根据策略显示不同的副图
            if selected_strategy == "多重底入场策略":
                # MACD图
                ax2 = fig.add_subplot(312, sharex=ax1)
                # 绘制MACD柱状图
                colors = ['red' if x < 0 else 'green' for x in df['macd_hist']]
                ax2.bar(df.index, df['macd_hist'], color=colors, alpha=0.6, width=1, label='MACD柱')
                ax2.plot(df.index, df['dif'], label='DIF', color='blue', linewidth=1, alpha=0.7)
                ax2.plot(df.index, df['dea'], label='DEA', color='orange', linewidth=1, alpha=0.7)
                ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.3)
                ax2.axhline(y=params['zero_threshold'], color='purple', linestyle='--', linewidth=0.5, alpha=0.3, label='0轴阈值')
                ax2.axhline(y=-params['zero_threshold'], color='purple', linestyle='--', linewidth=0.5, alpha=0.3)
                # 标记MACD低点
                macd_troughs = df[df['is_macd_trough'] == True]
                if len(macd_troughs) > 0:
                    ax2.scatter(macd_troughs.index, macd_troughs['macd_hist'], 
                               marker='o', c='purple', s=60, label='MACD低点', zorder=5)
                ax2.legend(loc='upper left', fontsize=8)
                ax2.set_title("MACD指标与底背离")
                ax2.grid(True, alpha=0.2)
            
                # 资金曲线
                ax3 = fig.add_subplot(313, sharex=ax1)
                ax3.plot(df.index, df['equity'], label='策略净值', color='#d62728', linewidth=2)
                ax3.plot(df.index, df['benchmark'], label='基准净值 (买入持有)', color='#7f7f7f', linestyle='--', alpha=0.8)
                ax3.fill_between(df.index, df['equity'], initial_cash, where=(df['equity']>=initial_cash), facecolor='#d62728', alpha=0.1)
                ax3.legend(loc='upper left')
                ax3.set_title("策略资金 vs 基准对比")
                ax3.grid(True, alpha=0.2)
            else:
                # 其他策略：资金曲线 vs 基准
                ax2 = fig.add_subplot(212, sharex=ax1)
                ax2.plot(df.index, df['equity'], label='策略净值', color='#d62728', linewidth=2)
                ax2.plot(df.index, df['benchmark'], label='基准净值 (买入持有)', color='#7f7f7f', linestyle='--', alpha=0.8)
                ax2.fill_between(df.index, df['equity'], initial_cash, where=(df['equity']>=initial_cash), facecolor='#d62728', alpha=0.1)
                ax2.legend(loc='upper left')
                ax2.set_title("策略资金 vs 基准对比")
                ax2.grid(True, alpha=0.2)
        
            st.pyplot(fig)

            # --- 交易日志 ---
            with st.expander("📋 查看详细交易日志"):
                if trade_log:
                    log_df = pd.DataFrame(trade_log)
                    st.dataframe(log_df, width='stretch')
                else:
                    st.info("该区间内未触发任何交易信号。")

else:
    # 欢迎页
    st.info("👋 欢迎来到量化实验室！")
    
    st.markdown("""
    ### 📊 支持的数据源
    
    **Tushare (专业数据源)** ⭐ **推荐**
    - 🇨🇳 A股：完整的历史数据，前复权处理（日线）
    - 📜 可转债：上交所、深交所可转债数据（日线）
    - 🔑 **特点**：数据质量高、更新及时、接口稳定
    - 💡 **提示**：已内置Token，可转债数据需要2000积分权限
    
    **AKShare (A股/港股)**
    - 🇨🇳 A股：完整的历史数据和实时行情（日线）
    - 🇭🇰 港股：港交所上市公司数据（日线）
    - 🇺🇸 美股：部分美股数据支持（日线）
    
    **YFinance (全球市场/加密货币)**
    - 🇺🇸 美股：纳斯达克、纽交所等（日线）
    - 🇭🇰 港股：港交所数据（日线，需加.HK后缀）
    - 💎 加密货币：比特币、以太坊等数字资产（**支持4小时线、1小时线**，最多730天）
    
    ### ⏰ 时间粒度支持
    
    - **日线 (1d)**：所有市场均支持，无时间限制
    - **4小时线 (4h)**：仅加密货币支持，最多回溯730天（约2年）
    - **1小时线 (1h)**：仅加密货币支持，最多回溯730天（约2年）
    
    ### 🚀 开始使用
    
    1. 在左侧选择**数据源**
    2. 选择**市场类型**
    3. 输入**股票/资产代码**
    4. 设置**回测区间**和**策略参数**
    5. 点击【🚀 开始回测】按钮
    
    ### 💡 代码示例
    
    | 市场 | 数据源 | 代码示例 |
    |------|--------|----------|
    | A股 | AKShare | `000001`, `600519`, `000858` |
    | 港股 | AKShare | `00700`, `09988`, `01810` |
    | 可转债 | AKShare | `128039`, `113050`, `127045` ⭐ |
    | 港股 | YFinance | `0700.HK`, `9988.HK`, `1810.HK` |
    | 美股 | YFinance | `AAPL`, `TSLA`, `MSFT`, `NVDA` |
    | 加密货币 | YFinance | `BTC-USD`, `ETH-USD`, `BNB-USD` |
    """)
    
    st.success("💡 提示：不同数据源有不同的代码格式，请根据界面提示输入正确的代码！")

# ===========================
# 侧边栏：缓存管理
# ===========================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📦 数据缓存")

# 显示缓存统计
try:
    from cache_manager import CacheManager
    cache_manager = CacheManager()
    stats = cache_manager.get_statistics()
    
    st.sidebar.info(f"""
    💾 **缓存统计**  
    缓存数: {stats['total_entries']} 个  
    大小: {stats['total_size_mb']:.1f} MB
    """)
except Exception as e:
    st.sidebar.caption("💾 缓存功能：启用")
    st.sidebar.caption("💡 数据会自动缓存")

# ===========================
# 3. 批量回测结果显示（独立于 run_btn，避免下载刷新问题）
# ===========================
if batch_mode == "批量回测" and st.session_state.batch_results is not None:
    results = st.session_state.batch_results
    all_trades = st.session_state.batch_trades
    failed_codes = st.session_state.batch_failed
    metadata = st.session_state.batch_metadata
    
    # 显示标题
    st.title("📊 批量回测报告")
    st.caption(f"数据源：{metadata['data_source']} | 市场：{metadata['market']} | 策略：{metadata['strategy']}")
    
    if results:
        st.success(f"✅ 成功回测 {len(results)} 只股票")
        
        # 创建结果DataFrame
        import pandas as pd
        results_df = pd.DataFrame(results)
        
        # 添加超额收益列
        results_df['excess_return'] = results_df['total_return'] - results_df['benchmark_return']
        
        # 排序（按策略收益率降序）
        results_df = results_df.sort_values('total_return', ascending=False)
        
        # 汇总统计
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("平均收益率", f"{results_df['total_return'].mean()*100:.2f}%")
        col2.metric("最佳收益", f"{results_df['total_return'].max()*100:.2f}%")
        col3.metric("最差收益", f"{results_df['total_return'].min()*100:.2f}%")
        col4.metric("胜率中位数", f"{results_df['win_rate'].median()*100:.1f}%")
        
        # 详细结果表格
        st.subheader("📋 详细结果")
        
        # 格式化显示
        display_df = results_df.copy()
        display_df['策略收益率'] = display_df['total_return'].apply(lambda x: f"{x*100:.2f}%")
        display_df['基准收益率'] = display_df['benchmark_return'].apply(lambda x: f"{x*100:.2f}%")
        display_df['超额收益'] = display_df['excess_return'].apply(lambda x: f"{x*100:.2f}%")
        display_df['胜率'] = display_df['win_rate'].apply(lambda x: f"{x*100:.1f}%")
        display_df['最终资产'] = display_df['final_equity'].apply(lambda x: f"{x:,.0f}")
        
        # 选择要显示的列
        st.dataframe(
            display_df[['code', '策略收益率', '基准收益率', '超额收益', '胜率', 'total_trades', '最终资产']].rename(columns={
                'code': '股票代码',
                'total_trades': '交易次数'
            }),
            use_container_width=True,
            height=400
        )
        
        # 下载按钮（使用列布局）
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            # 下载汇总结果（CSV，UTF-8 BOM编码）
            csv_summary = results_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载汇总结果 (CSV)",
                data=csv_summary,
                file_name=f"批量回测汇总_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_summary",
                use_container_width=True
            )
        
        with col_download2:
            # 下载交易记录（CSV，UTF-8 BOM编码）
            if all_trades:
                trades_df = pd.DataFrame(all_trades)
                # 调整列顺序，将股票代码放在最前面
                cols = ['股票代码'] + [col for col in trades_df.columns if col != '股票代码']
                trades_df = trades_df[cols]
                
                csv_trades = trades_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载交易记录 (CSV)",
                    data=csv_trades,
                    file_name=f"批量回测交易记录_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_trades",
                    use_container_width=True
                )
            else:
                st.info("📋 无交易记录")
        
        # 显示交易记录预览
        if all_trades:
            st.subheader("📋 交易记录预览")
            st.caption(f"共 {len(all_trades)} 笔交易，下载CSV查看完整记录")
            
            trades_df = pd.DataFrame(all_trades)
            cols = ['股票代码'] + [col for col in trades_df.columns if col != '股票代码']
            trades_df = trades_df[cols]
            
            # 只显示前20条
            st.dataframe(
                trades_df.head(20),
                use_container_width=True,
                height=300
            )
            
            if len(all_trades) > 20:
                st.info(f"💡 仅显示前20条记录，完整的 {len(all_trades)} 笔交易请下载CSV查看")
    
    # 显示失败的股票
    if failed_codes:
        st.warning(f"⚠️ {len(failed_codes)} 只股票回测失败")
        with st.expander("查看失败详情"):
            for code, reason in failed_codes:
                st.text(f"❌ {code}: {reason}")