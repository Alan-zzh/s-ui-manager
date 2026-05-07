import paramiko
import time
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )

host = '52.195.179.240'
port = 22
username = 'root'
password = 'je*pMaN8QNfCMK'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=15, allow_agent=False, look_for_keys=False)

checks = [
    ("1. project_snapshot.md", """
cat /root/singbox-eps-node/project_snapshot.md 2>/dev/null | head -200
"""),
    ("2. AI_DEBUG_HISTORY.md(最近部分)", """
tail -150 /root/singbox-eps-node/AI_DEBUG_HISTORY.md 2>/dev/null
"""),
    ("3. scripts目录结构", """
ls -la /root/singbox-eps-node/scripts/ 2>/dev/null
"""),
    ("4. subscription_service.py关键逻辑", """
head -100 /root/singbox-eps-node/scripts/subscription_service.py 2>/dev/null
"""),
    ("5. cdn_monitor.py关键逻辑", """
head -100 /root/singbox-eps-node/scripts/cdn_monitor.py 2>/dev/null
"""),
    ("6. config_generator.py关键逻辑", """
head -100 /root/singbox-eps-node/scripts/config_generator.py 2>/dev/null
"""),
    ("7. health_check.sh", """
cat /root/singbox-eps-node/scripts/health_check.sh 2>/dev/null
"""),
    ("8. cert_manager.py关键逻辑", """
head -80 /root/singbox-eps-node/scripts/cert_manager.py 2>/dev/null
"""),
    ("9. cdn_monitor锁文件和进程状态", """
echo "=== 锁文件 ==="
ls -la /tmp/cdn_monitor.lock 2>/dev/null || echo "锁文件不存在"
echo ""
echo "=== cdn_monitor进程 ==="
ps aux | grep cdn_monitor | grep -v grep
echo ""
echo "=== 所有python3进程 ==="
ps aux | grep python3 | grep -v grep
echo ""
echo "=== singbox-cdn服务详细状态 ==="
systemctl status singbox-cdn 2>/dev/null | head -20
"""),
    ("10. CDN数据库详细检查", """
cd /root/singbox-eps-node
python3 << 'PYEOF'
import sqlite3, os
db_path = os.path.join('data', 'cdn_ips.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        print(f"表: {[t[0] for t in tables]}")
        for table in tables:
            tname = table[0]
            c.execute(f"SELECT COUNT(*) FROM {tname}")
            count = c.fetchone()[0]
            print(f"  {tname}: {count}条记录")
            if count > 0 and count <= 20:
                c.execute(f"SELECT * FROM {tname}")
                for row in c.fetchall():
                    print(f"    {row}")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        conn.close()
else:
    print("CDN数据库不存在")
PYEOF
"""),
    ("11. singbox日志详细分析", """
echo "=== 日志大小 ==="
ls -lh /var/log/singbox.log 2>/dev/null
echo ""
echo "=== 最近100行日志 ==="
tail -100 /var/log/singbox.log 2>/dev/null
"""),
    ("12. subscription_service完整逻辑", """
wc -l /root/singbox-eps-node/scripts/subscription_service.py 2>/dev/null
echo ""
cat /root/singbox-eps-node/scripts/subscription_service.py 2>/dev/null
"""),
]

for title, cmd in checks:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(out)
    if err.strip():
        print(f"[STDERR] {err}")

client.close()
print("\n\n深度检查完成")
