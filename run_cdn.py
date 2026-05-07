import time
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n=== {srv['name']} ===")
    with ssh_connect(srv) as c:
        cmd = 'rm -f /tmp/cdn_monitor.lock && echo "锁文件已删除"'
        out, err = run_command(c, cmd)
        print(out.strip())

        cmd = 'cd /root/singbox-eps-node && nohup python3 scripts/cdn_monitor.py > /tmp/cdn_run.log 2>&1 & echo "已启动"'
        out, err = run_command(c, cmd)
        print(f"CDN监控: {out.strip()}")

print("\n等待CDN监控执行完成...")
time.sleep(90)

for srv in get_servers():
    print(f"\n=== {srv['name']} 结果 ===")
    with ssh_connect(srv) as c:
        cmd = 'tail -20 /tmp/cdn_run.log'
        out, err = run_command(c, cmd)
        print(f"CDN监控日志:")
        print(out)

        cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT value FROM cdn_settings WHERE key='cdn_ips_list'")
row = c.fetchone()
if row:
    print(f"新CDN IPs: {row[0]}")
conn.close()
EOF"""
        out, err = run_command(c, cmd)
        print(f"\n新CDN IPs: {out.strip()}")

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null'
        out, err = run_command(c, cmd)
        lines = [l for l in out.split('\n') if l.strip()]
        print(f"\n订阅节点({len(lines)}个):")
        for line in lines:
            if '#' in line:
                print(f"  {line.split('#')[-1]}")

print("\n全部完成")
