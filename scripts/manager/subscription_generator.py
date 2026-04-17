"""
订阅生成模块 - 从S-UI数据库读取节点，生成订阅链接
VLESS+Reality使用直连IP，VLESS-WS和Trojan-WS使用不同的优选IP
Author: Alan
Version: v3.0.0
"""
import json
import sqlite3
import base64
import os
import urllib.parse
import sys
from datetime import datetime
from dotenv import load_dotenv

# 设置UTF-8编码输出（解决Windows GBK编码问题）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

class SubscriptionGenerator:
    def __init__(self):
        self.server_ip = os.getenv('SERVER_IP', 'YOUR_SERVER_IP')
        self.db_path = os.getenv('SERVER_DB_PATH', '/usr/local/s-ui/db/s-ui.db')
        self.cf_domain = os.getenv('CF_DOMAIN', 'YOUR_CF_DOMAIN')
        self.vless_cdn_ip = None
        self.trojan_cdn_ip = None
        self.use_https = os.getenv('USE_HTTPS', 'true').lower() == 'true'
        self.sub_domain = os.getenv('SUB_DOMAIN', self.cf_domain)  # 订阅使用的域名
        
    def get_cdn_ips(self):
        """从数据库获取VLESS和Trojan的优选IP"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取VLESS-WS的优选IP
            cursor.execute("SELECT value FROM cdn_settings WHERE key='vless_cdn_ip'")
            row = cursor.fetchone()
            if row:
                self.vless_cdn_ip = row[0]
                print(f"  ✅ VLESS-WS优选IP: {self.vless_cdn_ip}")
            else:
                print("  ⚠️ 没有VLESS优选IP，使用源IP")
                self.vless_cdn_ip = self.server_ip
            
            # 获取Trojan-WS的优选IP
            cursor.execute("SELECT value FROM cdn_settings WHERE key='trojan_cdn_ip'")
            row = cursor.fetchone()
            if row:
                self.trojan_cdn_ip = row[0]
                print(f"  ✅ Trojan-WS优选IP: {self.trojan_cdn_ip}")
            else:
                print("  ⚠️ 没有Trojan优选IP，使用源IP")
                self.trojan_cdn_ip = self.server_ip
            
            conn.close()
            return True
        except Exception as e:
            print(f"  ❌ 获取优选IP失败: {e}")
            self.vless_cdn_ip = self.server_ip
            self.trojan_cdn_ip = self.server_ip
            return False
    
    def get_inbounds(self):
        """从数据库获取所有inbounds"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, tag, addrs, out_json FROM inbounds")
        inbounds = cursor.fetchall()
        conn.close()
        return inbounds
    
    def generate_vless_link(self, inbound):
        """生成VLESS链接"""
        inbound_id, type_, tag, addrs_blob, out_json_blob = inbound
        
        try:
            addrs = json.loads(addrs_blob) if addrs_blob else []
            out_json = json.loads(out_json_blob) if out_json_blob else {}
            
            # 获取UUID（直接从out_json根级别获取）
            uuid = out_json.get('uuid', '')
            if not uuid:
                return None
            
            flow = out_json.get('flow', '')
            
            # 获取TLS配置
            tls = out_json.get('tls', {})
            is_reality = tls.get('reality', False)  # 可能是布尔值
            sni = tls.get('server_name', '')
            public_key = tls.get('public_key', '')
            short_id = tls.get('short_id', '')
            
            # 获取传输配置
            transport = out_json.get('transport', {})
            transport_type = transport.get('type', 'tcp')
            path = transport.get('path', '/')
            
            # 获取服务器地址和端口
            if addrs:
                server = addrs[0].get('server', self.server_ip)
                port = addrs[0].get('server_port', 443)
            else:
                server = out_json.get('server', self.server_ip)
                port = out_json.get('server_port', 443)
            
            # 如果是VLESS+Reality，使用直连IP
            if is_reality:
                server = self.server_ip
            
            # 如果是VLESS-WS，使用优选IP
            if transport_type == 'ws' and self.vless_cdn_ip:
                server = self.vless_cdn_ip
                port = 443  # CDN端口
            
            # 构建参数
            params = {
                'encryption': 'none',
                'type': transport_type
            }
            
            if is_reality:
                params['flow'] = flow
                params['security'] = 'reality'
                params['sni'] = sni
                params['fp'] = 'chrome'
                params['pbk'] = public_key
                params['sid'] = short_id
            elif transport_type == 'ws':
                params['security'] = 'tls'
                params['sni'] = self.cf_domain
                params['path'] = path
            
            # 构建链接
            param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
            link = f"vless://{uuid}@{server}:{port}?{param_str}#{urllib.parse.quote(tag)}"
            
            return link
            
        except Exception as e:
            print(f"  ❌ 生成VLESS链接失败 {tag}: {e}")
            return None
    
    def generate_trojan_link(self, inbound):
        """生成Trojan链接"""
        inbound_id, type_, tag, addrs_blob, out_json_blob = inbound
        
        try:
            addrs = json.loads(addrs_blob) if addrs_blob else []
            out_json = json.loads(out_json_blob) if out_json_blob else {}
            
            # 获取密码（直接从out_json根级别获取）
            password = out_json.get('password', '')
            if not password:
                return None
            
            # 获取传输配置
            transport = out_json.get('transport', {})
            transport_type = transport.get('type', 'tcp')
            path = transport.get('path', '/')
            
            # 获取服务器地址和端口
            if addrs:
                server = addrs[0].get('server', self.server_ip)
                port = addrs[0].get('server_port', 8080)
            else:
                server = out_json.get('server', self.server_ip)
                port = out_json.get('server_port', 8080)
            
            # 如果是Trojan-WS，使用优选IP
            if transport_type == 'ws' and self.trojan_cdn_ip:
                server = self.trojan_cdn_ip
                port = 443  # CDN端口
            
            # 构建参数
            params = {
                'type': transport_type,
                'security': 'tls',
                'sni': self.cf_domain
            }
            
            if transport_type == 'ws':
                params['path'] = path
            
            # 构建链接
            param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
            link = f"trojan://{password}@{server}:{port}?{param_str}#{urllib.parse.quote(tag)}"
            
            return link
            
        except Exception as e:
            print(f"  ❌ 生成Trojan链接失败 {tag}: {e}")
            return None
    
    def generate_hysteria2_link(self, inbound):
        """生成Hysteria2链接"""
        inbound_id, type_, tag, addrs_blob, out_json_blob = inbound
        
        try:
            addrs = json.loads(addrs_blob) if addrs_blob else []
            out_json = json.loads(out_json_blob) if out_json_blob else {}
            
            # 获取密码（直接从out_json根级别获取）
            password = out_json.get('password', '')
            if not password:
                return None
            
            # 获取服务器地址和端口
            if addrs:
                server = addrs[0].get('server', self.server_ip)
                port = addrs[0].get('server_port', 20000)
            else:
                server = out_json.get('server', self.server_ip)
                port = out_json.get('server_port', 20000)
            
            # 获取TLS配置
            tls = out_json.get('tls', {})
            sni = tls.get('server_name', '')
            insecure = tls.get('insecure', True)
            
            # 获取obfs配置
            obfs = out_json.get('obfs', {})
            obfs_type = obfs.get('type', '')
            obfs_password = obfs.get('password', '')
            
            # 获取UDP over TCP配置
            udp_over_tcp = out_json.get('udp_over_tcp', {})
            udp_over_tcp_enabled = udp_over_tcp.get('enabled', False)
            udp_over_tcp_mode = udp_over_tcp.get('mode', 'auto')
            
            # 构建参数
            params = {
                'sni': sni,
                'insecure': '1' if insecure else '0'
            }
            
            if obfs_type:
                params['obfs'] = obfs_type
                params['obfs-password'] = obfs_password
            
            # 如果启用了UDP over TCP，添加参数
            if udp_over_tcp_enabled:
                params['udp_over_tcp'] = udp_over_tcp_mode
            
            # 构建链接
            param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
            link = f"hysteria2://{password}@{server}:{port}?{param_str}#{urllib.parse.quote(tag)}"
            
            return link
            
        except Exception as e:
            print(f"  ❌ 生成Hysteria2链接失败 {tag}: {e}")
            return None
    
    def generate_all_links(self):
        """生成所有链接"""
        inbounds = self.get_inbounds()
        links = []
        
        for inbound in inbounds:
            type_ = inbound[1]
            tag = inbound[2]
            
            if type_ == 'vless':
                link = self.generate_vless_link(inbound)
            elif type_ == 'trojan':
                link = self.generate_trojan_link(inbound)
            elif type_ == 'hysteria2':
                link = self.generate_hysteria2_link(inbound)
            else:
                continue
            
            if link:
                links.append(link)
                print(f"  ✅ {tag}")
        
        return links
    
    def generate_base64_subscription(self):
        """生成Base64订阅"""
        links = self.generate_all_links()
        content = '\n'.join(links)
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    def generate_json_subscription(self):
        """生成JSON订阅"""
        links = self.generate_all_links()
        return json.dumps({'links': links}, ensure_ascii=False, indent=2)
    
    def generate_subscription_url(self, format='base64'):
        """生成订阅链接（支持域名/IP自动切换）"""
        protocol = 'https' if self.use_https else 'http'
        port = 443 if self.use_https else 80
        
        # 优先使用订阅域名，没有则使用服务器IP
        host = self.sub_domain if self.sub_domain and self.sub_domain != 'YOUR_CF_DOMAIN' else self.server_ip
        
        # 处理端口显示
        if (protocol == 'https' and port == 443) or (protocol == 'http' and port == 80):
            port_str = ''
        else:
            port_str = f":{port}"
        
        if format == 'base64':
            return f"{protocol}://{host}{port_str}/sub/{base64.b64encode(self.cf_domain.encode()).decode()}"
        elif format == 'json':
            return f"{protocol}://{host}{port_str}/sub-json/{base64.b64encode(self.cf_domain.encode()).decode()}"
        return ""
    
    def run(self, format='base64'):
        """运行订阅生成"""
        print("=" * 50)
        print("订阅生成开始")
        print("=" * 50)
        
        # 获取优选IP
        self.get_cdn_ips()
        
        # 生成订阅
        if format == 'base64':
            return self.generate_base64_subscription()
        elif format == 'json':
            return self.generate_json_subscription()
        else:
            return self.generate_all_links()

if __name__ == "__main__":
    import sys
    
    generator = SubscriptionGenerator()
    
    # 获取命令行参数
    format_type = sys.argv[1] if len(sys.argv) > 1 else 'base64'
    
    # 生成订阅
    if format_type == 'base64':
        sub = generator.generate_base64_subscription()
        print(sub)
    elif format_type == 'json':
        sub_json = generator.generate_json_subscription()
        print(sub_json)
    else:
        # 显示所有链接
        links = generator.generate_all_links()
        for link in links:
            print(link)
        
        # 显示订阅URL
        print("\n=== 订阅链接 ===")
        print(f"Base64: {generator.generate_subscription_url('base64')}")
        print(f"JSON: {generator.generate_subscription_url('json')}")
