import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== 修复 {name} DNS配置 ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查sing-box版本
    cmd = '/usr/local/bin/sing-box version 2>/dev/null | head -1'
    stdin, stdout, stderr = c.exec_command(cmd)
    version = stdout.read().decode().strip()
    print(f"sing-box版本: {version}")
    
    # 2. 更新systemd服务文件，添加环境变量
    print("\n1. 更新systemd服务...")
    cmd = """
cat > /etc/systemd/system/singbox.service << 'EOF'
[Unit]
Description=Singbox Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/singbox-eps-node
Environment="ENABLE_DEPRECATED_LEGACY_DNS_SERVERS=true"
ExecStart=/usr/local/bin/sing-box run -c /root/singbox-eps-node/config.json
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
echo "OK"
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"结果: {stdout.read().decode().strip()}")
    
    # 3. 重启singbox
    print("\n2. 重启singbox...")
    cmd = 'systemctl restart singbox && sleep 2 && systemctl is-active singbox'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"状态: {stdout.read().decode().strip()}")
    
    # 4. 验证配置
    print("\n3. 验证配置语法...")
    cmd = 'ENABLE_DEPRECATED_LEGACY_DNS_SERVERS=true /usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    check_out = stdout.read().decode().strip()
    if 'valid' in check_out.lower() or check_out == '':
        print("✅ 配置语法正确")
    else:
        print(f"⚠️ {check_out}")
    
    # 5. 检查日志
    print("\n4. 检查日志...")
    cmd = 'sleep 1 && tail -5 /var/log/singbox.log'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(stdout.read().decode())
    
    c.close()
    print(f"\n{'='*60}")
    print(f"=== {name} 修复完成 ===")
    print(f"{'='*60}")

print("\n全部修复完成")
