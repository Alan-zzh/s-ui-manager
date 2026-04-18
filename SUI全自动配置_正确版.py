#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S-UI v1.4.1全自动配置脚本（正确版）
根据实际数据库结构编写
"""

import paramiko
import json
import time
import base64
import uuid
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

# VPS配置
VPS_IP = 'YOUR_SERVER_IP'
SSH_PORT = 22
SSH_USER = 'root'
SSH_PASS = 'YOUR_SSH_PASSWORD'

# 代理配置
REGION = 'JP'
DESCRIPTION = 'puzan'
DB_PATH = '/usr/local/s-ui/db/s-ui.db'

class SUIAutoConfig:
    def __init__(self):
        self.ssh = None
        self.reality_private = ''
        self.reality_public = ''
        self.short_id = ''
    
    def connect(self):
        print("正在连接VPS...")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(VPS_IP, SSH_PORT, SSH_USER, SSH_PASS, timeout=30)
        print("✅ 连接成功！")
    
    def run_cmd(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        return out, err
    
    def generate_reality_keys(self):
        print("\n【步骤1】生成Reality X25519密钥对...")
        
        private_key = X25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        self.reality_private = base64.b64encode(private_key.private_bytes_raw()).decode('utf-8')
        self.reality_public = base64.b64encode(public_key.public_bytes_raw()).decode('utf-8')
        self.short_id = uuid.uuid4().hex[:16]
        
        print(f"Reality私钥: {self.reality_private}")
        print(f"Reality公钥: {self.reality_public}")
        print(f"ShortId: {self.short_id}")
    
    def create_config_script(self):
        print("\n【步骤2】创建配置脚本...")
        
        # 生成UUID和密码
        vless_reality_uuid = str(uuid.uuid4())
        vless_ws_uuid = str(uuid.uuid4())
        trojan_password = str(uuid.uuid4())[:8]
        hy2_password = str(uuid.uuid4())[:8]
        
        # 构建Python脚本
        script = f'''#!/usr/bin/env python3
import sqlite3
import json

DB_PATH = '{DB_PATH}'

def to_blob(data):
    """将Python对象转换为JSON BLOB"""
    return json.dumps(data, ensure_ascii=False).encode('utf-8')

def insert_inbound(type_val, tag, tls_id, addrs, out_json, options):
    """插入入站规则"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO inbounds (type, tag, tls_id, addrs, out_json, options) VALUES (?, ?, ?, ?, ?, ?)",
        (type_val, tag, tls_id, to_blob(addrs), to_blob(out_json), to_blob(options))
    )
    
    inbound_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inbound_id

def insert_tls(name, server, client):
    """插入TLS配置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO tls (name, server, client) VALUES (?, ?, ?)",
        (name, to_blob(server), to_blob(client))
    )
    
    tls_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tls_id

def insert_client(name, config, inbounds_list, desc=""):
    """插入客户端（用户）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO clients (enable, name, config, inbounds, links, volume, expiry, down, up, desc, `group`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, name, to_blob(config), to_blob(inbounds_list), to_blob([]), 0, 0, 0, 0, desc, "")
    )
    
    client_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return client_id

# ============================================
# 1. VLESS Reality (端口443)
# ============================================
print("\\n添加 VLESS Reality...")

# 创建TLS配置（Reality）
tls_id_reality = insert_tls(
    name='Reality',
    server={{
        "enabled": True,
        "reality": {{
            "enabled": True,
            "handshake": {{
                "server": "yahoo.com",
                "server_port": 443
            }},
            "private_key": "{self.reality_private}",
            "short_id": ["{self.short_id}"]
        }}
    }},
    client={{}}
)

# 创建入站
inbound_id_vr = insert_inbound(
    type_val='vless',
    tag='vless-reality',
    tls_id=tls_id_reality,
    addrs=[{{"remark": "{REGION}-Reality", "addr": "", "port": 443}}],
    out_json={{
        "type": "vless",
        "tag": "vless-reality",
        "listen": "::",
        "listen_port": 443,
        "sniff": True,
        "sniff_override_destination": True
    }},
    options={{
        "clients": [
            {{
                "id": "{vless_reality_uuid}",
                "flow": "xtls-rprx-vision"
            }}
        ]
    }}
)

# 添加客户端
insert_client(
    name="{REGION}-Reality",
    config={{"vless": [{{"id": "{vless_reality_uuid}", "flow": "xtls-rprx-vision"}}]}},
    inbounds_list=[inbound_id_vr],
    desc="{DESCRIPTION}"
)

print("✅ VLESS Reality 添加成功")

# ============================================
# 2. VLESS WS + TLS (端口8443)
# ============================================
print("\\n添加 VLESS WS...")

# 创建TLS配置
tls_id_ws = insert_tls(
    name='TLS',
    server={{
        "enabled": True
    }},
    client={{}}
)

# 创建入站
inbound_id_vw = insert_inbound(
    type_val='vless',
    tag='vless-ws',
    tls_id=tls_id_ws,
    addrs=[{{"remark": "{REGION}-WS", "addr": "", "port": 8443}}],
    out_json={{
        "type": "vless",
        "tag": "vless-ws",
        "listen": "::",
        "listen_port": 8443,
        "sniff": True,
        "sniff_override_destination": True,
        "transport": {{
            "type": "ws",
            "path": "/vless-ws"
        }}
    }},
    options={{
        "clients": [
            {{
                "id": "{vless_ws_uuid}"
            }}
        ]
    }}
)

