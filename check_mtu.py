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
        out, err = run_command(c, cmd)
        print(out)

        cmd = 'tc class show && echo "---" && tc filter show'
        out, err = run_command(c, cmd)
        print("\n【流量限制】")
        print(out)

        cmd = '/usr/local/bin/sing-box version'
        out, err = run_command(c, cmd)
        print("\n【singbox版本】")
        print(out)

print("\n全部完成")
