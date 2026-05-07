import time
import json
from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

results = {}

for srv in get_servers():
    print(f"\n{'='*70}")
    print(f"=== {srv['name']} 服务器全面检测 ({srv['host']}) ===")
    print(f"{'='*70}")

    try:
        start = time.time()
        with ssh_connect(srv) as c:
            conn_time = (time.time() - start) * 1000
            print(f"✅ SSH连接: {conn_time:.0f}ms")

            server_result = {'status': 'checking', 'checks': {}}

            print(f"\n【网络连通性】")
            cmd = """
ping -c 3 8.8.8.8 2>/dev/null | grep -E "time=|packet loss" | tail -2
echo "---"
ping -c 3 223.5.5.5 2>/dev/null | grep -E "time=|packet loss" | tail -2
"""
            out, err = run_command(c, cmd, timeout=15)
            print(out)
            server_result['checks']['network'] = 'ok' if 'time=' in out else 'warning'

            print(f"\n【端口监听状态】")
            cmd = """
for port in 443 8443 2053 2083 1080; do
    if ss -tlnp | grep -q ":$port "; then
        echo "✅ 端口 $port: 监听中"
    else
        echo "❌ 端口 $port: 未监听"
    fi
done
"""
            out, err = run_command(c, cmd)
            print(out)
            server_result['checks']['ports'] = 'ok' if '❌' not in out else 'warning'

            print(f"\n【进程状态】")
            cmd = """
for svc in singbox singbox-sub singbox-cdn; do
    if systemctl is-active --quiet $svc 2>/dev/null; then
        echo "✅ $svc: 运行中"
    else
        echo "❌ $svc: 未运行"
    fi
done
echo "---"
ps aux | grep sing-box | grep -v grep | awk '{print "CPU: "$3"%, MEM: "$4"%, PID: "$2}'
"""
            out, err = run_command(c, cmd)
            print(out)
            server_result['checks']['services'] = 'ok' if '❌' not in out else 'warning'

            print(f"\n【系统资源】")
            cmd = """
echo "负载: $(uptime | awk -F'load average:' '{print $2}')"
echo "内存: $(free -m | awk 'NR==2{printf "%.0f%% (%sMB/%sMB)", $3*100/$2, $3, $2}')"
echo "磁盘: $(df -h / | awk 'NR==2{print $5 " (" $3 "/" $2 ")"}')"
echo "TCP连接: $(ss -s | grep TCP | head -1)"
"""
            out, err = run_command(c, cmd)
            print(out)

            print(f"\n【MTU配置】")
            cmd = "ip link show ens5 | grep mtu"
            out, err = run_command(c, cmd)
            mtu_out = out.strip()
            print(mtu_out)
            server_result['checks']['mtu'] = 'ok' if 'mtu 1500' in mtu_out else 'warning'

            print(f"\n【订阅服务测试】")
            code = 'JP' if srv['name'] == '日本' else 'SG'
            cmd = f"""
curl -sk -o /dev/null -w "HTTP状态: %{{http_code}}, 耗时: %{{time_total}}s, 大小: %{{size_download}}B\n" https://localhost:2087/sub/{code}
curl -sk -o /dev/null -w "HTTP状态: %{{http_code}}, 耗时: %{{time_total}}s\n" https://localhost:2087/sub/{code.lower()}
"""
            out, err = run_command(c, cmd)
            print(out)
            server_result['checks']['subscription'] = 'ok' if '200' in out else 'warning'

            print(f"\n【日志错误统计（最近5分钟）】")
            cmd = """
if [ -f /var/log/singbox.log ]; then
    echo "错误数: $(grep -c 'ERROR' /var/log/singbox.log 2>/dev/null || echo 0)"
    echo "警告数: $(grep -c 'WARN' /var/log/singbox.log 2>/dev/null || echo 0)"
    echo "最近3条错误:"
    grep "ERROR" /var/log/singbox.log 2>/dev/null | tail -3
else
    echo "日志文件不存在"
fi
"""
            out, err = run_command(c, cmd)
            print(out)

            print(f"\n【CDN优选IP状态】")
            cmd = """
cd /root/singbox-eps-node
python3 << 'EOF'
import sqlite3, os
db_path = os.path.join('data', 'cdn_ips.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cdn_ips WHERE status='active'")
    active = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cdn_ips")
    total = c.fetchone()[0]
    c.execute("SELECT ip, latency, source FROM cdn_ips WHERE status='active' ORDER BY latency LIMIT 5")
    top5 = c.fetchall()
    conn.close()
    print(f"活跃IP: {active}/{total}")
    print("Top5:")
    for ip, lat, src in top5:
        print(f"  {ip} ({lat}ms, {src})")
else:
    print("数据库不存在")
EOF
"""
            out, err = run_command(c, cmd)
            print(out)

            print(f"\n【连接质量统计】")
            cmd = """
echo "当前活跃连接: $(ss -tnp | grep sing-box | wc -l)"
echo "TIME-WAIT: $(ss -tan | grep TIME-WAIT | wc -l)"
echo "ESTABLISHED: $(ss -tan | grep ESTAB | wc -l)"
echo "---"
echo "TCP重传统计:"
netstat -s | grep -E "retrans|timeout" | head -5
"""
            out, err = run_command(c, cmd)
            print(out)

            server_result['status'] = 'ok'
            results[srv['name']] = server_result

    except Exception as e:
        print(f"❌ SSH连接失败: {e}")
        results[srv['name']] = {'status': 'failed', 'error': str(e)}
        continue

    print(f"\n{'='*70}")
    print(f"=== {srv['name']} 检测完成 ===")
    print(f"{'='*70}")

print(f"\n{'='*70}")
print(f"=== 检测结果汇总 ===")
print(f"{'='*70}")
for name, result in results.items():
    status = result.get('status', 'unknown')
    if status == 'ok':
        checks = result.get('checks', {})
        issues = [k for k, v in checks.items() if v != 'ok']
        if issues:
            print(f"⚠️ {name}: 通过但有警告 ({', '.join(issues)})")
        else:
            print(f"✅ {name}: 全部正常")
    elif status == 'failed':
        print(f"❌ {name}: 连接失败 - {result.get('error', '未知错误')}")
    else:
        print(f"⏳ {name}: 检测中")

print(f"\n全部检测完成")
