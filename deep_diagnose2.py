import paramiko, time

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== {name} 深度诊断 ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查当前活跃连接的延迟分布
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 2. 检查singbox日志中的连接处理时间
    cmd = """
echo "=== 最近50条连接处理日志 ==="
grep "inbound connection" /var/log/singbox.log | tail -50 | while read line; do
    # 提取连接ID和时间
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 3. 检查DNS解析延迟
    cmd = """
echo "=== DNS解析测试 ==="
time dig @8.8.8.8 www.google.com +short 2>&1 | tail -3
echo ""
time dig @223.5.5.5 www.baidu.com +short 2>&1 | tail -3
"""
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    print(stdout.read().decode())
    
    # 4. 检查网络队列和缓冲
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 5. 检查是否有连接被限速或丢弃
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 6. 检查singbox配置中的sniff和路由
    cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

# 检查inbounds的sniff配置
for inbound in config.get('inbounds', []):
    tag = inbound.get('tag', '')
    sniff = inbound.get('sniff', False)
    sniff_override = inbound.get('sniff_override_destination', False)
    print(f"{tag}: sniff={sniff}, sniff_override={sniff_override}")

# 检查DNS配置
dns = config.get('dns', {})
print(f"\nDNS servers: {dns.get('servers', [])}")
print(f"DNS final: {dns.get('final', 'N/A')}")

# 检查route规则
route = config.get('route', {})
print(f"\nRoute rules: {len(route.get('rules', []))}")
print(f"Route final: {route.get('final', 'N/A')}")

# 检查outbounds
for outbound in config.get('outbounds', []):
    tag = outbound.get('tag', '')
    otype = outbound.get('type', '')
    print(f"\nOutbound: {tag} ({otype})")
    if 'domain_strategy' in outbound:
        print(f"  domain_strategy: {outbound['domain_strategy']}")
EOF
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
