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
        cmd = 'systemctl status singbox-cdn --no-pager 2>&1 | head -20'
        out, err = run_command(c, cmd)
        print("\n【服务状态】")
        print(out)

        cmd = 'journalctl -u singbox-cdn --no-pager -n 50 2>&1 | tail -30'
        out, err = run_command(c, cmd)
        print("\n【最近日志】")
        print(out)

        cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT key,value FROM cdn_settings WHERE key LIKE '%cdn%'")
for k,v in c.fetchall():
    print(f"{k}: {v}")
conn.close()
EOF"""
        out, err = run_command(c, cmd)
        print("\n【数据库CDN IP】")
        print(out)

        cmd = 'cd /root/singbox-eps-node && python3 -m py_compile scripts/cdn_monitor.py 2>&1 && echo "语法OK" || echo "语法错误"'
        out, err = run_command(c, cmd)
        print("\n【语法检查】")
        print(out)

        cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3, socket
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT value FROM cdn_settings WHERE key='cdn_ips_list'")
row = c.fetchone()
if row:
    ips = row[0].split(',')
    for ip in ips:
        ip = ip.strip()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 443))
            sock.close()
            status = "OK" if result == 0 else "FAIL"
            print(f"{ip}: {status}")
        except Exception as e:
            print(f"{ip}: ERROR {e}")
conn.close()
EOF"""
        out, err = run_command(c, cmd)
        print("\n【CDN IP连通性】")
        print(out)
