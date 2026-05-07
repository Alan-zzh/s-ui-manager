import paramiko, time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('52.195.179.240', username='root', password='je*pMaN8QNfCMK', timeout=15)

print("等待 singbox-cdn 启动...")
for i in range(30):
    cmd = 'systemctl is-active singbox-cdn'
    stdin, stdout, stderr = c.exec_command(cmd)
    status = stdout.read().decode().strip()
    if status == 'active':
        print(f"✅ singbox-cdn 已启动（{i+1}秒）")
        break
    else:
        print(f"  状态: {status} ({i+1}秒)")
        time.sleep(1)
else:
    print("❌ singbox-cdn 启动超时")
    # 检查日志
    cmd = 'journalctl -u singbox-cdn --no-pager -n 10'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("日志:")
    print(stdout.read().decode())

c.close()
