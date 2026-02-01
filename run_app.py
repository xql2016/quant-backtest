#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化回测工作台启动脚本
用于打包成可执行文件
"""

import os
import sys
import subprocess
import socket
import webbrowser
import time

def find_free_port():
    """查找可用端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def main():
    # 获取脚本所在目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        application_path = sys._MEIPASS
    else:
        # 如果是直接运行python脚本
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Streamlit 应用文件路径
    streamlit_app = os.path.join(application_path, '多策略可视化回测_小红书20260117.py')
    
    # 查找可用端口
    port = 8501
    
    print("=" * 60)
    print("量化回测工作台")
    print("=" * 60)
    print(f"正在启动应用...")
    print(f"端口: {port}")
    print(f"启动完成后将自动打开浏览器...")
    print("=" * 60)
    
    # 构建streamlit命令
    cmd = [
        sys.executable,
        '-m',
        'streamlit',
        'run',
        streamlit_app,
        '--server.port', str(port),
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'
    ]
    
    try:
        # 启动streamlit进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务启动
        time.sleep(5)
        
        # 打开浏览器
        url = f'http://localhost:{port}'
        print(f"\n访问地址: {url}")
        webbrowser.open(url)
        
        print("\n应用已启动！")
        print("关闭此窗口将停止应用。")
        print("=" * 60)
        
        # 保持进程运行
        process.wait()
        
    except KeyboardInterrupt:
        print("\n正在关闭应用...")
        process.terminate()
        print("应用已关闭。")
    except Exception as e:
        print(f"\n错误: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()

