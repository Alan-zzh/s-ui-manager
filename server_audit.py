import paramiko
import time
import sys
import io
from audit_config import get_servers

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )

servers = get_servers()

connected_server = None

for srv in servers:
    print(f"尝试连接 {srv['name']} ({srv['host']})...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        start = time.time()
        client.connect(srv['host'], port=srv['port'], username=srv['username'], password=srv['password'], timeout=15, allow_agent=False, look_for_keys=False)
        conn_time = (time.time() - start) * 1000
        print(f"✅ 连接成功: {conn_time:.0f}ms")
        connected_server = (srv, client)
        break
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        try:
            client.close()
        except Exception:
            pass

if not connected_server:
    print("所有服务器均无法连接")
    sys.exit(1)

srv, client = connected_server

checks = [
    ("1. 系统基本信息", """
echo "=== 系统信息 ==="
uname -a
echo ""
echo "=== 运行时间和负载 ==="
uptime
echo ""
echo "=== 内存使用 ==="
free -m
echo ""
echo "=== 磁盘使用 ==="
df -h
echo ""
echo "=== CPU信息 ==="
lscpu | grep -E "Model name|CPU\\(s\\)|Thread|Core"
"""),
    ("2. 三个服务运行状态", """
echo "=== systemd服务状态 ==="
for svc in singbox singbox-sub singbox-cdn; do
    echo "--- $svc ---"
    systemctl is-active $svc 2>/dev/null || echo "INACTIVE"
    systemctl is-enabled $svc 2>/dev/null || echo "NOT-ENABLED"
    echo ""
done
echo "=== sing-box进程详情 ==="
ps aux | grep sing-box | grep -v grep
echo ""
echo "=== Python服务进程 ==="
ps aux | grep python3 | grep -v grep | grep singbox
"""),
    ("3. 端口监听状态(TCP+UDP)", """
echo "=== TCP端口监听 ==="
for port in 443 8443 2053 2083 2087 1080; do
    if ss -tlnp | grep -q ":$port "; then
        echo "TCP $port: 监听中"
    else
        echo "TCP $port: 未监听"
    fi
done
echo ""
echo "=== UDP端口监听 ==="
for port in 443; do
    if ss -ulnp | grep -q ":$port "; then
        echo "UDP $port: 监听中"
    else
        echo "UDP $port: 未监听"
    fi
done
echo ""
echo "=== 完整监听端口列表 ==="
ss -tlnp | grep -E "sing-box|python3"
ss -ulnp | grep -E "sing-box|python3"
"""),
    ("4. singbox日志错误分析", """
echo "=== 日志文件状态 ==="
ls -la /var/log/singbox.log 2>/dev/null || echo "日志文件不存在"
echo ""
echo "=== 最近50行日志 ==="
tail -50 /var/log/singbox.log 2>/dev/null || echo "无日志"
echo ""
echo "=== ERROR统计 ==="
grep -c "ERROR" /var/log/singbox.log 2>/dev/null || echo "0"
echo ""
echo "=== WARN统计 ==="
grep -c "WARN" /var/log/singbox.log 2>/dev/null || echo "0"
echo ""
echo "=== 最近10条ERROR ==="
grep "ERROR" /var/log/singbox.log 2>/dev/null | tail -10
echo ""
echo "=== 最近10条WARN ==="
grep "WARN" /var/log/singbox.log 2>/dev/null | tail -10
"""),
    ("5. singbox-sub服务日志", """
echo "=== singbox-sub最近30行日志 ==="
journalctl -u singbox-sub -n 30 --no-pager 2>/dev/null
echo ""
echo "=== singbox-sub错误日志 ==="
journalctl -u singbox-sub --since "1 hour ago" --no-pager -p err 2>/dev/null
"""),
    ("6. singbox-cdn服务日志", """
echo "=== singbox-cdn最近30行日志 ==="
journalctl -u singbox-cdn -n 30 --no-pager 2>/dev/null
echo ""
echo "=== singbox-cdn错误日志 ==="
journalctl -u singbox-cdn --since "1 hour ago" --no-pager -p err 2>/dev/null
"""),
    ("7. 项目文件和配置检查", """
echo "=== 项目目录结构 ==="
ls -la /root/singbox-eps-node/ 2>/dev/null || echo "项目目录不存在"
echo ""
echo "=== .env文件内容 ==="
cat /root/singbox-eps-node/.env 2>/dev/null || echo ".env文件不存在"
echo ""
echo "=== config.json校验 ==="
cd /root/singbox-eps-node 2>/dev/null
python3 -c "import json; json.load(open('config.json')); print('config.json语法正确')" 2>&1 || echo "config.json语法错误"
echo ""
echo "=== cert目录 ==="
ls -la /root/singbox-eps-node/cert/ 2>/dev/null || echo "cert目录不存在"
echo ""
echo "=== 证书有效期 ==="
openssl x509 -in /root/singbox-eps-node/cert/cert.pem -noout -dates -subject 2>/dev/null || echo "证书读取失败"
"""),
    ("8. CDN优选IP数据库状态", """
cd /root/singbox-eps-node 2>/dev/null
python3 << 'PYEOF'
import sqlite3, os, time
db_path = os.path.join('data', 'cdn_ips.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM cdn_ips WHERE status='active'")
        active = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM cdn_ips")
        total = c.fetchone()[0]
        c.execute("SELECT ip, latency, source, updated_at FROM cdn_ips WHERE status='active' ORDER BY latency LIMIT 10")
        top10 = c.fetchall()
        c.execute("SELECT MAX(updated_at) FROM cdn_ips")
        last_update = c.fetchone()[0]
        print(f"活跃IP: {active}/{total}")
        print(f"最后更新: {last_update}")
        print("Top10:")
        for ip, lat, src, upd in top10:
            print(f"  {ip} ({lat}ms, {src}, {upd})")
    except Exception as e:
        print(f"数据库查询错误: {e}")
    finally:
        conn.close()
else:
    print("CDN数据库不存在")
PYEOF
"""),
    ("9. 网络和内核优化状态", """
echo "=== BBR状态 ==="
sysctl net.ipv4.tcp_congestion_control 2>/dev/null
echo ""
echo "=== 队列调度 ==="
sysctl net.core.default_qdisc 2>/dev/null
echo ""
echo "=== tc qdisc实际状态 ==="
tc qdisc show 2>/dev/null | head -5
echo ""
echo "=== TCP Fast Open ==="
sysctl net.ipv4.tcp_fastopen 2>/dev/null
echo ""
echo "=== MTU ==="
ip link show | grep mtu
echo ""
echo "=== 文件描述符限制 ==="
ulimit -n
echo ""
echo "=== sysctl优化参数 ==="
sysctl net.ipv4.tcp_tw_reuse 2>/dev/null
sysctl net.ipv4.ip_local_port_range 2>/dev/null
"""),
    ("10. 防火墙和iptables规则", """
echo "=== iptables默认策略 ==="
iptables -L -n | head -5
echo ""
echo "=== iptables NAT规则 ==="
iptables -t nat -L -n 2>/dev/null | head -20
echo ""
echo "=== 端口跳跃规则 ==="
iptables -t nat -L PREROUTING -n 2>/dev/null | grep -E "21000|21200|4433"
echo ""
echo "=== netfilter-persistent状态 ==="
systemctl is-active netfilter-persistent 2>/dev/null || echo "NOT ACTIVE"
"""),
    ("11. DNS解析测试", """
echo "=== DNS解析测试 ==="
nslookup jp.290372913.xyz 8.8.8.8 2>/dev/null | head -6
echo "---"
nslookup jp.290372913.xyz 223.5.5.5 2>/dev/null | head -6
echo "---"
echo "=== /etc/resolv.conf ==="
cat /etc/resolv.conf
"""),
    ("12. 订阅服务测试", """
echo "=== 本地订阅接口测试 ==="
curl -sk -o /dev/null -w "HTTPS 2087/sub/JP: HTTP %{http_code}, %{size_download}B, %{time_total}s\\n" https://localhost:2087/sub/JP 2>/dev/null
curl -sk -o /dev/null -w "HTTPS 2087/sub/jp: HTTP %{http_code}, %{size_download}B, %{time_total}s\\n" https://localhost:2087/sub/jp 2>/dev/null
curl -sk -o /dev/null -w "HTTPS 2087/singbox/JP: HTTP %{http_code}, %{size_download}B, %{time_total}s\\n" https://localhost:2087/singbox/JP 2>/dev/null
echo ""
echo "=== 订阅内容预览 ==="
curl -sk https://localhost:2087/sub/JP 2>/dev/null | head -5
echo ""
echo "=== singbox订阅内容预览 ==="
curl -sk https://localhost:2087/singbox/JP 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('inbounds:', len(d.get('inbounds',[])), 'outbounds:', len(d.get('outbounds',[])), 'route_rules:', len(d.get('route',{}).get('rules',[])))" 2>/dev/null || echo "singbox订阅解析失败"
"""),
    ("13. 连接质量统计", """
echo "=== 当前活跃连接 ==="
ss -tnp | grep sing-box | wc -l
echo "个singbox连接"
echo ""
echo "=== TCP状态统计 ==="
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
echo ""
echo "=== TCP重传统计 ==="
netstat -s | grep -E "retrans|timeout" | head -5
echo ""
echo "=== 网络接口流量 ==="
cat /proc/net/dev | grep -E "ens|eth"
"""),
    ("14. crontab定时任务", """
echo "=== root crontab ==="
crontab -l 2>/dev/null || echo "无crontab"
echo ""
echo "=== /etc/cron.d/ ==="
ls -la /etc/cron.d/ 2>/dev/null
"""),
    ("15. SSL证书详细检查", """
echo "=== 证书链验证 ==="
openssl verify -CAfile /root/singbox-eps-node/cert/cert.pem /root/singbox-eps-node/cert/cert.pem 2>&1
echo ""
echo "=== 证书详细信息 ==="
openssl x509 -in /root/singbox-eps-node/cert/cert.pem -noout -text 2>/dev/null | grep -E "Issuer|Subject|Not Before|Not After|DNS|IP"
echo ""
echo "=== fullchain.pem检查 ==="
ls -la /root/singbox-eps-node/cert/fullchain.pem 2>/dev/null || echo "fullchain.pem不存在(违反规则10)"
"""),
    ("16. config.json完整内容", """
cat /root/singbox-eps-node/config.json 2>/dev/null || echo "config.json不存在"
"""),
]

for title, cmd in checks:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(out)
    if err.strip():
        print(f"[STDERR] {err}")

client.close()
print("\n\n全部检查完成")
