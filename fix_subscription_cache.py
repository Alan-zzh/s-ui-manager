import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== 修复 {name} 订阅缓存 ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查订阅服务代码
    cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import os
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_vars[key] = value

print(f"env公钥: {env_vars.get('REALITY_PUBLIC_KEY', '未设置')}")
EOF
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"env公钥: {stdout.read().decode().strip()}")
    
    # 2. 检查config.json中的公钥
    cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)
for inbound in config.get('inbounds', []):
    if 'reality' in inbound.get('tls', {}):
        print(f"config公钥: {inbound['tls']['reality']['private_key'][:20]}...")
EOF
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"config私钥: {stdout.read().decode().strip()}")
    
    # 3. 重启订阅服务
    print("\n重启订阅服务...")
    cmd = 'systemctl restart singbox-sub && sleep 2 && systemctl is-active singbox-sub'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"状态: {stdout.read().decode().strip()}")
    
    # 4. 再次获取订阅
    code = 'JP' if name == '日本' else 'SG'
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality" | head -1'
    stdin, stdout, stderr = c.exec_command(cmd)
    link = stdout.read().decode().strip()
    if link and 'pbk=' in link:
        pbk = link.split('pbk=')[1].split('&')[0]
        print(f"\n新订阅公钥: {pbk}")
    
    c.close()

print("\n完成")
