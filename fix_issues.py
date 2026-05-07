import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== 修复 {name} ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 启动 singbox-cdn（日本）
    if name == '日本':
        print("\n1. 启动 singbox-cdn...")
        cmd = 'systemctl start singbox-cdn && echo "OK" || echo "FAIL"'
        stdin, stdout, stderr = c.exec_command(cmd)
        print(f"结果: {stdout.read().decode().strip()}")
        
        cmd = 'systemctl is-active singbox-cdn'
        stdin, stdout, stderr = c.exec_command(cmd)
        print(f"状态: {stdout.read().decode().strip()}")
    
    # 2. 检查CDN数据库
    print("\n2. 检查CDN数据库...")
    cmd = """
cd /root/singbox-eps-node
if [ ! -d data ]; then mkdir -p data; fi
python3 << 'EOF'
import sqlite3, os
db_path = os.path.join('data', 'cdn_ips.db')
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cdn_ips (
        ip TEXT PRIMARY KEY,
        latency REAL,
        source TEXT,
        status TEXT DEFAULT 'active',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
    print("数据库已创建")
else:
    print("数据库已存在")
EOF
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode().strip())
    
    # 3. 清理日志（避免日志过大）
    print("\n3. 清理旧日志...")
    cmd = 'echo "" > /var/log/singbox.log && echo "OK" || echo "FAIL"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"结果: {stdout.read().decode().strip()}")
    
    # 4. 检查singbox配置中的REALITY
    print("\n4. 检查REALITY配置...")
    cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

for inbound in config.get('inbounds', []):
    if inbound.get('tag') == 'vless-reality':
        tls = inbound.get('tls', {})
        reality = tls.get('reality', {})
        print(f"Tag: {inbound['tag']}")
        print(f"Port: {inbound['listen_port']}")
        print(f"server_name: {tls.get('server_name')}")
        print(f"private_key: {reality.get('private_key', '')[:20]}...")
        print(f"short_id: {reality.get('short_id')}")
        print(f"handshake_server: {reality.get('handshake', {}).get('server')}")
EOF
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 5. 检查.env中的REALITY配置
    print("\n5. 检查.env配置...")
    cmd = 'grep REALITY /root/singbox-eps-node/.env'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode().strip())
    
    # 6. 重启singbox（确保配置生效）
    print("\n6. 重启singbox...")
    cmd = 'systemctl restart singbox && sleep 2 && systemctl is-active singbox'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"状态: {stdout.read().decode().strip()}")
    
    c.close()
    print(f"\n{'='*60}")
    print(f"=== {name} 修复完成 ===")
    print(f"{'='*60}")

print("\n全部修复完成")
