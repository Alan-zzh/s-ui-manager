from audit_config import get_server
from ssh_utils import ssh_connect, run_command

cmd = """cd /root/singbox-eps-node
sed -i 's/CF_DOMAIN=us.290372913.xyz/CF_DOMAIN=sg.290372913.xyz/' .env
echo "修复完成"
grep CF_DOMAIN .env
"""

srv = get_server('sg')
with ssh_connect(srv) as c:
    out, err = run_command(c, cmd)
    print(f"新加坡CF_DOMAIN修复: {out.strip()}")

    for svc in ['singbox-cdn', 'singbox-sub', 'singbox']:
        cmd = f'systemctl restart {svc} && echo "OK" || echo "FAIL"'
        out, err = run_command(c, cmd)
        print(f"重启{svc}: {out.strip()}")

    cmd = 'curl -sk https://localhost:2087/sub/SG 2>&1 | base64 -d 2>/dev/null'
    out, err = run_command(c, cmd)
    content = out
    print("\n【新订阅内容】")
    for line in content.split('\n'):
        if line.strip():
            if '#' in line:
                name = line.split('#')[-1]
                if 'sni=' in line:
                    sni = line.split('sni=')[1].split('&')[0]
                else:
                    sni = '无'
                print(f"  {name} (SNI: {sni})")
