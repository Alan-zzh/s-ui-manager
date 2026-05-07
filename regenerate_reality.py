from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== {srv['name']} ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
        cmd = '/usr/local/bin/sing-box generate reality-keypair'
        out, err = run_command(c, cmd)

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
            continue

        print(f"新私钥: {private_key[:20]}...")
        print(f"新公钥: {public_key}")

        cmd = f"""cd /root/singbox-eps-node
sed -i 's|REALITY_PRIVATE_KEY=.*|REALITY_PRIVATE_KEY={private_key}|' .env
sed -i 's|REALITY_PUBLIC_KEY=.*|REALITY_PUBLIC_KEY={public_key}|' .env
echo "env已更新"
grep REALITY .env
"""
        out, err = run_command(c, cmd)
        print(f"\n.env更新: {out.strip()}")

        cmd = 'systemctl restart singbox && echo "OK" || echo "FAIL"'
        out, err = run_command(c, cmd)
        print(f"\n重启singbox: {out.strip()}")

        cmd = 'sleep 2 && grep -A 3 "private_key" /root/singbox-eps-node/config.json'
        out, err = run_command(c, cmd)
        print(f"\nconfig.json验证: {out.strip()}")

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality"'
        out, err = run_command(c, cmd)
        link = out.strip()
        print(f"\n新订阅REALITY: {link[:150]}...")

print("\n全部完成")
