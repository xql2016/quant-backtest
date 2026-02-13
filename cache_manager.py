"""
数据缓存管理模块
提供本地文件缓存功能，减少对不稳定API的依赖
"""

import pandas as pd
import os
import json
import hashlib
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List, Tuple
import logging
from pathlib import Path


class CacheManager:
    """缓存管理器 - 统一的缓存入口"""
    
    def __init__(self, cache_root: str = "cache"):
        """
        初始化缓存管理器
        
        Args:
            cache_root: 缓存根目录路径
        """
        self.cache_root = Path(cache_root)
        self.data_dir = self.cache_root / "data"
        self.metadata_dir = self.cache_root / "metadata"
        self.logs_dir = self.cache_root / "logs"
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化缓存索引
        self.index = CacheIndex(self.metadata_dir / "cache_index.json")
        
        # 初始化存储层
        self.storage = CacheStorage(self.data_dir, self.config)
        
        # 初始化策略管理器
        self.policy = CachePolicy(self.config)
        
        # 初始化日志
        self._setup_logging()
        
        self.logger.info("缓存管理器初始化完成")
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        config_path = self.cache_root / "config.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"配置文件未找到: {config_path}，使用默认配置")
            return self._get_default_config()
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "cache_settings": {
                "enabled": True,
                "max_size_mb": 1024,
                "default_ttl_hours": 168
            },
            "storage_format": {
                "format": "parquet",
                "compression": "snappy"
            },
            "logging": {
                "enabled": True,
                "log_level": "INFO"
            }
        }
    
    def _setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger("CacheManager")
        
        if not self.config.get("logging", {}).get("enabled", True):
            self.logger.disabled = True
            return
        
        log_level = self.config.get("logging", {}).get("log_level", "INFO")
        self.logger.setLevel(getattr(logging, log_level))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 文件handler
            if self.config.get("logging", {}).get("log_access", False):
                self.logs_dir.mkdir(parents=True, exist_ok=True)
                log_file = self.logs_dir / "cache_access.log"
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def get_data(self, 
                 data_source: str,
                 market: str,
                 code: str,
                 start_date: date,
                 end_date: date,
                 interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        获取数据（带缓存）
        
        Args:
            data_source: 数据源名称 ('akshare', 'yfinance', 'tushare')
            market: 市场类型 ('a_stock', 'hk_stock', 'us_stock', 'convertible_bond', 'crypto')
            code: 股票/资产代码
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间粒度 ('1d', '1h', '4h')
            
        Returns:
            DataFrame或None
        """
        if not self.config.get("cache_settings", {}).get("enabled", True):
            self.logger.info("缓存已禁用")
            return None
        
        # 生成缓存键
        cache_key = self._generate_cache_key(data_source, market, code, start_date, end_date, interval)
        
        self.logger.info(f"查询缓存: {cache_key}")
        
        # 查询缓存
        cache_result = self._query_cache(cache_key, start_date, end_date)
        
        if cache_result['status'] == 'full_match':
            self.logger.info(f"✅ 缓存命中: {cache_key}")
            return cache_result['data']
        elif cache_result['status'] == 'no_match':
            self.logger.info(f"❌ 缓存未命中: {cache_key}")
            return None
        else:
            # partial_match - 暂时不处理，返回None让调用方重新获取
            self.logger.info(f"⚠️ 缓存部分命中: {cache_key}, 需要重新获取")
            return None
    
    def save_data(self,
                  data: pd.DataFrame,
                  data_source: str,
                  market: str,
                  code: str,
                  start_date: date,
                  end_date: date,
                  interval: str = '1d') -> bool:
        """
        保存数据到缓存（带智能检查，避免重复缓存）
        
        Args:
            data: 要缓存的DataFrame
            data_source: 数据源名称
            market: 市场类型
            code: 股票/资产代码
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间粒度
            
        Returns:
            是否保存成功
        """
        if not self.config.get("cache_settings", {}).get("enabled", True):
            return False
        
        if data is None or data.empty:
            self.logger.warning("数据为空，不保存缓存")
            return False
        
        try:
            # 生成缓存键
            cache_key = self._generate_cache_key(data_source, market, code, start_date, end_date, interval)
            
            # 🆕 检查是否已有能覆盖此范围的更大缓存
            # 提取查询的基本信息
            all_entries = self.index.get_all_entries()
            for existing_key, existing_entry in all_entries.items():
                # 检查是否是同一个资产
                if (existing_entry.get('data_source') == data_source and
                    existing_entry.get('market') == market and
                    existing_entry.get('code') == code and
                    existing_entry.get('interval') == interval):
                    
                    # 检查现有缓存的日期范围
                    existing_start = datetime.strptime(existing_entry['start_date'], '%Y-%m-%d').date()
                    existing_end = datetime.strptime(existing_entry['end_date'], '%Y-%m-%d').date()
                    
                    # 如果现有缓存完全覆盖要保存的范围
                    if existing_start <= start_date and existing_end >= end_date:
                        # 检查是否过期
                        if not self.policy.is_expired(existing_entry):
                            self.logger.info(f"⏭️  跳过保存: 已有更大范围的缓存 ({existing_key}) 覆盖此查询")
                            return True  # 返回True表示不需要保存（已有缓存）
            
            # 保存数据文件
            file_path = self.storage.save(data, data_source, market, code, start_date, end_date, interval)
            
            if not file_path:
                self.logger.error(f"保存数据文件失败: {cache_key}")
                return False
            
            # 更新索引
            metadata = {
                'file_path': str(file_path),
                'data_source': data_source,
                'market': market,
                'code': code,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'interval': interval,
                'rows': len(data),
                'columns': list(data.columns),
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'file_size_kb': round(os.path.getsize(file_path) / 1024, 2),
                'checksum': self._calculate_checksum(file_path),
                'is_complete': True
            }
            
            self.index.add_entry(cache_key, metadata)
            
            self.logger.info(f"✅ 缓存保存成功: {cache_key} ({metadata['file_size_kb']} KB)")
            
            # 检查是否需要清理
            self._check_and_cleanup()
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存缓存失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_cache_key(self, data_source: str, market: str, code: str,
                           start_date: date, end_date: date, interval: str) -> str:
        """生成缓存键"""
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        return f"{data_source}_{market}_{code}_{start_str}_{end_str}_{interval}"
    
    def _query_cache(self, cache_key: str, start_date: date, end_date: date) -> dict:
        """
        查询缓存（支持智能日期范围匹配）
        
        Returns:
            {
                'status': 'full_match' | 'partial_match' | 'no_match',
                'data': DataFrame or None,
                'caches': List of matching cache entries
            }
        """
        # 1. 先尝试精确匹配（最快）
        if self.index.has_entry(cache_key):
            entry = self.index.get_entry(cache_key)
            result = self._check_and_load_cache(entry, cache_key, start_date, end_date)
            if result['status'] == 'full_match':
                return result
        
        # 2. 精确匹配失败，尝试查找能覆盖查询范围的更大缓存
        # 提取查询的基本信息（数据源、市场、代码、时间粒度）
        key_parts = cache_key.split('_')
        if len(key_parts) >= 6:
            data_source = key_parts[0]
            market = key_parts[1]
            code = key_parts[2]
            # key_parts[3] = start_date, key_parts[4] = end_date
            interval = key_parts[5] if len(key_parts) > 5 else '1d'
            
            # 遍历所有缓存，查找能覆盖查询范围的缓存
            all_entries = self.index.get_all_entries()
            for existing_key, existing_entry in all_entries.items():
                # 跳过已检查的精确匹配
                if existing_key == cache_key:
                    continue
                
                # 检查是否是同一个资产（数据源、市场、代码、时间粒度相同）
                if (existing_entry.get('data_source') == data_source and
                    existing_entry.get('market') == market and
                    existing_entry.get('code') == code and
                    existing_entry.get('interval') == interval):
                    
                    # 检查日期范围是否能覆盖查询范围
                    result = self._check_and_load_cache(existing_entry, existing_key, start_date, end_date)
                    if result['status'] == 'full_match':
                        self.logger.info(f"✅ 找到覆盖缓存: {existing_key} (覆盖查询范围)")
                        return result
        
        # 3. 未找到任何匹配的缓存
        return {'status': 'no_match', 'data': None, 'caches': []}
    
    def _check_and_load_cache(self, entry: dict, cache_key: str, start_date: date, end_date: date) -> dict:
        """
        检查并加载缓存
        
        Args:
            entry: 缓存条目
            cache_key: 缓存键
            start_date: 查询开始日期
            end_date: 查询结束日期
            
        Returns:
            查询结果字典
        """
        # 检查是否过期
        if self.policy.is_expired(entry):
            self.logger.info(f"缓存已过期: {cache_key}")
            return {'status': 'no_match', 'data': None, 'caches': []}
        
        # 检查文件是否存在
        file_path = Path(entry['file_path'])
        if not file_path.exists():
            self.logger.warning(f"缓存文件不存在: {file_path}")
            self.index.remove_entry(cache_key)
            return {'status': 'no_match', 'data': None, 'caches': []}
        
        # 读取数据
        data = self.storage.load(file_path)
        if data is None:
            self.logger.error(f"读取缓存文件失败: {file_path}")
            return {'status': 'no_match', 'data': None, 'caches': []}
        
        # 检查日期范围是否完全包含查询范围
        cache_start = datetime.strptime(entry['start_date'], '%Y-%m-%d').date()
        cache_end = datetime.strptime(entry['end_date'], '%Y-%m-%d').date()
        
        if cache_start <= start_date and cache_end >= end_date:
            # ✅ 缓存范围完全覆盖查询范围，过滤数据
            filtered_data = data[(data.index.date >= start_date) & (data.index.date <= end_date)]
            
            if filtered_data.empty:
                self.logger.warning(f"过滤后数据为空: {cache_key}")
                return {'status': 'no_match', 'data': None, 'caches': []}
            
            # 更新访问记录
            self.index.update_access(cache_key)
            
            self.logger.info(f"✅ 从缓存过滤数据: {len(filtered_data)} 条记录 (原缓存: {len(data)} 条)")
            
            return {
                'status': 'full_match',
                'data': filtered_data,
                'caches': [entry],
                'from_larger_cache': cache_key != f"{entry['data_source']}_{entry['market']}_{entry['code']}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{entry['interval']}"
            }
        
        # 日期范围不匹配
        return {'status': 'no_match', 'data': None, 'caches': []}
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        try:
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            return f"md5:{md5_hash.hexdigest()}"
        except Exception as e:
            self.logger.warning(f"计算校验和失败: {e}")
            return "md5:unknown"
    
    def _check_and_cleanup(self):
        """检查缓存大小并清理"""
        stats = self.index.get_statistics()
        max_size_mb = self.config.get("cache_settings", {}).get("max_size_mb", 1024)
        
        if stats['total_size_mb'] > max_size_mb:
            self.logger.warning(f"缓存超过限制 ({stats['total_size_mb']:.2f} MB > {max_size_mb} MB)，开始清理")
            self.cleanup_cache()
    
    def cleanup_cache(self, force: bool = False):
        """
        清理缓存
        
        Args:
            force: 是否强制清理（忽略访问记录）
        """
        self.logger.info("开始清理缓存...")
        
        entries = self.index.get_all_entries()
        to_delete = []
        
        # 清理过期缓存
        for key, entry in entries.items():
            if self.policy.is_expired(entry):
                to_delete.append(key)
        
        # 如果还需要清理更多（超过容量限制）
        stats = self.index.get_statistics()
        max_size_mb = self.config.get("cache_settings", {}).get("max_size_mb", 1024)
        
        if stats['total_size_mb'] > max_size_mb or force:
            # LRU策略：删除最久未访问的
            sorted_entries = sorted(
                entries.items(),
                key=lambda x: x[1].get('last_accessed', ''),
                reverse=False  # 最旧的在前
            )
            
            for key, entry in sorted_entries:
                if key not in to_delete:
                    to_delete.append(key)
                    if self.index.get_statistics()['total_size_mb'] <= max_size_mb * 0.8:
                        break
        
        # 执行删除
        deleted_count = 0
        for key in to_delete:
            if self.delete_cache(key):
                deleted_count += 1
        
        self.logger.info(f"清理完成，删除了 {deleted_count} 个缓存")
    
    def delete_cache(self, cache_key: str) -> bool:
        """删除指定缓存"""
        try:
            entry = self.index.get_entry(cache_key)
            if entry:
                file_path = Path(entry['file_path'])
                if file_path.exists():
                    file_path.unlink()
                    self.logger.info(f"删除缓存文件: {file_path}")
            
            self.index.remove_entry(cache_key)
            return True
        except Exception as e:
            self.logger.error(f"删除缓存失败: {e}")
            return False
    
    def clear_all_cache(self):
        """清空所有缓存"""
        self.logger.warning("清空所有缓存...")
        entries = self.index.get_all_entries()
        for key in list(entries.keys()):
            self.delete_cache(key)
        self.logger.info("所有缓存已清空")
    
    def get_statistics(self) -> dict:
        """获取缓存统计信息"""
        return self.index.get_statistics()


class CacheIndex:
    """缓存索引管理器"""
    
    def __init__(self, index_file: Path):
        """
        初始化索引管理器
        
        Args:
            index_file: 索引文件路径
        """
        self.index_file = index_file
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_index()
    
    def _load_index(self) -> dict:
        """加载索引文件"""
        if not self.index_file.exists():
            return {
                "version": "1.0",
                "last_update": "",
                "entries": {},
                "statistics": {
                    "total_entries": 0,
                    "total_size_mb": 0,
                    "oldest_entry": "",
                    "newest_entry": ""
                }
            }
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载索引文件失败: {e}")
            return self._load_index()  # 返回默认值
    
    def _save_index(self):
        """保存索引文件"""
        try:
            self.data['last_update'] = datetime.now().isoformat()
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存索引文件失败: {e}")
    
    def has_entry(self, key: str) -> bool:
        """检查是否存在指定缓存"""
        return key in self.data['entries']
    
    def get_entry(self, key: str) -> Optional[dict]:
        """获取缓存条目"""
        return self.data['entries'].get(key)
    
    def add_entry(self, key: str, metadata: dict):
        """添加缓存条目"""
        self.data['entries'][key] = metadata
        self._update_statistics()
        self._save_index()
    
    def remove_entry(self, key: str):
        """删除缓存条目"""
        if key in self.data['entries']:
            del self.data['entries'][key]
            self._update_statistics()
            self._save_index()
    
    def update_access(self, key: str):
        """更新访问记录"""
        if key in self.data['entries']:
            self.data['entries'][key]['last_accessed'] = datetime.now().isoformat()
            self.data['entries'][key]['access_count'] = self.data['entries'][key].get('access_count', 0) + 1
            self._save_index()
    
    def get_all_entries(self) -> dict:
        """获取所有缓存条目"""
        return self.data['entries']
    
    def _update_statistics(self):
        """更新统计信息"""
        entries = self.data['entries']
        
        if not entries:
            self.data['statistics'] = {
                "total_entries": 0,
                "total_size_mb": 0,
                "oldest_entry": "",
                "newest_entry": ""
            }
            return
        
        total_size_kb = sum(entry.get('file_size_kb', 0) for entry in entries.values())
        created_times = [entry.get('created_at', '') for entry in entries.values() if entry.get('created_at')]
        
        self.data['statistics'] = {
            "total_entries": len(entries),
            "total_size_mb": round(total_size_kb / 1024, 2),
            "oldest_entry": min(created_times) if created_times else "",
            "newest_entry": max(created_times) if created_times else ""
        }
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        return self.data['statistics']


class CacheStorage:
    """缓存存储层 - 负责文件读写"""
    
    def __init__(self, data_dir: Path, config: dict):
        """
        初始化存储层
        
        Args:
            data_dir: 数据目录
            config: 配置字典
        """
        self.data_dir = data_dir
        self.config = config
        self.format = config.get('storage_format', {}).get('format', 'parquet')
        self.compression = config.get('storage_format', {}).get('compression', 'snappy')
    
    def save(self, data: pd.DataFrame, data_source: str, market: str, code: str,
             start_date: date, end_date: date, interval: str) -> Optional[Path]:
        """
        保存数据到文件
        
        Returns:
            文件路径或None
        """
        try:
            # 构建文件路径
            subdir = self.data_dir / data_source / market
            subdir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            if interval == '1d':
                filename = f"{code}_{start_str}_{end_str}.{self.format}"
            else:
                filename = f"{code}_{start_str}_{end_str}_{interval}.{self.format}"
            
            file_path = subdir / filename
            
            # 保存文件
            if self.format == 'parquet':
                data.to_parquet(file_path, compression=self.compression)
            elif self.format == 'csv':
                data.to_csv(file_path)
            else:
                raise ValueError(f"不支持的存储格式: {self.format}")
            
            return file_path
            
        except Exception as e:
            print(f"保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        从文件加载数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            DataFrame或None
        """
        try:
            if not file_path.exists():
                return None
            
            if file_path.suffix == '.parquet':
                return pd.read_parquet(file_path)
            elif file_path.suffix == '.csv':
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                return df
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")
                
        except Exception as e:
            print(f"加载文件失败: {e}")
            return None


class CachePolicy:
    """缓存策略管理器 - 负责TTL和清理策略"""
    
    def __init__(self, config: dict):
        """
        初始化策略管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
    
    def is_expired(self, entry: dict) -> bool:
        """
        判断缓存是否过期
        
        Args:
            entry: 缓存条目
            
        Returns:
            是否过期
        """
        try:
            # 获取缓存结束日期
            end_date_str = entry.get('end_date', '')
            if not end_date_str:
                return True
            
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            today = date.today()
            days_diff = (today - end_date).days
            
            # TTL规则
            ttl_rules = self.config.get('ttl_rules', {})
            
            # 历史数据（结束日期 > 7天前）：永不过期
            recent_days = ttl_rules.get('recent_data_days', 7)
            if days_diff > recent_days:
                return False  # 永不过期
            
            # 近期数据（结束日期在1-7天前）：7天过期
            if 1 <= days_diff <= recent_days:
                created_at_str = entry.get('created_at', '')
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                    ttl_hours = ttl_rules.get('recent_data_ttl_hours', 168)
                    expire_time = created_at + timedelta(hours=ttl_hours)
                    return datetime.now() > expire_time
                return False
            
            # 最新数据（结束日期是今天）：1小时过期
            if days_diff == 0:
                created_at_str = entry.get('created_at', '')
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                    
                    # 加密货币：30分钟
                    market = entry.get('market', '')
                    if market == 'crypto':
                        ttl_minutes = ttl_rules.get('crypto_ttl_minutes', 30)
                        expire_time = created_at + timedelta(minutes=ttl_minutes)
                    else:
                        ttl_minutes = ttl_rules.get('realtime_data_ttl_minutes', 60)
                        expire_time = created_at + timedelta(minutes=ttl_minutes)
                    
                    return datetime.now() > expire_time
                return False
            
            return False
            
        except Exception as e:
            print(f"判断缓存过期失败: {e}")
            return True  # 出错时认为过期
