import paramiko

def check_sub(name, ip, password):
    print(f"\n{'='*50}")
    print(f"=== {name} ({ip}) ===")
    print(f"{'='*50}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查订阅服务状态
    cmd = 'systemctl status singbox-sub --no-pager -l 2>&1 | head -20'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【订阅服务状态】")
    print(stdout.read().decode())
    
    # 2. 测试订阅链接
    cmd = 'curl -sk https://localhost:2087/sub/sg -o /dev/null -w "HTTP: %{http_code}, Size: %{size_download}" 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【订阅测试】")
    print(stdout.read().decode())
    
    # 3. 检查订阅服务日志
    cmd = 'journalctl -u singbox-sub --no-pager -n 20 2>&1 | tail -15'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【订阅日志】")
    print(stdout.read().decode())
    
    # 4. 检查CDN IP
    cmd = 'cd /root/singbox-eps-node && python3 -c "import sqlite3; conn=sqlite3.connect(\'data/singbox.db\'); c=conn.cursor(); c.execute(\'SELECT key,value FROM cdn_settings\'); [print(k,v) for k,v in c.fetchall()]; conn.close()"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【数据库CDN IP】")
    print(stdout.read().decode())
    
    # 5. 检查端口监听
    cmd = 'ss -tlnp | grep -E "2087|8443|2053|2083|443"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【端口监听】")
    print(stdout.read().decode())
    
    c.close()

check_sub('日本', '52.195.179.240', 'je*pMaN8QNfCMK')
check_sub('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com')
