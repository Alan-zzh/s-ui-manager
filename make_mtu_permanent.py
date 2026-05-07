from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n=== {srv['name']} ===")

    with ssh_connect(srv) as c:
        script = """#!/bin/bash
ip link set dev ens5 mtu 1500

sysctl -w net.core.rmem_max=25000000
sysctl -w net.core.wmem_max=25000000
sysctl -w net.core.netdev_max_backlog=65536

echo "网络优化已应用"
"""

        cmd = f'cat > /etc/network-optimization.sh << \'EOF\'\n{script}\nEOF\nchmod +x /etc/network-optimization.sh'
        out, err = run_command(c, cmd)
        print(f"优化脚本: {'已创建' if not err.strip() else '失败: ' + err.strip()[:100]}")

        cmd = """
if [ ! -f /etc/rc.local ]; then
    echo '#!/bin/bash' > /etc/rc.local
    chmod +x /etc/rc.local
fi

if ! grep -q "network-optimization" /etc/rc.local; then
    echo "/etc/network-optimization.sh" >> /etc/rc.local
    echo "已添加到rc.local"
else
    echo "已存在rc.local"
fi
"""
        out, err = run_command(c, cmd)
        print(f"开机自启: {out.strip()}")

        sysctl_conf = """net.core.rmem_max = 25000000
net.core.wmem_max = 25000000
net.core.netdev_max_backlog = 65536
"""
        cmd = f'cat > /etc/sysctl.d/99-network-optimization.conf << \'EOF\'\n{sysctl_conf}\nEOF\nsysctl -p /etc/sysctl.d/99-network-optimization.conf'
        out, err = run_command(c, cmd)
        print(f"sysctl配置: {out.strip()}")

print("\n全部完成")
