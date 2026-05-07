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
    
    # 1. 检查MTU设置
    cmd = 'ip link show | grep mtu'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("【MTU设置】")
    print(stdout.read().decode())
    
    # 2. 检查TCP拥塞控制算法
    cmd = 'sysctl net.ipv4.tcp_congestion_control && sysctl net.core.default_qdisc'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【TCP拥塞控制】")
    print(stdout.read().decode())
    
    # 3. 检查TCP缓冲区
    cmd = 'sysctl net.ipv4.tcp_rmem && sysctl net.ipv4.tcp_wmem && sysctl net.core.rmem_max && sysctl net.core.wmem_max'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【TCP缓冲区】")
    print(stdout.read().decode())
    
    # 4. 检查singbox配置中的MTU
    cmd = 'grep -i mtu /root/singbox-eps-node/config.json || echo "无MTU设置"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【singbox MTU】")
    print(stdout.read().decode())
    
    # 5. 检查是否有BBR加速
    cmd = 'sysctl net.ipv4.tcp_congestion_control | grep bbr || echo "未启用BBR"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【BBR状态】")
    print(stdout.read().decode())
    
    # 6. 检查网络丢包
    cmd = 'ping -c 10 8.8.8.8 2>&1 | tail -3'
    stdin, stdout, stderr = c.exec_command(cmd, timeout=15)
    print("\n【到8.8.8.8的延迟】")
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
