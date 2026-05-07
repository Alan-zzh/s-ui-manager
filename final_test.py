from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    code = 'JP' if srv['name'] == '日本' else 'SG'
    print(f"\n=== {srv['name']} ===")

    with ssh_connect(srv) as c:
        for path in [f'/sub/{code}', f'/sub/{code.lower()}', f'/singbox/{code}', f'/singbox/{code.lower()}']:
            cmd = f'curl -sk https://localhost:2087{path} -o /dev/null -w "HTTP: %{{http_code}}" 2>&1'
            out, err = run_command(c, cmd)
            print(f"  {path}: {out.strip()}")

        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null'
        out, err = run_command(c, cmd)
        lines = [l for l in out.split('\n') if l.strip()]
        print(f"\n  节点数: {len(lines)}")
        for line in lines:
            if '#' in line:
                print(f"  {line.split('#')[-1]}")

        cmd = """cd /root/singbox-eps-node && python3 << 'PYEOF'
import sqlite3, socket, time
conn = sqlite3.connect('data/singbox.db')
c = conn.cursor()
c.execute("SELECT value FROM cdn_settings WHERE key='cdn_ips_list'")
row = c.fetchone()
if row:
    for ip in row[0].split(','):
        ip = ip.strip()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            t0 = time.time()
            r = s.connect_ex((ip, 443))
            t1 = time.time()
            s.close()
            status = "OK" if r==0 else "FAIL"
            print(f'{ip}: {status} ({int((t1-t0)*1000)}ms)')
        except Exception as e:
            print(f'{ip}: ERROR {e}')
conn.close()
PYEOF"""
        out, err = run_command(c, cmd)
        print(f"\n  CDN IP连通性:")
        print(out)
