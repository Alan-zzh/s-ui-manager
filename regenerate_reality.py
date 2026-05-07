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
    
    # 1. 生成新的REALITY密钥对
    cmd = '/usr/local/bin/sing-box generate reality-keypair'
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    
    private_key = ''
    public_key = ''
    for line in out.split('\n'):
        line = line.strip()
        if line.startswith('PrivateKey:'):
            private_key = line.split(':', 1)[1].strip()
        elif line.startswith('PublicKey:'):
            public_key = line.split(':', 1)[1].strip()
    
    if not private_key or not public_key:
        print(f"密钥生成失败: {out}")
        c.close()
        continue
    
    print(f"新私钥: {private_key[:20]}...")
    print(f"新公钥: {public_key}")
    
    # 2. 更新.env
    cmd = f"""cd /root/singbox-eps-node
sed -i 's|REALITY_PRIVATE_KEY=.*|REALITY_PRIVATE_KEY={private_key}|' .env
sed -i 's|REALITY_PUBLIC_KEY=.*|REALITY_PUBLIC_KEY={public_key}|' .env
echo "env已更新"
grep REALITY .env
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n.env更新: {stdout.read().decode().strip()}")
    
    # 3. 重启singbox
    cmd = 'systemctl restart singbox && echo "OK" || echo "FAIL"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n重启singbox: {stdout.read().decode().strip()}")
    
    # 4. 验证新配置
    cmd = 'sleep 2 && grep -A 3 "private_key" /root/singbox-eps-node/config.json'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\nconfig.json验证: {stdout.read().decode().strip()}")
    
    # 5. 获取新订阅
    code = 'JP' if name == '日本' else 'SG'
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality"'
    stdin, stdout, stderr = c.exec_command(cmd)
    link = stdout.read().decode().strip()
    print(f"\n新订阅REALITY: {link[:150]}...")
    
    c.close()

print("\n全部完成")
