import sys
import io
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for srv in get_servers():
    name = srv['name']
    with ssh_connect(srv) as c:
        out, err = run_command(c, 'cat /root/singbox-eps-node/.env')
        print(f"【{name} .env】")
        print(out)
