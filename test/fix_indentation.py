#!/usr/bin/env python3
"""
修复 run_main.py 中 with 块的缩进问题
"""

# 读取文件
with open('run_main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 需要增加缩进的行范围（481-677行，索引从0开始，所以是480-676）
start_line = 480  # 第481行
end_line = 677    # 第678行（不包含）

# 修复缩进
for i in range(start_line, min(end_line, len(lines))):
    # 只增加4个空格的缩进
    if lines[i].strip():  # 如果不是空行
        lines[i] = '    ' + lines[i]
    # 空行保持不变

# 写回文件
with open('run_main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ 缩进修复完成")
print(f"修复范围：第 {start_line+1} 到 {end_line} 行")
