import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== {name} ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查config.json中的REALITY配置
    cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

for inbound in config.get('inbounds', []):
    if 'reality' in inbound.get('tls', {}):
        print(f"=== {inbound['tag']} ===")
        print(f"Port: {inbound['listen_port']}")
        tls = inbound['tls']
        reality = tls['reality']
        print(f"server_name: {tls.get('server_name')}")
        print(f"private_key: {reality.get('private_key')[:20]}...")
        print(f"short_id: {reality.get('short_id')}")
        print(f"handshake: {reality.get('handshake')}")
EOF
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 2. 检查.env中的REALITY配置
    cmd = 'grep REALITY /root/singbox-eps-node/.env'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n.env配置: {stdout.read().decode().strip()}")
    
    # 3. 检查当前订阅中的REALITY链接
    code = 'JP' if name == '日本' else 'SG'
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n订阅链接: {stdout.read().decode().strip()[:200]}")
    
    c.close()

print("\n全部完成")
