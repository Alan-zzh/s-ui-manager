import paramiko
import time
import sys
import io
from audit_config import get_server_old_jp

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )

server = get_server_old_jp()
host = server['host']
port = server['port']
username = server['username']
password = server['password']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=15, allow_agent=False, look_for_keys=False)

checks = [
    ("1. project_snapshot.md", """
cat /root/singbox-eps-node/project_snapshot.md 2>/dev/null
"""),
    ("2. AI_DEBUG_HISTORY.md(尾部)", """
tail -200 /root/singbox-eps-node/AI_DEBUG_HISTORY.md 2>/dev/null
"""),
    ("3. cdn_monitor.py完整内容", """
cat /root/singbox-eps-node/scripts/cdn_monitor.py 2>/dev/null
"""),
    ("4. config_generator.py完整内容", """
cat /root/singbox-eps-node/scripts/config_generator.py 2>/dev/null
"""),
    ("5. config.py完整内容", """
cat /root/singbox-eps-node/scripts/config.py 2>/dev/null
"""),
    ("6. cert_manager.py完整内容", """
cat /root/singbox-eps-node/scripts/cert_manager.py 2>/dev/null
"""),
    ("7. health_check.sh完整内容", """
cat /root/singbox-eps-node/scripts/health_check.sh 2>/dev/null
"""),
    ("8. singbox日志(最近200行)", """
tail -200 /var/log/singbox.log 2>/dev/null
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
        print(out[:5000])
        if len(out) > 5000:
            print(f"\n... [截断，共{len(out)}字符]")
    if err.strip():
        print(f"[STDERR] {err[:1000]}")

client.close()
print("\n\n第三轮检查完成")
