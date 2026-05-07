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
    ("1. singbox.db CDN数据", """
cd /root/singbox-eps-node
python3 << 'PYEOF'
import sqlite3, os
db_path = os.path.join('data', 'singbox.db')
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
            print(f"\n--- {tname} ({count}条) ---")
            if tname == 'cdn_settings':
                c.execute(f"SELECT * FROM {tname}")
                for row in c.fetchall():
                    print(f"  {row}")
            elif tname == 'ip_performance':
                c.execute(f"SELECT ip, total_tests, success_count, fail_count, consecutive_fails, avg_latency, last_test_time, last_success_time, source FROM {tname} ORDER BY avg_latency LIMIT 20")
                for row in c.fetchall():
                    print(f"  {row}")
            elif count <= 30:
                c.execute(f"SELECT * FROM {tname}")
                for row in c.fetchall():
                    print(f"  {row}")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        conn.close()
else:
    print("singbox.db不存在")
PYEOF
"""),
    ("2. 订阅实际输出内容解码", """
cd /root/singbox-eps-node
python3 << 'PYEOF'
import urllib.request, base64, json

try:
    req = urllib.request.Request('https://localhost:2087/sub/JP', headers={'User-Agent': 'test'})
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
        raw = resp.read().decode()
        decoded = base64.b64decode(raw).decode()
        lines = decoded.strip().split('\n')
        for i, line in enumerate(lines):
            print(f"节点{i+1}: {line[:120]}...")
except Exception as e:
    print(f"错误: {e}")

print("\n=== singbox配置结构 ===")
try:
    req = urllib.request.Request('https://localhost:2087/singbox/JP')
    with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
        config = json.loads(resp.read().decode())
        print(f"inbounds: {len(config.get('inbounds', []))}")
        for ib in config.get('inbounds', []):
            print(f"  - {ib.get('tag')}: {ib.get('type')} :{ib.get('listen_port')}")
        print(f"outbounds: {len(config.get('outbounds', []))}")
        for ob in config.get('outbounds', []):
            print(f"  - {ob.get('tag')}: {ob.get('type')}")
        print(f"route.rules: {len(config.get('route', {}).get('rules', []))}")
        for i, rule in enumerate(config.get('route', {}).get('rules', [])):
            outbound = rule.get('outbound', 'N/A')
            keys = [k for k in rule.keys() if k != 'outbound']
            print(f"  规则{i+1}: {keys} -> {outbound}")
        print(f"route.rule_set: {len(config.get('route', {}).get('rule_set', []))}")
        for rs in config.get('route', {}).get('rule_set', []):
            print(f"  - {rs.get('tag')}: {rs.get('url', 'N/A')[:80]}")
        print(f"route.final: {config.get('route', {}).get('final')}")
except Exception as e:
    print(f"错误: {e}")
PYEOF
"""),
    ("3. cdn_monitor锁文件机制检查", """
cd /root/singbox-eps-node
python3 << 'PYEOF'
import os, fcntl

lock_file = '/tmp/cdn_monitor.lock'
print(f"锁文件存在: {os.path.exists(lock_file)}")
if os.path.exists(lock_file):
    print(f"锁文件大小: {os.path.getsize(lock_file)}")
    print(f"锁文件修改时间: {os.path.getmtime(lock_file)}")

# 尝试获取锁
try:
    fd = os.open(lock_file, os.O_RDWR | os.O_CREAT)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print("锁获取成功(无竞争)")
        fcntl.flock(fd, fcntl.LOCK_UN)
    except IOError:
        print("锁获取失败(被其他进程持有)")
    os.close(fd)
except Exception as e:
    print(f"锁操作异常: {e}")
PYEOF
"""),
    ("4. 外部CDN API连通性测试", """
echo "=== WeTest ==="
curl -sk --connect-timeout 5 "https://ct.cloudflare.182682.xyz" 2>/dev/null | head -3 || echo "WeTest不可达"
echo ""
echo "=== vvhan ==="
curl -sk --connect-timeout 5 "https://api.vvhan.com/tool/cf_ip" 2>/dev/null | head -3 || echo "vvhan不可达"
echo ""
echo "=== 090227 ==="
curl -sk --connect-timeout 5 "https://addressesapi.090227.xyz/ct" 2>/dev/null | head -3 || echo "090227不可达"
echo ""
echo "=== 001315 ==="
curl -sk --connect-timeout 5 "https://cf.001315.xyz/ct" 2>/dev/null | head -3 || echo "001315不可达"
echo ""
echo "=== IPDB ==="
curl -sk --connect-timeout 5 "https://ipdb.api.030101.xyz/?type=bestcf" 2>/dev/null | head -3 || echo "IPDB不可达"
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
        print(out[:6000])
        if len(out) > 6000:
            print(f"\n... [截断，共{len(out)}字符]")
    if err.strip():
        print(f"[STDERR] {err[:1000]}")

client.close()
print("\n\n最终验证完成")
