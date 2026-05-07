import paramiko, json

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== {name} 配置合理性检查 ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查config.json完整性和合理性
    cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json, os

with open('config.json', 'r') as f:
    config = json.load(f)

issues = []

# 检查inbounds
print("=== Inbounds检查 ===")
inbounds = config.get('inbounds', [])
print(f"入站数量: {len(inbounds)}")

for inbound in inbounds:
    tag = inbound.get('tag', 'unknown')
    port = inbound.get('listen_port', 0)
    
    # 检查端口冲突
    ports = [i.get('listen_port') for i in inbounds if i != inbound]
    if port in ports:
        issues.append(f"{tag}: 端口 {port} 冲突")
    
    # 检查TLS配置
    if 'tls' in inbound:
        tls = inbound['tls']
        if tls.get('enabled') and 'certificate_path' in tls:
            cert_path = tls['certificate_path']
            if not os.path.exists(cert_path):
                issues.append(f"{tag}: 证书不存在 {cert_path}")
            else:
                print(f"✅ {tag}: 证书存在")
        
        # 检查REALITY
        if 'reality' in tls:
            reality = tls['reality']
            if not reality.get('private_key'):
                issues.append(f"{tag}: REALITY私钥为空")
            if not reality.get('short_id'):
                issues.append(f"{tag}: REALITY short_id为空")
            if reality.get('enabled') and not reality.get('handshake', {}).get('server'):
                issues.append(f"{tag}: REALITY握手服务器未配置")
    
    # 检查用户凭据
    users = inbound.get('users', [])
    for user in users:
        if 'uuid' in user and not user['uuid']:
            issues.append(f"{tag}: UUID为空")
        if 'password' in user and not user['password']:
            issues.append(f"{tag}: 密码为空")

# 检查outbounds
print("\n=== Outbounds检查 ===")
outbounds = config.get('outbounds', [])
print(f"出站数量: {len(outbounds)}")

tags = [o.get('tag') for o in outbounds]
if 'direct' not in tags:
    issues.append("缺少direct出站")
if 'block' not in tags:
    issues.append("缺少block出站")

# 检查route规则
print("\n=== Route规则检查 ===")
route = config.get('route', {})
rules = route.get('rules', [])
print(f"规则数量: {len(rules)}")

final = route.get('final', '')
if final not in tags:
    issues.append(f"final出站 '{final}' 不存在于outbounds")

# 检查DNS
print("\n=== DNS配置检查 ===")
dns = config.get('dns', {})
servers = dns.get('servers', [])
print(f"DNS服务器数量: {len(servers)}")

for s in servers:
    if 'address' in s:
        print(f"  {s['tag']}: {s['address']}")

# 检查log配置
print("\n=== Log配置检查 ===")
log = config.get('log', {})
if log.get('disabled'):
    print("⚠️ 日志已禁用")
else:
    print(f"✅ 日志级别: {log.get('level', '未设置')}")
    print(f"✅ 日志输出: {log.get('output', '未设置')}")

# 汇总
print(f"\n=== 问题汇总 ===")
if issues:
    for issue in issues:
        print(f"❌ {issue}")
else:
    print("✅ 所有配置检查通过")

EOF
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 2. 检查.env配置
    print(f"\n=== .env配置检查 ===")
    cmd = """
cd /root/singbox-eps-node
echo "--- 关键变量 ---"
for key in SERVER_IP CF_DOMAIN VLESS_UUID VLESS_WS_UUID TROJAN_PASSWORD HYSTERIA2_PASSWORD REALITY_PRIVATE_KEY REALITY_PUBLIC_KEY; do
    value=$(grep "^$key=" .env 2>/dev/null | cut -d= -f2-)
    if [ -z "$value" ]; then
        echo "❌ $key: 未设置"
    else
        echo "✅ $key: 已设置 (${#value}字符)"
    fi
done
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 3. 检查证书
    print(f"\n=== 证书检查 ===")
    cmd = """
cd /root/singbox-eps-node/cert 2>/dev/null || cd /root/singbox-eps-node
for f in fullchain.pem cert.pem key.pem; do
    if [ -f "$f" ]; then
        echo "✅ $f: 存在 ($(stat -c%s "$f" 2>/dev/null || stat -f%z "$f") bytes)"
    else
        echo "❌ $f: 不存在"
    fi
done
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 4. 检查singbox语法
    print(f"\n=== singbox配置语法检查 ===")
    cmd = '/usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    check_out = stdout.read().decode().strip()
    if 'valid' in check_out.lower() or check_out == '':
        print("✅ 配置语法正确")
    else:
        print(f"❌ 配置错误: {check_out}")
    
    c.close()
    print(f"\n{'='*60}")
    print(f"=== {name} 配置检查完成 ===")
    print(f"{'='*60}")

print("\n全部检查完成")
