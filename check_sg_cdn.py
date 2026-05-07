import sys
import io
from audit_config import get_server
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

srv = get_server('sg')

with ssh_connect(srv) as c:
    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT key,value FROM cdn_settings")
for k,v in c.fetchall():
    print(f"{k}: {v}")
conn.close()
EOF"""
    out, err = run_command(c, cmd)
    print("【数据库CDN设置】")
    print(out)

    cmd = 'curl -sk https://localhost:2087/sub/SG 2>&1 | base64 -d 2>/dev/null'
    out, err = run_command(c, cmd)
    print("\n【订阅内容】")
    for line in out.split('\n'):
        if line.strip():
            print(line[:150])

    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3, socket, time
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT value FROM cdn_settings WHERE key='cdn_ips_list'")
row = c.fetchone()
if row:
    for ip in row[0].split(','):
        ip = ip.strip()
        for port in [443, 2053, 2083, 8443]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                t0 = time.time()
                r = s.connect_ex((ip, port))
                t1 = time.time()
                s.close()
                status = "OK" if r==0 else "FAIL"
                print(f"{ip}:{port} {status} ({int((t1-t0)*1000)}ms)")
            except Exception as e:
                print(f"{ip}:{port} ERROR {e}")
conn.close()
EOF"""
    out, err = run_command(c, cmd)
    print("\n【CDN IP端口连通性】")
    print(out)

    cmd = "grep -A 30 'CDN_PREFERRED_IPS' /root/singbox-eps-node/scripts/config.py | head -35"
    out, err = run_command(c, cmd)
    print("\n【config.py CDN_PREFERRED_IPS】")
    print(out)
