from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== 修复 {srv['name']} DNS配置 ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
        cmd = '/usr/local/bin/sing-box version 2>/dev/null | head -1'
        out, err = run_command(c, cmd)
        version = out.strip()
        print(f"sing-box版本: {version}")

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
        out, err = run_command(c, cmd)
        print(f"结果: {out.strip()}")

        print("\n2. 重启singbox...")
        cmd = 'systemctl restart singbox && sleep 2 && systemctl is-active singbox'
        out, err = run_command(c, cmd)
        print(f"状态: {out.strip()}")

        print("\n3. 验证配置语法...")
        cmd = 'ENABLE_DEPRECATED_LEGACY_DNS_SERVERS=true /usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1'
        out, err = run_command(c, cmd)
        check_out = out.strip()
        if 'valid' in check_out.lower() or check_out == '':
            print("✅ 配置语法正确")
        else:
            print(f"⚠️ {check_out}")

        print("\n4. 检查日志...")
        cmd = 'sleep 1 && tail -5 /var/log/singbox.log'
        out, err = run_command(c, cmd)
        print(out)

    print(f"\n{'='*60}")
    print(f"=== {srv['name']} 修复完成 ===")
    print(f"{'='*60}")

print("\n全部修复完成")
