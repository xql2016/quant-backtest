"""
工具1：两缓存连续合并工具
判断两个缓存是否完全连续，如果是则合并并删除原缓存
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, date
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))


class CacheMergeTool:
    """缓存合并工具"""
    
    def __init__(self, cache_root: str = "cache"):
        """
        初始化合并工具
        
        Args:
            cache_root: 缓存根目录
        """
        self.cache_root = Path(cache_root)
        self.data_dir = self.cache_root / "data"
        self.metadata_file = self.cache_root / "metadata" / "cache_index.json"
    
    def merge_continuous_caches(self, file1: str, file2: str, dry_run: bool = False) -> dict:
        """
        合并两个连续的缓存
        
        Args:
            file1: 第一个缓存文件路径（相对于cache/data/）
            file2: 第二个缓存文件路径（相对于cache/data/）
            dry_run: 是否只检查不执行（预览模式）
            
        Returns:
            结果字典，包含status和message
        """
        print("=" * 80)
        print("🔄 两缓存连续合并工具")
        print("=" * 80)
        
        # 1. 解析文件信息
        info1 = self._parse_cache_file(file1)
        info2 = self._parse_cache_file(file2)
        
        if not info1 or not info2:
            return {
                'status': 'error',
                'message': '文件信息解析失败'
            }
        
        print(f"\n缓存A: {info1['code']} ({info1['start_date']} ~ {info1['end_date']})")
        print(f"缓存B: {info2['code']} ({info2['start_date']} ~ {info2['end_date']})")
        
        # 2. 验证基本信息一致
        if not self._validate_same_asset(info1, info2):
            return {
                'status': 'error',
                'message': '两个缓存不是同一个资产（数据源、市场、代码或时间粒度不同）'
            }
        
        print("✅ 基本信息验证通过（同一资产）")
        
        # 3. 检查连续性
        continuity_result = self._check_continuity(info1, info2)
        
        if not continuity_result['is_continuous']:
            return {
                'status': 'error',
                'message': continuity_result['message']
            }
        
        print(f"✅ 连续性检查通过: {continuity_result['message']}")
        
        # 4. 确定合并顺序和处理重叠
        merge_plan = self._plan_merge(info1, info2, continuity_result)
        
        print(f"\n📋 合并计划:")
        print(f"   时间顺序: 缓存{merge_plan['first']} → 缓存{merge_plan['second']}")
        print(f"   合并范围: {merge_plan['start_date']} ~ {merge_plan['end_date']}")
        print(f"   重叠处理: {merge_plan['overlap_strategy']}")
        
        if dry_run:
            print("\n🔍 预览模式：不执行实际合并")
            return {
                'status': 'preview',
                'message': '预览成功，使用 dry_run=False 执行实际合并',
                'plan': merge_plan
            }
        
        # 5. 执行合并
        print(f"\n🔧 开始合并...")
        merge_result = self._execute_merge(info1, info2, merge_plan)
        
        if not merge_result['success']:
            return {
                'status': 'error',
                'message': f"合并失败: {merge_result['message']}"
            }
        
        print(f"✅ 数据合并成功: {merge_result['rows']} 条记录")
        print(f"   保存路径: {merge_result['file_path']}")
        
        # 6. 更新索引
        self._update_index_after_merge(merge_result, merge_plan)
        print(f"✅ 索引更新成功")
        
        # 7. 删除原缓存
        self._delete_original_caches(file1, file2)
        print(f"✅ 原缓存已删除")
        
        print("\n" + "=" * 80)
        print("🎉 合并完成！")
        print("=" * 80)
        
        return {
            'status': 'success',
            'message': '合并成功',
            'merged_file': merge_result['file_path'],
            'merged_rows': merge_result['rows']
        }
    
    def _parse_cache_file(self, file_path: str) -> dict:
        """
        从文件名解析缓存信息
        
        文件名格式: {code}_{start_date}_{end_date}_{interval}.parquet
        或: {code}_{start_date}_{end_date}.parquet
        """
        try:
            file_path = Path(file_path)
            full_path = self.data_dir / file_path
            
            if not full_path.exists():
                print(f"❌ 文件不存在: {full_path}")
                return None
            
            # 解析路径
            parts = file_path.parts
            if len(parts) < 3:
                print(f"❌ 文件路径格式错误: {file_path}")
                return None
            
            data_source = parts[0]  # akshare/yfinance/tushare
            market = parts[1]       # a_stock/hk_stock/etc
            filename = parts[-1]    # 文件名
            
            # 解析文件名
            name_parts = Path(filename).stem.split('_')
            if len(name_parts) < 3:
                print(f"❌ 文件名格式错误: {filename}")
                return None
            
            code = name_parts[0]
            start_date_str = name_parts[1]
            end_date_str = name_parts[2]
            interval = name_parts[3] if len(name_parts) > 3 else '1d'
            
            # 转换日期
            start_date = datetime.strptime(start_date_str, '%Y%m%d').date()
            end_date = datetime.strptime(end_date_str, '%Y%m%d').date()
            
            return {
                'file_path': str(file_path),
                'full_path': full_path,
                'data_source': data_source,
                'market': market,
                'code': code,
                'start_date': start_date,
                'end_date': end_date,
                'interval': interval,
                'filename': filename
            }
            
        except Exception as e:
            print(f"❌ 解析文件失败: {e}")
            return None
    
    def _validate_same_asset(self, info1: dict, info2: dict) -> bool:
        """验证是否是同一资产"""
        return (info1['data_source'] == info2['data_source'] and
                info1['market'] == info2['market'] and
                info1['code'] == info2['code'] and
                info1['interval'] == info2['interval'])
    
    def _check_continuity(self, info1: dict, info2: dict) -> dict:
        """
        检查两个缓存是否连续
        
        Returns:
            {
                'is_continuous': bool,
                'type': 'continuous' | 'overlap' | 'gap',
                'message': str
            }
        """
        # 确定时间顺序
        if info1['start_date'] <= info2['start_date']:
            first, second = info1, info2
        else:
            first, second = info2, info1
        
        # 计算时间差
        gap = (second['start_date'] - first['end_date']).days
        
        if gap == 1:
            # 完全连续（中间无缺口，无重叠）
            return {
                'is_continuous': True,
                'type': 'continuous',
                'message': f"完全连续（缓存A到{first['end_date']}，缓存B从{second['start_date']}）",
                'gap_days': 0
            }
        elif gap == 0:
            # 边界重叠1天
            return {
                'is_continuous': True,
                'type': 'overlap',
                'message': f"边界日期重叠: {second['start_date']}",
                'overlap_start': second['start_date'],
                'overlap_end': min(first['end_date'], second['end_date'])
            }
        elif gap < 0:
            # 多天重叠
            overlap_days = abs(gap) + 1
            return {
                'is_continuous': True,
                'type': 'overlap',
                'message': f"日期重叠 {overlap_days} 天 ({second['start_date']} ~ {first['end_date']})",
                'overlap_start': second['start_date'],
                'overlap_end': first['end_date']
            }
        else:
            # 存在缺口
            return {
                'is_continuous': False,
                'type': 'gap',
                'message': f"存在 {gap} 天缺口 ({first['end_date']} 到 {second['start_date']})",
                'gap_days': gap
            }
    
    def _plan_merge(self, info1: dict, info2: dict, continuity: dict) -> dict:
        """制定合并计划"""
        # 确定顺序
        if info1['start_date'] <= info2['start_date']:
            first, second = info1, info2
            first_label, second_label = 'A', 'B'
        else:
            first, second = info2, info1
            first_label, second_label = 'B', 'A'
        
        # 合并后的日期范围
        start_date = first['start_date']
        end_date = second['end_date']
        
        # 重叠处理策略
        if continuity['type'] == 'overlap':
            overlap_strategy = "使用缓存B的数据（更新）"
        else:
            overlap_strategy = "无重叠"
        
        return {
            'first': first_label,
            'second': second_label,
            'first_info': first,
            'second_info': second,
            'start_date': start_date,
            'end_date': end_date,
            'overlap_strategy': overlap_strategy,
            'continuity_type': continuity['type']
        }
    
    def _execute_merge(self, info1: dict, info2: dict, plan: dict) -> dict:
        """执行合并操作"""
        try:
            first_info = plan['first_info']
            second_info = plan['second_info']
            
            # 读取数据
            df1 = pd.read_parquet(first_info['full_path'])
            df2 = pd.read_parquet(second_info['full_path'])
            
            print(f"   读取缓存A: {len(df1)} 条记录")
            print(f"   读取缓存B: {len(df2)} 条记录")
            
            # 处理重叠
            if plan['continuity_type'] == 'overlap':
                # 从df1中删除重叠部分，使用df2的数据
                overlap_start = second_info['start_date']
                df1_filtered = df1[df1.index.date < overlap_start]
                print(f"   处理重叠: 保留缓存A {len(df1) - len(df1_filtered)} 条，使用缓存B的数据")
            else:
                df1_filtered = df1
            
            # 合并
            merged_df = pd.concat([df1_filtered, df2])
            merged_df = merged_df.sort_index()
            
            # 去重（以防万一）
            if merged_df.index.duplicated().any():
                print(f"   ⚠️ 发现重复日期，去重处理")
                merged_df = merged_df[~merged_df.index.duplicated(keep='last')]
            
            # 生成合并后的文件路径
            merged_file_path = self._generate_merged_file_path(
                first_info, plan['start_date'], plan['end_date']
            )
            
            # 保存合并后的数据
            merged_df.to_parquet(merged_file_path, compression='snappy')
            
            return {
                'success': True,
                'file_path': str(merged_file_path),
                'rows': len(merged_df),
                'start_date': merged_df.index[0].date(),
                'end_date': merged_df.index[-1].date(),
                'message': '合并成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'合并失败: {e}'
            }
    
    def _generate_merged_file_path(self, info: dict, start_date: date, end_date: date) -> Path:
        """生成合并后的文件路径"""
        subdir = self.data_dir / info['data_source'] / info['market']
        
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        if info['interval'] == '1d':
            filename = f"{info['code']}_{start_str}_{end_str}.parquet"
        else:
            filename = f"{info['code']}_{start_str}_{end_str}_{info['interval']}.parquet"
        
        return subdir / filename
    
    def _update_index_after_merge(self, merge_result: dict, plan: dict):
        """更新索引文件"""
        try:
            # 读取索引
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # 生成新的缓存键
            first_info = plan['first_info']
            start_str = plan['start_date'].strftime('%Y%m%d')
            end_str = plan['end_date'].strftime('%Y%m%d')
            
            new_key = f"{first_info['data_source']}_{first_info['market']}_{first_info['code']}_{start_str}_{end_str}_{first_info['interval']}"
            
            # 创建新的元数据
            file_path = Path(merge_result['file_path'])
            metadata = {
                'file_path': merge_result['file_path'],
                'data_source': first_info['data_source'],
                'market': first_info['market'],
                'code': first_info['code'],
                'start_date': str(plan['start_date']),
                'end_date': str(plan['end_date']),
                'interval': first_info['interval'],
                'rows': merge_result['rows'],
                'columns': ['open', 'high', 'low', 'close', 'volume'],
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'file_size_kb': round(file_path.stat().st_size / 1024, 2),
                'checksum': f"md5:merged",
                'is_complete': True,
                'merged_from': [first_info['filename'], plan['second_info']['filename']]
            }
            
            # 添加新条目
            index_data['entries'][new_key] = metadata
            
            # 删除旧条目
            old_keys = [k for k, v in index_data['entries'].items() 
                       if v.get('file_path') in [first_info['file_path'], plan['second_info']['file_path']]]
            for old_key in old_keys:
                del index_data['entries'][old_key]
            
            # 重新计算统计信息
            if index_data['entries']:
                total_size = sum(e.get('file_size_kb', 0) for e in index_data['entries'].values()) / 1024
                created_times = [e['created_at'] for e in index_data['entries'].values() if 'created_at' in e]
                
                index_data['statistics'] = {
                    'total_entries': len(index_data['entries']),
                    'total_size_mb': round(total_size, 2),
                    'oldest_entry': min(created_times) if created_times else None,
                    'newest_entry': max(created_times) if created_times else None
                }
            else:
                index_data['statistics'] = {
                    'total_entries': 0,
                    'total_size_mb': 0.0,
                    'oldest_entry': None,
                    'newest_entry': None
                }
            
            # 更新时间戳
            index_data['last_update'] = datetime.now().isoformat()
            
            # 保存
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"⚠️ 更新索引失败: {e}")
    
    def _delete_original_caches(self, file1: str, file2: str):
        """删除原始缓存文件"""
        try:
            path1 = self.data_dir / file1
            path2 = self.data_dir / file2
            
            if path1.exists():
                path1.unlink()
                print(f"   删除: {file1}")
            
            if path2.exists():
                path2.unlink()
                print(f"   删除: {file2}")
                
        except Exception as e:
            print(f"⚠️ 删除原文件失败: {e}")


def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python merge_continuous_caches.py <文件1> <文件2> [--dry-run]")
        print()
        print("示例:")
        print("  python tools/merge_continuous_caches.py \\")
        print("    tushare/a_stock/000001_20250101_20250708.parquet \\")
        print("    tushare/a_stock/000001_20250602_20260101.parquet")
        print()
        print("预览模式（不实际执行）:")
        print("  python tools/merge_continuous_caches.py <文件1> <文件2> --dry-run")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    dry_run = '--dry-run' in sys.argv
    
    tool = CacheMergeTool()
    result = tool.merge_continuous_caches(file1, file2, dry_run=dry_run)
    
    print(f"\n结果: {result['status']}")
    print(f"信息: {result['message']}")


if __name__ == '__main__':
    main()
