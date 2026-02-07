"""
数据源获取模块
支持多种数据源，目前实现了AKShare，可方便扩展其他数据源
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional
import datetime
import streamlit as st


class DataSource(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def fetch_data(self, code: str, start_date: datetime.date, end_date: datetime.date, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取股票数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数(如market等)
            
        Returns:
            标准化的DataFrame，包含以下列：
            - date (index): 日期
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
        """
        pass
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """验证数据格式是否符合标准"""
        if df is None or df.empty:
            return False
        
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            return False
        
        if not isinstance(df.index, pd.DatetimeIndex):
            return False
            
        return True


class AKShareDataSource(DataSource):
    """AKShare数据源实现"""
    
    def __init__(self):
        """初始化AKShare数据源"""
        # 延迟导入，在实际使用时才导入
        self.ak = None
        self.yf = None
    
    @st.cache_data(ttl=3600)
    def fetch_data(_self, code: str, start_date: datetime.date, end_date: datetime.date, market: str = 'A股') -> Optional[pd.DataFrame]:
        """
        从AKShare获取股票数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            market: 市场类型 ('A股', '港股', '美股')
            
        Returns:
            标准化的DataFrame
        """
        try:
            if market == 'A股':
                return _self._fetch_a_stock(code, start_date, end_date)
            elif market == '港股':
                return _self._fetch_hk_stock(code, start_date, end_date)
            elif market == '美股':
                return _self._fetch_us_stock(code, start_date, end_date)
            else:
                return None
        except Exception as e:
            print(f"数据获取失败: {e}")
            return None
    
    def _fetch_a_stock(self, code: str, start_date: datetime.date, end_date: datetime.date) -> Optional[pd.DataFrame]:
        """获取A股数据"""
        # 延迟导入
        if self.ak is None:
            try:
                import akshare as ak
                self.ak = ak
            except Exception as e:
                print(f"❌ AKShare导入失败: {e}")
                print("💡 解决方案：")
                print("   1. 重新安装akshare: pip install --upgrade akshare")
                print("   2. 安装py_mini_racer: pip install py_mini_racer")
                print("   3. 如果是Mac M1/M2芯片，尝试: pip install py-mini-racer")
                return None
        
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        df = self.ak.stock_zh_a_hist(
            symbol=code, 
            period="daily", 
            start_date=start_str, 
            end_date=end_str, 
            adjust="qfq"
        )
        
        if df.empty:
            return None
        
        # 标准化列名
        df.rename(columns={
            '日期': 'date', 
            '收盘': 'close', 
            '最高': 'high', 
            '最低': 'low', 
            '开盘': 'open', 
            '成交量': 'volume'
        }, inplace=True)
        
        return self._standardize_dataframe(df)
    
    def _fetch_hk_stock(self, code: str, start_date: datetime.date, end_date: datetime.date) -> Optional[pd.DataFrame]:
        """获取港股数据"""
        # 延迟导入
        if self.ak is None:
            try:
                import akshare as ak
                self.ak = ak
            except Exception as e:
                print(f"❌ AKShare导入失败: {e}")
                return None
        
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        df = self.ak.stock_hk_hist(
            symbol=code, 
            period="daily", 
            start_date=start_str, 
            end_date=end_str, 
            adjust="qfq"
        )
        
        if df.empty:
            return None
        
        # 标准化列名
        df.rename(columns={
            '日期': 'date', 
            '收盘': 'close', 
            '最高': 'high', 
            '最低': 'low', 
            '开盘': 'open', 
            '成交量': 'volume'
        }, inplace=True)
        
        return self._standardize_dataframe(df)
    
    def _fetch_us_stock(self, code: str, start_date: datetime.date, end_date: datetime.date) -> Optional[pd.DataFrame]:
        """获取美股数据 (使用yfinance)"""
        # 延迟导入
        if self.yf is None:
            try:
                import yfinance as yf
                self.yf = yf
            except Exception as e:
                print(f"❌ yfinance导入失败: {e}")
                return None
        
        ticker = self.yf.Ticker(code)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return None
        
        # yfinance返回的列名是英文大写，需要转换
        df.rename(columns={
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # 重置索引，将日期作为列
        df.reset_index(inplace=True)
        df.rename(columns={'Date': 'date'}, inplace=True)
        
        return self._standardize_dataframe(df)
    
    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化数据框格式"""
        # 转换日期列
        df['date'] = pd.to_datetime(df['date'])
        
        # 去除时区信息（如果有）
        if df['date'].dt.tz is not None:
            df['date'] = df['date'].dt.tz_localize(None)
        
        # 设置日期为索引
        df.set_index('date', inplace=True)
        
        # 确保数据类型正确
        numeric_cols = ['close', 'high', 'low', 'open', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df


class CSVDataSource(DataSource):
    """CSV文件数据源（示例扩展）"""
    
    def __init__(self, csv_dir: str):
        """
        初始化CSV数据源
        
        Args:
            csv_dir: CSV文件所在目录
        """
        self.csv_dir = csv_dir
    
    def fetch_data(self, code: str, start_date: datetime.date, end_date: datetime.date, **kwargs) -> Optional[pd.DataFrame]:
        """
        从CSV文件读取数据
        
        Args:
            code: 股票代码（作为文件名）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            标准化的DataFrame
        """
        try:
            import os
            csv_path = os.path.join(self.csv_dir, f"{code}.csv")
            
            if not os.path.exists(csv_path):
                return None
            
            df = pd.read_csv(csv_path)
            
            # 假设CSV格式已经是标准格式
            # 如果不是，需要在这里做列名转换
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 过滤日期范围
            df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
            
            return df if not df.empty else None
            
        except Exception as e:
            print(f"CSV数据读取失败: {e}")
            return None


class DatabaseDataSource(DataSource):
    """数据库数据源（示例扩展）"""
    
    def __init__(self, connection_string: str):
        """
        初始化数据库数据源
        
        Args:
            connection_string: 数据库连接字符串
        """
        self.connection_string = connection_string
    
    def fetch_data(self, code: str, start_date: datetime.date, end_date: datetime.date, **kwargs) -> Optional[pd.DataFrame]:
        """
        从数据库读取数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            标准化的DataFrame
        """
        try:
            # 这里是示例代码，需要根据实际数据库结构修改
            # import sqlalchemy
            # engine = sqlalchemy.create_engine(self.connection_string)
            # 
            # query = f"""
            # SELECT date, open, high, low, close, volume
            # FROM stock_data
            # WHERE code = '{code}'
            # AND date >= '{start_date}'
            # AND date <= '{end_date}'
            # ORDER BY date
            # """
            # 
            # df = pd.read_sql(query, engine)
            # df['date'] = pd.to_datetime(df['date'])
            # df.set_index('date', inplace=True)
            # 
            # return df if not df.empty else None
            
            # 占位符实现
            raise NotImplementedError("数据库数据源需要根据实际情况实现")
            
        except Exception as e:
            print(f"数据库数据读取失败: {e}")
            return None


class DataSourceFactory:
    """数据源工厂类"""
    
    @staticmethod
    def create_data_source(source_type: str = 'akshare', **kwargs) -> DataSource:
        """
        创建数据源实例
        
        Args:
            source_type: 数据源类型 ('akshare', 'csv', 'database')
            **kwargs: 数据源特定的参数
            
        Returns:
            DataSource实例
        """
        if source_type == 'akshare':
            return AKShareDataSource()
        elif source_type == 'csv':
            csv_dir = kwargs.get('csv_dir', './data')
            return CSVDataSource(csv_dir)
        elif source_type == 'database':
            connection_string = kwargs.get('connection_string', '')
            return DatabaseDataSource(connection_string)
        else:
            raise ValueError(f"不支持的数据源类型: {source_type}")


# 便捷函数
def get_stock_data(code: str, start_date: datetime.date, end_date: datetime.date, 
                   market: str = 'A股', source_type: str = 'akshare', **kwargs) -> Optional[pd.DataFrame]:
    """
    获取股票数据的便捷函数
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        market: 市场类型
        source_type: 数据源类型
        **kwargs: 其他参数
        
    Returns:
        标准化的DataFrame
    """
    data_source = DataSourceFactory.create_data_source(source_type, **kwargs)
    return data_source.fetch_data(code, start_date, end_date, market=market)

