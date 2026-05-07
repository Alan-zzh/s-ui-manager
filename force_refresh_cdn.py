import time
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

with open(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()

for srv in get_servers():
    print(f"\n=== {srv['name']} ===")
    with ssh_connect(srv) as c:
        cmd = 'systemctl stop singbox-cdn'
        out, err = run_command(c, cmd)

        cmd = 'rm -f /tmp/cdn_monitor.lock && echo "OK"'
        out, err = run_command(c, cmd)
        print(f"删除锁文件: {out.strip()}")

        cmd = f'cat > /root/singbox-eps-node/scripts/config.py << \'ENDOFILE\'\n{config_content}\nENDOFILE'
        out, err = run_command(c, cmd)
        print(f"config.py: {'已同步' if not err.strip() else '失败'}")

        cmd = 'cd /root/singbox-eps-node && nohup python3 scripts/cdn_monitor.py > /tmp/cdn_run.log 2>&1 & echo "已启动"'
        out, err = run_command(c, cmd)
        print(f"CDN监控: {out.strip()}")

print("\n等待CDN监控执行（约60秒）...")
time.sleep(60)

for srv in get_servers():
    print(f"\n=== {srv['name']} 结果 ===")
    with ssh_connect(srv) as c:
        cmd = 'tail -15 /tmp/cdn_run.log'
        out, err = run_command(c, cmd)
        print(f"CDN监控日志:")
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
        print(f"\n数据库CDN设置:")
        print(out)

        cmd = 'systemctl restart singbox-cdn && echo "OK" || echo "FAIL"'
        out, err = run_command(c, cmd)
        print(f"重启singbox-cdn: {out.strip()}")

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null'
        out, err = run_command(c, cmd)
        print(f"\n订阅节点:")
        for line in out.split('\n'):
            if line.strip() and '#' in line:
                node_name = line.split('#')[-1]
                if 'sni=' in line:
                    sni = line.split('sni=')[1].split('&')[0]
                else:
                    sni = '无'
                print(f"  {node_name} (SNI: {sni})")

print("\n全部完成")
