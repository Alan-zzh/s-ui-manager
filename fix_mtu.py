from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*50}")
    print(f"=== {srv['name']} ===")
    print(f"{'='*50}")

    with ssh_connect(srv) as c:
        cmd = 'ip link set dev ens5 mtu 1500 && ip link show ens5 | grep mtu'
        out, err = run_command(c, cmd)
        print(f"MTU修改: {out.strip()}")

        cmd = """
sysctl -w net.core.rmem_max=25000000
sysctl -w net.core.wmem_max=25000000
sysctl -w net.core.netdev_max_backlog=65536
echo "UDP缓冲区已优化"
"""
        out, err = run_command(c, cmd)
        print(f"UDP优化: {out.strip()}")

        cmd = 'systemctl restart singbox && echo "OK" || echo "FAIL"'
        out, err = run_command(c, cmd)
        print(f"重启singbox: {out.strip()}")

        cmd = 'ip link show ens5 | grep mtu'
        out, err = run_command(c, cmd)
        print(f"当前MTU: {out.strip()}")

print("\n全部完成")
