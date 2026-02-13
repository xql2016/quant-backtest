"""
数据源缓存装饰器
在现有数据源基础上透明地添加缓存功能
"""

import pandas as pd
from typing import Optional
import datetime
from cache_manager import CacheManager


class CachedDataSourceWrapper:
    """
    数据源缓存包装器
    
    使用装饰器模式，在不修改原有数据源代码的情况下添加缓存功能
    """
    
    def __init__(self, data_source, cache_manager: Optional[CacheManager] = None):
        """
        初始化缓存包装器
        
        Args:
            data_source: 原始数据源对象 (AKShareDataSource, YFinanceDataSource, TushareDataSource)
            cache_manager: 缓存管理器实例，如果为None则创建新实例
        """
        self.data_source = data_source
        self.cache_manager = cache_manager or CacheManager()
        
        # 获取数据源类型
        self.source_type = self._get_source_type()
    
    def _get_source_type(self) -> str:
        """获取数据源类型"""
        class_name = self.data_source.__class__.__name__
        if 'AKShare' in class_name:
            return 'akshare'
        elif 'YFinance' in class_name:
            return 'yfinance'
        elif 'Tushare' in class_name:
            return 'tushare'
        else:
            return 'unknown'
    
    def fetch_data(self, code: str, start_date: datetime.date, end_date: datetime.date, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取数据（带缓存）
        
        查询流程：
        1. 先查缓存
        2. 缓存命中 -> 返回缓存数据
        3. 缓存未命中 -> 调用原始数据源获取数据 -> 保存到缓存 -> 返回数据
        
        Args:
            code: 股票/资产代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数（market, interval等）
            
        Returns:
            DataFrame或None
        """
        # 获取参数
        market = kwargs.get('market', 'A股')
        interval = kwargs.get('interval', '1d')
        
        # 标准化market名称（用于目录结构）
        market_normalized = self._normalize_market_name(market)
        
        # 1. 先查缓存
        cached_data = self.cache_manager.get_data(
            data_source=self.source_type,
            market=market_normalized,
            code=code,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        if cached_data is not None and not cached_data.empty:
            print(f"🎯 使用缓存数据: {code} ({len(cached_data)} 条记录)")
            return cached_data
        
        # 2. 缓存未命中，调用原始数据源
        print(f"🌐 从API获取数据: {code}")
        data = self.data_source.fetch_data(code, start_date, end_date, **kwargs)
        
        # 3. 保存到缓存
        if data is not None and not data.empty:
            success = self.cache_manager.save_data(
                data=data,
                data_source=self.source_type,
                market=market_normalized,
                code=code,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )
            
            if success:
                print(f"💾 数据已缓存: {code}")
        
        return data
    
    def _normalize_market_name(self, market: str) -> str:
        """
        标准化市场名称（用于目录结构）
        
        将中文市场名称转换为英文目录名
        """
        market_map = {
            'A股': 'a_stock',
            '港股': 'hk_stock',
            '美股': 'us_stock',
            '可转债': 'convertible_bond',
            '加密货币': 'crypto',
            'stock': 'stock_1d',
            'crypto': 'crypto'
        }
        
        return market_map.get(market, market.lower().replace(' ', '_'))
    
    # 代理其他方法（如果有）
    def __getattr__(self, name):
        """将其他方法调用转发到原始数据源"""
        return getattr(self.data_source, name)


def create_cached_data_source(source_type: str = 'akshare', cache_enabled: bool = True, **kwargs):
    """
    创建带缓存的数据源
    
    这是一个便捷工厂函数，用于替代原来的 DataSourceFactory.create_data_source
    
    Args:
        source_type: 数据源类型 ('akshare', 'yfinance', 'tushare')
        cache_enabled: 是否启用缓存
        **kwargs: 数据源特定参数（如token）
        
    Returns:
        带缓存的数据源对象
    
    Example:
        # 创建带缓存的Tushare数据源
        data_source = create_cached_data_source('tushare', token='your_token')
        
        # 获取数据（自动使用缓存）
        df = data_source.fetch_data('000001', start_date, end_date, market='A股')
    """
    # 导入数据源工厂
    from data_source import DataSourceFactory
    
    # 创建原始数据源
    original_source = DataSourceFactory.create_data_source(source_type, **kwargs)
    
    # 如果不启用缓存，直接返回原始数据源
    if not cache_enabled:
        return original_source
    
    # 包装成带缓存的数据源
    return CachedDataSourceWrapper(original_source)


# 便捷函数：获取带缓存的股票数据
def get_cached_stock_data(code: str, 
                          start_date: datetime.date, 
                          end_date: datetime.date,
                          market: str = 'A股',
                          source_type: str = 'akshare',
                          cache_enabled: bool = True,
                          **kwargs) -> Optional[pd.DataFrame]:
    """
    获取股票数据的便捷函数（带缓存）
    
    这个函数可以直接替代 data_source.get_stock_data
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        market: 市场类型
        source_type: 数据源类型
        cache_enabled: 是否启用缓存
        **kwargs: 其他参数（interval, token等）
        
    Returns:
        DataFrame或None
    
    Example:
        df = get_cached_stock_data(
            code='000001',
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            market='A股',
            source_type='tushare',
            token='your_token'
        )
    """
    data_source = create_cached_data_source(source_type, cache_enabled, **kwargs)
    return data_source.fetch_data(code, start_date, end_date, market=market, **kwargs)
