from audit_config import get_server_old_jp
from ssh_utils import ssh_connect, run_command
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )

server = get_server_old_jp()
with ssh_connect(server) as client:
    checks = [
        ("1. config.py完整内容", """
cat /root/singbox-eps-node/scripts/config.py 2>/dev/null
"""),
        ("2. cdn_monitor.py完整内容", """
cat /root/singbox-eps-node/scripts/cdn_monitor.py 2>/dev/null
"""),
        ("3. 锁文件详情和清理", """
echo "=== 锁文件 ==="
ls -la /tmp/cdn_monitor.lock 2>/dev/null
cat /tmp/cdn_monitor.lock 2>/dev/null
echo ""
echo "=== cdn_monitor进程 ==="
ps aux | grep cdn_monitor | grep -v grep
echo ""
echo "=== 所有python3进程 ==="
ps aux | grep python3 | grep -v grep
echo ""
echo "=== singbox-cdn systemd状态 ==="
systemctl status singbox-cdn 2>/dev/null
"""),
        ("4. 日志目录内容", """
ls -la /root/singbox-eps-node/logs/ 2>/dev/null
echo ""
echo "=== health_check.log最近20行 ==="
tail -20 /root/singbox-eps-node/logs/health_check.log 2>/dev/null
echo ""
echo "=== cert_renew.log ==="
cat /root/singbox-eps-node/logs/cert_renew.log 2>/dev/null
"""),
        ("5. singbox日志ERROR和FATAL", """
echo "=== FATAL错误 ==="
grep -c "FATAL" /var/log/singbox.log 2>/dev/null || echo "0"
grep "FATAL" /var/log/singbox.log 2>/dev/null | tail -5
echo ""
echo "=== ERROR错误 ==="
grep "ERROR" /var/log/singbox.log 2>/dev/null | tail -10
echo ""
echo "=== 日志大小和轮转 ==="
ls -lh /var/log/singbox.log* 2>/dev/null
"""),
        ("6. AWS安全组/网络接口信息", """
echo "=== 网络接口 ==="
ip addr show | grep -E "inet |link/"
echo ""
echo "=== 路由表 ==="
ip route | head -10
echo ""
echo "=== 服务器公网IP ==="
curl -s --connect-timeout 5 https://api.ipify.org 2>/dev/null || echo "无法获取"
"""),
    ]
    for title, cmd in checks:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
        out, err = run_command(client, cmd)
        if out.strip():
            print(out[:8000])
            if len(out) > 8000:
                print(f"\n... [截断，共{len(out)}字符]")
        if err.strip():
            print(f"[STDERR] {err[:1000]}")

print("\n\n第四轮检查完成")
