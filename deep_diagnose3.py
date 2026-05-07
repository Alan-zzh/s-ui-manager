from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== {srv['name']} ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
        cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

print("=== Inbounds详细配置 ===")
for inbound in config.get('inbounds', []):
    tag = inbound.get('tag', '')
    print(f"\n--- {tag} ---")
    print(f"Type: {inbound.get('type')}")
    print(f"Port: {inbound.get('listen_port')}")
    print(f"Sniff: {inbound.get('sniff', '未设置')}")
    print(f"Sniff Override: {inbound.get('sniff_override_destination', '未设置')}")
    print(f"Domain Strategy: {inbound.get('domain_strategy', '未设置')}")

    if 'tls' in inbound:
        tls = inbound['tls']
        print(f"TLS enabled: {tls.get('enabled')}")
        print(f"TLS server_name: {tls.get('server_name')}")
        if 'reality' in tls:
            print(f"Reality enabled: True")
            print(f"Reality short_id: {tls['reality'].get('short_id')}")
        if 'alpn' in tls:
            print(f"ALPN: {tls['alpn']}")

    if 'transport' in inbound:
        t = inbound['transport']
        print(f"Transport type: {t.get('type')}")
        if 'headers' in t:
            print(f"Headers: {t['headers']}")

print("\n=== Route规则 ===")
route = config.get('route', {})
rules = route.get('rules', [])
for i, rule in enumerate(rules):
    print(f"规则{i+1}: {json.dumps(rule)}")
print(f"Final: {route.get('final')}")

print("\n=== DNS配置 ===")
dns = config.get('dns', {})
print(json.dumps(dns, indent=2))

print("\n=== Outbounds ===")
for outbound in config.get('outbounds', []):
    print(f"{outbound.get('tag')}: {outbound.get('type')}")
    if 'domain_strategy' in outbound:
        print(f"  domain_strategy: {outbound['domain_strategy']}")
EOF
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
echo "=== 当前TCP连接RTT ==="
ss -tnpi | grep -E "175.10.215.20|172.26" | head -10
echo ""
echo "=== 连接数统计 ==="
ss -tnp | grep sing-box | wc -l
echo "个singbox连接"
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
echo "=== 最近20条错误连接的处理时间 ==="
grep "processed invalid connection" /var/log/singbox.log | tail -20 | grep -oP '\[\d+ \d+ms\]' | head -20
echo ""
echo "=== 最近20条成功连接的处理时间 ==="
grep "inbound connection" /var/log/singbox.log | tail -20 | grep -oP '\[\d+ \d+ms\]' | head -20
"""
        out, err = run_command(c, cmd)
        print(out)

print("\n全部完成")
