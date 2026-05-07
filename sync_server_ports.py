from audit_config import get_server
from ssh_utils import ssh_connect, run_command

srv = get_server('other')

with ssh_connect(srv) as client:
    print("清除错误的端口跳跃规则 (14430-14629)...")
    run_command(client, "iptables -t nat -D PREROUTING -p udp --dport 14430:14629 -j REDIRECT --to-port 443 2>/dev/null || true")
    run_command(client, "iptables -t nat -D PREROUTING -p tcp --dport 14430:14629 -j REDIRECT --to-port 443 2>/dev/null || true")

    print("执行 cert_manager.py --setup-iptables（正确的 21000-21200）...")
    out, err = run_command(client, "cd /root/singbox-eps-node && python3 scripts/cert_manager.py --setup-iptables 2>&1", timeout=60)
    print(out)

    print("\n验证:")
    out, err = run_command(client, "iptables -t nat -L PREROUTING -n --line-numbers | head -10")
    print(out)

    out, err = run_command(client, "iptables -t nat -L PREROUTING -n | wc -l")
    print(f"PREROUTING 规则总数: {out.strip()}")
