import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    print(f"\n{'='*60}")
    print(f"=== {name} ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
        cmd = 'ss -tnp | grep sing-box | awk "{print $5}" | cut -d: -f1 | sort | uniq -c | sort -rn'
        out, err = run_command(c, cmd)
        print("【连接来源IP统计】")
        print(out)

        cmd = 'grep "REALITY" /var/log/singbox.log | tail -100 | grep -c "invalid"'
        out, err = run_command(c, cmd)
        print(f"\nREALITY失败连接数（最近100条）: {out.strip()}")

        cmd = 'grep "REALITY" /var/log/singbox.log | tail -100 | grep -c "inbound connection"'
        out, err = run_command(c, cmd)
        print(f"REALITY总连接数（最近100条）: {out.strip()}")

        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | grep "reality"'
        out, err = run_command(c, cmd)
        print("\n【当前订阅中的REALITY配置】")
        reality_link = out.strip()
        print(reality_link[:200] if reality_link else "无")

        if reality_link and 'pbk=' in reality_link:
            pbk = reality_link.split('pbk=')[1].split('&')[0]
            print(f"\n当前公钥: {pbk}")

        cmd = 'grep REALITY_PUBLIC_KEY /root/singbox-eps-node/.env'
        out, err = run_command(c, cmd)
        print(f"\n服务器公钥配置: {out.strip()}")

print("\n全部完成")
