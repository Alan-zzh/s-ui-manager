import paramiko

def check_cdn(name, ip, password):
    print(f"\n{'='*50}")
    print(f"=== {name} ({ip}) ===")
    print(f"{'='*50}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查服务状态
    cmd = 'systemctl status singbox-cdn --no-pager 2>&1 | head -20'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【服务状态】")
    print(stdout.read().decode())
    
    # 2. 检查最近日志
    cmd = 'journalctl -u singbox-cdn --no-pager -n 50 2>&1 | tail -30'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【最近日志】")
    print(stdout.read().decode())
    
    # 3. 检查数据库CDN IP
    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT key,value FROM cdn_settings WHERE key LIKE '%cdn%'")
for k,v in c.fetchall():
    print(f"{k}: {v}")
conn.close()
EOF"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【数据库CDN IP】")
    print(stdout.read().decode())
    
    # 4. 检查cdn_monitor.py语法
    cmd = 'cd /root/singbox-eps-node && python3 -m py_compile scripts/cdn_monitor.py 2>&1 && echo "语法OK" || echo "语法错误"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【语法检查】")
    print(stdout.read().decode())
    
    # 5. 检查CDN IP连通性
    cmd = """cd /root/singbox-eps-node && python3 << 'EOF'
import sqlite3, socket
conn = sqlite3.connect("data/singbox.db")
c = conn.cursor()
c.execute("SELECT value FROM cdn_settings WHERE key='cdn_ips_list'")
row = c.fetchone()
if row:
    ips = row[0].split(',')
    for ip in ips:
        ip = ip.strip()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 443))
            sock.close()
            status = "OK" if result == 0 else "FAIL"
            print(f"{ip}: {status}")
        except Exception as e:
            print(f"{ip}: ERROR {e}")
conn.close()
EOF"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【CDN IP连通性】")
    print(stdout.read().decode())
    
    c.close()

check_cdn('日本', '52.195.179.240', 'je*pMaN8QNfCMK')
check_cdn('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com')
