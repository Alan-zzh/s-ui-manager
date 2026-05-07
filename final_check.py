import time
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

all_ok = True

for srv in get_servers():
    print(f"\n{'='*60}")
    print(f"=== {srv['name']} 最终验证 ===")
    print(f"{'='*60}")

    with ssh_connect(srv) as c:
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
        out, err = run_command(c, cmd)
        print(out)
        if '❌' in out:
            all_ok = False

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
        out, err = run_command(c, cmd)
        print(out)
        if '❌' in out:
            all_ok = False

        print("【配置语法】")
        cmd = 'ENABLE_DEPRECATED_LEGACY_DNS_SERVERS=true ENABLE_DEPRECATED_MISSING_DOMAIN_RESOLVER=true /usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1 | grep -E "ERROR|FATAL|valid" || echo "OK"'
        out, err = run_command(c, cmd)
        check_out = out.strip()
        if 'ERROR' in check_out or 'FATAL' in check_out:
            print(f"❌ {check_out}")
            all_ok = False
        else:
            print("✅ 配置语法正确")

        print("【订阅服务】")
        code = 'JP' if srv['name'] == '日本' else 'SG'
        cmd = f"curl -sk -o /dev/null -w '%{{http_code}}' https://localhost:2087/sub/{code}"
        out, err = run_command(c, cmd)
        sub_code = out.strip()
        if sub_code == '200':
            print("✅ 订阅正常")
        else:
            print(f"❌ 订阅异常: {sub_code}")
            all_ok = False

        print("【日志状态】")
        cmd = 'sleep 1 && grep -c "ERROR" /var/log/singbox.log 2>/dev/null || echo 0'
        out, err = run_command(c, cmd)
        err_count = int(out.strip())
        if err_count > 10:
            print(f"⚠️ 错误数: {err_count}")
        else:
            print(f"✅ 错误数: {err_count}")

        print("【系统资源】")
        cmd = 'uptime | awk -F"load average:" "{print \\$2}"'
        out, err = run_command(c, cmd)
        load = out.strip()
        print(f"负载: {load}")

    print(f"{'='*60}")

print(f"\n{'='*60}")
if all_ok:
    print("✅ 所有检查通过，服务器状态稳定")
    print("可以安全更新REALITY配置")
else:
    print("⚠️ 存在警告，建议修复后再更新")
print(f"{'='*60}")
