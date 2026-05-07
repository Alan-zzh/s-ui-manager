from audit_config import get_server
from ssh_utils import ssh_connect, run_command

srv = get_server('sg')
with ssh_connect(srv) as c:
    cmd = 'grep REALITY /root/singbox-eps-node/.env'
    out, err = run_command(c, cmd)
    print("【.env】")
    print(out)

    cmd = 'grep -A 3 "private_key" /root/singbox-eps-node/config.json'
    out, err = run_command(c, cmd)
    print("\n【config.json】")
    print(out)

    cmd = 'cd /root/singbox-eps-node && python3 scripts/config_generator.py && echo "OK" || echo "FAIL"'
    out, err = run_command(c, cmd)
    print(f"\n【config_generator输出】")
    print(out)

    cmd = 'grep -A 3 "private_key" /root/singbox-eps-node/config.json'
    out, err = run_command(c, cmd)
    print(f"\n【config.json更新后】")
    print(out)

    cmd = 'systemctl restart singbox && echo "OK" || echo "FAIL"'
    out, err = run_command(c, cmd)
    print(f"\n重启singbox: {out.strip()}")
