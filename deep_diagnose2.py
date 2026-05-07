import time
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== {srv['name']} 深度诊断 ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
        cmd = """
echo "=== TCP连接延迟分布 ==="
ss -tnpi | grep sing-box | head -20
echo ""
echo "=== 连接状态分布 ==="
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn
echo ""
echo "=== RTT统计 ==="
ss -tnpi | grep -oP 'rtt:\K[0-9]+' | awk '{sum+=$1; count++; if($1>max) max=$1; if(min=="" || $1<min) min=$1} END {if(count>0) printf "平均RTT: %.1fms, 最小: %sms, 最大: %sms, 连接数: %d\n", sum/count, min, max, count; else print "无连接"}'
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
echo "=== 最近50条连接处理日志 ==="
grep "inbound connection" /var/log/singbox.log | tail -50 | while read line; do
    echo "$line"
done
echo ""
echo "=== 错误连接统计 ==="
grep "processed invalid connection" /var/log/singbox.log | tail -100 | wc -l
echo "条无效连接（最近100条）"
echo ""
echo "=== 成功连接统计 ==="
grep "inbound connection" /var/log/singbox.log | tail -100 | wc -l
echo "条入站连接（最近100条）"
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
echo "=== DNS解析测试 ==="
time dig @8.8.8.8 www.google.com +short 2>&1 | tail -3
echo ""
time dig @223.5.5.5 www.baidu.com +short 2>&1 | tail -3
"""
        out, err = run_command(c, cmd, timeout=10)
        print(out)

        cmd = """
echo "=== 网络队列深度 ==="
tc -s qdisc show dev ens5
echo ""
echo "=== TCP缓冲区使用 ==="
cat /proc/net/sockstat
echo ""
echo "=== 连接跟踪表使用率 ==="
conntrack -C 2>/dev/null || cat /proc/sys/net/netfilter/nf_conntrack_count
echo "/"
cat /proc/sys/net/netfilter/nf_conntrack_max
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
echo "=== iptables丢弃统计 ==="
iptables -L -v -n | grep -E "DROP|REJECT" | head -10
echo ""
echo "=== 网络接口丢包 ==="
cat /sys/class/net/ens5/statistics/rx_dropped
cat /sys/class/net/ens5/statistics/tx_dropped
cat /sys/class/net/ens5/statistics/rx_missed
echo ""
echo "=== TCP连接队列溢出 ==="
netstat -s | grep -i "listen\|overflow\|drop" | head -10
"""
        out, err = run_command(c, cmd)
        print(out)

        cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

for inbound in config.get('inbounds', []):
    tag = inbound.get('tag', '')
    sniff = inbound.get('sniff', False)
    sniff_override = inbound.get('sniff_override_destination', False)
    print(f"{tag}: sniff={sniff}, sniff_override={sniff_override}")

dns = config.get('dns', {})
print(f"\nDNS servers: {dns.get('servers', [])}")
print(f"DNS final: {dns.get('final', 'N/A')}")

route = config.get('route', {})
print(f"\nRoute rules: {len(route.get('rules', []))}")
print(f"Route final: {route.get('final', 'N/A')}")

for outbound in config.get('outbounds', []):
    tag = outbound.get('tag', '')
    otype = outbound.get('type', '')
    print(f"\nOutbound: {tag} ({otype})")
    if 'domain_strategy' in outbound:
        print(f"  domain_strategy: {outbound['domain_strategy']}")
EOF
"""
        out, err = run_command(c, cmd)
        print(out)

print("\n全部完成")
