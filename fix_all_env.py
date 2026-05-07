from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== 修复 {srv['name']} 环境变量 ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
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
        out, err = run_command(c, cmd)
        print(f"singbox状态: {out.strip()}")

        cmd = 'ENABLE_DEPRECATED_LEGACY_DNS_SERVERS=true ENABLE_DEPRECATED_MISSING_DOMAIN_RESOLVER=true /usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1'
        out, err = run_command(c, cmd)
        check_out = out.strip()
        if 'valid' in check_out.lower() or check_out == '':
            print("✅ 配置语法正确")
        else:
            print(f"⚠️ {check_out}")

print("\n全部修复完成")
