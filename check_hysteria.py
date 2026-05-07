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
    
    # 1. 检查Hysteria2日志
    cmd = 'grep -i hysteria /var/log/singbox.log 2>/dev/null | tail -20 || echo "无Hysteria日志"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("【Hysteria2日志】")
    print(stdout.read().decode())
    
    # 2. 检查Hysteria2端口连接
    cmd = 'ss -tnp | grep ":443" | head -10'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【443端口连接】")
    print(stdout.read().decode())
    
    # 3. 检查UDP连接（Hysteria2使用UDP）
    cmd = 'ss -unp | grep ":443" | head -10'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【443端口UDP连接】")
    print(stdout.read().decode())
    
    # 4. 检查iptables UDP规则
    cmd = 'iptables -L -v -n | grep -E "udp|UDP"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【iptables UDP规则】")
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
