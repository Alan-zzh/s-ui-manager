import paramiko

def check_jp(ip, password):
    print("=== 日本服务器详细检查 ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 检查订阅服务状态
    cmd = 'systemctl status singbox-sub --no-pager -l 2>&1 | head -30'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【订阅服务状态】")
    print(stdout.read().decode())
    
    # 2. 检查.env中的COUNTRY_CODE
    cmd = 'grep COUNTRY_CODE /root/singbox-eps-node/.env'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【COUNTRY_CODE】")
    print(stdout.read().decode())
    
    # 3. 检查subscription_service.py路由
    cmd = 'grep -n "@app.route" /root/singbox-eps-node/scripts/subscription_service.py | head -20'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【路由定义】")
    print(stdout.read().decode())
    
    # 4. 检查订阅服务日志
    cmd = 'journalctl -u singbox-sub --no-pager -n 30 2>&1 | tail -20'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【订阅服务日志】")
    print(stdout.read().decode())
    
    # 5. 直接测试订阅
    cmd = 'curl -svk https://localhost:2087/sub/JP 2>&1 | head -30'
    stdin, stdout, stderr = c.exec_command(cmd)
    print("\n【订阅测试详细】")
    print(stdout.read().decode())
    
    c.close()

check_jp('52.195.179.240', 'je*pMaN8QNfCMK')
