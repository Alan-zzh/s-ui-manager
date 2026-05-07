import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    print(f"\n=== {name} ===")

    with ssh_connect(srv) as c:
        cmd = 'systemctl is-active singbox'
        out, err = run_command(c, cmd)
        print(f"singbox服务: {out.strip()}")

        cmd = 'top -bn1 | head -5'
        out, err = run_command(c, cmd)
        print(f"\n【系统负载】")
        print(out)

        cmd = 'ps aux | grep sing-box | grep -v grep'
        out, err = run_command(c, cmd)
        print(f"\n【sing-box进程】")
        print(out)

        cmd = 'ping -c 3 8.8.8.8 2>&1 | tail -2'
        out, err = run_command(c, cmd)
        print(f"\n【网络延迟】")
        print(out)

        cmd = 'iostat -x 1 1 2>&1 | tail -5'
        out, err = run_command(c, cmd)
        print(f"\n【磁盘IO】")
        print(out)

        cmd = 'ss -s 2>&1'
        out, err = run_command(c, cmd)
        print(f"\n【连接统计】")
        print(out)

        cmd = 'journalctl -u singbox --no-pager -n 100 2>&1 | grep -iE "error|fail|close|reset|timeout" | tail -10'
        out, err = run_command(c, cmd)
        print(f"\n【singbox错误】")
        print(out if out else "无错误")

        cmd = 'iptables -t nat -L -n -v 2>&1 | head -20'
        out, err = run_command(c, cmd)
        print(f"\n【iptables端口跳跃】")
        print(out)
