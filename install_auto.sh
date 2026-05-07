#!/bin/bash
# ============================================================
# 全自动安装脚本 - 直接在服务器上运行
# 域名: us.290372913.xyz
# 使用方法: 复制此脚本到服务器，执行 bash install_auto.sh
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

BASE_DIR="/root/singbox-eps-node"
DOMAIN="us.290372913.xyz"

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "${CYAN}>>> $1${NC}"; }

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
}

echo ""
echo "=========================================="
echo -e "${CYAN}  Singbox EPS Node 全自动安装脚本${NC}"
echo "=========================================="
echo ""

check_root

# 步骤1: 系统更新
log_step "【步骤1/8】系统更新和安装依赖..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl wget git python3 python3-pip python3-venv \
    cron sqlite3 openssl net-tools procps iproute2 \
    iptables-persistent locales sudo gnupg2 ca-certificates
log_info "系统更新和依赖安装完成"

# 步骤2: 下载项目
log_step "【步骤2/8】下载 singbox-eps-node 项目..."
cd /root
rm -rf singbox-eps-node
git clone https://github.com/Alan-zzh/singbox-eps-node.git
cd singbox-eps-node
mkdir -p logs data cert backups
log_info "项目下载完成"

# 步骤3: 安装 sing-box
log_step "【步骤3/8】安装 sing-box 内核..."
ARCH=$(uname -m)
case $ARCH in
    x86_64)  SINGBOX_ARCH="amd64" ;;
    aarch64) SINGBOX_ARCH="arm64" ;;
    *)       log_error "不支持的架构: $ARCH"; exit 1 ;;
esac

cd /tmp
wget -q "https://github.com/SagerNet/sing-box/releases/download/v1.13.9/sing-box-1.13.9-linux-${SINGBOX_ARCH}.tar.gz" -O singbox.tar.gz
tar -xzf singbox.tar.gz
cp "sing-box-1.13.9-linux-${SINGBOX_ARCH}/sing-box" /usr/local/bin/sing-box
chmod +x /usr/local/bin/sing-box
ln -sf /usr/local/bin/sing-box /usr/local/bin/singbox
rm -rf "sing-box-1.13.9-linux-${SINGBOX_ARCH}" singbox.tar.gz
log_info "Singbox 安装完成: $(sing-box version | head -1)"

# 步骤4: 生成配置
log_step "【步骤4/8】生成配置文件..."
cd /root/singbox-eps-node

# 生成 UUID 和密码
VLESS_UUID=$(python3 -c "import uuid; print(uuid.uuid4())")
VLESS_WS_UUID=$(python3 -c "import uuid; print(uuid.uuid4())")
TROJAN_PASSWORD=$(python3 -c "import secrets; print(secrets.token_hex(16))")
HYSTERIA2_PASSWORD=$(python3 -c "import secrets; print(secrets.token_hex(16))")

# 生成 Reality 密钥
REALITY_OUTPUT=$(singbox generate reality-keypair 2>/dev/null)
REALITY_PRIVATE_KEY=$(echo "$REALITY_OUTPUT" | grep "PrivateKey" | awk '{print $2}')
REALITY_PUBLIC_KEY=$(echo "$REALITY_OUTPUT" | grep "PublicKey" | awk '{print $2}')

