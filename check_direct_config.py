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
        cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

for inbound in config.get('inbounds', []):
    tag = inbound.get('tag', '')
    if 'Reality' in tag or 'Hysteria' in tag or 'reality' in tag or 'hysteria' in tag:
        print(f"\nInbound: {tag}")
        print(f"  Type: {inbound.get('type')}")
        print(f"  Listen: {inbound.get('listen')}:{inbound.get('listen_port')}")
        if 'tls' in inbound:
            print(f"  TLS: {json.dumps(inbound['tls'], indent=4)}")
        if 'transport' in inbound:
            print(f"  Transport: {json.dumps(inbound['transport'], indent=4)}")
        if 'sniff' in inbound:
            print(f"  Sniff: {inbound.get('sniff')}")
        if 'sniff_override_destination' in inbound:
            print(f"  Sniff Override: {inbound.get('sniff_override_destination')}")
        if 'domain_strategy' in inbound:
            print(f"  Domain Strategy: {inbound.get('domain_strategy')}")
EOF"""
        out, err = run_command(c, cmd)
        print("【直连协议配置】")
        print(out)

        cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

for outbound in config.get('outbounds', []):
    tag = outbound.get('tag', '')
    if 'direct' in tag.lower() or 'block' in tag.lower():
        print(f"\nOutbound: {tag}")
        print(f"  Type: {outbound.get('type')}")
        if 'domain_strategy' in outbound:
            print(f"  Domain Strategy: {outbound.get('domain_strategy')}")
EOF"""
        out, err = run_command(c, cmd)
        print("\n【出站配置】")
        print(out)

        cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

route = config.get('route', {})
rules = route.get('rules', [])
print(f"路由规则数量: {len(rules)}")
for i, rule in enumerate(rules):
    print(f"\n规则{i+1}:")
    print(f"  Type: {rule.get('type', 'N/A')}")
    if 'inbound' in rule:
        print(f"  Inbound: {rule['inbound']}")
    if 'domain' in rule:
        print(f"  Domain: {rule['domain'][:5]}...")
    if 'outbound' in rule:
        print(f"  Outbound: {rule['outbound']}")
EOF"""
        out, err = run_command(c, cmd)
        print("\n【路由规则】")
        print(out)

        cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

exp = config.get('experimental', {})
print(f"实验性配置: {json.dumps(exp, indent=2)}")
EOF"""
        out, err = run_command(c, cmd)
        print("\n【实验性配置】")
        print(out)

print("\n全部完成")
