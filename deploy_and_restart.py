#!/usr/bin/env python3
import paramiko
import sys
import os

SERVER = '54.250.149.157'
USERNAME = 'root'
PASSWORD = 'oroVIG38@jh.dxclouds.com'
REMOTE_DIR = '/root/singbox-eps-node/scripts'

def upload_file(ssh_client, local_path, remote_path):
    sftp = ssh_client.open_sftp()
    filename = os.path.basename(local_path)
    remote_file = f"{REMOTE_DIR}/{filename}"
    print(f"  上传: {filename}")
    sftp.put(local_path, remote_file)
    sftp.close()

def run_cmd(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f">>> 连接服务器 {SERVER}...")
    ssh.connect(SERVER, username=USERNAME, password=PASSWORD, timeout=10)
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
    run_cmd(ssh, f"cp {REMOTE_DIR}/cdn_monitor.py {REMOTE_DIR}/cdn_monitor.py.bak.v2.1.0")
    run_cmd(ssh, f"cp {REMOTE_DIR}/config.py {REMOTE_DIR}/config.py.bak.v2.1.0")

    print("\n>>> 重启 singbox-cdn 服务...")
    out, err = run_cmd(ssh, "systemctl restart singbox-cdn")
    if err:
        print(f"  [WARN] {err}")
    else:
        print("[OK] 服务已重启")

    print("\n>>> 检查服务状态...")
    out, err = run_cmd(ssh, "systemctl is-active singbox-cdn")
    print(f"  singbox-cdn 状态: {out}")

    print("\n>>> 检查数据库当前CDN IP...")
    out2, _ = run_cmd(ssh, f"cd {REMOTE_DIR} && python3 -c \"import sqlite3; conn=sqlite3.connect('/root/singbox-eps-node/data/singbox.db'); cur=conn.cursor(); cur.execute('SELECT * FROM cdn_settings'); rows=cur.fetchall(); [print(f'  {r[0]}: {r[1]}') for r in rows]; conn.close()\"")
    print("\n" + out2)

    ssh.close()
    print("\n[OK] 部署完成")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
