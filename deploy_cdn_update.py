import os
from audit_config import get_server
from ssh_utils import ssh_connect, run_command

srv = get_server('jp_old')
REMOTE_DIR = '/root/singbox-eps-node/scripts'

def upload_file(ssh_client, local_path, remote_path):
    sftp = ssh_client.open_sftp()
    filename = os.path.basename(local_path)
    remote_file = f"{REMOTE_DIR}/{filename}"
    print(f"  上传: {filename}")
    sftp.put(local_path, remote_file)
    sftp.close()
    return remote_file

try:
    with ssh_connect(srv) as ssh:
        print(f">>> 连接服务器 {srv['host']}...")
        print("[OK] 连接成功")

        files_to_upload = [
            'cdn_monitor.py',
            'config.py',
        ]

        print("\n>>> 上传文件:")
        for f in files_to_upload:
            local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'singbox-eps-node', 'scripts', f)
            upload_file(ssh, local_path, f"{REMOTE_DIR}/{f}")
        print("[OK] 所有文件已上传")

        print("\n>>> 备份旧版本...")
        run_command(ssh, f"cp {REMOTE_DIR}/cdn_monitor.py {REMOTE_DIR}/cdn_monitor.py.bak.v2.0.0")
        run_command(ssh, f"cp {REMOTE_DIR}/config.py {REMOTE_DIR}/config.py.bak.v2.0.0")

        print("\n>>> 测试 cdn_monitor.py 单次运行...")
        out, err = run_command(ssh, f"cd {REMOTE_DIR} && python3 -c \"import cdn_monitor; cdn_monitor.init_db(); cdn_monitor.run_once()\"", timeout=120)
        print("\n--- 输出 ---")
        print(out.strip())
        if err.strip():
            print("\n--- 错误 ---")
            print(err.strip())

        print("\n>>> 检查数据库中的CDN IP...")
        out2, err2 = run_command(ssh, f"cd {REMOTE_DIR} && python3 -c \"import sqlite3; conn=sqlite3.connect('/root/singbox-eps-node/data/singbox.db'); cur=conn.cursor(); cur.execute('SELECT * FROM cdn_settings'); rows=cur.fetchall(); [print(r) for r in rows]; conn.close()\"")
        print("\n--- 数据库记录 ---")
        print(out2.strip())
        if err2.strip():
            print("\n--- 错误 ---")
            print(err2.strip())

    print("\n[OK] 全部完成")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
