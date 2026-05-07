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
        cmd = 'tail -50 /var/log/singbox.log 2>/dev/null || journalctl -u singbox --no-pager -n 50'
        out, err = run_command(c, cmd)
        print("【singbox日志（最近50行）】")
        print(out)

        cmd = 'ss -tlnp | grep -E "443|8443|2053|2083"'
        out, err = run_command(c, cmd)
        print("\n【端口监听状态】")
        print(out)

        cmd = 'ss -tnp | grep -E "443|8443|2053|2083" | head -20'
        out, err = run_command(c, cmd)
        print("\n【活跃连接】")
        print(out)

        cmd = 'netstat -s | grep -i "retrans" | head -5'
        out, err = run_command(c, cmd)
        print("\n【TCP重传率】")
        print(out)

        cmd = 'tc qdisc show'
        out, err = run_command(c, cmd)
        print("\n【网络队列】")
        print(out)

print("\n全部完成")
