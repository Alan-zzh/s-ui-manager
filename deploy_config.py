import paramiko

# 读取本地config.py
with open(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*50}")
    print(f"=== {name} ({ip}) ===")
    print(f"{'='*50}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 同步config.py
    cmd = f'cat > /root/singbox-eps-node/scripts/config.py << \'ENDOFILE\'\n{config_content}\nENDOFILE'
    stdin, stdout, stderr = c.exec_command(cmd, get_pty=True)
    err = stderr.read().decode()
    print(f"config.py: {'已同步' if not err else '失败: ' + err[:100]}")
    
    # 2. 重启所有相关服务
    for svc in ['singbox-cdn', 'singbox-sub', 'singbox']:
        cmd = f'systemctl restart {svc} && echo "OK" || echo "FAIL"'
        stdin, stdout, stderr = c.exec_command(cmd)
        out = stdout.read().decode().strip()
        print(f"重启{svc}: {out}")
    
    # 3. 检查服务状态
    for svc in ['singbox-cdn', 'singbox-sub', 'singbox']:
        cmd = f'systemctl is-active {svc}'
        stdin, stdout, stderr = c.exec_command(cmd)
        status = stdout.read().decode().strip()
        print(f"{svc}状态: {status}")
    
    # 4. 测试订阅
    code = 'JP' if name == '日本' else 'SG'
    cmd = f'curl -sk https://localhost:2087/sub/{code} -o /dev/null -w "HTTP: %{{http_code}}" 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"订阅测试(/sub/{code}): {stdout.read().decode().strip()}")
    
    # 5. 检查数据库CDN IP
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"数据库CDN IP: {stdout.read().decode().strip()}")
    
    c.close()

print("\n全部完成")
