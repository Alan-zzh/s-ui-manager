import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('13.212.37.11', username='root', password='jbfCMP75@jh.dxclouds.com', timeout=15)

# 1. 检查.env
cmd = 'grep REALITY /root/singbox-eps-node/.env'
stdin, stdout, stderr = c.exec_command(cmd)
print("【.env】")
print(stdout.read().decode())

# 2. 检查config.json
cmd = 'grep -A 3 "private_key" /root/singbox-eps-node/config.json'
stdin, stdout, stderr = c.exec_command(cmd)
print("\n【config.json】")
print(stdout.read().decode())

# 3. 手动运行config_generator
cmd = 'cd /root/singbox-eps-node && python3 scripts/config_generator.py && echo "OK" || echo "FAIL"'
stdin, stdout, stderr = c.exec_command(cmd)
print(f"\n【config_generator输出】")
print(stdout.read().decode())

# 4. 再次检查config.json
cmd = 'grep -A 3 "private_key" /root/singbox-eps-node/config.json'
stdin, stdout, stderr = c.exec_command(cmd)
print(f"\n【config.json更新后】")
print(stdout.read().decode())

# 5. 重启singbox
cmd = 'systemctl restart singbox && echo "OK" || echo "FAIL"'
stdin, stdout, stderr = c.exec_command(cmd)
print(f"\n重启singbox: {stdout.read().decode().strip()}")

c.close()
