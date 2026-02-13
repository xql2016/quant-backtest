"""
测试缓存优化工具
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.merge_continuous_caches import CacheMergeTool
from tools.check_cache_overlap import CacheOverlapTool
from tools.auto_optimize_cache import CacheAutoOptimizer


def test_merge_tool():
    """测试连续缓存合并工具"""
    print("\n" + "=" * 80)
    print("测试1：连续缓存合并工具")
    print("=" * 80)
    
    tool = CacheMergeTool()
    
    # 检查是否有测试文件
    test_files = list(Path("cache/data").rglob("*.parquet"))
    
    if len(test_files) < 2:
        print("❌ 测试跳过：缓存文件不足2个")
        return
    
    # 取前两个文件测试（预览模式）
    file1 = test_files[0].relative_to(Path("cache/data"))
    file2 = test_files[1].relative_to(Path("cache/data"))
    
    print(f"\n测试文件:")
    print(f"  文件1: {file1}")
    print(f"  文件2: {file2}")
    
    result = tool.merge_continuous_caches(str(file1), str(file2), dry_run=True)
    
    print(f"\n结果: {result['status']}")
    print(f"信息: {result['message']}")


def test_overlap_tool():
    """测试缓存覆盖判断工具"""
    print("\n" + "=" * 80)
    print("测试2：缓存覆盖判断工具")
    print("=" * 80)
    
    tool = CacheOverlapTool()
    
    # 检查是否有测试文件
    test_files = list(Path("cache/data").rglob("*.parquet"))
    
    if len(test_files) < 2:
        print("❌ 测试跳过：缓存文件不足2个")
        return
    
    # 取前两个文件测试（预览模式）
    file1 = test_files[0].relative_to(Path("cache/data"))
    file2 = test_files[1].relative_to(Path("cache/data"))
    
    print(f"\n测试文件:")
    print(f"  文件1: {file1}")
    print(f"  文件2: {file2}")
    
    result = tool.check_and_remove_covered(str(file1), str(file2), dry_run=True)
    
    print(f"\n结果: {result['status']}")
    print(f"信息: {result['message']}")


def test_auto_optimizer():
    """测试自动优化工具"""
    print("\n" + "=" * 80)
    print("测试3：自动优化工具")
    print("=" * 80)
    
    optimizer = CacheAutoOptimizer()
    
    # 生成报告
    print("\n生成优化报告...")
    report = optimizer.get_optimization_report()
    
    # 预览优化
    print("\n" + "=" * 80)
    print("预览自动优化")
    print("=" * 80)
    optimizer.auto_optimize(dry_run=True)


def main():
    """主测试函数"""
    print("\n")
    print("🧪 缓存优化工具测试套件")
    print("=" * 80)
    
    # 测试1：连续缓存合并
    test_merge_tool()
    
    # 测试2：缓存覆盖判断
    test_overlap_tool()
    
    # 测试3：自动优化
    test_auto_optimizer()
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成")
    print("=" * 80)
    print("\n💡 提示：以上测试均为预览模式，未执行实际操作")
    print()


if __name__ == '__main__':
    main()
