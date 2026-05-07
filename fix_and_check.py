import paramiko

# 读取本地subscription_service.py
with open(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\subscription_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

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
    
    # 1. 同步subscription_service.py
    cmd = f'cat > /root/singbox-eps-node/scripts/subscription_service.py << \'ENDOFILE\'\n{content}\nENDOFILE'
    stdin, stdout, stderr = c.exec_command(cmd, get_pty=True)
    err = stderr.read().decode()
    print(f"subscription_service.py: {'已同步' if not err else '失败: ' + err[:100]}")
    
    # 2. 重启订阅服务
    cmd = 'systemctl restart singbox-sub && echo "重启成功" || echo "重启失败"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"重启singbox-sub: {stdout.read().decode().strip()}")
    
    # 3. 测试大小写订阅
    cmd = 'curl -sk https://localhost:2087/sub/sg -o /dev/null -w "HTTP: %{http_code}" 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"小写/sub/sg: {stdout.read().decode().strip()}")
    
    cmd = 'curl -sk https://localhost:2087/sub/SG -o /dev/null -w "HTTP: %{http_code}" 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"大写/sub/SG: {stdout.read().decode().strip()}")
    
    # 4. 检测协议端口监听
    cmd = 'ss -tlnp | grep -E "443|8443|2053|2083"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【核心端口监听】")
    print(stdout.read().decode())
    
    # 5. 检查singbox日志错误
    cmd = 'journalctl -u singbox --no-pager -n 50 2>&1 | grep -iE "error|fail|warn" | tail -10'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【singbox错误日志】")
    out = stdout.read().decode()
    print(out if out else "无错误")
    
    # 6. 测试订阅内容
    cmd = 'curl -sk https://localhost:2087/sub/sg 2>&1 | base64 -d 2>/dev/null | wc -l'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【订阅节点数】")
    print(stdout.read().decode())
    
    c.close()

print("\n全部完成")
