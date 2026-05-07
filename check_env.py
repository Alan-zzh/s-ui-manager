import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('13.212.37.11', username='root', password='jbfCMP75@jh.dxclouds.com', timeout=15)

# 检查.env
cmd = 'cat /root/singbox-eps-node/.env'
stdin, stdout, stderr = c.exec_command(cmd)
print("【新加坡 .env】")
print(stdout.read().decode())

# 检查日本.env
c2 = paramiko.SSHClient()
c2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c2.connect('52.195.179.240', username='root', password='je*pMaN8QNfCMK', timeout=15)

cmd = 'cat /root/singbox-eps-node/.env'
stdin, stdout, stderr = c2.exec_command(cmd)
print("\n【日本 .env】")
print(stdout.read().decode())

c.close()
c2.close()
