import paramiko

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

for name, ip, password in servers:
    print(f"\n{'='*50}")
    print(f"=== {name} ===")
    print(f"{'='*50}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 直接读取config.json
    cmd = 'cat /root/singbox-eps-node/config.json'
    stdin, stdout, stderr = c.exec_command(cmd)
    config_json = stdout.read().decode()
    
    # 保存到本地分析
    with open(f'config_{name}.json', 'w', encoding='utf-8') as f:
        f.write(config_json)
    
    print(f"config.json已保存到本地: config_{name}.json")
    print(f"文件大小: {len(config_json)} 字节")
    
    c.close()

print("\n全部完成")
