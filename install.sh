#!/bin/bash
# =============================================================
# S-UI 一键安装脚本（含系统优化）
# 版本: v2.0.0
# 作者: Alan
# 功能: 自动优化系统 + 安装S-UI面板 + 配置SSL证书 + CDN监控
# 使用方法: bash <(curl -sL https://raw.githubusercontent.com/Alan-zzh/s-ui-manager/master/install.sh)
# =============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 打印函数
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 自动切换到root权限
auto_root() {
    if [[ $EUID -ne 0 ]]; then
        print_warning "当前不是root用户，尝试切换到root权限..."
        if command -v sudo &> /dev/null; then
            exec sudo bash "$0" "$@"
        elif command -v su &> /dev/null; then
            exec su -c "bash $0 $@"
        else
            print_error "无法获取root权限，请使用root用户运行"
            exit 1
        fi
    fi
}

# 检测系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "无法检测操作系统"
        exit 1
    fi
    print_info "检测到系统: $OS $VER"
}

# 第一步：更新系统源
update_sources() {
    print_info "更新系统源..."
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        apt update -y
    elif [[ "$OS" == "centos" || "$OS" == "almalinux" || "$OS" == "rocky" ]]; then
        yum makecache -y
    fi
    print_success "系统源更新完成"
}

# 第二步：更新系统包
update_system() {
    print_info "更新系统包..."
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        apt upgrade -y
    elif [[ "$OS" == "centos" || "$OS" == "almalinux" || "$OS" == "rocky" ]]; then
        yum update -y
    fi
    print_success "系统包更新完成"
}

# 第三步：安装必要依赖
install_dependencies() {
    print_info "安装必要依赖..."
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        apt install -y curl wget git jq iproute2 sqlite3 cron python3 python3-pip
    elif [[ "$OS" == "centos" || "$OS" == "almalinux" || "$OS" == "rocky" ]]; then
        yum install -y curl wget git jq iproute sqlite3 crontabs python3 python3-pip
    fi
    print_success "依赖安装完成"
}

# 第四步：配置BBR + FQ + CAKE三合一加速
install_bbr_fq_cake() {
    print_info "配置BBR + FQ + CAKE三合一加速..."
    
    # 获取网卡名称
    NIC=$(ip route | grep default | awk '{print $5}' | head -n1)
    if [[ -z "$NIC" ]]; then
        NIC="eth0"
    fi
    print_info "检测到网卡: $NIC"
    
    # 启用BBR拥塞控制
    sysctl -w net.ipv4.tcp_congestion_control=bbr
    
    # 设置FQ为默认队列规则
    sysctl -w net.core.default_qdisc=fq
    
    # 配置CAKE队列规则
    tc qdisc replace dev $NIC root cake bandwidth 1000mbit flowmode triple-isolate 2>/dev/null || true
    
    # 优化BBR参数
    sysctl -w net.ipv4.tcp_bbr_min_rtt_win_sec=60
    sysctl -w net.ipv4.tcp_slow_start_after_idle=0
    
    # 保存配置
    cat >> /etc/sysctl.conf << 'EOF'

# BBR + FQ + CAKE 三合一加速配置
net.ipv4.tcp_congestion_control=bbr
net.core.default_qdisc=fq
net.ipv4.tcp_bbr_min_rtt_win_sec=60
net.ipv4.tcp_slow_start_after_idle=0
EOF
    
    print_success "BBR + FQ + CAKE三合一加速配置完成"
}

# 第五步：优化TCP参数
optimize_tcp() {
    print_info "优化TCP参数..."
    
    sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
    sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"
    sysctl -w net.ipv4.tcp_max_tw_buckets=65536
    sysctl -w net.ipv4.tcp_tw_reuse=1
    sysctl -w net.ipv4.tcp_fin_timeout=15
    sysctl -w net.ipv4.tcp_keepalive_time=600
    sysctl -w net.ipv4.tcp_keepalive_probes=5
    sysctl -w net.ipv4.tcp_keepalive_intvl=15
    sysctl -w net.ipv4.ip_local_port_range="1024 65535"
    sysctl -w net.core.somaxconn=65535
    sysctl -w net.core.netdev_max_backlog=65535
    sysctl -w net.ipv4.tcp_max_syn_backlog=65535
    
    cat >> /etc/sysctl.conf << 'EOF'

# TCP参数优化
net.ipv4.tcp_rmem=4096 87380 67108864
net.ipv4.tcp_wmem=4096 65536 67108864
net.ipv4.tcp_max_tw_buckets=65536
net.ipv4.tcp_tw_reuse=1
net.ipv4.tcp_fin_timeout=15
net.ipv4.tcp_keepalive_time=600
net.ipv4.tcp_keepalive_probes=5
net.ipv4.tcp_keepalive_intvl=15
net.ipv4.ip_local_port_range=1024 65535
net.core.somaxconn=65535
net.core.netdev_max_backlog=65535
net.ipv4.tcp_max_syn_backlog=65535
EOF
    
    print_success "TCP参数优化完成"
}

