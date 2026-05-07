import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== 修复 {name} 环境变量 ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 更新systemd服务，添加所有需要的环境变量
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
Environment="ENABLE_DEPRECATED_MISSING_DOMAIN_RESOLVER=true"
ExecStart=/usr/local/bin/sing-box run -c /root/singbox-eps-node/config.json
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl restart singbox
sleep 2
systemctl is-active singbox
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"singbox状态: {stdout.read().decode().strip()}")
    
    # 验证配置
    cmd = 'ENABLE_DEPRECATED_LEGACY_DNS_SERVERS=true ENABLE_DEPRECATED_MISSING_DOMAIN_RESOLVER=true /usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    check_out = stdout.read().decode().strip()
    if 'valid' in check_out.lower() or check_out == '':
        print("✅ 配置语法正确")
    else:
        print(f"⚠️ {check_out}")
    
    c.close()

print("\n全部修复完成")
