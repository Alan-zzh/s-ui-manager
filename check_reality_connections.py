import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== {name} ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查当前活跃连接来源IP
    cmd = 'ss -tnp | grep sing-box | awk "{print $5}" | cut -d: -f1 | sort | uniq -c | sort -rn'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("【连接来源IP统计】")
    print(stdout.read().decode())
    
    # 2. 检查REALITY成功/失败连接比例
    cmd = 'grep "REALITY" /var/log/singbox.log | tail -100 | grep -c "invalid"'
    stdin, stdout, stderr = c.exec_command(cmd)
    invalid_count = stdout.read().decode().strip()
    print(f"\nREALITY失败连接数（最近100条）: {invalid_count}")
    
    cmd = 'grep "REALITY" /var/log/singbox.log | tail -100 | grep -c "inbound connection"'
    stdin, stdout, stderr = c.exec_command(cmd)
    total_count = stdout.read().decode().strip()
    print(f"REALITY总连接数（最近100条）: {total_count}")
    
    # 3. 获取当前订阅链接
    code = 'JP' if name == '日本' else 'SG'
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【当前订阅中的REALITY配置】")
    reality_link = stdout.read().decode().strip()
    print(reality_link[:200] if reality_link else "无")
    
    # 提取公钥
    if reality_link and 'pbk=' in reality_link:
        pbk = reality_link.split('pbk=')[1].split('&')[0]
        print(f"\n当前公钥: {pbk}")
    
    # 4. 检查服务器配置的公钥
    cmd = 'grep REALITY_PUBLIC_KEY /root/singbox-eps-node/.env'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n服务器公钥配置: {stdout.read().decode().strip()}")
    
    c.close()

print("\n全部完成")
