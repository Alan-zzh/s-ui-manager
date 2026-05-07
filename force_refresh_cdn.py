import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n=== {name} ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 停止CDN服务
    cmd = 'systemctl stop singbox-cdn'
    stdin, stdout, stderr = c.exec_command(cmd)
    stdout.read()
    
    # 删除锁文件
    cmd = 'rm -f /tmp/cdn_monitor.lock && echo "OK"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"删除锁文件: {stdout.read().decode().strip()}")
    
    # 同步最新config.py（含黑名单）
    with open(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\config.py', 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    cmd = f'cat > /root/singbox-eps-node/scripts/config.py << \'ENDOFILE\'\n{config_content}\nENDOFILE'
    stdin, stdout, stderr = c.exec_command(cmd, get_pty=True)
    err = stderr.read().decode()
    print(f"config.py: {'已同步' if not err else '失败'}")
    
    # 后台执行CDN监控
    cmd = 'cd /root/singbox-eps-node && nohup python3 scripts/cdn_monitor.py > /tmp/cdn_run.log 2>&1 & echo "已启动"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"CDN监控: {stdout.read().decode().strip()}")
    
    c.close()

print("\n等待CDN监控执行（约60秒）...")
import time
time.sleep(60)

# 检查结果
for name, ip, password in servers:
    print(f"\n=== {name} 结果 ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 检查日志
    cmd = 'tail -15 /tmp/cdn_run.log'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"CDN监控日志:")
    print(stdout.read().decode())
    
    # 检查新CDN IP
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
    print(f"\n数据库CDN设置:")
    print(stdout.read().decode())
    
    # 重启CDN服务
    cmd = 'systemctl restart singbox-cdn && echo "OK" || echo "FAIL"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"重启singbox-cdn: {stdout.read().decode().strip()}")
    
    # 测试订阅
    code = 'JP' if name == '日本' else 'SG'
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null'
    stdin, stdout, stderr = c.exec_command(cmd)
    content = stdout.read().decode()
    print(f"\n订阅节点:")
    for line in content.split('\n'):
        if line.strip() and '#' in line:
            node_name = line.split('#')[-1]
            if 'sni=' in line:
                sni = line.split('sni=')[1].split('&')[0]
            else:
                sni = '无'
            print(f"  {node_name} (SNI: {sni})")
    
    c.close()

print("\n全部完成")
