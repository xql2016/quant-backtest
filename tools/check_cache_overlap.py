"""
工具2：缓存覆盖判断和清理工具
判断一个缓存是否完全覆盖另一个，如果是则删除被覆盖的缓存
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, date
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))


class CacheOverlapTool:
    """缓存覆盖判断工具"""
    
    def __init__(self, cache_root: str = "cache"):
        """
        初始化覆盖工具
        
        Args:
            cache_root: 缓存根目录
        """
        self.cache_root = Path(cache_root)
        self.data_dir = self.cache_root / "data"
        self.metadata_file = self.cache_root / "metadata" / "cache_index.json"
    
    def check_and_remove_covered(self, file1: str, file2: str, dry_run: bool = False) -> dict:
        """
        检查并删除被覆盖的缓存
        
        Args:
            file1: 第一个缓存文件路径
            file2: 第二个缓存文件路径
            dry_run: 是否只检查不执行
            
        Returns:
            结果字典
        """
        print("=" * 80)
        print("🔍 缓存覆盖判断工具")
        print("=" * 80)
        
        # 1. 解析文件信息
        info1 = self._parse_cache_file(file1)
        info2 = self._parse_cache_file(file2)
        
        if not info1 or not info2:
            return {
                'status': 'error',
                'message': '文件信息解析失败'
            }
        
        print(f"\n缓存A: {info1['code']} ({info1['start_date']} ~ {info1['end_date']}) - {info1['file_size_mb']:.2f} MB")
        print(f"缓存B: {info2['code']} ({info2['start_date']} ~ {info2['end_date']}) - {info2['file_size_mb']:.2f} MB")
        
        # 2. 验证基本信息一致
        if not self._validate_same_asset(info1, info2):
            return {
                'status': 'error',
                'message': '两个缓存不是同一个资产'
            }
        
        print("✅ 基本信息验证通过（同一资产）")
        
        # 3. 检查覆盖关系
        coverage = self._check_coverage(info1, info2)
        
        print(f"\n📊 覆盖关系分析:")
        print(f"   关系类型: {coverage['type']}")
        print(f"   说明: {coverage['message']}")
        
        if coverage['type'] == 'no_coverage':
            return {
                'status': 'no_action',
                'message': '两个缓存无覆盖关系，无需删除'
            }
        
        # 4. 确定要删除的文件
        to_delete = coverage['covered_cache']
        to_keep = coverage['covering_cache']
        
        print(f"\n🗑️  删除决策:")
        print(f"   保留: {to_keep['filename']} ({to_keep['start_date']} ~ {to_keep['end_date']})")
        print(f"   删除: {to_delete['filename']} ({to_delete['start_date']} ~ {to_delete['end_date']})")
        print(f"   原因: 被完全覆盖")
        
        if dry_run:
            print("\n🔍 预览模式：不执行实际删除")
            return {
                'status': 'preview',
                'message': '预览成功，使用 dry_run=False 执行实际删除',
                'to_delete': to_delete['file_path'],
                'to_keep': to_keep['file_path']
            }
        
        # 5. 执行删除
        print(f"\n🔧 执行删除...")
        delete_result = self._delete_cache(to_delete)
        
        if delete_result['success']:
            print(f"✅ 删除成功")
            print(f"   释放空间: {to_delete['file_size_mb']:.2f} MB")
            
            return {
                'status': 'success',
                'message': '删除成功',
                'deleted_file': to_delete['file_path'],
                'freed_space_mb': to_delete['file_size_mb']
            }
        else:
            return {
                'status': 'error',
                'message': f"删除失败: {delete_result['message']}"
            }
    
    def _parse_cache_file(self, file_path: str) -> dict:
        """从文件名解析缓存信息"""
        try:
            file_path = Path(file_path)
            full_path = self.data_dir / file_path
            
            if not full_path.exists():
                print(f"❌ 文件不存在: {full_path}")
                return None
            
            # 解析路径
            parts = file_path.parts
            data_source = parts[0]
            market = parts[1]
            filename = parts[-1]
            
            # 解析文件名
            name_parts = Path(filename).stem.split('_')
            code = name_parts[0]
            start_date_str = name_parts[1]
            end_date_str = name_parts[2]
            interval = name_parts[3] if len(name_parts) > 3 else '1d'
            
            # 转换日期
            start_date = datetime.strptime(start_date_str, '%Y%m%d').date()
            end_date = datetime.strptime(end_date_str, '%Y%m%d').date()
            
            # 文件大小
            file_size_mb = full_path.stat().st_size / (1024 * 1024)
            
            return {
                'file_path': str(file_path),
                'full_path': full_path,
                'data_source': data_source,
                'market': market,
                'code': code,
                'start_date': start_date,
                'end_date': end_date,
                'interval': interval,
                'filename': filename,
                'file_size_mb': file_size_mb
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
    
    def _check_coverage(self, info1: dict, info2: dict) -> dict:
        """
        检查覆盖关系
        
        Returns:
            {
                'type': 'full_coverage' | 'partial_coverage' | 'no_coverage',
                'message': str,
                'covering_cache': 覆盖者的info,
                'covered_cache': 被覆盖者的info
            }
        """
        # 检查 info1 是否完全覆盖 info2
        if info1['start_date'] <= info2['start_date'] and info1['end_date'] >= info2['end_date']:
            return {
                'type': 'full_coverage',
                'message': f"缓存A完全覆盖缓存B",
                'covering_cache': info1,
                'covered_cache': info2
            }
        
        # 检查 info2 是否完全覆盖 info1
        if info2['start_date'] <= info1['start_date'] and info2['end_date'] >= info1['end_date']:
            return {
                'type': 'full_coverage',
                'message': f"缓存B完全覆盖缓存A",
                'covering_cache': info2,
                'covered_cache': info1
            }
        
        # 检查是否有部分覆盖
        if (info1['start_date'] <= info2['end_date'] and info1['end_date'] >= info2['start_date']):
            return {
                'type': 'partial_coverage',
                'message': f"两个缓存部分重叠，但无完全覆盖关系"
            }
        
        # 无覆盖
        return {
            'type': 'no_coverage',
            'message': '两个缓存无覆盖关系'
        }
    
    def _delete_cache(self, cache_info: dict) -> dict:
        """删除缓存文件和索引"""
        try:
            # 删除文件
            file_path = Path(cache_info['full_path'])
            if file_path.exists():
                file_path.unlink()
            
            # 更新索引
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # 查找并删除对应的索引条目
            to_remove = []
            for key, entry in index_data['entries'].items():
                if entry.get('file_path') == cache_info['file_path']:
                    to_remove.append(key)
            
            for key in to_remove:
                del index_data['entries'][key]
            
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
            
            index_data['last_update'] = datetime.now().isoformat()
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'message': '删除成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }


def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python check_cache_overlap.py <文件1> <文件2> [--dry-run]")
        print()
        print("示例:")
        print("  python tools/check_cache_overlap.py \\")
        print("    tushare/a_stock/000001_20240101_20260101.parquet \\")
        print("    tushare/a_stock/000001_20250101_20260101.parquet")
        print()
        print("预览模式（不实际执行）:")
        print("  python tools/check_cache_overlap.py <文件1> <文件2> --dry-run")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    dry_run = '--dry-run' in sys.argv
    
    tool = CacheOverlapTool()
    result = tool.check_and_remove_covered(file1, file2, dry_run=dry_run)
    
    print(f"\n结果: {result['status']}")
    print(f"信息: {result['message']}")


if __name__ == '__main__':
    main()
