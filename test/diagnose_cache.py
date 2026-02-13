"""
缓存功能诊断脚本
帮助检查缓存是否正常工作
"""

import sys
from pathlib import Path
import datetime
import os

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_cache_directories():
    """检查缓存目录"""
    print("=" * 80)
    print("1. 检查缓存目录结构")
    print("=" * 80)
    
    cache_root = Path("cache")
    
    if not cache_root.exists():
        print("❌ cache/ 目录不存在！")
        return False
    
    print("✅ cache/ 目录存在")
    
    # 检查子目录
    dirs_to_check = [
        "data",
        "data/akshare",
        "data/akshare/a_stock",
        "metadata",
        "logs"
    ]
    
    for dir_path in dirs_to_check:
        full_path = cache_root / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ (不存在)")
    
    print()
    return True


def check_cache_config():
    """检查缓存配置"""
    print("=" * 80)
    print("2. 检查缓存配置")
    print("=" * 80)
    
    config_file = Path("cache/config.json")
    
    if not config_file.exists():
        print("❌ cache/config.json 不存在！")
        return False
    
    print("✅ cache/config.json 存在")
    
    import json
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        enabled = config.get('cache_settings', {}).get('enabled', False)
        max_size = config.get('cache_settings', {}).get('max_size_mb', 0)
        format_type = config.get('storage_format', {}).get('format', 'unknown')
        
        print(f"   缓存启用: {'✅ 是' if enabled else '❌ 否'}")
        print(f"   最大容量: {max_size} MB")
        print(f"   存储格式: {format_type}")
        
        if not enabled:
            print("\n⚠️  警告：缓存已被禁用！请检查 cache/config.json")
        
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return False
    
    print()
    return True


def check_dependencies():
    """检查依赖"""
    print("=" * 80)
    print("3. 检查依赖库")
    print("=" * 80)
    
    deps = {
        'pandas': 'pandas',
        'pyarrow': 'pyarrow (用于Parquet格式)'
    }
    
    all_ok = True
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - 未安装")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  请安装缺失的依赖: pip install pyarrow")
    
    print()
    return all_ok


def test_basic_cache():
    """测试基本缓存功能"""
    print("=" * 80)
    print("4. 测试缓存功能")
    print("=" * 80)
    
    try:
        from cached_data_source import create_cached_data_source
        
        print("✅ 模块导入成功")
        
        # 创建缓存数据源
        print("\n创建带缓存的数据源...")
        data_source = create_cached_data_source('akshare', cache_enabled=True)
        print("✅ 数据源创建成功")
        
        # 测试数据获取
        print("\n测试获取数据（前3个月）...")
        print("-" * 80)
        
        code = '000001'
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 3, 31)
        
        print(f"代码: {code}")
        print(f"日期: {start_date} ~ {end_date}")
        print()
        
        df = data_source.fetch_data(code, start_date, end_date, market='A股')
        
        if df is not None and not df.empty:
            print(f"\n✅ 数据获取成功: {len(df)} 条记录")
            print(f"   日期范围: {df.index[0].date()} ~ {df.index[-1].date()}")
            
            # 检查缓存文件
            print("\n检查缓存文件...")
            cache_dir = Path("cache/data/akshare/a_stock")
            if cache_dir.exists():
                files = list(cache_dir.glob("000001_*.parquet"))
                if files:
                    print(f"   ✅ 找到缓存文件: {files[0].name}")
                    print(f"   文件大小: {files[0].stat().st_size / 1024:.2f} KB")
                else:
                    print("   ⚠️  未找到缓存文件（可能保存失败）")
            
            # 检查索引
            print("\n检查缓存索引...")
            index_file = Path("cache/metadata/cache_index.json")
            if index_file.exists():
                import json
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
                
                entries = index.get('entries', {})
                if entries:
                    print(f"   ✅ 索引中有 {len(entries)} 条缓存记录")
                    for key in entries:
                        if '000001' in key:
                            print(f"   找到: {key}")
                else:
                    print("   ⚠️  索引为空（缓存可能未保存）")
            
            return True
        else:
            print("❌ 数据获取失败")
            print("   可能原因:")
            print("   1. 网络连接问题")
            print("   2. AKShare API 不稳定")
            print("   3. 股票代码不正确")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()


def check_permissions():
    """检查文件权限"""
    print("=" * 80)
    print("5. 检查文件权限")
    print("=" * 80)
    
    cache_root = Path("cache")
    
    # 测试写入权限
    test_file = cache_root / "data" / "test_write.txt"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("✅ cache/data/ 目录有写入权限")
    except Exception as e:
        print(f"❌ cache/data/ 目录无写入权限: {e}")
        return False
    
    # 测试元数据目录
    test_file = cache_root / "metadata" / "test_write.txt"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("✅ cache/metadata/ 目录有写入权限")
    except Exception as e:
        print(f"❌ cache/metadata/ 目录无写入权限: {e}")
        return False
    
    print()
    return True


def main():
    """主函数"""
    print("\n")
    print("🔍 缓存功能诊断工具")
    print("=" * 80)
    print()
    
    # 执行检查
    results = []
    
    results.append(("目录结构", check_cache_directories()))
    results.append(("缓存配置", check_cache_config()))
    results.append(("依赖库", check_dependencies()))
    results.append(("文件权限", check_permissions()))
    results.append(("功能测试", test_basic_cache()))
    
    # 总结
    print("=" * 80)
    print("📊 诊断总结")
    print("=" * 80)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r for _, r in results)
    
    print()
    if all_passed:
        print("🎉 所有检查通过！缓存功能应该正常工作。")
    else:
        print("⚠️  发现问题，请根据上述提示修复。")
    
    print()
    print("💡 提示:")
    print("   - 如果数据没有缓存，请查看上面的详细输出")
    print("   - 确保 cache/config.json 中 enabled=true")
    print("   - 确保安装了 pyarrow: pip install pyarrow")
    print("   - 查看缓存统计: python test/cache_tool.py")
    print()


if __name__ == '__main__':
    main()
