from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== {srv['name']} 实时诊断 ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
        cmd = """
echo "=== 当前活跃连接 ==="
ss -tnp | grep sing-box | head -20
echo ""
echo "=== 连接统计 ==="
ss -s | grep -E "TCP|ESTAB"
echo ""
echo "=== 各协议连接数 ==="
echo "443端口(Reality+HY2): $(ss -tnp | grep ':443' | wc -l)"
echo "8443端口(VLESS-WS): $(ss -tnp | grep ':8443' | wc -l)"
echo "2053端口(VLESS-Upgrade): $(ss -tnp | grep ':2053' | wc -l)"
echo "2083端口(Trojan-WS): $(ss -tnp | grep ':2083' | wc -l)"
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = 'grep -i "error\|warn\|fail" /var/log/singbox.log 2>/dev/null | tail -30'
        out, err = run_command(c, cmd)
        print(f"\n【错误日志（最近30条）】")
        print(out if out else "无错误日志")

        cmd = """
echo "=== TCP重传统计 ==="
netstat -s | grep -E "retransmit|retrans|timeout" | head -10
echo ""
echo "=== 网络接口实时统计 ==="
cat /sys/class/net/ens5/statistics/rx_dropped
cat /sys/class/net/ens5/statistics/tx_dropped
cat /sys/class/net/ens5/statistics/rx_errors
cat /sys/class/net/ens5/statistics/tx_errors
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
echo "=== singbox进程资源占用 ==="
ps aux | grep sing-box | grep -v grep
echo ""
echo "=== 系统负载 ==="
uptime
echo ""
echo "=== 内存使用 ==="
free -m
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
echo "=== TIME-WAIT连接数 ==="
ss -tan | grep TIME-WAIT | wc -l
echo ""
echo "=== CLOSE-WAIT连接数 ==="
ss -tan | grep CLOSE-WAIT | wc -l
echo ""
echo "=== 孤儿连接数 ==="
ss -tan | grep -v ESTAB | grep -v LISTEN | grep -v TIME-WAIT | wc -l
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
echo "=== config.json检查 ==="
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

for inbound in config.get('inbounds', []):
    tag = inbound.get('tag', '')
    print(f"\nInbound: {tag}")
    print(f"  Type: {inbound.get('type')}")
    print(f"  Port: {inbound.get('listen_port')}")

    if 'sniff' in inbound:
        print(f"  Sniff: {inbound['sniff']}")
    else:
        print(f"  Sniff: 未启用")

    if 'tls' in inbound:
        tls = inbound['tls']
        if 'reality' in tls:
            print(f"  Reality: 已启用")
        if 'alpn' in tls:
            print(f"  ALPN: {tls['alpn']}")

    if 'transport' in inbound:
        transport = inbound['transport']
        print(f"  Transport: {transport.get('type')}")
        if 'headers' in transport:
            print(f"  Headers: {transport['headers']}")

route = config.get('route', {})
rules = route.get('rules', [])
print(f"\n路由规则数量: {len(rules)}")
print(f"Final: {route.get('final', 'N/A')}")
EOF
"""
        out, err = run_command(c, cmd)
        print(out)

print("\n全部完成")
