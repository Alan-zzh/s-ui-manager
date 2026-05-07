import sys
import io
from audit_config import get_server
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

srv = get_server('jp')
print("=== 日本服务器详细检查 ===")

with ssh_connect(srv) as c:
    cmd = 'systemctl status singbox-sub --no-pager -l 2>&1 | head -30'
    out, err = run_command(c, cmd)
    print("\n【订阅服务状态】")
    print(out)

    cmd = 'grep COUNTRY_CODE /root/singbox-eps-node/.env'
    out, err = run_command(c, cmd)
    print("\n【COUNTRY_CODE】")
    print(out)

    cmd = 'grep -n "@app.route" /root/singbox-eps-node/scripts/subscription_service.py | head -20'
    out, err = run_command(c, cmd)
    print("\n【路由定义】")
    print(out)

    cmd = 'journalctl -u singbox-sub --no-pager -n 30 2>&1 | tail -20'
    out, err = run_command(c, cmd)
    print("\n【订阅服务日志】")
    print(out)

    cmd = 'curl -svk https://localhost:2087/sub/JP 2>&1 | head -30'
    out, err = run_command(c, cmd)
    print("\n【订阅测试详细】")
    print(out)
