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
    
    # 1. 检查服务器负载
    cmd = 'uptime && echo "---" && free -m && echo "---" && top -bn1 | head -15'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("【服务器负载】")
    print(stdout.read().decode())
    
    # 2. 检查singbox进程CPU占用
    cmd = 'ps aux | grep sing-box | grep -v grep'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【singbox进程】")
    print(stdout.read().decode())
    
    # 3. 检查网络带宽占用
    cmd = 'iftop -t -s 5 2>/dev/null || nethogs 2>/dev/null || echo "无iftop/nethogs"'
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    print("\n【网络带宽】")
    print(stdout.read().decode())
    
    # 4. 检查iptables流量统计（看是否有异常流量）
    cmd = 'iptables -L -v -n | head -30'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【iptables流量统计】")
    print(stdout.read().decode())
    
    # 5. 检查磁盘IO
    cmd = 'iostat -x 1 2 2>/dev/null || echo "无iostat"'
    stdin, stdout, stderr = c.exec_command(cmd, timeout=5)
    print("\n【磁盘IO】")
    print(stdout.read().decode())
    
    # 6. 检查网络连接数
    cmd = 'ss -s && echo "---" && ss -tan | awk "{print \$1}" | sort | uniq -c'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【网络连接数】")
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
