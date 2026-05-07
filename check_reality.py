import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    print(f"\n{'='*50}")
    print(f"=== {name} ===")
    print(f"{'='*50}")

    with ssh_connect(srv) as c:
        cmd = 'grep REALITY /root/singbox-eps-node/.env'
        out, err = run_command(c, cmd)
        print("【.env中的REALITY配置】")
        print(out)

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
        out, err = run_command(c, cmd)
        print("\n【config.json中的REALITY配置】")
        print(out)

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "vless.*reality" || echo "无Reality节点"'
        out, err = run_command(c, cmd)
        print("\n【订阅中的VLESS-Reality链接】")
        print(out)

print("\n全部完成")