# 添加客户端
insert_client(
    name="{REGION}-WS",
    config={{"vless": [{{"id": "{vless_ws_uuid}"}}]}},
    inbounds_list=[inbound_id_vw],
    desc="{DESCRIPTION}"
)

print("✅ VLESS WS 添加成功")

# ============================================
# 3. Trojan WS + TLS (端口8444)
# ============================================
print("\\n添加 Trojan WS...")

# 创建入站
inbound_id_tw = insert_inbound(
    type_val='trojan',
    tag='trojan-ws',
    tls_id=tls_id_ws,
    addrs=[{{"remark": "{REGION}-Trojan", "addr": "", "port": 8444}}],
    out_json={{
        "type": "trojan",
        "tag": "trojan-ws",
        "listen": "::",
        "listen_port": 8444,
        "sniff": True,
        "sniff_override_destination": True,
        "transport": {{
            "type": "ws",
            "path": "/trojan-ws"
        }}
    }},
    options={{
        "clients": [
            {{
                "password": "{trojan_password}"
            }}
        ]
    }}
)

# 添加客户端
insert_client(
    name="{REGION}-Trojan",
    config={{"trojan": [{{"password": "{trojan_password}"}}]}},
    inbounds_list=[inbound_id_tw],
    desc="{DESCRIPTION}"
)

print("✅ Trojan WS 添加成功")

# ============================================
# 4. Hysteria2 (端口4433)
# ============================================
print("\\n添加 Hysteria2...")

# 创建入站
inbound_id_h2 = insert_inbound(
    type_val='hysteria2',
    tag='hysteria2',
    tls_id=tls_id_ws,
    addrs=[{{"remark": "{REGION}-HY2", "addr": "", "port": 4433}}],
    out_json={{
        "type": "hysteria2",
        "tag": "hysteria2",
        "listen": "::",
        "listen_port": 4433,
        "sniff": True,
        "sniff_override_destination": True,
        "masquerade": "https://www.apple.com"
    }},
    options={{
        "clients": [
            {{
                "password": "{hy2_password}"
            }}
        ]
    }}
)

# 添加客户端
insert_client(
    name="{REGION}-HY2",
    config={{"hysteria2": [{{"password": "{hy2_password}"}}]}},
    inbounds_list=[inbound_id_h2],
    desc="{DESCRIPTION}"
)

print("✅ Hysteria2 添加成功")

print("\\n" + "=" * 50)
print("✅ 所有入站规则添加完成！")
print("=" * 50)
'''
        
        # 上传脚本到VPS
        sftp = self.ssh.open_sftp()
        remote_path = '/tmp/sui_v141_config_v2.py'
        
        with sftp.file(remote_path, 'w') as f:
            f.write(script)
        
        sftp.close()
        print("✅ 脚本已上传到VPS")
        
        return remote_path
    
    def execute_config(self, remote_path):
        print("\n【步骤3】执行配置脚本...")
        
        out, err = self.run_cmd(f'python3 {remote_path}')
        print(out)
        if err:
            print(f"错误: {err}")
        
        self.run_cmd(f'rm -f {remote_path}')
    
    def restart_service(self):
        print("\n【步骤4】重启S-UI服务...")
        
        self.run_cmd('systemctl restart s-ui')
        time.sleep(5)
        
        out, _ = self.run_cmd('systemctl is-active s-ui')
        if out == 'active':
            print("✅ S-UI服务运行正常！")
        else:
            print(f"⚠️ 服务状态: {out}")
    
    def check_results(self):
        print("\n【步骤5】检查配置结果...")
        
        # 查看入站规则
        out, _ = self.run_cmd(f'sqlite3 {DB_PATH} "SELECT id, type, tag, tls_id FROM inbounds;"')
        print(f"入站规则:\n{out}")
        
        # 查看客户端
        out, _ = self.run_cmd(f'sqlite3 {DB_PATH} "SELECT id, name, `group` FROM clients;"')
        print(f"\n客户端:\n{out}")
        
        # 查看TLS配置
        out, _ = self.run_cmd(f'sqlite3 {DB_PATH} "SELECT id, name FROM tls;"')
        print(f"\nTLS配置:\n{out}")
        
        # 检查端口
        print("\n端口监听:")
        out, _ = self.run_cmd('ss -tlnp | grep -E "443|8443|8444|4433"')
        print(out)
    
    def backup_database(self):
        print("\n【步骤6】备份数据库...")
        
        sftp = self.ssh.open_sftp()
        local_path = f'd:\\Documents\\Syncdisk\\工作用\\job\\S-ui\\backup_{REGION}_{int(time.time())}.db'
        
        try:
            sftp.get(DB_PATH, local_path)
            print(f"✅ 数据库已备份到: {local_path}")
        except Exception as e:
            print(f"⚠️ 备份失败: {e}")
        
        sftp.close()
    
    def run(self):
        print("=" * 60)
        print("S-UI v1.4.1全自动配置脚本（正确版）")
        print("=" * 60)
        
        try:
            self.connect()
            self.generate_reality_keys()
            remote_path = self.create_config_script()
            self.execute_config(remote_path)
            self.restart_service()
            self.check_results()
            self.backup_database()
            
            print("\n" + "=" * 60)
            print("✅ 自动配置全部完成！")
            print("=" * 60)
            print(f"\n面板地址: http://{VPS_IP}:2095/app/")
            print(f"用户名: admin")
            print(f"密码: admin")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 配置失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.ssh:
                self.ssh.close()

if __name__ == "__main__":
    config = SUIAutoConfig()
    config.run()
