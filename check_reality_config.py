import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    print(f"\n{'='*60}")
    print(f"=== {name} ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
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
        out, err = run_command(c, cmd)
        print(out)

        cmd = 'grep REALITY /root/singbox-eps-node/.env'
        out, err = run_command(c, cmd)
        print(f"\n.env配置: {out.strip()}")

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality"'
        out, err = run_command(c, cmd)
        print(f"\n订阅链接: {out.strip()[:200]}")

print("\n全部完成")
