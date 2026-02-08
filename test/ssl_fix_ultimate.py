"""
终极 SSL 修复方案
通过 monkey patch 方式修复所有 SSL 相关问题
"""

import ssl
import warnings

# 禁用所有 SSL 警告
warnings.filterwarnings('ignore')

# 方法1: 修改默认 SSL 上下文
ssl._create_default_https_context = ssl._create_unverified_context

# 方法2: 修改 urllib3
try:
    import urllib3
    urllib3.disable_warnings()
    
    # Monkey patch HTTPSConnectionPool
    from urllib3.util import ssl_
    ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=0'
except:
    pass

# 方法3: 修改 requests
try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.poolmanager import PoolManager
    
    class NoSSLAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            context = ssl._create_unverified_context()
            kwargs['ssl_context'] = context
            return super().init_poolmanager(*args, **kwargs)
    
    # 创建默认 session 并配置
    _original_session = requests.Session
    
    class PatchedSession(_original_session):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verify = False
            adapter = NoSSLAdapter()
            self.mount('https://', adapter)
            self.mount('http://', adapter)
    
    requests.Session = PatchedSession
    requests.sessions.Session = PatchedSession
except:
    pass

print("🔓 SSL 验证已完全禁用（仅用于开发环境）")

# 测试连接
if __name__ == "__main__":
    print("\n测试连接...")
    
    # 测试 requests
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=5, verify=False)
        print(f"✅ requests 连接成功 ({response.status_code})")
    except Exception as e:
        print(f"❌ requests 失败: {e}")
    
    # 测试 urllib
    try:
        import urllib.request
        response = urllib.request.urlopen("https://www.google.com", timeout=5)
        print(f"✅ urllib 连接成功 ({response.status})")
    except Exception as e:
        print(f"❌ urllib 失败: {e}")
