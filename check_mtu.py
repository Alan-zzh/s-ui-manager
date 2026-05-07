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
    
    # 1. 检查MTU和分片
    cmd = """
echo "=== MTU ==="
ip link show | grep mtu
echo ""
echo "=== UDP缓冲区 ==="
sysctl net.core.rmem_max
sysctl net.core.wmem_max
sysctl net.core.netdev_max_backlog
echo ""
echo "=== 连接跟踪 ==="
sysctl net.netfilter.nf_conntrack_max
sysctl net.netfilter.nf_conntrack_tcp_timeout_established
echo ""
echo "=== 网络接口统计 ==="
ip -s link show ens5 | head -20
echo ""
echo "=== 丢包统计 ==="
netstat -s | grep -i "drop\|loss\|error" | head -10
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    # 2. 检查是否有流量限制
    cmd = 'tc class show && echo "---" && tc filter show'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【流量限制】")
    print(stdout.read().decode())
    
    # 3. 检查singbox版本
    cmd = '/usr/local/bin/sing-box version'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【singbox版本】")
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
