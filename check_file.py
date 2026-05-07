import paramiko

def check_file(name, ip, password):
    print(f"\n=== {name} ({ip}) ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 检查文件大小
    cmd = 'wc -l /root/singbox-eps-node/scripts/cdn_monitor.py'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"服务器文件行数: {stdout.read().decode().strip()}")
    
    # 检查本地文件大小
    local_lines = len(open(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\cdn_monitor.py', 'r', encoding='utf-8').readlines())
    print(f"本地文件行数: {local_lines}")
    
    # 检查服务器文件最后几行
    cmd = 'tail -5 /root/singbox-eps-node/scripts/cdn_monitor.py'
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"服务器文件末尾: {stdout.read().decode().strip()}")
    
    # 检查是否有语法错误
    cmd = 'cd /root/singbox-eps-node && python3 -c "import scripts.cdn_monitor; print(\'OK\')" 2>&1'
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"导入测试: {out if out else err}")
    
    c.close()

check_file('日本', '52.195.179.240', 'je*pMaN8QNfCMK')
check_file('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com')
