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
    
    # 1. 完整config.json分析
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
    
    # 检查TLS
    if 'tls' in inbound:
        tls = inbound['tls']
        print(f"TLS enabled: {tls.get('enabled')}")
        print(f"TLS server_name: {tls.get('server_name')}")
        if 'reality' in tls:
            print(f"Reality enabled: True")
            print(f"Reality short_id: {tls['reality'].get('short_id')}")
        if 'alpn' in tls:
            print(f"ALPN: {tls['alpn']}")
    
    # 检查transport
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 2. 检查当前连接的RTT
    cmd = """
echo "=== 当前TCP连接RTT ==="
ss -tnpi | grep -E "175.10.215.20|172.26" | head -10
echo ""
echo "=== 连接数统计 ==="
ss -tnp | grep sing-box | wc -l
echo "个singbox连接"
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 3. 检查singbox日志中的连接处理时间
    cmd = """
echo "=== 最近20条错误连接的处理时间 ==="
grep "processed invalid connection" /var/log/singbox.log | tail -20 | grep -oP '\[\d+ \d+ms\]' | head -20
echo ""
echo "=== 最近20条成功连接的处理时间 ==="
grep "inbound connection" /var/log/singbox.log | tail -20 | grep -oP '\[\d+ \d+ms\]' | head -20
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
