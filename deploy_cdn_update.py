#!/usr/bin/env python3
import paramiko
import sys
import os

SERVER = '54.250.149.157'
USERNAME = 'root'
PASSWORD = 'oroVIG38@jh.dxclouds.com'
REMOTE_DIR = '/root/singbox-eps-node/scripts'

def upload_file(ssh_client, local_path, remote_path):
    """上传单个文件"""
    sftp = ssh_client.open_sftp()
    filename = os.path.basename(local_path)
    remote_file = f"{REMOTE_DIR}/{filename}"
    print(f"  上传: {filename}")
    sftp.put(local_path, remote_file)
    sftp.close()
    return remote_file

def run_cmd(ssh, cmd, timeout=60):
    """执行远程命令"""
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
    run_cmd(ssh, f"cp {REMOTE_DIR}/cdn_monitor.py {REMOTE_DIR}/cdn_monitor.py.bak.v2.0.0")
    run_cmd(ssh, f"cp {REMOTE_DIR}/config.py {REMOTE_DIR}/config.py.bak.v2.0.0")

    print("\n>>> 测试 cdn_monitor.py 单次运行...")
    out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && python3 -c \"import cdn_monitor; cdn_monitor.init_db(); cdn_monitor.run_once()\"", timeout=120)
    print("\n--- 输出 ---")
    print(out)
    if err:
        print("\n--- 错误 ---")
        print(err)

    print("\n>>> 检查数据库中的CDN IP...")
    out2, err2 = run_cmd(ssh, f"cd {REMOTE_DIR} && python3 -c \"import sqlite3; conn=sqlite3.connect('/root/singbox-eps-node/data/singbox.db'); cur=conn.cursor(); cur.execute('SELECT * FROM cdn_settings'); rows=cur.fetchall(); [print(r) for r in rows]; conn.close()\"")
    print("\n--- 数据库记录 ---")
    print(out2)
    if err2:
        print("\n--- 错误 ---")
        print(err2)

    ssh.close()
    print("\n[OK] 全部完成")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
