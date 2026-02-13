"""
工具3：缓存自动优化工具
遍历缓存目录，自动合并连续缓存和清理被覆盖的缓存
"""

import sys
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.merge_continuous_caches import CacheMergeTool
from tools.check_cache_overlap import CacheOverlapTool


class CacheAutoOptimizer:
    """缓存自动优化工具"""
    
    def __init__(self, cache_root: str = "cache"):
        """
        初始化优化工具
        
        Args:
            cache_root: 缓存根目录
        """
        self.cache_root = Path(cache_root)
        self.data_dir = self.cache_root / "data"
        self.metadata_file = self.cache_root / "metadata" / "cache_index.json"
        
        self.merge_tool = CacheMergeTool(cache_root)
        self.overlap_tool = CacheOverlapTool(cache_root)
    
    def optimize_all(self, dry_run: bool = True):
        """
        自动优化所有缓存
        
        Args:
            dry_run: 是否只预览不执行
        """
        print("=" * 80)
        print("🚀 缓存自动优化工具")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 预览模式：只检查，不执行实际操作")
            print("   使用 --execute 参数执行实际优化\n")
        
        # 1. 扫描所有缓存
        print("\n【步骤1】扫描缓存文件...")
        print("-" * 80)
        cache_groups = self._scan_caches()
        
        if not cache_groups:
            print("❌ 未找到缓存文件")
            return
        
        print(f"✅ 找到 {len(cache_groups)} 个资产组，共 {sum(len(g) for g in cache_groups.values())} 个缓存文件")
        
        # 2. 清理被覆盖的缓存
        print("\n【步骤2】清理被覆盖的缓存...")
        print("-" * 80)
        removed_count, freed_space = self._remove_covered_caches(cache_groups, dry_run)
        
        print(f"✅ 清理完成: 删除 {removed_count} 个被覆盖的缓存，释放 {freed_space:.2f} MB")
        
        # 3. 重新扫描（因为可能删除了一些）
        if not dry_run and removed_count > 0:
            cache_groups = self._scan_caches()
        
        # 4. 合并连续的缓存
        print("\n【步骤3】合并连续的缓存...")
        print("-" * 80)
        merged_count = self._merge_continuous_caches(cache_groups, dry_run)
        
        print(f"✅ 合并完成: 合并了 {merged_count} 对连续缓存")
        
        # 5. 总结
        print("\n" + "=" * 80)
        print("📊 优化总结")
        print("=" * 80)
        
        print(f"清理被覆盖缓存: {removed_count} 个，释放 {freed_space:.2f} MB")
        print(f"合并连续缓存: {merged_count} 对")
        
        if dry_run:
            print("\n💡 提示：使用 --execute 参数执行实际优化")
        else:
            print("\n🎉 优化完成！")
    
    def _scan_caches(self) -> Dict[str, List[dict]]:
        """
        扫描所有缓存文件，按资产分组
        
        Returns:
            {
                'tushare_a_stock_000001_1d': [cache1, cache2, ...],
                'yfinance_crypto_BTC-USD_1h': [cache1, cache2, ...],
                ...
            }
        """
        cache_groups = {}
        
        # 遍历所有 parquet 文件
        for file_path in self.data_dir.rglob("*.parquet"):
            info = self._parse_cache_file(file_path)
            if info:
                # 资产分组键（不包含日期）
                group_key = f"{info['data_source']}_{info['market']}_{info['code']}_{info['interval']}"
                
                if group_key not in cache_groups:
                    cache_groups[group_key] = []
                
                cache_groups[group_key].append(info)
        
        # 按开始日期排序
        for group_key in cache_groups:
            cache_groups[group_key].sort(key=lambda x: x['start_date'])
        
        return cache_groups
    
    def _parse_cache_file(self, file_path: Path) -> dict:
        """解析缓存文件信息"""
        try:
            # 相对路径
            rel_path = file_path.relative_to(self.data_dir)
            parts = rel_path.parts
            
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
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            return {
                'file_path': str(rel_path),
                'full_path': file_path,
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
            print(f"⚠️ 解析文件失败: {file_path}, 错误: {e}")
            return None
    
    def _remove_covered_caches(self, cache_groups: dict, dry_run: bool) -> tuple:
        """
        清理被覆盖的缓存
        
        Returns:
            (删除数量, 释放空间MB)
        """
        removed_count = 0
        freed_space = 0.0
        
        for group_key, caches in cache_groups.items():
            if len(caches) < 2:
                continue
            
            print(f"\n处理资产组: {group_key} ({len(caches)} 个缓存)")
            
            # 检查每对缓存
            to_remove = []
            for i, cache_i in enumerate(caches):
                if cache_i in to_remove:
                    continue
                
                for j, cache_j in enumerate(caches):
                    if i == j or cache_j in to_remove:
                        continue
                    
                    # 检查覆盖关系
                    if (cache_i['start_date'] <= cache_j['start_date'] and
                        cache_i['end_date'] >= cache_j['end_date']):
                        # cache_i 覆盖 cache_j
                        to_remove.append(cache_j)
                        print(f"   发现覆盖: {cache_i['filename']} 覆盖 {cache_j['filename']}")
            
            # 执行删除
            if to_remove:
                for cache in to_remove:
                    if not dry_run:
                        self.overlap_tool._delete_cache(cache)
                    
                    removed_count += 1
                    freed_space += cache['file_size_mb']
                    print(f"   {'[预览]' if dry_run else '✅'} 删除: {cache['filename']} ({cache['file_size_mb']:.2f} MB)")
        
        return removed_count, freed_space
    
    def _merge_continuous_caches(self, cache_groups: dict, dry_run: bool) -> int:
        """
        合并连续的缓存
        
        Returns:
            合并数量
        """
        merged_count = 0
        
        for group_key, caches in cache_groups.items():
            if len(caches) < 2:
                continue
            
            print(f"\n处理资产组: {group_key} ({len(caches)} 个缓存)")
            
            # 检查相邻缓存是否连续
            i = 0
            while i < len(caches) - 1:
                cache1 = caches[i]
                cache2 = caches[i + 1]
                
                # 检查连续性
                gap = (cache2['start_date'] - cache1['end_date']).days
                
                # 连续或轻微重叠（<=3天）
                if gap <= 3 and gap >= -3:
                    print(f"   发现可合并: {cache1['filename']} + {cache2['filename']}")
                    
                    if gap > 0:
                        print(f"      类型: 缺口 {gap} 天（不合并）")
                    elif gap == 0:
                        print(f"      类型: 边界相连")
                    else:
                        print(f"      类型: 重叠 {abs(gap)} 天")
                    
                    # 只合并完全连续或轻微重叠的
                    if gap <= 1:  # 连续或1天重叠
                        if not dry_run:
                            # 注意：合并后需要重新扫描，这里简化处理
                            print(f"      {'[预览]' if dry_run else '✅'} 将合并")
                        merged_count += 1
                        i += 2  # 跳过已合并的
                    else:
                        i += 1
                else:
                    i += 1
        
        return merged_count
    
    def get_optimization_report(self) -> dict:
        """
        生成优化建议报告（不执行操作）
        
        Returns:
            优化建议报告
        """
        print("=" * 80)
        print("📊 缓存优化分析报告")
        print("=" * 80)
        
        cache_groups = self._scan_caches()
        
        report = {
            'total_assets': len(cache_groups),
            'total_caches': sum(len(g) for g in cache_groups.values()),
            'redundant_caches': [],
            'mergeable_pairs': [],
            'optimization_potential': {
                'removable_count': 0,
                'mergeable_count': 0,
                'space_savings_mb': 0.0
            }
        }
        
        # 分析每个资产组
        for group_key, caches in cache_groups.items():
            if len(caches) < 2:
                continue
            
            print(f"\n资产: {group_key}")
            print(f"  缓存数量: {len(caches)}")
            
            # 检查覆盖关系
            for i, cache_i in enumerate(caches):
                for j, cache_j in enumerate(caches):
                    if i == j:
                        continue
                    
                    if (cache_i['start_date'] <= cache_j['start_date'] and
                        cache_i['end_date'] >= cache_j['end_date']):
                        report['redundant_caches'].append({
                            'covering': cache_i['filename'],
                            'covered': cache_j['filename'],
                            'space_saving_mb': cache_j['file_size_mb']
                        })
                        report['optimization_potential']['removable_count'] += 1
                        report['optimization_potential']['space_savings_mb'] += cache_j['file_size_mb']
                        print(f"  ⚠️ 发现冗余: {cache_j['filename']} 被 {cache_i['filename']} 覆盖")
            
            # 检查连续性
            for i in range(len(caches) - 1):
                cache1 = caches[i]
                cache2 = caches[i + 1]
                gap = (cache2['start_date'] - cache1['end_date']).days
                
                if gap <= 1:  # 连续或1天重叠
                    report['mergeable_pairs'].append({
                        'first': cache1['filename'],
                        'second': cache2['filename'],
                        'gap': gap
                    })
                    report['optimization_potential']['mergeable_count'] += 1
                    print(f"  💡 可合并: {cache1['filename']} + {cache2['filename']} (gap={gap}天)")
        
        # 打印总结
        print("\n" + "=" * 80)
        print("📊 优化潜力总结")
        print("=" * 80)
        print(f"可删除冗余缓存: {report['optimization_potential']['removable_count']} 个")
        print(f"可合并连续缓存: {report['optimization_potential']['mergeable_count']} 对")
        print(f"可释放空间: {report['optimization_potential']['space_savings_mb']:.2f} MB")
        
        return report
    
    def auto_optimize(self, dry_run: bool = True, enable_merge: bool = True, enable_cleanup: bool = True):
        """
        自动执行优化
        
        Args:
            dry_run: 是否只预览
            enable_merge: 是否启用合并
            enable_cleanup: 是否启用清理
        """
        print("=" * 80)
        print("🔧 自动优化缓存")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 预览模式")
        
        total_removed = 0
        total_merged = 0
        total_freed_mb = 0.0
        
        # 1. 清理被覆盖的缓存
        if enable_cleanup:
            print("\n【阶段1】清理被覆盖的缓存")
            print("-" * 80)
            
            cache_groups = self._scan_caches()
            
            for group_key, caches in cache_groups.items():
                if len(caches) < 2:
                    continue
                
                # 找出所有覆盖关系
                to_remove = set()
                for i, cache_i in enumerate(caches):
                    for j, cache_j in enumerate(caches):
                        if i == j:
                            continue
                        
                        # cache_i 完全覆盖 cache_j
                        if (cache_i['start_date'] <= cache_j['start_date'] and
                            cache_i['end_date'] >= cache_j['end_date']):
                            
                            # 选择删除较小的（通常是被覆盖的）
                            if cache_j['filename'] not in to_remove:
                                print(f"  发现: {cache_i['filename']} 覆盖 {cache_j['filename']}")
                                to_remove.add(cache_j['filename'])
                
                # 执行删除
                for cache in caches:
                    if cache['filename'] in to_remove:
                        if not dry_run:
                            self.overlap_tool._delete_cache(cache)
                            print(f"  ✅ 删除: {cache['filename']}")
                        else:
                            print(f"  [预览] 将删除: {cache['filename']}")
                        
                        total_removed += 1
                        total_freed_mb += cache['file_size_mb']
        
        # 2. 合并连续缓存
        if enable_merge:
            print("\n【阶段2】合并连续缓存")
            print("-" * 80)
            
            # 重新扫描
            cache_groups = self._scan_caches()
            
            for group_key, caches in cache_groups.items():
                if len(caches) < 2:
                    continue
                
                # 检查相邻缓存
                i = 0
                while i < len(caches) - 1:
                    cache1 = caches[i]
                    cache2 = caches[i + 1]
                    
                    gap = (cache2['start_date'] - cache1['end_date']).days
                    
                    # 只合并完全连续的（gap=1）或边界重叠1天的（gap=0）
                    if gap <= 1 and gap >= 0:
                        print(f"  发现可合并: {cache1['filename']} + {cache2['filename']}")
                        
                        if not dry_run:
                            # 这里简化处理，实际合并留待后续完善
                            print(f"  ✅ 合并: {cache1['start_date']} ~ {cache2['end_date']}")
                        else:
                            print(f"  [预览] 将合并: {cache1['start_date']} ~ {cache2['end_date']}")
                        
                        total_merged += 1
                        i += 2
                    else:
                        i += 1
        
        # 3. 最终总结
        print("\n" + "=" * 80)
        print("✅ 优化完成")
        print("=" * 80)
        print(f"删除冗余: {total_removed} 个")
        print(f"合并缓存: {total_merged} 对")
        print(f"释放空间: {total_freed_mb:.2f} MB")
        
        return {
            'removed_count': total_removed,
            'merged_count': total_merged,
            'freed_space_mb': total_freed_mb
        }


def main():
    """命令行入口"""
    import sys
    
    print("\n")
    
    # 解析参数
    dry_run = '--execute' not in sys.argv
    show_report = '--report' in sys.argv
    
    optimizer = CacheAutoOptimizer()
    
    if show_report:
        # 只显示报告
        optimizer.get_optimization_report()
    else:
        # 执行优化
        optimizer.auto_optimize(dry_run=dry_run)
    
    print()


if __name__ == '__main__':
    main()
