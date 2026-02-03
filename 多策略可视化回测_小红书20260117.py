import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import akshare as ak
import yfinance as yf
import datetime

# ===========================
# 0. 全局配置与工具函数
# ===========================
st.set_page_config(
    page_title="全能量化回测工作台", 
    page_icon="📈", 
    layout="wide"
)

# 绘图字体适配（解决中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data(ttl=3600)
def get_stock_data(code, start, end, market='A股'):
    """获取股票数据并做基础清洗
    
    Args:
        code: 股票代码
        start: 开始日期
        end: 结束日期
        market: 市场类型，'A股'、'港股' 或 '美股'
    """
    try:
        # 根据市场类型选择不同的数据接口
        if market == 'A股':
            start_str = start.strftime("%Y%m%d")
            end_str = end.strftime("%Y%m%d")
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_str, end_date=end_str, adjust="qfq")
            
            if df.empty:
                return None
            
            # 标准化列名
            df.rename(columns={'日期': 'date', '收盘': 'close', '最高': 'high', '最低': 'low', '开盘': 'open', '成交量': 'volume'}, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
        elif market == '港股':
            start_str = start.strftime("%Y%m%d")
            end_str = end.strftime("%Y%m%d")
            df = ak.stock_hk_hist(symbol=code, period="daily", start_date=start_str, end_date=end_str, adjust="qfq")
            
            if df.empty:
                return None
            
            # 标准化列名
            df.rename(columns={'日期': 'date', '收盘': 'close', '最高': 'high', '最低': 'low', '开盘': 'open', '成交量': 'volume'}, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
        elif market == '美股':
            # 使用 yfinance 获取美股数据
            ticker = yf.Ticker(code)
            df = ticker.history(start=start, end=end)
            
            if df.empty:
                return None
            
            # yfinance 返回的列名是英文大写，需要转换
            df.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            
            # 重置索引，将日期作为普通列
            df.reset_index(inplace=True)
            df.rename(columns={'Date': 'date'}, inplace=True)
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)  # 去除时区信息
            df.set_index('date', inplace=True)
        else:
            return None
        
        # 确保数据类型正确
        numeric_cols = ['close', 'high', 'low', 'open', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
    except Exception as e:
        return None

# ===========================
# 1. 侧边栏：控制面板
# ===========================
st.sidebar.title("🎛️ 策略控制面板")

# --- A. 基础设置 ---
st.sidebar.markdown("### 1. 基础回测设置")

# 市场选择
market_type = st.sidebar.selectbox(
    "选择市场",
    ["A股", "港股", "美股"],
    help="选择要回测的市场类型"
)

# 根据市场类型显示不同的股票代码输入提示
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

# 默认回测最近3年
default_start = datetime.date.today() - datetime.timedelta(days=365*3)
default_end = datetime.date.today()
date_range = st.sidebar.date_input("回测区间", [default_start, default_end])

initial_cash = st.sidebar.number_input("初始资金 (元)", value=100000, step=10000)
commission_rate = st.sidebar.number_input("双边手续费率 (比如 0.0003)", value=0.0003, format="%.4f")

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
    params['subsequent_position'] = st.sidebar.slider("后续建仓比例 (%)", 50, 90, 80)
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
if run_btn:
    market_flags = {"A股": "🇨🇳", "港股": "🇭🇰", "美股": "🇺🇸"}
    market_flag = market_flags.get(market_type, "")
    st.title(f"📊 量化回测报告：{market_flag} {stock_code}")
    
    with st.spinner('正在拉取数据并进行量化计算...'):
        # 1. 获取数据
        df = get_stock_data(stock_code, start_date, end_date, market_type)
        
        if df is None or df.empty:
            st.error(f"❌ 无法获取代码 {stock_code} 的数据，请检查代码是否正确，或该股在区间内已退市。")
            st.stop()

        # 2. 计算指标 & 生成信号 (Signal: 1买, -1卖, 0持)
        df['signal'] = 0
        
        # 记录开始价格（用于波段策略）
        start_price = df['close'].iloc[0]
        
        # --- 策略逻辑分支 ---
        if selected_strategy == "MACD趋势策略":
            # 计算 MACD
            ema_fast = df['close'].ewm(span=params['fast'], adjust=False).mean()
            ema_slow = df['close'].ewm(span=params['slow'], adjust=False).mean()
            df['dif'] = ema_fast - ema_slow
            df['dea'] = df['dif'].ewm(span=params['signal'], adjust=False).mean()
            df['macd_hist'] = (df['dif'] - df['dea']) * 2
            
            # 信号
            c_buy = (df['dif'].shift(1) < df['dea'].shift(1)) & (df['dif'] > df['dea'])
            c_sell = (df['dif'].shift(1) > df['dea'].shift(1)) & (df['dif'] < df['dea'])
            df.loc[c_buy, 'signal'] = 1
            df.loc[c_sell, 'signal'] = -1

        elif selected_strategy == "双均线策略(SMA)":
            df['sma_short'] = df['close'].rolling(window=params['short']).mean()
            df['sma_long'] = df['close'].rolling(window=params['long']).mean()
            
            c_buy = (df['sma_short'].shift(1) < df['sma_long'].shift(1)) & (df['sma_short'] > df['sma_long'])
            c_sell = (df['sma_short'].shift(1) > df['sma_long'].shift(1)) & (df['sma_short'] < df['sma_long'])
            df.loc[c_buy, 'signal'] = 1
            df.loc[c_sell, 'signal'] = -1

        elif selected_strategy == "RSI超买超卖":
            # 计算 RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=params['period']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=params['period']).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # 信号: RSI < Lower -> 买入; RSI > Upper -> 卖出
            df.loc[df['rsi'] < params['lower'], 'signal'] = 1
            df.loc[df['rsi'] > params['upper'], 'signal'] = -1

        elif selected_strategy == "布林带突破":
            df['ma'] = df['close'].rolling(window=params['period']).mean()
            df['std'] = df['close'].rolling(window=params['period']).std()
            df['upper'] = df['ma'] + (df['std'] * params['std'])
            df['lower'] = df['ma'] - (df['std'] * params['std'])
            
            # 策略：价格跌破下轨买入（博反弹），突破上轨卖出（止盈）
            # 注意：这是震荡策略，如果做趋势策略逻辑相反
            df.loc[df['close'] < df['lower'], 'signal'] = 1 
            df.loc[df['close'] > df['upper'], 'signal'] = -1

        elif selected_strategy == "波段策略":
            # 计算多条均线：首次止盈MA、后续入场突破MA、后续止盈MA
            df['first_profit_ma'] = df['close'].rolling(window=params['first_profit_ma']).mean()
            df['reentry_ma'] = df['close'].rolling(window=params['reentry_ma']).mean()
            df['subsequent_profit_ma'] = df['close'].rolling(window=params['subsequent_profit_ma']).mean()
            # 波段策略的信号将在交易循环中特殊处理
            # 这里标记第一天为初始买入信号
            df.loc[df.index[0], 'signal'] = 1

        elif selected_strategy == "多重底入场策略":
            # 计算 MACD
            ema_fast = df['close'].ewm(span=params['fast'], adjust=False).mean()
            ema_slow = df['close'].ewm(span=params['slow'], adjust=False).mean()
            df['dif'] = ema_fast - ema_slow
            df['dea'] = df['dif'].ewm(span=params['signal'], adjust=False).mean()
            df['macd_hist'] = (df['dif'] - df['dea']) * 2
            
            # 识别MACD柱的局部低点（前后都比当前值大）
            df['is_macd_trough'] = False
            for i in range(2, len(df) - 2):
                if (df['macd_hist'].iloc[i] < df['macd_hist'].iloc[i-1] and 
                    df['macd_hist'].iloc[i] < df['macd_hist'].iloc[i-2] and
                    df['macd_hist'].iloc[i] < df['macd_hist'].iloc[i+1] and
                    df['macd_hist'].iloc[i] < df['macd_hist'].iloc[i+2] and
                    df['macd_hist'].iloc[i] < 0):  # 只考虑负值的低点
                    df.loc[df.index[i], 'is_macd_trough'] = True
            
            # 查找多重底信号
            lookback = params['lookback']
            divergence_count = params['divergence_count']
            zero_threshold = params['zero_threshold']
            
            for i in range(lookback, len(df)):
                if df['is_macd_trough'].iloc[i]:
                    # 当前是MACD低点，检查是否形成多重底
                    current_price = df['close'].iloc[i]
                    current_macd = df['macd_hist'].iloc[i]
                    
                    # 查找前面的MACD低点
                    previous_troughs = []
                    for j in range(i - 5, max(i - lookback, 0), -1):
                        if df['is_macd_trough'].iloc[j]:
                            previous_troughs.append(j)
                            if len(previous_troughs) >= divergence_count - 1:
                                break
                    
                    # 如果找到足够的前置低点
                    if len(previous_troughs) >= divergence_count - 1:
                        valid_divergence = True
                        
                        # 检查每对相邻底是否符合条件
                        all_indices = previous_troughs[::-1] + [i]  # 按时间顺序排列
                        
                        for k in range(len(all_indices) - 1):
                            idx1 = all_indices[k]
                            idx2 = all_indices[k + 1]
                            
                            price1 = df['close'].iloc[idx1]
                            price2 = df['close'].iloc[idx2]
                            macd1 = df['macd_hist'].iloc[idx1]
                            macd2 = df['macd_hist'].iloc[idx2]
                            
                            # 条件1：价格创新低
                            if price2 >= price1:
                                valid_divergence = False
                                break
                            
                            # 条件2：MACD柱不创新低（底背离）
                            if macd2 <= macd1:
                                valid_divergence = False
                                break
                            
                            # 条件3：两底之间MACD要回到接近0轴
                            between_max = df['macd_hist'].iloc[idx1:idx2+1].max()
                            if between_max < -zero_threshold:  # 没有回到0轴附近
                                valid_divergence = False
                                break
                        
                        # 如果所有条件都满足，产生买入信号
                        if valid_divergence:
                            df.loc[df.index[i], 'signal'] = 1
                            
                            # 止盈：价格上涨达到目标百分比
                            entry_price = df['close'].iloc[i]
                            target_price = entry_price * (1 + params['profit_pct'] / 100)
                            for j in range(i + 1, len(df)):
                                if df['close'].iloc[j] >= target_price:
                                    df.loc[df.index[j], 'signal'] = -1
                                    break

        # 3. 模拟交易循环
        cash = initial_cash
        position = 0
        equity_curve = []
        trade_log = []
        
        # 波段策略专用变量
        if selected_strategy == "波段策略":
            has_added = False  # 是否已加仓
            current_start_price = start_price  # 当前波段的初始价格
            waiting_for_reentry = False  # 是否在等待重新入场（止盈后）
            is_first_band = True  # 是否是第一个波段（True=首次，False=后续）
        
        for date, row in df.iterrows():
            price = row['close']
            sig = row['signal']
            
            # === 波段策略的特殊逻辑 ===
            if selected_strategy == "波段策略":
                # 第一个波段：第一天买入首批仓位
                if position == 0 and not waiting_for_reentry and is_first_band:
                    position_ratio = params['first_position'] / 100
                    cost = price * (1 + commission_rate)
                    buy_cash = cash * position_ratio
                    hands = int(buy_cash / (cost * 100))
                    if hands > 0:
                        position = hands * 100
                        cash -= position * cost
                        current_start_price = price
                        trade_log.append({'日期': date, '操作': f'首次买入{params["first_position"]}%', '价格': price, '资产': cash + position*price})
                
                # 等待重新入场：价格突破后续入场MA时，买入后续建仓比例
                elif position == 0 and waiting_for_reentry:
                    reentry_ma_value = row['reentry_ma']
                    prev_close = df['close'].shift(1).loc[date]
                    prev_reentry_ma = df['reentry_ma'].shift(1).loc[date]
                    
                    # 判断是否突破后续入场MA：前一日在MA下方，今日收盘价在MA上方
                    if not pd.isna(reentry_ma_value) and not pd.isna(prev_close) and not pd.isna(prev_reentry_ma):
                        cross_above_ma = (prev_close < prev_reentry_ma) and (price > reentry_ma_value)
                        if cross_above_ma:
                            position_ratio = params['subsequent_position'] / 100
                            cost = price * (1 + commission_rate)
                            buy_cash = cash * position_ratio
                            hands = int(buy_cash / (cost * 100))
                            if hands > 0:
                                position = hands * 100
                                cash -= position * cost
                                current_start_price = price  # 更新新的波段初始价格
                                has_added = False  # 重置加仓标志
                                waiting_for_reentry = False  # 重新开始持仓
                                is_first_band = False  # 标记为后续波段
                                trade_log.append({'日期': date, '操作': f'突破MA{params["reentry_ma"]}买入{params["subsequent_position"]}%', '价格': price, '资产': cash + position*price})
                
                # 持仓中：判断加仓或止盈
                elif position > 0:
                    # 根据是首次还是后续，使用不同的参数
                    if is_first_band:
                        # 首次波段参数
                        add_drop_pct = params['first_add_drop']
                        profit_target_pct = params['first_profit_target']
                        profit_ma_col = 'first_profit_ma'
                        position_ratio = params['first_position'] / 100
                    else:
                        # 后续波段参数
                        add_drop_pct = params['subsequent_add_drop']
                        profit_target_pct = params['subsequent_profit_target']
                        profit_ma_col = 'subsequent_profit_ma'
                        position_ratio = params['subsequent_position'] / 100
                    
                    # 加仓条件：价格比当前波段初始价格跌超过设定比例，且尚未加仓
                    drop_threshold = current_start_price * (1 - add_drop_pct / 100)
                    if price <= drop_threshold and not has_added:
                        cost = price * (1 + commission_rate)
                        hands = int(cash / (cost * 100))
                        if hands > 0:
                            add_shares = hands * 100
                            cash -= add_shares * cost
                            position += add_shares
                            has_added = True
                            add_ratio = int((1 - position_ratio) * 100)
                            trade_log.append({'日期': date, '操作': f'加仓{add_ratio}%', '价格': price, '资产': cash + position*price})
                    
                    # 止盈条件：价格超过当前波段初始价格的目标涨幅 且 当日跌破相应MA
                    profit_threshold = current_start_price * (1 + profit_target_pct / 100)
                    profit_ma_value = row[profit_ma_col]
                    prev_close = df['close'].shift(1).loc[date]
                    
                    # 判断是否跌破MA：前一日在MA上方，今日收盘价在MA下方
                    if not pd.isna(profit_ma_value) and not pd.isna(prev_close):
                        prev_profit_ma = df[profit_ma_col].shift(1).loc[date]
                        if not pd.isna(prev_profit_ma):
                            cross_below_ma = (prev_close >= prev_profit_ma) and (price < profit_ma_value)
                            if price >= profit_threshold and cross_below_ma:
                                revenue = price * position * (1 - commission_rate)
                                cash += revenue
                                position = 0
                                has_added = False
                                waiting_for_reentry = True  # 标记为等待重新入场
                                trade_log.append({'日期': date, '操作': '止盈', '价格': price, '资产': cash})
            
            # === 其他策略的标准逻辑 ===
            else:
                # 买入
                if sig == 1 and position == 0:
                    cost = price * (1 + commission_rate)
                    hands = int(cash / (cost * 100))
                    if hands > 0:
                        position = hands * 100
                        cash -= position * cost
                        trade_log.append({'日期': date, '操作': '买入', '价格': price, '资产': cash + position*price})
                
                # 卖出
                elif sig == -1 and position > 0:
                    revenue = price * position * (1 - commission_rate)
                    cash += revenue
                    position = 0
                    trade_log.append({'日期': date, '操作': '卖出', '价格': price, '资产': cash})
            
            # 记录每日净值
            equity_curve.append(cash + position * price)
            
        df['equity'] = equity_curve
        
        # 4. 结果统计
        total_ret = (df['equity'].iloc[-1] - initial_cash) / initial_cash
        df['benchmark'] = initial_cash * (df['close'] / df['close'].iloc[0]) # 简单的买入持有
        bench_ret = (df['benchmark'].iloc[-1] - initial_cash) / initial_cash
        
        # 胜率计算（简单版：基于卖出时的资金变化）
        win_count = 0
        sell_count = 0
        last_asset = initial_cash
        for trade in trade_log:
            if trade['操作'] == '卖出':
                sell_count += 1
                if trade['资产'] > last_asset:
                    win_count += 1
                last_asset = trade['资产'] # 更新上一笔卖出后的资产水位
        win_rate = win_count / sell_count if sell_count > 0 else 0

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
                st.dataframe(log_df, use_container_width=True)
            else:
                st.info("该区间内未触发任何交易信号。")

else:
    # 欢迎页
    st.info("👋 欢迎来到量化实验室！\n\n支持 🇨🇳 A股、🇭🇰 港股 和 🇺🇸 美股回测。请在左侧侧边栏选择市场、输入股票代码并选择策略，点击【开始回测】按钮。")