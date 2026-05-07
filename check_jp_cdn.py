import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('52.195.179.240', username='root', password='je*pMaN8QNfCMK', timeout=15)

# 1. 检查.env的CF_DOMAIN
cmd = 'grep CF_DOMAIN /root/singbox-eps-node/.env'
stdin, stdout, stderr = c.exec_command(cmd)
print(f"【CF_DOMAIN】{stdout.read().decode().strip()}")

# 2. 获取订阅内容看SNI
cmd = 'curl -sk https://localhost:2087/sub/JP 2>&1 | base64 -d 2>/dev/null'
stdin, stdout, stderr = c.exec_command(cmd)
content = stdout.read().decode()
print("\n【订阅节点SNI】")
for line in content.split('\n'):
    if line.strip() and '#' in line:
        name = line.split('#')[-1]
        if 'sni=' in line:
            sni = line.split('sni=')[1].split('&')[0]
        else:
            sni = '无'
        print(f"  {name} -> SNI: {sni}")

# 3. 测试CDN IP到服务器的延迟
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
stdin, stdout, stderr = c.exec_command(cmd)
print(f"\n【CDN IP延迟】")
print(stdout.read().decode())

# 4. 检查CDN IP是否真的是Cloudflare IP
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
print(f"\n【数据库CDN设置】")
print(stdout.read().decode())

c.close()
