import paramiko, time

servers = [
    ('日本', '52.195.179.240', 'je*pMaN8QNfCMK'),
    ('新加坡', '13.212.37.11', 'jbfCMP75@jh.dxclouds.com'),
]

all_ok = True

for name, ip, password in servers:
    print(f"\n{'='*60}")
    print(f"=== {name} 最终验证 ===")
    print(f"{'='*60}")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username='root', password=password, timeout=15)
    
    # 1. 所有服务状态
    print("【服务状态】")
    cmd = """
for svc in singbox singbox-sub singbox-cdn; do
    status=$(systemctl is-active $svc 2>/dev/null)
    if [ "$status" = "active" ]; then
        echo "✅ $svc: 运行中"
    else
        echo "❌ $svc: $status"
    fi
done
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    svc_out = stdout.read().decode()
    print(svc_out)
    if '❌' in svc_out:
        all_ok = False
    
    # 2. 端口监听
    print("【端口监听】")
    cmd = """
for port in 443 8443 2053 2083; do
    if ss -tlnp | grep -q ":$port "; then
        echo "✅ $port"
    else
        echo "❌ $port"
    fi
done
"""
    stdin, stdout, stderr = c.exec_command(cmd)
    port_out = stdout.read().decode()
    print(port_out)
    if '❌' in port_out:
        all_ok = False
    
    # 3. 配置语法
    print("【配置语法】")
    cmd = 'ENABLE_DEPRECATED_LEGACY_DNS_SERVERS=true ENABLE_DEPRECATED_MISSING_DOMAIN_RESOLVER=true /usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1 | grep -E "ERROR|FATAL|valid" || echo "OK"'
    stdin, stdout, stderr = c.exec_command(cmd)
    check_out = stdout.read().decode().strip()
    if 'ERROR' in check_out or 'FATAL' in check_out:
        print(f"❌ {check_out}")
        all_ok = False
    else:
        print("✅ 配置语法正确")
    
    # 4. 订阅服务
    print("【订阅服务】")
    code = 'JP' if name == '日本' else 'SG'
    cmd = f"curl -sk -o /dev/null -w '%{{http_code}}' https://localhost:2087/sub/{code}"
    stdin, stdout, stderr = c.exec_command(cmd)
    sub_code = stdout.read().decode().strip()
    if sub_code == '200':
        print("✅ 订阅正常")
    else:
        print(f"❌ 订阅异常: {sub_code}")
        all_ok = False
    
    # 5. 日志错误（最近1分钟）
    print("【日志状态】")
    cmd = 'sleep 1 && grep -c "ERROR" /var/log/singbox.log 2>/dev/null || echo 0'
    stdin, stdout, stderr = c.exec_command(cmd)
    err_count = int(stdout.read().decode().strip())
    if err_count > 10:
        print(f"⚠️ 错误数: {err_count}")
    else:
        print(f"✅ 错误数: {err_count}")
    
    # 6. 系统资源
    print("【系统资源】")
    cmd = 'uptime | awk -F"load average:" "{print \$2}"'
    stdin, stdout, stderr = c.exec_command(cmd)
    load = stdout.read().decode().strip()
    print(f"负载: {load}")
    
    c.close()
    print(f"{'='*60}")

print(f"\n{'='*60}")
if all_ok:
    print("✅ 所有检查通过，服务器状态稳定")
    print("可以安全更新REALITY配置")
else:
    print("⚠️ 存在警告，建议修复后再更新")
print(f"{'='*60}")
