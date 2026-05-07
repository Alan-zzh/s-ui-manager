import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n=== {name} ===")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 创建网络优化脚本
    script = """#!/bin/bash
# 网络优化配置（开机自动执行）
# MTU设置
ip link set dev ens5 mtu 1500

# UDP缓冲区优化（Hysteria2需要）
sysctl -w net.core.rmem_max=25000000
sysctl -w net.core.wmem_max=25000000
sysctl -w net.core.netdev_max_backlog=65536

echo "网络优化已应用"
"""
    
    cmd = f'cat > /etc/network-optimization.sh << \'EOF\'\n{script}\nEOF\nchmod +x /etc/network-optimization.sh'
    stdin, stdout, stderr = c.exec_command(cmd)
    err = stderr.read().decode()
    print(f"优化脚本: {'已创建' if not err else '失败: ' + err[:100]}")
    
    # 2. 添加到rc.local（开机自启）
    cmd = """
# 确保rc.local存在
if [ ! -f /etc/rc.local ]; then
    echo '#!/bin/bash' > /etc/rc.local
    chmod +x /etc/rc.local
fi

# 添加网络优化（如果还没有）
if ! grep -q "network-optimization" /etc/rc.local; then
    echo "/etc/network-optimization.sh" >> /etc/rc.local
    echo "已添加到rc.local"
else
    echo "已存在rc.local"
fi
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"开机自启: {stdout.read().decode().strip()}")
    
    # 3. 创建sysctl配置文件
    sysctl_conf = """# 网络优化配置
net.core.rmem_max = 25000000
net.core.wmem_max = 25000000
net.core.netdev_max_backlog = 65536
"""
    cmd = f'cat > /etc/sysctl.d/99-network-optimization.conf << \'EOF\'\n{sysctl_conf}\nEOF\nsysctl -p /etc/sysctl.d/99-network-optimization.conf'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"sysctl配置: {stdout.read().decode().strip()}")
    
    c.close()

print("\n全部完成")
