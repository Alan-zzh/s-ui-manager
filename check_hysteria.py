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
        cmd = 'grep -i hysteria /var/log/singbox.log 2>/dev/null | tail -20 || echo "无Hysteria日志"'
        out, err = run_command(c, cmd)
        print("【Hysteria2日志】")
        print(out)

        cmd = 'ss -tnp | grep ":443" | head -10'
        out, err = run_command(c, cmd)
        print("\n【443端口连接】")
        print(out)

        cmd = 'ss -unp | grep ":443" | head -10'
        out, err = run_command(c, cmd)
        print("\n【443端口UDP连接】")
        print(out)

        cmd = 'iptables -L -v -n | grep -E "udp|UDP"'
        out, err = run_command(c, cmd)
        print("\n【iptables UDP规则】")
        print(out)

print("\n全部完成")
