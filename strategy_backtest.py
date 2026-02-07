"""
策略与回测模块
包含各种交易策略的实现和回测引擎
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class BacktestResult:
    """回测结果数据类"""
    df: pd.DataFrame  # 包含equity, signal等的完整数据
    trade_log: List[Dict]  # 交易日志
    total_return: float  # 总收益率
    benchmark_return: float  # 基准收益率
    win_rate: float  # 胜率
    total_trades: int  # 交易次数
    initial_cash: float  # 初始资金
    final_equity: float  # 最终资产


class Strategy(ABC):
    """策略抽象基类"""
    
    def __init__(self, params: Dict):
        """
        初始化策略
        
        Args:
            params: 策略参数字典
        """
        self.params = params
    
    @abstractmethod
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算交易信号
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            添加了signal列的DataFrame (1=买入, -1=卖出, 0=持有)
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """返回策略名称"""
        pass


class MACDStrategy(Strategy):
    """MACD趋势策略"""
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        # 计算MACD
        ema_fast = df['close'].ewm(span=self.params['fast'], adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.params['slow'], adjust=False).mean()
        df['dif'] = ema_fast - ema_slow
        df['dea'] = df['dif'].ewm(span=self.params['signal'], adjust=False).mean()
        df['macd_hist'] = (df['dif'] - df['dea']) * 2
        
        # 信号: DIF上穿DEA买入，下穿卖出
        c_buy = (df['dif'].shift(1) < df['dea'].shift(1)) & (df['dif'] > df['dea'])
        c_sell = (df['dif'].shift(1) > df['dea'].shift(1)) & (df['dif'] < df['dea'])
        df.loc[c_buy, 'signal'] = 1
        df.loc[c_sell, 'signal'] = -1
        
        return df
    
    def get_strategy_name(self) -> str:
        return "MACD趋势策略"


class DoubleSMAStrategy(Strategy):
    """双均线策略"""
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        # 计算均线
        df['sma_short'] = df['close'].rolling(window=self.params['short']).mean()
        df['sma_long'] = df['close'].rolling(window=self.params['long']).mean()
        
        # 信号: 短线上穿长线买入，下穿卖出
        c_buy = (df['sma_short'].shift(1) < df['sma_long'].shift(1)) & (df['sma_short'] > df['sma_long'])
        c_sell = (df['sma_short'].shift(1) > df['sma_long'].shift(1)) & (df['sma_short'] < df['sma_long'])
        df.loc[c_buy, 'signal'] = 1
        df.loc[c_sell, 'signal'] = -1
        
        return df
    
    def get_strategy_name(self) -> str:
        return "双均线策略(SMA)"


class RSIStrategy(Strategy):
    """RSI超买超卖策略"""
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params['period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params['period']).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 信号: RSI < 下轨买入, RSI > 上轨卖出
        df.loc[df['rsi'] < self.params['lower'], 'signal'] = 1
        df.loc[df['rsi'] > self.params['upper'], 'signal'] = -1
        
        return df
    
    def get_strategy_name(self) -> str:
        return "RSI超买超卖"


class BollingerBandsStrategy(Strategy):
    """布林带突破策略"""
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        # 计算布林带
        df['ma'] = df['close'].rolling(window=self.params['period']).mean()
        df['std'] = df['close'].rolling(window=self.params['period']).std()
        df['upper'] = df['ma'] + (df['std'] * self.params['std'])
        df['lower'] = df['ma'] - (df['std'] * self.params['std'])
        
        # 信号: 跌破下轨买入，突破上轨卖出
        df.loc[df['close'] < df['lower'], 'signal'] = 1
        df.loc[df['close'] > df['upper'], 'signal'] = -1
        
        return df
    
    def get_strategy_name(self) -> str:
        return "布林带突破"


class WaveStrategy(Strategy):
    """波段策略"""
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        # 计算多条均线
        df['first_profit_ma'] = df['close'].rolling(window=self.params['first_profit_ma']).mean()
        df['reentry_ma'] = df['close'].rolling(window=self.params['reentry_ma']).mean()
        df['subsequent_profit_ma'] = df['close'].rolling(window=self.params['subsequent_profit_ma']).mean()
        
        # 第一天标记为初始买入信号
        df.loc[df.index[0], 'signal'] = 1
        
        return df
    
    def get_strategy_name(self) -> str:
        return "波段策略"


class MultipleDivergenceStrategy(Strategy):
    """多重底入场策略"""
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        
        # 计算MACD
        ema_fast = df['close'].ewm(span=self.params['fast'], adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.params['slow'], adjust=False).mean()
        df['dif'] = ema_fast - ema_slow
        df['dea'] = df['dif'].ewm(span=self.params['signal'], adjust=False).mean()
        df['macd_hist'] = (df['dif'] - df['dea']) * 2
        
        # 识别MACD柱的局部低点
        df['is_macd_trough'] = False
        for i in range(2, len(df) - 2):
            if (df['macd_hist'].iloc[i] < df['macd_hist'].iloc[i-1] and 
                df['macd_hist'].iloc[i] < df['macd_hist'].iloc[i-2] and
                df['macd_hist'].iloc[i] < df['macd_hist'].iloc[i+1] and
                df['macd_hist'].iloc[i] < df['macd_hist'].iloc[i+2] and
                df['macd_hist'].iloc[i] < 0):
                df.loc[df.index[i], 'is_macd_trough'] = True
        
        # 查找多重底信号
        lookback = self.params['lookback']
        divergence_count = self.params['divergence_count']
        zero_threshold = self.params['zero_threshold']
        
        for i in range(lookback, len(df)):
            if df['is_macd_trough'].iloc[i]:
                # 查找前面的MACD低点
                previous_troughs = []
                for j in range(i - 5, max(i - lookback, 0), -1):
                    if df['is_macd_trough'].iloc[j]:
                        previous_troughs.append(j)
                        if len(previous_troughs) >= divergence_count - 1:
                            break
                
                if len(previous_troughs) >= divergence_count - 1:
                    valid_divergence = True
                    all_indices = previous_troughs[::-1] + [i]
                    
                    for k in range(len(all_indices) - 1):
                        idx1 = all_indices[k]
                        idx2 = all_indices[k + 1]
                        
                        price1 = df['close'].iloc[idx1]
                        price2 = df['close'].iloc[idx2]
                        macd1 = df['macd_hist'].iloc[idx1]
                        macd2 = df['macd_hist'].iloc[idx2]
                        
                        # 价格创新低但MACD不创新低
                        if price2 >= price1 or macd2 <= macd1:
                            valid_divergence = False
                            break
                        
                        # 两底之间MACD要回到接近0轴
                        between_max = df['macd_hist'].iloc[idx1:idx2+1].max()
                        if between_max < -zero_threshold:
                            valid_divergence = False
                            break
                    
                    if valid_divergence:
                        df.loc[df.index[i], 'signal'] = 1
                        
                        # 止盈
                        entry_price = df['close'].iloc[i]
                        target_price = entry_price * (1 + self.params['profit_pct'] / 100)
                        for j in range(i + 1, len(df)):
                            if df['close'].iloc[j] >= target_price:
                                df.loc[df.index[j], 'signal'] = -1
                                break
        
        return df
    
    def get_strategy_name(self) -> str:
        return "多重底入场策略"


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_cash: float = 100000, commission_rate: float = 0.0003, 
                 allow_fractional: bool = True, min_trade_value: float = 0):
        """
        初始化回测引擎
        
        Args:
            initial_cash: 初始资金
            commission_rate: 双边手续费率
            allow_fractional: 是否允许小数股交易（True=支持小数，False=只能整股）
            min_trade_value: 最小交易金额（0=无限制）
        """
        self.initial_cash = initial_cash
        self.commission_rate = commission_rate
        self.allow_fractional = allow_fractional
        self.min_trade_value = min_trade_value
    
    def run(self, df: pd.DataFrame, strategy: Strategy) -> BacktestResult:
        """
        运行回测
        
        Args:
            df: 包含OHLCV数据的DataFrame
            strategy: 策略实例
            
        Returns:
            BacktestResult对象
        """
        # 计算信号
        df = strategy.calculate_signals(df)
        
        # 根据策略类型选择回测逻辑
        if isinstance(strategy, WaveStrategy):
            return self._run_wave_backtest(df, strategy)
        else:
            return self._run_standard_backtest(df, strategy)
    
    def _run_standard_backtest(self, df: pd.DataFrame, strategy: Strategy) -> BacktestResult:
        """标准回测逻辑（适用于大多数策略）"""
        cash = self.initial_cash
        position = 0
        equity_curve = []
        trade_log = []
        
        for date, row in df.iterrows():
            price = row['close']
            sig = row['signal']
            
            # 买入
            if sig == 1 and position == 0:
                cost = price * (1 + self.commission_rate)
                
                # 计算可购买数量（支持小数股）
                if self.allow_fractional:
                    # 小数股：使用全部资金，精确到小数点后8位
                    max_shares = cash / cost
                    position = round(max_shares, 8)
                else:
                    # 整股：只能买整数股
                    position = int(cash / cost)
                
                # 检查是否满足最小交易金额
                trade_value = position * price
                if position > 0 and trade_value >= self.min_trade_value:
                    actual_cost = position * cost
                    cash -= actual_cost
                    trade_log.append({
                        '日期': date, 
                        '操作': '买入', 
                        '价格': price,
                        '数量': position,
                        '资产': cash + position * price
                    })
            
            # 卖出
            elif sig == -1 and position > 0:
                revenue = price * position * (1 - self.commission_rate)
                cash += revenue
                position = 0
                trade_log.append({
                    '日期': date, 
                    '操作': '卖出', 
                    '价格': price, 
                    '资产': cash
                })
            
            # 记录每日净值
            equity_curve.append(cash + position * price)
        
        df['equity'] = equity_curve
        
        return self._calculate_result(df, trade_log)
    
    def _run_wave_backtest(self, df: pd.DataFrame, strategy: WaveStrategy) -> BacktestResult:
        """波段策略专用回测逻辑"""
        cash = self.initial_cash
        position = 0
        equity_curve = []
        trade_log = []
        
        # 波段策略专用变量
        has_added = False
        start_price = df['close'].iloc[0]
        current_start_price = start_price
        waiting_for_reentry = False
        is_first_band = True
        
        params = strategy.params
        
        for date, row in df.iterrows():
            price = row['close']
            
            # 第一个波段：第一天买入首批仓位
            if position == 0 and not waiting_for_reentry and is_first_band:
                position_ratio = params['first_position'] / 100
                cost = price * (1 + self.commission_rate)
                buy_cash = cash * position_ratio
                
                # 计算可购买数量（支持小数股）
                if self.allow_fractional:
                    max_shares = buy_cash / cost
                    shares_to_buy = round(max_shares, 8)
                else:
                    shares_to_buy = int(buy_cash / cost)
                
                if shares_to_buy > 0:
                    position = shares_to_buy
                    actual_cost = position * cost
                    cash -= actual_cost
                    current_start_price = price
                    trade_log.append({
                        '日期': date, 
                        '操作': f'首次买入{params["first_position"]}%', 
                        '价格': price,
                        '数量': position,
                        '资产': cash + position * price
                    })
            
            # 等待重新入场
            elif position == 0 and waiting_for_reentry:
                reentry_ma_value = row['reentry_ma']
                prev_close = df['close'].shift(1).loc[date]
                prev_reentry_ma = df['reentry_ma'].shift(1).loc[date]
                
                if not pd.isna(reentry_ma_value) and not pd.isna(prev_close) and not pd.isna(prev_reentry_ma):
                    cross_above_ma = (prev_close < prev_reentry_ma) and (price > reentry_ma_value)
                    if cross_above_ma:
                        position_ratio = params['subsequent_position'] / 100
                        cost = price * (1 + self.commission_rate)
                        buy_cash = cash * position_ratio
                        
                        # 计算可购买数量（支持小数股）
                        if self.allow_fractional:
                            max_shares = buy_cash / cost
                            shares_to_buy = round(max_shares, 8)
                        else:
                            shares_to_buy = int(buy_cash / cost)
                        
                        if shares_to_buy > 0:
                            position = shares_to_buy
                            actual_cost = position * cost
                            cash -= actual_cost
                            current_start_price = price
                            has_added = False
                            waiting_for_reentry = False
                            is_first_band = False
                            trade_log.append({
                                '日期': date, 
                                '操作': f'突破MA{params["reentry_ma"]}买入{params["subsequent_position"]}%', 
                                '价格': price,
                                '数量': position,
                                '资产': cash + position * price
                            })
            
            # 持仓中：判断加仓或止盈
            elif position > 0:
                if is_first_band:
                    add_drop_pct = params['first_add_drop']
                    profit_target_pct = params['first_profit_target']
                    profit_ma_col = 'first_profit_ma'
                    position_ratio = params['first_position'] / 100
                else:
                    add_drop_pct = params['subsequent_add_drop']
                    profit_target_pct = params['subsequent_profit_target']
                    profit_ma_col = 'subsequent_profit_ma'
                    position_ratio = params['subsequent_position'] / 100
                
                # 加仓
                drop_threshold = current_start_price * (1 - add_drop_pct / 100)
                if price <= drop_threshold and not has_added:
                    cost = price * (1 + self.commission_rate)
                    
                    # 计算可购买数量（支持小数股）
                    if self.allow_fractional:
                        max_shares = cash / cost
                        add_shares = round(max_shares, 8)
                    else:
                        add_shares = int(cash / cost)
                    
                    if add_shares > 0:
                        actual_cost = add_shares * cost
                        cash -= actual_cost
                        position += add_shares
                        has_added = True
                        add_ratio = int((1 - position_ratio) * 100)
                        trade_log.append({
                            '日期': date, 
                            '操作': f'加仓{add_ratio}%', 
                            '价格': price,
                            '数量': add_shares,
                            '资产': cash + position * price
                        })
                
                # 止盈
                profit_threshold = current_start_price * (1 + profit_target_pct / 100)
                profit_ma_value = row[profit_ma_col]
                prev_close = df['close'].shift(1).loc[date]
                
                if not pd.isna(profit_ma_value) and not pd.isna(prev_close):
                    prev_profit_ma = df[profit_ma_col].shift(1).loc[date]
                    if not pd.isna(prev_profit_ma):
                        cross_below_ma = (prev_close >= prev_profit_ma) and (price < profit_ma_value)
                        if price >= profit_threshold and cross_below_ma:
                            revenue = price * position * (1 - self.commission_rate)
                            cash += revenue
                            position = 0
                            has_added = False
                            waiting_for_reentry = True
                            trade_log.append({
                                '日期': date, 
                                '操作': '止盈', 
                                '价格': price, 
                                '资产': cash
                            })
            
            equity_curve.append(cash + position * price)
        
        df['equity'] = equity_curve
        
        return self._calculate_result(df, trade_log)
    
    def _calculate_result(self, df: pd.DataFrame, trade_log: List[Dict]) -> BacktestResult:
        """计算回测结果"""
        # 基准收益（买入持有）
        df['benchmark'] = self.initial_cash * (df['close'] / df['close'].iloc[0])
        
        # 总收益率
        total_return = (df['equity'].iloc[-1] - self.initial_cash) / self.initial_cash
        benchmark_return = (df['benchmark'].iloc[-1] - self.initial_cash) / self.initial_cash
        
        # 胜率计算
        win_count = 0
        sell_count = 0
        last_asset = self.initial_cash
        
        for trade in trade_log:
            if trade['操作'] in ['卖出', '止盈']:
                sell_count += 1
                if trade['资产'] > last_asset:
                    win_count += 1
                last_asset = trade['资产']
        
        win_rate = win_count / sell_count if sell_count > 0 else 0
        
        return BacktestResult(
            df=df,
            trade_log=trade_log,
            total_return=total_return,
            benchmark_return=benchmark_return,
            win_rate=win_rate,
            total_trades=sell_count,
            initial_cash=self.initial_cash,
            final_equity=df['equity'].iloc[-1]
        )


class StrategyFactory:
    """策略工厂类"""
    
    @staticmethod
    def create_strategy(strategy_name: str, params: Dict) -> Strategy:
        """
        创建策略实例
        
        Args:
            strategy_name: 策略名称
            params: 策略参数
            
        Returns:
            Strategy实例
        """
        strategy_map = {
            "MACD趋势策略": MACDStrategy,
            "双均线策略(SMA)": DoubleSMAStrategy,
            "RSI超买超卖": RSIStrategy,
            "布林带突破": BollingerBandsStrategy,
            "波段策略": WaveStrategy,
            "多重底入场策略": MultipleDivergenceStrategy
        }
        
        strategy_class = strategy_map.get(strategy_name)
        if strategy_class is None:
            raise ValueError(f"不支持的策略: {strategy_name}")
        
        return strategy_class(params)

