import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    ip = srv['host']
    print(f"\n=== {name} ({ip}) ===")

    with ssh_connect(srv) as c:
        cmd = 'wc -l /root/singbox-eps-node/scripts/cdn_monitor.py'
        out, err = run_command(c, cmd)
        print(f"服务器文件行数: {out.strip()}")

        local_lines = len(open(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\cdn_monitor.py', 'r', encoding='utf-8').readlines())
        print(f"本地文件行数: {local_lines}")

        cmd = 'tail -5 /root/singbox-eps-node/scripts/cdn_monitor.py'
        out, err = run_command(c, cmd)
        print(f"服务器文件末尾: {out.strip()}")

        cmd = 'cd /root/singbox-eps-node && python3 -c "import scripts.cdn_monitor; print(\'OK\')" 2>&1'
        out, err = run_command(c, cmd)
        print(f"导入测试: {out.strip() if out.strip() else err.strip()}")
