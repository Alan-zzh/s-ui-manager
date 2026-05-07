import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    print(f"\n{'='*60}")
    print(f"=== {name} 配置合理性检查 ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
        cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json, os

with open('config.json', 'r') as f:
    config = json.load(f)

issues = []

print("=== Inbounds检查 ===")
inbounds = config.get('inbounds', [])
print(f"入站数量: {len(inbounds)}")

for inbound in inbounds:
    tag = inbound.get('tag', 'unknown')
    port = inbound.get('listen_port', 0)

    ports = [i.get('listen_port') for i in inbounds if i != inbound]
    if port in ports:
        issues.append(f"{tag}: 端口 {port} 冲突")

    if 'tls' in inbound:
        tls = inbound['tls']
        if tls.get('enabled') and 'certificate_path' in tls:
            cert_path = tls['certificate_path']
            if not os.path.exists(cert_path):
                issues.append(f"{tag}: 证书不存在 {cert_path}")
            else:
                print(f"✅ {tag}: 证书存在")

        if 'reality' in tls:
            reality = tls['reality']
            if not reality.get('private_key'):
                issues.append(f"{tag}: REALITY私钥为空")
            if not reality.get('short_id'):
                issues.append(f"{tag}: REALITY short_id为空")
            if reality.get('enabled') and not reality.get('handshake', {}).get('server'):
                issues.append(f"{tag}: REALITY握手服务器未配置")

    users = inbound.get('users', [])
    for user in users:
        if 'uuid' in user and not user['uuid']:
            issues.append(f"{tag}: UUID为空")
        if 'password' in user and not user['password']:
            issues.append(f"{tag}: 密码为空")

print("\n=== Outbounds检查 ===")
outbounds = config.get('outbounds', [])
print(f"出站数量: {len(outbounds)}")

tags = [o.get('tag') for o in outbounds]
if 'direct' not in tags:
    issues.append("缺少direct出站")
if 'block' not in tags:
    issues.append("缺少block出站")

print("\n=== Route规则检查 ===")
route = config.get('route', {})
rules = route.get('rules', [])
print(f"规则数量: {len(rules)}")

final = route.get('final', '')
if final not in tags:
    issues.append(f"final出站 '{final}' 不存在于outbounds")

print("\n=== DNS配置检查 ===")
dns = config.get('dns', {})
servers = dns.get('servers', [])
print(f"DNS服务器数量: {len(servers)}")

for s in servers:
    if 'address' in s:
        print(f"  {s['tag']}: {s['address']}")

print("\n=== Log配置检查 ===")
log = config.get('log', {})
if log.get('disabled'):
    print("⚠️ 日志已禁用")
else:
    print(f"✅ 日志级别: {log.get('level', '未设置')}")
    print(f"✅ 日志输出: {log.get('output', '未设置')}")

print(f"\n=== 问题汇总 ===")
if issues:
    for issue in issues:
        print(f"❌ {issue}")
else:
    print("✅ 所有配置检查通过")

EOF
"""
        out, err = run_command(c, cmd)
        print(out)

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
        out, err = run_command(c, cmd)
        print(out)

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
        out, err = run_command(c, cmd)
        print(out)

        print(f"\n=== singbox配置语法检查 ===")
        cmd = '/usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1'
        out, err = run_command(c, cmd)
        check_out = out.strip()
        if 'valid' in check_out.lower() or check_out == '':
            print("✅ 配置语法正确")
        else:
            print(f"❌ 配置错误: {check_out}")

    print(f"\n{'='*60}")
    print(f"=== {name} 配置检查完成 ===")
    print(f"{'='*60}")

print("\n全部检查完成")
