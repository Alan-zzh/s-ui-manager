from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== 修复 {srv['name']} ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
        if srv['name'] == '日本':
            print("\n1. 启动 singbox-cdn...")
            cmd = 'systemctl start singbox-cdn && echo "OK" || echo "FAIL"'
            out, err = run_command(c, cmd)
            print(f"结果: {out.strip()}")

            cmd = 'systemctl is-active singbox-cdn'
            out, err = run_command(c, cmd)
            print(f"状态: {out.strip()}")

        print("\n2. 检查CDN数据库...")
        cmd = """
cd /root/singbox-eps-node
if [ ! -d data ]; then mkdir -p data; fi
python3 << 'EOF'
import sqlite3, os
db_path = os.path.join('data', 'cdn_ips.db')
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cdn_ips (
        ip TEXT PRIMARY KEY,
        latency REAL,
        source TEXT,
        status TEXT DEFAULT 'active',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
    print("数据库已创建")
else:
    print("数据库已存在")
EOF
"""
        out, err = run_command(c, cmd)
        print(out.strip())

        print("\n3. 清理旧日志...")
        cmd = 'echo "" > /var/log/singbox.log && echo "OK" || echo "FAIL"'
        out, err = run_command(c, cmd)
        print(f"结果: {out.strip()}")

        print("\n4. 检查REALITY配置...")
        cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import json
with open('config.json', 'r') as f:
    config = json.load(f)

for inbound in config.get('inbounds', []):
    if inbound.get('tag') == 'vless-reality':
        tls = inbound.get('tls', {})
        reality = tls.get('reality', {})
        print(f"Tag: {inbound['tag']}")
        print(f"Port: {inbound['listen_port']}")
        print(f"server_name: {tls.get('server_name')}")
        print(f"private_key: {reality.get('private_key', '')[:20]}...")
        print(f"short_id: {reality.get('short_id')}")
        print(f"handshake_server: {reality.get('handshake', {}).get('server')}")
EOF
"""
        out, err = run_command(c, cmd)
        print(out)

        print("\n5. 检查.env配置...")
        cmd = 'grep REALITY /root/singbox-eps-node/.env'
        out, err = run_command(c, cmd)
        print(out.strip())

        print("\n6. 重启singbox...")
        cmd = 'systemctl restart singbox && sleep 2 && systemctl is-active singbox'
        out, err = run_command(c, cmd)
        print(f"状态: {out.strip()}")

    print(f"\n{'='*60}")
    print(f"=== {srv['name']} 修复完成 ===")
    print(f"{'='*60}")

print("\n全部修复完成")
