import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    ip = srv['host']
    print(f"\n{'='*50}")
    print(f"=== {name} ({ip}) ===")
    print(f"{'='*50}")

    with ssh_connect(srv) as c:
        cmd = 'systemctl status singbox-sub --no-pager -l 2>&1 | head -20'
        out, err = run_command(c, cmd)
        print("\n【订阅服务状态】")
        print(out)

        cmd = 'curl -sk https://localhost:2087/sub/sg -o /dev/null -w "HTTP: %{http_code}, Size: %{size_download}" 2>&1'
        out, err = run_command(c, cmd)
        print("\n【订阅测试】")
        print(out)

        cmd = 'journalctl -u singbox-sub --no-pager -n 20 2>&1 | tail -15'
        out, err = run_command(c, cmd)
        print("\n【订阅日志】")
        print(out)

        cmd = 'cd /root/singbox-eps-node && python3 -c "import sqlite3; conn=sqlite3.connect(\'data/singbox.db\'); c=conn.cursor(); c.execute(\'SELECT key,value FROM cdn_settings\'); [print(k,v) for k,v in c.fetchall()]; conn.close()"'
        out, err = run_command(c, cmd)
        print("\n【数据库CDN IP】")
        print(out)

        cmd = 'ss -tlnp | grep -E "2087|8443|2053|2083|443"'
        out, err = run_command(c, cmd)
        print("\n【端口监听】")
        print(out)
