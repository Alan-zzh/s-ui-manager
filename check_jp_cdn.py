import sys
import io
from audit_config import get_server
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

srv = get_server('jp')

with ssh_connect(srv) as c:
    cmd = 'grep CF_DOMAIN /root/singbox-eps-node/.env'
    out, err = run_command(c, cmd)
    print(f"【CF_DOMAIN】{out.strip()}")

    cmd = 'curl -sk https://localhost:2087/sub/JP 2>&1 | base64 -d 2>/dev/null'
    out, err = run_command(c, cmd)
    print("\n【订阅节点SNI】")
    for line in out.split('\n'):
        if line.strip() and '#' in line:
            name = line.split('#')[-1]
            if 'sni=' in line:
                sni = line.split('sni=')[1].split('&')[0]
            else:
                sni = '无'
            print(f"  {name} -> SNI: {sni}")

    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3, socket, time
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT value FROM cdn_settings WHERE key='cdn_ips_list'")
row = c.fetchone()
if row:
    for ip in row[0].split(','):
        ip = ip.strip()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            t0 = time.time()
            r = s.connect_ex((ip, 443))
            t1 = time.time()
            s.close()
            status = "OK" if r==0 else "FAIL"
            print(f"{ip}: {status} ({int((t1-t0)*1000)}ms)")
        except Exception as e:
            print(f"{ip}: ERROR {e}")
conn.close()
EOF"""
    out, err = run_command(c, cmd)
    print(f"\n【CDN IP延迟】")
    print(out)

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
    print(f"\n【数据库CDN设置】")
    print(out)
