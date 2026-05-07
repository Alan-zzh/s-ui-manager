import paramiko

def test(name, ip, password, code):
    print(f"\n=== {name} ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 测试大小写
    for path in [f'/sub/{code}', f'/sub/{code.lower()}', f'/singbox/{code}', f'/singbox/{code.lower()}']:
        cmd = f'curl -sk https://localhost:2087{path} -o /dev/null -w "HTTP: %{{http_code}}" 2>&1'
        stdin, stdout, stderr = c.exec_command(cmd)
        print(f"  {path}: {stdout.read().decode().strip()}")
    
    # 获取订阅内容看CDN IP
    cmd = f'curl -sk https://localhost:2087/sub/{code} 2>&1 | base64 -d 2>/dev/null'
    stdin, stdout, stderr = c.exec_command(cmd)
    content = stdout.read().decode()
    lines = [l for l in content.split('\n') if l.strip()]
    print(f"\n  节点数: {len(lines)}")
    for line in lines:
        if '#' in line:
            print(f"  {line.split('#')[-1]}")
    
    # 测试CDN IP连通性
    cmd = """cd /root/singbox-eps-node && python3 << 'PYEOF'
import sqlite3, socket, time
conn = sqlite3.connect('data/singbox.db')
c = conn.cursor()
c.execute("SELECT value FROM cdn_settings WHERE key='cdn_ips_list'")
row = c.fetchone()
if row:
    for ip in row[0].split(','):
        ip = ip.strip()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            t0 = time.time()
            r = s.connect_ex((ip, 443))
            t1 = time.time()
            s.close()
            status = "OK" if r==0 else "FAIL"
            print(f'{ip}: {status} ({int((t1-t0)*1000)}ms)')
        except Exception as e:
            print(f'{ip}: ERROR {e}')
conn.close()
PYEOF"""
    stdin, stdout, stderr = c.exec_command(cmd)
    print(f"\n  CDN IP连通性:")
    print(stdout.read().decode())
    
    c.close()

test('日本', '52.195.179.240', 'je*pMaN8QNfCMK', 'JP')
test('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com', 'SG')
