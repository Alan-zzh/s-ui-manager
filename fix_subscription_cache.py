from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== 修复 {srv['name']} 订阅缓存 ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
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
        out, err = run_command(c, cmd)
        print(f"env公钥: {out.strip()}")

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
        out, err = run_command(c, cmd)
        print(f"config私钥: {out.strip()}")

        print("\n重启订阅服务...")
        cmd = 'systemctl restart singbox-sub && sleep 2 && systemctl is-active singbox-sub'
        out, err = run_command(c, cmd)
        print(f"状态: {out.strip()}")

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality" | head -1'
        out, err = run_command(c, cmd)
        link = out.strip()
        if link and 'pbk=' in link:
            pbk = link.split('pbk=')[1].split('&')[0]
            print(f"\n新订阅公钥: {pbk}")

print("\n完成")
