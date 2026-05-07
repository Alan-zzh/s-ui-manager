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
    
    # 1. 检查singbox日志（最近50行）
    cmd = 'tail -50 /var/log/singbox.log 2>/dev/null || journalctl -u singbox --no-pager -n 50'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("【singbox日志（最近50行）】")
    print(stdout.read().decode())
    
    # 2. 检查端口监听状态
    cmd = 'ss -tlnp | grep -E "443|8443|2053|2083"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【端口监听状态】")
    print(stdout.read().decode())
    
    # 3. 检查当前活跃连接
    cmd = 'ss -tnp | grep -E "443|8443|2053|2083" | head -20'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【活跃连接】")
    print(stdout.read().decode())
    
    # 4. 检查TCP重传率
    cmd = 'netstat -s | grep -i "retrans" | head -5'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【TCP重传率】")
    print(stdout.read().decode())
    
    # 5. 检查网络队列
    cmd = 'tc qdisc show'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【网络队列】")
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
