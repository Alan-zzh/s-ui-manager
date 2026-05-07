import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== {name} 实时诊断 ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 实时连接数和状态
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 2. 实时singbox日志（最近30行错误）
    cmd = 'grep -i "error\|warn\|fail" /var/log/singbox.log 2>/dev/null | tail -30'
    stdin, stdout, stderr = c.exec_command(cmd)
    logs = stdout.read().decode()
    print(f"\n【错误日志（最近30条）】")
    print(logs if logs else "无错误日志")
    
    # 3. TCP重传统计
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 4. CPU和内存实时占用
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 5. 检查是否有连接超时
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 6. 检查singbox配置问题
    cmd = """
echo "=== config.json检查 ==="
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

# 检查inbounds配置
for inbound in config.get('inbounds', []):
    tag = inbound.get('tag', '')
    print(f"\nInbound: {tag}")
    print(f"  Type: {inbound.get('type')}")
    print(f"  Port: {inbound.get('listen_port')}")
    
    # 检查是否有sniff配置
    if 'sniff' in inbound:
        print(f"  Sniff: {inbound['sniff']}")
    else:
        print(f"  Sniff: 未启用")
    
    # 检查TLS配置
    if 'tls' in inbound:
        tls = inbound['tls']
        if 'reality' in tls:
            print(f"  Reality: 已启用")
        if 'alpn' in tls:
            print(f"  ALPN: {tls['alpn']}")
    
    # 检查transport配置
    if 'transport' in inbound:
        transport = inbound['transport']
        print(f"  Transport: {transport.get('type')}")
        if 'headers' in transport:
            print(f"  Headers: {transport['headers']}")

# 检查route规则
route = config.get('route', {})
rules = route.get('rules', [])
print(f"\n路由规则数量: {len(rules)}")
print(f"Final: {route.get('final', 'N/A')}")
EOF
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
