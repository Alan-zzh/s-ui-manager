import paramiko

# 连接服务器
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('54.250.149.157', 22, 'root', 'oroVIG38@jh.dxclouds.com', timeout=30)

print("=" * 60)
print("配置Hysteria2端口跳跃")
print("=" * 60)

# 配置iptables端口转发
print("\n【1】配置iptables端口转发...")
commands = [
    # 清除现有规则
    'iptables -t nat -F',
    # 添加端口转发规则（20000-50000端口转发到4433）
    'iptables -t nat -A PREROUTING -p udp --dport 20000:50000 -j REDIRECT --to-ports 4433',
    # 保存规则
    'iptables-save > /etc/iptables/rules.v4',
    # 查看规则
    'iptables -t nat -L PREROUTING -n'
]

for cmd in commands:
    print(f"执行: {cmd}")
    stdin, stdout, stderr = c.exec_command(cmd)
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    print(output)
    if error:
        print(f"错误: {error}")
    print()

# 更新Hysteria2配置
print("\n【2】更新Hysteria2配置...")
update_script = '''
import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('/usr/local/s-ui/db/s-ui.db')
cursor = conn.cursor()

# 更新Hysteria2配置
print("更新Hysteria2配置...")
hysteria2_out = json.dumps({
    "type": "hysteria2",
    "tag": "hysteria2",
    "listen": "0.0.0.0",
    "listen_port": 4433,
    "users": [{
        "password": "hysteria2-password-123"
    }],
    "quic": {
        "init_max_streams_bidi": 100
    }
}).encode('utf-8')

cursor.execute("UPDATE inbounds SET out_json = ? WHERE tag = 'hysteria2'", (hysteria2_out,))

# 提交并关闭
conn.commit()
conn.close()
print("Hysteria2配置已更新")
'''

# 写入并执行更新脚本
with c.open_sftp() as sftp:
    with sftp.file('/tmp/update_hysteria2.py', 'w') as f:
        f.write(update_script)

stdin, stdout, stderr = c.exec_command('python3 /tmp/update_hysteria2.py')
output = stdout.read().decode().strip()
error = stderr.read().decode().strip()
print(output)
if error:
    print(f"错误: {error}")

# 重启S-UI服务
print("\n【3】重启S-UI服务...")
stdin, stdout, stderr = c.exec_command('systemctl restart s-ui.service')
stdout.read()

# 检查服务状态
print("\n【4】检查服务状态...")
stdin, stdout, stderr = c.exec_command('systemctl status s-ui.service --no-pager')
output = stdout.read().decode().strip()
print(output)

# 检查端口
print("\n【5】检查端口...")
stdin, stdout, stderr = c.exec_command('ss -tlnp | grep -E "sui|4433"')
output = stdout.read().decode().strip()
print(output)

# 检查iptables规则
print("\n【6】检查iptables规则...")
stdin, stdout, stderr = c.exec_command('iptables -t nat -L PREROUTING -n')
output = stdout.read().decode().strip()
print(output)

c.close()
print("\nHysteria2端口跳跃配置完成！")
