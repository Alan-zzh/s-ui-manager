#!/usr/bin/env python3
"""同步服务器上的 HY2 端口跳跃为正确的范围 21000-21200"""
import paramiko
import base64

SERVER_HOST = "43.159.168.175"
SERVER_PORT = 22
SERVER_PASS = "&L5Td^!^#m@X3B"

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    return exit_code, out, err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_HOST, SERVER_PORT, "root", SERVER_PASS, timeout=15, allow_agent=False, look_for_keys=False)

print("清除错误的端口跳跃规则 (14430-14629)...")
run_cmd(client, "iptables -t nat -D PREROUTING -p udp --dport 14430:14629 -j REDIRECT --to-port 443 2>/dev/null || true")
run_cmd(client, "iptables -t nat -D PREROUTING -p tcp --dport 14430:14629 -j REDIRECT --to-port 443 2>/dev/null || true")

print("执行 cert_manager.py --setup-iptables（正确的 21000-21200）...")
_, out, err = run_cmd(client, "cd /root/singbox-eps-node && python3 scripts/cert_manager.py --setup-iptables 2>&1", timeout=60)
print(out)

print("\n验证:")
_, out, _ = run_cmd(client, "iptables -t nat -L PREROUTING -n --line-numbers | head -10")
print(out)

_, out, _ = run_cmd(client, "iptables -t nat -L PREROUTING -n | wc -l")
print(f"PREROUTING 规则总数: {out.strip()}")

client.close()
