import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    print(f"\n{'='*50}")
    print(f"=== {name} ===")
    print(f"{'='*50}")

    with ssh_connect(srv) as c:
        cmd = 'ip link show | grep mtu'
        out, err = run_command(c, cmd)
        print("【MTU设置】")
        print(out)

        cmd = 'sysctl net.ipv4.tcp_congestion_control && sysctl net.core.default_qdisc'
        out, err = run_command(c, cmd)
        print("\n【TCP拥塞控制】")
        print(out)

        cmd = 'sysctl net.ipv4.tcp_rmem && sysctl net.ipv4.tcp_wmem && sysctl net.core.rmem_max && sysctl net.core.wmem_max'
        out, err = run_command(c, cmd)
        print("\n【TCP缓冲区】")
        print(out)

        cmd = 'grep -i mtu /root/singbox-eps-node/config.json || echo "无MTU设置"'
        out, err = run_command(c, cmd)
        print("\n【singbox MTU】")
        print(out)

        cmd = 'sysctl net.ipv4.tcp_congestion_control | grep bbr || echo "未启用BBR"'
        out, err = run_command(c, cmd)
        print("\n【BBR状态】")
        print(out)

        cmd = 'ping -c 10 8.8.8.8 2>&1 | tail -3'
        out, err = run_command(c, cmd, timeout=15)
        print("\n【到8.8.8.8的延迟】")
        print(out)

print("\n全部完成")
