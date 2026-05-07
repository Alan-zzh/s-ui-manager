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
        cmd = 'uptime && echo "---" && free -m && echo "---" && top -bn1 | head -15'
        out, err = run_command(c, cmd)
        print("【服务器负载】")
        print(out)

        cmd = 'ps aux | grep sing-box | grep -v grep'
        out, err = run_command(c, cmd)
        print("\n【singbox进程】")
        print(out)

        cmd = 'iftop -t -s 5 2>/dev/null || nethogs 2>/dev/null || echo "无iftop/nethogs"'
        out, err = run_command(c, cmd, timeout=10)
        print("\n【网络带宽】")
        print(out)

        cmd = 'iptables -L -v -n | head -30'
        out, err = run_command(c, cmd)
        print("\n【iptables流量统计】")
        print(out)

        cmd = 'iostat -x 1 2 2>/dev/null || echo "无iostat"'
        out, err = run_command(c, cmd, timeout=5)
        print("\n【磁盘IO】")
        print(out)

        cmd = 'ss -s && echo "---" && ss -tan | awk "{print \\$1}" | sort | uniq -c'
        out, err = run_command(c, cmd)
        print("\n【网络连接数】")
        print(out)

print("\n全部完成")
