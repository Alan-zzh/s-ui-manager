#!/usr/bin/env python3
import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('54.250.149.157', 22, 'root', 'oroVIG38@jh.dxclouds.com', timeout=30)

# 查找数据库文件
cmds = [
    'find / -name "*.db" -type f 2>/dev/null | grep -i s-ui',
    'find / -name "*.db" -type f 2>/dev/null | grep -i x-ui',
    'ls -la /etc/s-ui/ 2>/dev/null || echo "NO_SUI_DIR"',
    'ls -la /etc/x-ui/ 2>/dev/null || echo "NO_XUI_DIR"',
    'ls -la /usr/local/s-ui/ 2>/dev/null || echo "NO_LOCAL_SUI"',
    'systemctl list-units --type=service | grep -E "(s-ui|x-ui)"',
    'cat /etc/systemd/system/s-ui.service 2>/dev/null | grep -E "(ExecStart|DBPath)" || echo "NO_SUI_SERVICE"',
    'cat /etc/systemd/system/x-ui.service 2>/dev/null | grep -E "(ExecStart|DBPath)" || echo "NO_XUI_SERVICE"',
]

for cmd in cmds:
    print(f"\n命令: {cmd}")
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"输出: {out if out else '(无输出)'}")
    if err:
        print(f"错误: {err}")

c.close()