# 第六步：优化系统限制
optimize_system_limits() {
    print_info "优化系统限制..."
    
    cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
EOF
    
    mkdir -p /etc/systemd/system.conf.d
    cat > /etc/systemd/system.conf.d/limits.conf << 'EOF'
[Manager]
DefaultLimitNOFILE=65535
DefaultLimitNPROC=65535
EOF
    
    ulimit -n 65535
    ulimit -u 65535
    
    print_success "系统限制优化完成"
}

# 第七步：配置防火墙
configure_firewall() {
    print_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw allow 6868/tcp
        ufw --force enable
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=22/tcp
        firewall-cmd --permanent --add-port=80/tcp
        firewall-cmd --permanent --add-port=443/tcp
        firewall-cmd --permanent --add-port=6868/tcp
        firewall-cmd --reload
    fi
    
    print_success "防火墙配置完成"
}

# 安装S-UI
install_sui() {
    print_info "安装S-UI面板..."
    bash <(curl -Ls https://raw.githubusercontent.com/eooce/test/main/install_sui.sh)
    print_success "S-UI安装完成"
}

# 配置SSL证书
setup_ssl() {
    print_info "配置SSL证书..."
    
    # Cloudflare API配置（写死在脚本里）
    CF_EMAIL="puzangroup@gmail.com"
    CF_API_KEY="73a1fd81dd0f5087d45572135d5bf783ab26a"
    CF_DOMAIN="$DOMAIN"
    
    if [[ -z "$CF_DOMAIN" ]]; then
        print_warning "未配置域名，使用自签名证书"
        return
    fi
    
    # 安装acme.sh
    curl https://get.acme.sh | sh -s email=$CF_EMAIL
    source ~/.bashrc
    
    # 设置Cloudflare API
    export CF_Email="$CF_EMAIL"
    export CF_Key="$CF_API_KEY"
    
    # 申请证书
    ~/.acme.sh/acme.sh --issue --dns dns_cf -d "$CF_DOMAIN" -d "*.$CF_DOMAIN"
    
    # 安装证书到S-UI
    ~/.acme.sh/acme.sh --install-cert -d "$CF_DOMAIN" \
        --key-file /usr/local/s-ui/bin/cert/key.pem \
        --fullchain-file /usr/local/s-ui/bin/cert/cert.pem \
        --reloadcmd "systemctl restart s-ui"
    
    print_success "SSL证书申请完成"
}

# 配置CDN监控
setup_cdn_monitor() {
    print_info "配置CDN监控..."
    
    # 创建目录
    mkdir -p /opt/s-ui-manager
    mkdir -p /opt/s-ui-manager/sub
    cd /opt/s-ui-manager
    
    # 下载脚本
    curl -sL https://raw.githubusercontent.com/Alan-zzh/s-ui-manager/master/scripts/manager/cdn_monitor.py -o cdn_monitor.py
    curl -sL https://raw.githubusercontent.com/Alan-zzh/s-ui-manager/master/scripts/manager/subscription_generator.py -o subscription_generator.py
    chmod +x cdn_monitor.py subscription_generator.py
    
    # 创建.env配置文件
    cat > /opt/s-ui-manager/.env << EOF
# 服务器配置
SERVER_IP=$(curl -s ifconfig.me)
SERVER_DB_PATH=/usr/local/s-ui/db/s-ui.db
CF_DOMAIN=$DOMAIN

# 订阅配置
USE_HTTPS=true
SUB_DOMAIN=$DOMAIN

# CDN监控配置
CDN_MONITOR_INTERVAL=86400
CDN_IP_URL=https://api.uouin.com/cloudflare.html
EOF
    
    print_success "CDN监控配置完成"
}

# 配置Nginx提供订阅服务
setup_nginx() {
    print_info "配置Nginx订阅服务..."
    
    # 安装Nginx
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        apt install -y nginx
    elif [[ "$OS" == "centos" || "$OS" == "almalinux" || "$OS" == "rocky" ]]; then
        yum install -y nginx
    fi
    
    # 创建Nginx配置
    cat > /etc/nginx/conf.d/s-ui-subscription.conf << EOF
server {
    listen 80;
    listen 443 ssl;
    server_name $DOMAIN;
    
    # SSL证书
    ssl_certificate /usr/local/s-ui/bin/cert/cert.pem;
    ssl_certificate_key /usr/local/s-ui/bin/cert/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 订阅服务
    location /sub/ {
        alias /opt/s-ui-manager/sub/;
        autoindex on;
        add_header Content-Type text/plain;
        add_header Access-Control-Allow-Origin *;
    }
    
    location /sub-json/ {
        alias /opt/s-ui-manager/sub/;
        autoindex on;
        add_header Content-Type application/json;
        add_header Access-Control-Allow-Origin *;
    }
    
    # CDN监控API
    location /api/ {
        proxy_pass http://127.0.0.1:8080/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
    
    # 测试并重启Nginx
    nginx -t && systemctl restart nginx
    
    print_success "Nginx订阅服务配置完成"
}

# 创建订阅生成定时任务
setup_subscription_cron() {
    print_info "配置订阅生成定时任务..."
    
    # 创建订阅生成脚本
    cat > /opt/s-ui-manager/generate_sub.sh << 'EOF'
#!/bin/bash
cd /opt/s-ui-manager
python3 subscription_generator.py base64 > /opt/s-ui-manager/sub/sub_base64.txt
python3 subscription_generator.py json > /opt/s-ui-manager/sub/sub_json.json
EOF
    
    chmod +x /opt/s-ui-manager/generate_sub.sh
    
    # 添加到cron（每5分钟更新一次）
    (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/s-ui-manager/generate_sub.sh >> /var/log/sub-gen.log 2>&1") | crontab -
    
    # 立即执行一次
    /opt/s-ui-manager/generate_sub.sh
    
    print_success "订阅生成定时任务已配置"
}

# 创建systemd服务
create_service() {
    print_info "创建systemd服务..."
    
    cat > /etc/systemd/system/s-ui-cdn-monitor.service << 'EOF'
[Unit]
Description=S-UI CDN Monitor Service
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/s-ui-manager
ExecStart=/usr/bin/python3 /opt/s-ui-manager/cdn_monitor.py --daemon
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable s-ui-cdn-monitor
    systemctl start s-ui-cdn-monitor
    
    print_success "CDN监控服务已创建并启动"
}

# 创建定时任务
setup_cron() {
    print_info "创建定时任务..."
    
    (crontab -l 2>/dev/null; echo "0 3 * * * cd /opt/s-ui-manager && /usr/bin/python3 cdn_monitor.py >> /var/log/cdn-monitor.log 2>&1") | crontab -
    
    print_success "定时任务已创建（每天凌晨3点）"
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    
    pip3 install requests python-dotenv --break-system-packages 2>/dev/null || \
    pip3 install requests python-dotenv
    
    print_success "Python依赖安装完成"
}

# 显示使用说明
show_usage() {
    SUI_PORT=$(cat /usr/local/s-ui/bin/config.json 2>/dev/null | grep -o '"port":[0-9]*' | cut -d':' -f2)
    
    echo ""
    echo "========================================="
    echo "安装完成！"
    echo "========================================="
    echo ""
    echo "面板地址: https://$(curl -s ifconfig.me):${SUI_PORT:-6868}"
    echo "CDN监控服务: 已启动（每天凌晨3点自动测试优选IP）"
    echo ""
    echo "常用命令："
    echo "  查看服务状态: systemctl status s-ui-cdn-monitor"
    echo "  查看运行日志: journalctl -u s-ui-cdn-monitor -f"
    echo "  重启服务: systemctl restart s-ui-cdn-monitor"
    echo ""
    echo "========================================="
}

# 主函数
main() {
    # 自动切换到root权限
    auto_root "$@"
    
    echo "========================================="
    echo "S-UI 一键安装脚本 v2.0.0"
    echo "系统优化 + 面板安装 + SSL证书 + CDN监控"
    echo "========================================="
    echo ""
    
    # 提示用户输入域名
    read -p "请输入你的Cloudflare域名（例如：us.290372913.xyz）: " DOMAIN
    echo ""
    
    detect_os
    update_sources
    update_system
    install_dependencies
    install_bbr_fq_cake
    optimize_tcp
    optimize_system_limits
    configure_firewall
    install_sui
    install_python_deps
    setup_ssl
    setup_cdn_monitor
    setup_nginx
    setup_subscription_cron
    create_service
    setup_cron
    
    show_usage
}

# 运行主函数
main
