"""
缓存优化工具包

提供三个核心工具：
1. CacheMergeTool - 连续缓存合并工具
2. CacheOverlapTool - 缓存覆盖判断工具
3. CacheAutoOptimizer - 自动优化工具
"""

from .merge_continuous_caches import CacheMergeTool
from .check_cache_overlap import CacheOverlapTool
from .auto_optimize_cache import CacheAutoOptimizer

__version__ = '1.0.0'
__all__ = [
    'CacheMergeTool',
    'CacheOverlapTool', 
    'CacheAutoOptimizer'
]
