import paramiko, time

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n=== {name} ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 删除锁文件
    cmd = 'rm -f /tmp/cdn_monitor.lock && echo "锁文件已删除"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode().strip())
    
    # 后台执行CDN监控
    cmd = 'cd /root/singbox-eps-node && nohup python3 scripts/cdn_monitor.py > /tmp/cdn_run.log 2>&1 & echo "已启动"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"CDN监控: {stdout.read().decode().strip()}")
    
    c.close()

print("\n等待CDN监控执行完成...")
time.sleep(90)

# 检查结果
for name, ip, password in servers:
    print(f"\n=== {name} 结果 ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 检查日志
    cmd = 'tail -20 /tmp/cdn_run.log'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"CDN监控日志:")
    print(stdout.read().decode())
    
    # 检查新的CDN IP
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
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n新CDN IPs: {stdout.read().decode().strip()}")
    
    # 测试订阅内容
    code = 'JP' if name == '日本' else 'SG'
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null'
    stdin, stdout, stderr = c.exec_command(cmd)
    content = stdout.read().decode()
    lines = [l for l in content.split('\n') if l.strip()]
    print(f"\n订阅节点({len(lines)}个):")
    for line in lines:
        if '#' in line:
            print(f"  {line.split('#')[-1]}")
    
    c.close()

print("\n全部完成")
