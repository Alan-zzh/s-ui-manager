from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== 更新 {srv['name']} REALITY密钥 ===")
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
            print(f"❌ 密钥生成失败: {out}")
            continue

        print(f"✅ 新私钥: {private_key[:20]}...")
        print(f"✅ 新公钥: {public_key}")

        cmd = f"""cd /root/singbox-eps-node
sed -i 's|REALITY_PRIVATE_KEY=.*|REALITY_PRIVATE_KEY={private_key}|' .env
sed -i 's|REALITY_PUBLIC_KEY=.*|REALITY_PUBLIC_KEY={public_key}|' .env
echo "OK"
"""
        out, err = run_command(c, cmd)
        print(f"✅ .env已更新")

        cmd = 'cd /root/singbox-eps-node && python3 scripts/config_generator.py'
        out, err = run_command(c, cmd)
        print(f"✅ config.json已重新生成")

        cmd = 'grep -A 2 "private_key" /root/singbox-eps-node/config.json | head -3'
        out, err = run_command(c, cmd)
        print(f"✅ 配置验证: {out.strip()}")

        cmd = 'systemctl restart singbox && sleep 2 && systemctl is-active singbox'
        out, err = run_command(c, cmd)
        status = out.strip()
        print(f"✅ singbox状态: {status}")

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality" | head -1'
        out, err = run_command(c, cmd)
        link = out.strip()
        if link and 'pbk=' in link:
            pbk = link.split('pbk=')[1].split('&')[0]
            print(f"✅ 订阅公钥: {pbk}")
            if pbk == public_key:
                print("✅ 公钥匹配正确")
            else:
                print("⚠️ 公钥不匹配，需要检查")

    print(f"{'='*60}")
    print(f"=== {srv['name']} 更新完成 ===")
    print(f"{'='*60}")

print("\n全部更新完成")
