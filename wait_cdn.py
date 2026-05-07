import time
from audit_config import get_server
from ssh_utils import ssh_connect, run_command

srv = get_server('jp')

with ssh_connect(srv) as c:
    print("等待 singbox-cdn 启动...")
    for i in range(30):
        cmd = 'systemctl is-active singbox-cdn'
        out, err = run_command(c, cmd)
        status = out.strip()
        if status == 'active':
            print(f"✅ singbox-cdn 已启动（{i+1}秒）")
            break
        else:
            print(f"  状态: {status} ({i+1}秒)")
            time.sleep(1)
    else:
        print("❌ singbox-cdn 启动超时")
        cmd = 'journalctl -u singbox-cdn --no-pager -n 10'
        out, err = run_command(c, cmd)
        print("日志:")
        print(out)
