"""
Streamlit 缓存清理工具
清除可能导致问题的缓存数据
"""

import os
import shutil

print("=" * 70)
print("🧹 Streamlit 缓存清理工具")
print("=" * 70)

# Streamlit 缓存目录通常在
cache_dirs = [
    os.path.expanduser("~/.streamlit/cache"),
    os.path.expanduser("~/.cache/streamlit"),
    ".streamlit",
    "__pycache__",
]

print("\n正在查找缓存目录...")

for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        try:
            print(f"\n找到缓存目录: {cache_dir}")
            
            # 计算缓存大小
            total_size = 0
            file_count = 0
            for dirpath, dirnames, filenames in os.walk(cache_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                        file_count += 1
                    except:
                        pass
            
            print(f"   文件数: {file_count}")
            print(f"   大小: {total_size / 1024 / 1024:.2f} MB")
            
            # 询问是否删除（自动删除）
            if cache_dir in ["__pycache__", ".streamlit"]:
                # Python 缓存，安全删除
                try:
                    shutil.rmtree(cache_dir)
                    print(f"   ✅ 已删除")
                except Exception as e:
                    print(f"   ❌ 删除失败: {e}")
            else:
                print(f"   ℹ️  保留系统缓存（建议手动清理）")
                    
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
    else:
        print(f"未找到: {cache_dir}")

print("\n" + "=" * 70)
print("💡 清理建议")
print("=" * 70)
print("""
1. 已清理本地 Python 缓存 (__pycache__)

2. 如需清理 Streamlit 缓存，可以:
   方法A: 在 Streamlit 应用中按 'C' 键，选择 "Clear cache"
   方法B: 重启 Streamlit 应用
   方法C: 手动删除 ~/.streamlit/cache 目录

3. 重新启动 Streamlit:
   pkill -f "streamlit run"
   python -m streamlit run run_main.py

4. 如果仍有问题，尝试:
   python -m streamlit run run_main.py --server.enableStaticServing=false
""")

print("\n✅ 清理完成！")
