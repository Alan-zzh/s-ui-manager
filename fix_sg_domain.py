import paramiko

# 修复新加坡.env
cmd = """cd /root/singbox-eps-node
sed -i 's/CF_DOMAIN=us.290372913.xyz/CF_DOMAIN=sg.290372913.xyz/' .env
echo "修复完成"
grep CF_DOMAIN .env
"""

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('13.212.37.11', username='root', password='jbfCMP75@jh.dxclouds.com', timeout=15)

stdin, stdout, stderr = c.exec_command(cmd)
print(f"新加坡CF_DOMAIN修复: {stdout.read().decode().strip()}")

# 重启所有服务
for svc in ['singbox-cdn', 'singbox-sub', 'singbox']:
    cmd = f'systemctl restart {svc} && echo "OK" || echo "FAIL"'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"重启{svc}: {stdout.read().decode().strip()}")

# 验证订阅
cmd = 'curl -sk https://localhost:2087/sub/SG 2>&1 | base64 -d 2>/dev/null'
stdin, stdout, stderr = c.exec_command(cmd)
content = stdout.read().decode()
print("\n【新订阅内容】")
for line in content.split('\n'):
    if line.strip():
        # 提取节点名
        if '#' in line:
            name = line.split('#')[-1]
            # 提取SNI
            if 'sni=' in line:
                sni = line.split('sni=')[1].split('&')[0]
            else:
                sni = '无'
            print(f"  {name} (SNI: {sni})")

c.close()