# 获取服务器 IP 和国家代码
SERVER_IP=$(curl -s --connect-timeout 5 https://api.ipify.org 2>/dev/null || echo "")
COUNTRY_CODE=$(curl -s --connect-timeout 5 "https://ipinfo.io/${SERVER_IP}/country" 2>/dev/null | tr -d '[:space:]' || echo "")
COUNTRY_CODE=${COUNTRY_CODE:-US}

log_info "服务器IP: ${SERVER_IP}，国家代码: ${COUNTRY_CODE}"

# 创建 .env 文件
cat > /root/singbox-eps-node/.env << ENVEOF
# Singbox EPS Node 配置文件
SERVER_IP=${SERVER_IP}
CF_DOMAIN=${DOMAIN}
CF_API_TOKEN=73a1fd81dd0f5087d45572135d5bf783ab26a
COUNTRY_CODE=${COUNTRY_CODE}
VLESS_UUID=${VLESS_UUID}
VLESS_WS_UUID=${VLESS_WS_UUID}
TROJAN_PASSWORD=${TROJAN_PASSWORD}
HYSTERIA2_PASSWORD=${HYSTERIA2_PASSWORD}
REALITY_PRIVATE_KEY=${REALITY_PRIVATE_KEY}
REALITY_PUBLIC_KEY=${REALITY_PUBLIC_KEY}
AI_SOCKS5_SERVER=
AI_SOCKS5_PORT=
AI_SOCKS5_USER=
AI_SOCKS5_PASS=
SUB_TOKEN=
TG_BOT_TOKEN=
TG_ADMIN_CHAT_ID=
ENVEOF

log_info ".env 文件已创建"

# 步骤5: 安装 Python 依赖并生成配置
log_step "【步骤5/8】安装 Python 依赖并生成配置..."
pip3 install flask python-dotenv
python3 scripts/config_generator.py
log_info "配置生成完成"

# 步骤6: 创建 systemd 服务
log_step "【步骤6/8】创建 systemd 服务..."

cat > /etc/systemd/system/singbox.service << 'EOF'
[Unit]
Description=Singbox Proxy Service
After=network.target

[Service]
Type=simple
ExecStartPre=/bin/bash -c 'test -f /root/singbox-eps-node/config.json || python3 /root/singbox-eps-node/scripts/config_generator.py'
ExecStart=/usr/local/bin/sing-box run -c /root/singbox-eps-node/config.json
Restart=on-failure
RestartSec=5s
StartLimitIntervalSec=60
StartLimitBurst=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/singbox-sub.service << 'EOF'
[Unit]
Description=Singbox Subscription Service
After=network.target singbox.service

[Service]
Type=simple
WorkingDirectory=/root/singbox-eps-node
ExecStart=/usr/bin/python3 /root/singbox-eps-node/scripts/subscription_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/singbox-cdn.service << 'EOF'
[Unit]
Description=Singbox CDN Monitor Service
After=network.target singbox.service

[Service]
Type=simple
WorkingDirectory=/root/singbox-eps-node
ExecStart=/usr/bin/python3 /root/singbox-eps-node/scripts/cdn_monitor.py --daemon
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
log_info "systemd 服务已创建"

# 步骤7: 配置防火墙和系统优化
log_step "【步骤7/8】配置防火墙和系统优化..."

# 防火墙全放行
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
iptables -F
netfilter-persistent save 2>/dev/null || true

# BBR + CAKE 加速
echo "net.core.default_qdisc=cake" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
echo "net.ipv4.tcp_fastopen=3" >> /etc/sysctl.conf
echo "net.ipv4.tcp_tw_reuse=1" >> /etc/sysctl.conf
echo "net.ipv4.ip_local_port_range=1024 65535" >> /etc/sysctl.conf
sysctl -p 2>/dev/null || true

# 文件描述符
grep -q "65535" /etc/security/limits.conf 2>/dev/null || cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 65535
* hard nofile 65535
root soft nofile 65535
root hard nofile 65535
EOF

# 生成自签名证书
cd /root/singbox-eps-node
openssl req -x509 -nodes -newkey rsa:2048 -days 3650 \
  -keyout cert/key.pem -out cert/cert.pem \
  -subj "/CN=${DOMAIN}" 2>/dev/null || true

log_info "防火墙和系统优化完成"

# 步骤8: 启动服务
log_step "【步骤8/8】启动所有服务..."
systemctl enable singbox singbox-sub singbox-cdn 2>/dev/null || true
systemctl start singbox
sleep 3
systemctl start singbox-sub
sleep 2
systemctl start singbox-cdn
log_info "所有服务已启动"

# 验证
echo ""
log_step "验证服务状态..."
echo ""

for svc in singbox singbox-sub singbox-cdn; do
    if systemctl is-active --quiet "$svc"; then
        echo -e "  ${GREEN}✅${NC} $svc: 运行中"
    else
        echo -e "  ${RED}❌${NC} $svc: 未运行"
    fi
done

echo ""
echo -e "  端口监听:"
for port in 443 8443 2053 2083 2087; do
    if ss -tlnp | grep -q ":$port "; then
        echo -e "    ${GREEN}✅${NC} 端口 $port: 监听中"
    else
        echo -e "    ${RED}❌${NC} 端口 $port: 未监听"
    fi
done

echo ""
if sysctl net.ipv4.tcp_congestion_control 2>/dev/null | grep -q "bbr"; then
    echo -e "  ${GREEN}✅${NC} BBR加速: 已启用"
else
    echo -e "  ${YELLOW}⚠️${NC} BBR加速: 未启用"
fi

echo ""
echo "=========================================="
echo -e "${CYAN}  安装完成！${NC}"
echo "=========================================="
echo ""
echo "📍 服务器IP: ${SERVER_IP}"
echo "🌐 域名: ${DOMAIN}"
echo "🔗 订阅链接: https://${DOMAIN}:2087/sub/${COUNTRY_CODE}"
echo "📱 sing-box订阅: https://${DOMAIN}:2087/singbox/${COUNTRY_CODE}"
echo "📊 流量统计: https://${DOMAIN}:2087/"
echo ""
echo "📝 配置文件: /root/singbox-eps-node/.env"
echo "📝 查看配置: cat /root/singbox-eps-node/.env"
echo ""
echo "🔧 服务管理:"
echo "  查看状态: systemctl status singbox singbox-sub singbox-cdn"
echo "  查看日志: journalctl -u singbox-sub -f"
echo "  重启服务: systemctl restart singbox singbox-sub singbox-cdn"
echo ""
