"""
缓存管理工具
提供缓存查看、清理、统计等功能
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from cache_manager import CacheManager


def print_separator():
    """打印分隔线"""
    print("=" * 80)


def format_size(size_mb: float) -> str:
    """格式化文件大小"""
    if size_mb < 1:
        return f"{size_mb * 1024:.2f} KB"
    elif size_mb < 1024:
        return f"{size_mb:.2f} MB"
    else:
        return f"{size_mb / 1024:.2f} GB"


def show_statistics(cache_manager: CacheManager):
    """显示缓存统计信息"""
    print_separator()
    print("📊 缓存统计信息")
    print_separator()
    
    stats = cache_manager.get_statistics()
    
    print(f"📦 缓存总数: {stats['total_entries']} 个")
    print(f"💾 缓存大小: {format_size(stats['total_size_mb'])}")
    print(f"📅 最早缓存: {stats.get('oldest_entry', 'N/A')}")
    print(f"📅 最新缓存: {stats.get('newest_entry', 'N/A')}")
    
    max_size_mb = cache_manager.config.get('cache_settings', {}).get('max_size_mb', 1024)
    usage_percent = (stats['total_size_mb'] / max_size_mb) * 100 if max_size_mb > 0 else 0
    
    print(f"📈 容量使用: {usage_percent:.1f}% ({format_size(stats['total_size_mb'])} / {format_size(max_size_mb)})")
    
    print()


def list_caches(cache_manager: CacheManager, limit: int = 20):
    """列出缓存条目"""
    print_separator()
    print("📝 缓存列表")
    print_separator()
    
    entries = cache_manager.index.get_all_entries()
    
    if not entries:
        print("📭 暂无缓存数据")
        return
    
    # 按最后访问时间排序
    sorted_entries = sorted(
        entries.items(),
        key=lambda x: x[1].get('last_accessed', ''),
        reverse=True
    )
    
    print(f"{'代码':<15} {'市场':<15} {'日期范围':<25} {'大小':<12} {'访问次数':<8} {'最后访问':<20}")
    print("-" * 115)
    
    for i, (key, entry) in enumerate(sorted_entries[:limit]):
        code = entry.get('code', 'N/A')
        market = entry.get('market', 'N/A')
        start = entry.get('start_date', '')
        end = entry.get('end_date', '')
        date_range = f"{start} ~ {end}"
        size = format_size(entry.get('file_size_kb', 0) / 1024)
        access_count = entry.get('access_count', 0)
        last_access = entry.get('last_accessed', 'N/A')
        
        # 格式化最后访问时间
        if last_access != 'N/A':
            try:
                dt = datetime.fromisoformat(last_access)
                last_access = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        print(f"{code:<15} {market:<15} {date_range:<25} {size:<12} {access_count:<8} {last_access:<20}")
    
    if len(entries) > limit:
        print(f"\n... 还有 {len(entries) - limit} 条缓存未显示")
    
    print()


def show_cache_detail(cache_manager: CacheManager, code: str):
    """显示指定代码的缓存详情"""
    print_separator()
    print(f"🔍 缓存详情: {code}")
    print_separator()
    
    entries = cache_manager.index.get_all_entries()
    
    # 查找匹配的缓存
    matched = [(k, v) for k, v in entries.items() if code in k]
    
    if not matched:
        print(f"❌ 未找到 {code} 的缓存")
        return
    
    for key, entry in matched:
        print(f"\n缓存键: {key}")
        print(f"  数据源: {entry.get('data_source', 'N/A')}")
        print(f"  市场: {entry.get('market', 'N/A')}")
        print(f"  代码: {entry.get('code', 'N/A')}")
        print(f"  日期范围: {entry.get('start_date', 'N/A')} ~ {entry.get('end_date', 'N/A')}")
        print(f"  时间粒度: {entry.get('interval', 'N/A')}")
        print(f"  数据行数: {entry.get('rows', 0)}")
        print(f"  数据列: {', '.join(entry.get('columns', []))}")
        print(f"  文件大小: {format_size(entry.get('file_size_kb', 0) / 1024)}")
        print(f"  文件路径: {entry.get('file_path', 'N/A')}")
        print(f"  创建时间: {entry.get('created_at', 'N/A')}")
        print(f"  最后访问: {entry.get('last_accessed', 'N/A')}")
        print(f"  访问次数: {entry.get('access_count', 0)}")
        print(f"  数据完整: {'是' if entry.get('is_complete', False) else '否'}")
        print(f"  校验和: {entry.get('checksum', 'N/A')}")
    
    print()


def cleanup_cache(cache_manager: CacheManager, force: bool = False):
    """清理缓存"""
    print_separator()
    print("🧹 清理缓存")
    print_separator()
    
    stats_before = cache_manager.get_statistics()
    print(f"清理前: {stats_before['total_entries']} 个缓存, {format_size(stats_before['total_size_mb'])}")
    
    cache_manager.cleanup_cache(force=force)
    
    stats_after = cache_manager.get_statistics()
    print(f"清理后: {stats_after['total_entries']} 个缓存, {format_size(stats_after['total_size_mb'])}")
    
    deleted = stats_before['total_entries'] - stats_after['total_entries']
    freed = stats_before['total_size_mb'] - stats_after['total_size_mb']
    
    print(f"✅ 删除了 {deleted} 个缓存，释放了 {format_size(freed)}")
    print()


def clear_all_cache(cache_manager: CacheManager):
    """清空所有缓存"""
    print_separator()
    print("⚠️  清空所有缓存")
    print_separator()
    
    stats = cache_manager.get_statistics()
    print(f"当前有 {stats['total_entries']} 个缓存，共 {format_size(stats['total_size_mb'])}")
    
    confirm = input("确认要删除所有缓存吗？(yes/no): ")
    
    if confirm.lower() == 'yes':
        cache_manager.clear_all_cache()
        print("✅ 所有缓存已清空")
    else:
        print("❌ 已取消")
    
    print()


def delete_cache_by_code(cache_manager: CacheManager, code: str):
    """删除指定代码的缓存"""
    print_separator()
    print(f"🗑️  删除缓存: {code}")
    print_separator()
    
    entries = cache_manager.index.get_all_entries()
    matched = [(k, v) for k, v in entries.items() if code in k]
    
    if not matched:
        print(f"❌ 未找到 {code} 的缓存")
        return
    
    print(f"找到 {len(matched)} 个匹配的缓存:")
    for key, entry in matched:
        print(f"  - {key} ({format_size(entry.get('file_size_kb', 0) / 1024)})")
    
    confirm = input(f"\n确认删除这 {len(matched)} 个缓存吗？(yes/no): ")
    
    if confirm.lower() == 'yes':
        deleted = 0
        for key, _ in matched:
            if cache_manager.delete_cache(key):
                deleted += 1
        print(f"✅ 删除了 {deleted} 个缓存")
    else:
        print("❌ 已取消")
    
    print()


def show_menu():
    """显示菜单"""
    print_separator()
    print("🛠️  缓存管理工具")
    print_separator()
    print()
    print("1. 查看缓存统计")
    print("2. 列出所有缓存")
    print("3. 查看指定代码的缓存详情")
    print("4. 清理过期/冗余缓存")
    print("5. 删除指定代码的缓存")
    print("6. 清空所有缓存 (危险操作)")
    print("0. 退出")
    print()


def main():
    """主函数"""
    # 初始化缓存管理器
    try:
        cache_manager = CacheManager()
    except Exception as e:
        print(f"❌ 初始化缓存管理器失败: {e}")
        return
    
    while True:
        show_menu()
        
        choice = input("请选择操作 (0-6): ").strip()
        print()
        
        if choice == '0':
            print("👋 再见!")
            break
        elif choice == '1':
            show_statistics(cache_manager)
        elif choice == '2':
            limit = input("显示条数 (默认20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            list_caches(cache_manager, limit)
        elif choice == '3':
            code = input("输入股票代码: ").strip()
            if code:
                show_cache_detail(cache_manager, code)
        elif choice == '4':
            cleanup_cache(cache_manager)
        elif choice == '5':
            code = input("输入股票代码: ").strip()
            if code:
                delete_cache_by_code(cache_manager, code)
        elif choice == '6':
            clear_all_cache(cache_manager)
        else:
            print("❌ 无效的选择，请重试\n")
        
        input("按回车继续...")
        print("\n" * 2)


if __name__ == '__main__':
    main()
