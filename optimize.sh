#!/bin/bash
# =============================================================
# 系统优化脚本 - BBR Plus加速 + 系统优化
# 版本: v1.0.0
# 作者: Alan
# 功能: 安装BBR Plus加速，优化系统网络性能，免重启生效
# =============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    print_error "请使用root用户运行此脚本"
    exit 1
fi

echo "========================================="
echo "系统优化脚本 v1.0.0"
echo "BBR Plus加速 + 系统优化"
echo "========================================="
echo ""

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

# 安装BBR Plus加速
install_bbr_plus() {
    print_info "安装BBR Plus加速..."
    
    # 下载BBR Plus内核模块
    curl -sL https://raw.githubusercontent.com/ylx2016/Linux-NetSpeed/master/tcp.sh -o /tmp/tcp.sh
    chmod +x /tmp/tcp.sh
    
    # 自动选择BBR Plus并安装
    echo "14" | /tmp/tcp.sh
    
    # 启用BBR Plus
    sysctl -w net.core.default_qdisc=fq
    sysctl -w net.ipv4.tcp_congestion_control=bbr
    sysctl -w net.ipv4.tcp_congestion_control=bbr_plus 2>/dev/null || true
    
    # 应用优化参数（免重启）
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
    
    # 保存配置到sysctl.conf（重启后依然生效）
    cat >> /etc/sysctl.conf << 'EOF'

# BBR Plus 优化配置
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr_plus
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
    
    print_success "BBR Plus加速安装完成（已免重启生效）"
}

# 优化系统限制
optimize_system() {
    print_info "优化系统限制..."
    
    # 优化文件描述符限制
    cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
EOF
    
    # 优化systemd限制
    mkdir -p /etc/systemd/system.conf.d
    cat > /etc/systemd/system.conf.d/limits.conf << 'EOF'
[Manager]
DefaultLimitNOFILE=65535
DefaultLimitNPROC=65535
EOF
    
    # 应用新限制
    ulimit -n 65535
    ulimit -u 65535
    
    print_success "系统限制优化完成"
}

# 优化防火墙
optimize_firewall() {
    print_info "优化防火墙配置..."
    
    # 开放必要端口
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

# 验证优化结果
verify_optimization() {
    echo ""
    echo "========================================="
    echo "优化结果验证"
    echo "========================================="
    echo ""
    
    # 检查BBR状态
    BBR_STATUS=$(sysctl net.ipv4.tcp_congestion_control | awk '{print $3}')
    echo "BBR状态: $BBR_STATUS"
    
    # 检查文件描述符
    echo "文件描述符限制: $(ulimit -n)"
    
    # 检查网络参数
    echo "TCP重用: $(sysctl net.ipv4.tcp_tw_reuse | awk '{print $3}')"
    
    echo ""
    print_success "系统优化全部完成！"
    echo ""
    print_info "下一步：运行一键安装脚本安装S-UI面板"
    echo "========================================="
}

# 主函数
main() {
    detect_os
    install_bbr_plus
    optimize_system
    optimize_firewall
    verify_optimization
}

# 运行主函数
main
