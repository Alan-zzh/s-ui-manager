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
    
    # 1. 检查config.json中Reality和Hysteria2的配置
    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

# 检查inbounds
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print("【直连协议配置】")
    print(stdout.read().decode())
    
    # 2. 检查outbounds配置
    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

# 检查outbounds
for outbound in config.get('outbounds', []):
    tag = outbound.get('tag', '')
    if 'direct' in tag.lower() or 'block' in tag.lower():
        print(f"\nOutbound: {tag}")
        print(f"  Type: {outbound.get('type')}")
        if 'domain_strategy' in outbound:
            print(f"  Domain Strategy: {outbound.get('domain_strategy')}")
EOF"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【出站配置】")
    print(stdout.read().decode())
    
    # 3. 检查路由规则
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【路由规则】")
    print(stdout.read().decode())
    
    # 4. 检查实验性配置
    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

exp = config.get('experimental', {})
print(f"实验性配置: {json.dumps(exp, indent=2)}")
EOF"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【实验性配置】")
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
