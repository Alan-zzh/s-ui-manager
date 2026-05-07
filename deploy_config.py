from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

with open(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()

for srv in get_servers():
    print(f"\n{'='*50}")
    print(f"=== {srv['name']} ({srv['host']}) ===")
    print(f"{'='*50}")

    with ssh_connect(srv) as c:
        cmd = f'cat > /root/singbox-eps-node/scripts/config.py << \'ENDOFILE\'\n{config_content}\nENDOFILE'
        out, err = run_command(c, cmd)
        print(f"config.py: {'已同步' if not err.strip() else '失败: ' + err.strip()[:100]}")

        for svc in ['singbox-cdn', 'singbox-sub', 'singbox']:
            cmd = f'systemctl restart {svc} && echo "OK" || echo "FAIL"'
            out, err = run_command(c, cmd)
            print(f"重启{svc}: {out.strip()}")

        for svc in ['singbox-cdn', 'singbox-sub', 'singbox']:
            cmd = f'systemctl is-active {svc}'
            out, err = run_command(c, cmd)
            print(f"{svc}状态: {out.strip()}")

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} -o /dev/null -w "HTTP: %{{http_code}}" 2>&1'
        out, err = run_command(c, cmd)
        print(f"订阅测试(/sub/{code}): {out.strip()}")

        cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT value FROM cdn_settings WHERE key='cdn_ips_list'")
row = c.fetchone()
if row:
    print(f"CDN IPs: {row[0]}")
conn.close()
EOF"""
        out, err = run_command(c, cmd)
        print(f"数据库CDN IP: {out.strip()}")

print("\n全部完成")
