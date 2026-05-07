import paramiko

def check_protocols(name, ip, password):
    print(f"\n=== {name} ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查singbox服务状态
    cmd = 'systemctl is-active singbox'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"singbox服务: {stdout.read().decode().strip()}")
    
    # 2. 检查CPU和内存
    cmd = 'top -bn1 | head -5'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【系统负载】")
    print(stdout.read().decode())
    
    # 3. 检查sing-box进程内存
    cmd = 'ps aux | grep sing-box | grep -v grep'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【sing-box进程】")
    print(stdout.read().decode())
    
    # 4. 检查网络延迟
    cmd = 'ping -c 3 8.8.8.8 2>&1 | tail -2'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【网络延迟】")
    print(stdout.read().decode())
    
    # 5. 检查磁盘IO
    cmd = 'iostat -x 1 1 2>&1 | tail -5'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【磁盘IO】")
    print(stdout.read().decode())
    
    # 6. 检查连接数
    cmd = 'ss -s 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【连接统计】")
    print(stdout.read().decode())
    
    # 7. 检查singbox最近错误
    cmd = 'journalctl -u singbox --no-pager -n 100 2>&1 | grep -iE "error|fail|close|reset|timeout" | tail -10'
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode()
    print(f"\n【singbox错误】")
    print(out if out else "无错误")
    
    # 8. 检查HY2端口跳跃配置
    cmd = 'iptables -t nat -L -n -v 2>&1 | head -20'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n【iptables端口跳跃】")
    print(stdout.read().decode())
    
    c.close()

check_protocols('日本', '52.195.179.240', 'je*pMaN8QNfCMK')
check_protocols('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com')
