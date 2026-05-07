from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

with open(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\subscription_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

for srv in get_servers():
    print(f"\n{'='*50}")
    print(f"=== {srv['name']} ({srv['host']}) ===")
    print(f"{'='*50}")

    with ssh_connect(srv) as c:
        cmd = f'cat > /root/singbox-eps-node/scripts/subscription_service.py << \'ENDOFILE\'\n{content}\nENDOFILE'
        out, err = run_command(c, cmd)
        print(f"subscription_service.py: {'已同步' if not err else '失败: ' + err[:100]}")

        cmd = 'systemctl restart singbox-sub && echo "重启成功" || echo "重启失败"'
        out, err = run_command(c, cmd)
        print(f"重启singbox-sub: {out.strip()}")

        cmd = 'curl -sk https://localhost:2087/sub/sg -o /dev/null -w "HTTP: %{http_code}" 2>&1'
        out, err = run_command(c, cmd)
        print(f"小写/sub/sg: {out.strip()}")

        cmd = 'curl -sk https://localhost:2087/sub/SG -o /dev/null -w "HTTP: %{http_code}" 2>&1'
        out, err = run_command(c, cmd)
        print(f"大写/sub/SG: {out.strip()}")

        cmd = 'ss -tlnp | grep -E "443|8443|2053|2083"'
        out, err = run_command(c, cmd)
        print(f"\n【核心端口监听】")
        print(out)

        cmd = 'journalctl -u singbox --no-pager -n 50 2>&1 | grep -iE "error|fail|warn" | tail -10'
        out, err = run_command(c, cmd)
        print(f"\n【singbox错误日志】")
        print(out if out else "无错误")

        cmd = 'curl -sk https://localhost:2087/sub/sg 2>&1 | base64 -d 2>/dev/null | wc -l'
        out, err = run_command(c, cmd)
        print(f"\n【订阅节点数】")
        print(out)

print("\n全部完成")
