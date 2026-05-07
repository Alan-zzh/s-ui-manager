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
    
    # 1. 修改MTU为1500
    cmd = 'ip link set dev ens5 mtu 1500 && ip link show ens5 | grep mtu'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"MTU修改: {stdout.read().decode().strip()}")
    
    # 2. 优化UDP缓冲区（Hysteria2需要）
    cmd = """
sysctl -w net.core.rmem_max=25000000
sysctl -w net.core.wmem_max=25000000
sysctl -w net.core.netdev_max_backlog=65536
echo "UDP缓冲区已优化"
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"UDP优化: {stdout.read().decode().strip()}")
    
    # 3. 重启singbox
    cmd = 'systemctl restart singbox && echo "OK" || echo "FAIL"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"重启singbox: {stdout.read().decode().strip()}")
    
    # 4. 验证
    cmd = 'ip link show ens5 | grep mtu'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"当前MTU: {stdout.read().decode().strip()}")
    
    c.close()

print("\n全部完成")
