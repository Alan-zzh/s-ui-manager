import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*50}")
    print(f"=== {name} ===")
    print(f"{'='*50}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查.env中的REALITY密钥
    cmd = 'grep REALITY /root/singbox-eps-node/.env'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("【.env中的REALITY配置】")
    print(stdout.read().decode())
    
    # 2. 检查config.json中的REALITY配置
    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

for inbound in config.get('inbounds', []):
    if inbound.get('type') == 'vless' and 'reality' in inbound.get('tls', {}):
        reality = inbound['tls']['reality']
        print(f"Private Key: {reality.get('private_key', 'N/A')}")
        print(f"Short IDs: {reality.get('short_id', 'N/A')}")
        print(f"Server Name: {inbound['tls'].get('server_name', 'N/A')}")
EOF"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【config.json中的REALITY配置】")
    print(stdout.read().decode())
    
    # 3. 检查订阅中的VLESS-Reality链接
    code = 'JP' if name == '日本' else 'SG'
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "vless.*reality" || echo "无Reality节点"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【订阅中的VLESS-Reality链接】")
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
