"""
SSL 配置模块
在数据获取前导入此模块以禁用 SSL 验证（仅用于开发环境）
"""

import ssl
import urllib.request
import warnings

# 防止重复初始化的标志
_ssl_disabled = False

def disable_ssl_verification():
    """
    禁用 SSL 证书验证
    警告：这会降低安全性，仅在开发/测试环境使用！
    """
    global _ssl_disabled
    
    # 如果已经禁用过，直接返回
    if _ssl_disabled:
        return
    
    # 创建不验证证书的 SSL 上下文
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # 禁用 SSL 警告
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    warnings.filterwarnings('ignore', module='urllib3')
    
    # 同时配置 urllib3 的 SSL 验证（用于 requests 库）
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except (ImportError, AttributeError):
        pass
    
    # 配置 requests 库（如果使用）
    # 这里简化处理，只设置默认的 verify=False
    try:
        import requests
        # Monkey patch requests 默认不验证证书
        original_request = requests.Session.request
        
        def patched_request(self, method, url, **kwargs):
            kwargs.setdefault('verify', False)
            return original_request(self, method, url, **kwargs)
        
        requests.Session.request = patched_request
    except (ImportError, AttributeError):
        pass
    
    _ssl_disabled = True
    print("⚠️  已禁用 SSL 证书验证（仅用于开发环境）")

def enable_ssl_verification():
    """恢复 SSL 证书验证"""
    global _ssl_disabled
    ssl._create_default_https_context = ssl.create_default_context
    _ssl_disabled = False
    print("✅ 已恢复 SSL 证书验证")
