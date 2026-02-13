#!/usr/bin/env python
"""
快速验证工具是否可用
"""

import sys
from pathlib import Path

def test_imports():
    """测试导入"""
    print("🧪 测试工具导入...")
    
    try:
        from tools import CacheMergeTool, CacheOverlapTool, CacheAutoOptimizer
        print("✅ 所有工具导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_initialization():
    """测试初始化"""
    print("\n🧪 测试工具初始化...")
    
    try:
        from tools import CacheMergeTool, CacheOverlapTool, CacheAutoOptimizer
        
        merge_tool = CacheMergeTool()
        print(f"✅ CacheMergeTool 初始化成功")
        
        overlap_tool = CacheOverlapTool()
        print(f"✅ CacheOverlapTool 初始化成功")
        
        optimizer = CacheAutoOptimizer()
        print(f"✅ CacheAutoOptimizer 初始化成功")
        
        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n🧪 检查文件结构...")
    
    files = [
        'tools/__init__.py',
        'tools/merge_continuous_caches.py',
        'tools/check_cache_overlap.py',
        'tools/auto_optimize_cache.py',
        'tools/README.md',
        'docs/缓存优化工具快速指南.md',
        'docs/缓存优化工具实现总结.md',
        'docs/README.md',
    ]
    
    all_exist = True
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} 不存在")
            all_exist = False
    
    return all_exist

def main():
    """主测试"""
    print("\n" + "=" * 80)
    print("🚀 缓存优化工具验证")
    print("=" * 80)
    
    results = []
    
    # 测试1：导入
    results.append(test_imports())
    
    # 测试2：初始化
    results.append(test_initialization())
    
    # 测试3：文件结构
    results.append(test_file_structure())
    
    # 总结
    print("\n" + "=" * 80)
    if all(results):
        print("✅ 所有测试通过！工具可以正常使用。")
        print("\n💡 快速开始:")
        print("   python tools/auto_optimize_cache.py --report")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
