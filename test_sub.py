import paramiko

def test_sub(name, ip, password, code):
    print(f"\n=== {name} ({ip}) ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 用大写获取订阅内容
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null | head -20'
    stdin, stdout, stderr = c.exec_command(cmd)
    content = stdout.read().decode()
    print(f"\n【订阅内容】")
    print(content[:800] if content else "空")
    
    # 检查是否有CDN IP
    if '104.' in content or '173.' in content or '172.' in content:
        print("\n✅ 订阅包含CDN IP")
    else:
        print("\n❌ 订阅不包含CDN IP，可能用的服务器IP")
    
    c.close()

test_sub('日本', '52.195.179.240', 'je*pMaN8QNfCMK', 'JP')
test_sub('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com', 'SG')
