#!/bin/bash
# S-UI 一键安装脚本
# 作者: Alan
# 版本: v1.0.0
# 功能: 自动安装S-UI面板、配置节点、设置CDN监控
# 使用方法: bash <(curl -sL https://raw.githubusercontent.com/YOUR_USERNAME/s-ui-manager/main/install.sh)

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

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    print_error "请使用root用户运行此脚本"
    exit 1
fi

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

# 安装依赖
install_dependencies() {
    print_info "安装依赖..."
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        apt update && apt install -y curl wget git sqlite3 cron
    elif [[ "$OS" == "centos" || "$OS" == "almalinux" || "$OS" == "rocky" ]]; then
        yum install -y curl wget git sqlite3 crontabs
    fi
    print_success "依赖安装完成"
}

# 安装S-UI
install_sui() {
    print_info "安装S-UI面板..."
    bash <(curl -Ls https://raw.githubusercontent.com/eooce/test/main/install_sui.sh)
    print_success "S-UI安装完成"
}

# 配置CDN监控
setup_cdn_monitor() {
    print_info "配置CDN监控..."
    
    # 创建目录
    mkdir -p /opt/s-ui-manager
    cd /opt/s-ui-manager
    
    # 下载脚本
    curl -sL https://raw.githubusercontent.com/YOUR_USERNAME/s-ui-manager/main/scripts/manager/cdn_monitor.py -o cdn_monitor.py
    curl -sL https://raw.githubusercontent.com/YOUR_USERNAME/s-ui-manager/main/scripts/manager/subscription_generator.py -o subscription_generator.py
    chmod +x cdn_monitor.py subscription_generator.py
    
    # 创建.env配置文件
    cat > /opt/s-ui-manager/.env << 'EOF'
# 服务器配置（请根据实际情况修改）
SERVER_IP=YOUR_SERVER_IP
SERVER_DB_PATH=/usr/local/s-ui/db/s-ui.db
CF_DOMAIN=YOUR_CF_DOMAIN

# CDN监控配置
CDN_MONITOR_INTERVAL=86400
CDN_IP_URL=https://api.uouin.com/cloudflare.html
EOF
    
    print_warning "请编辑 /opt/s-ui-manager/.env 文件，填入你的服务器IP和域名"
    print_info "运行: nano /opt/s-ui-manager/.env"
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
    
    # 每天凌晨3点运行
    (crontab -l 2>/dev/null; echo "0 3 * * * cd /opt/s-ui-manager && /usr/bin/python3 cdn_monitor.py >> /var/log/cdn-monitor.log 2>&1") | crontab -
    
    print_success "定时任务已创建（每天凌晨3点）"
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    
    if ! command -v python3 &> /dev/null; then
        print_info "安装Python3..."
        if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
            apt install -y python3 python3-pip
        elif [[ "$OS" == "centos" || "$OS" == "almalinux" || "$OS" == "rocky" ]]; then
            yum install -y python3 python3-pip
        fi
    fi
    
    pip3 install requests python-dotenv --break-system-packages 2>/dev/null || \
    pip3 install requests python-dotenv
    
    print_success "Python依赖安装完成"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "========================================="
    echo "安装完成！"
    echo "========================================="
    echo ""
    echo "后续步骤："
    echo "  1. 编辑配置文件: nano /opt/s-ui-manager/.env"
    echo "  2. 修改以下参数："
    echo "     - SERVER_IP=你的服务器IP"
    echo "     - CF_DOMAIN=你的Cloudflare域名"
    echo "  3. 重启服务: systemctl restart s-ui-cdn-monitor"
    echo ""
    echo "常用命令："
    echo "  查看服务状态: systemctl status s-ui-cdn-monitor"
    echo "  查看运行日志: journalctl -u s-ui-cdn-monitor -f"
    echo "  手动运行一次: cd /opt/s-ui-manager && python3 cdn_monitor.py"
    echo "  重启服务: systemctl restart s-ui-cdn-monitor"
    echo "  停止服务: systemctl stop s-ui-cdn-monitor"
    echo ""
    echo "定时任务：每天凌晨3点自动测试优选IP"
    echo "========================================="
}

# 主函数
main() {
    echo "========================================="
    echo "S-UI 一键安装脚本 v1.0.0"
    echo "========================================="
    echo ""
    
    detect_os
    install_dependencies
    install_sui
    install_python_deps
    setup_cdn_monitor
    create_service
    setup_cron
    
    show_usage
}

# 运行主函数
main
