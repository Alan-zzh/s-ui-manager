import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('13.212.37.11', username='root', password='jbfCMP75@jh.dxclouds.com', timeout=15)

# 1. 检查当前CDN IP
cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT key,value FROM cdn_settings")
for k,v in c.fetchall():
    print(f"{k}: {v}")
conn.close()
EOF"""
stdin, stdout, stderr = c.exec_command(cmd)
print("【数据库CDN设置】")
print(stdout.read().decode())

# 2. 获取订阅内容
cmd = 'curl -sk https://localhost:2087/sub/SG 2>&1 | base64 -d 2>/dev/null'
stdin, stdout, stderr = c.exec_command(cmd)
content = stdout.read().decode()
print("\n【订阅内容】")
for line in content.split('\n'):
    if line.strip():
        print(line[:150])

# 3. 测试CDN IP连通性
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
stdin, stdout, stderr = c.exec_command(cmd)
print("\n【CDN IP端口连通性】")
print(stdout.read().decode())

# 4. 检查config.py里的CDN_PREFERRED_IPS
cmd = "grep -A 30 'CDN_PREFERRED_IPS' /root/singbox-eps-node/scripts/config.py | head -35"
stdin, stdout, stderr = c.exec_command(cmd)
print("\n【config.py CDN_PREFERRED_IPS】")
print(stdout.read().decode())

c.close()
