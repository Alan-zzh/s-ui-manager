from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    code = 'JP' if srv['name'] == '日本' else 'SG'
    print(f"\n=== {srv['name']} ({srv['host']}) ===")

    with ssh_connect(srv) as c:
        cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | head -20'
        out, err = run_command(c, cmd)
        print(f"\n【订阅内容】")
        print(out[:800] if out else "空")

        if '104.' in out or '173.' in out or '172.' in out:
            print("\n✅ 订阅包含CDN IP")
        else:
            print("\n❌ 订阅不包含CDN IP，可能用的服务器IP")
