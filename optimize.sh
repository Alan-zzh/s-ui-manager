#!/bin/bash
# =============================================================
# 系统优化脚本 - BBR + FQ + CAKE三合一加速 + 系统优化
# 版本: v2.0.0
# 作者: Alan
# 功能: 安装BBR+FQ+CAKE三合一加速，优化系统网络性能，免重启生效
# 适用: 海外连接且存在丢包问题的代理服务器
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
echo "系统优化脚本 v2.0.0"
echo "BBR + FQ + CAKE三合一加速 + 系统优化"
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

# 第一步：更新系统源
update_sources() {
    print_info "更新系统源..."
    
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        apt update
    elif [[ "$OS" == "centos" || "$OS" == "almalinux" || "$OS" == "rocky" ]]; then
        yum makecache
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
        apt install -y curl wget git jq iproute2
    elif [[ "$OS" == "centos" || "$OS" == "almalinux" || "$OS" == "rocky" ]]; then
        yum install -y curl wget git jq iproute
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
    
    # 设置FQ为默认队列规则（必须与BBR配合）
    sysctl -w net.core.default_qdisc=fq
    
    # 配置CAKE队列规则（集成FQ和PIE功能）
    tc qdisc replace dev $NIC root cake bandwidth 1000mbit flowmode triple-isolate
    
    # 优化BBR参数（针对高丢包环境）
    sysctl -w net.ipv4.tcp_bbr_min_rtt_win_sec=60
    sysctl -w net.ipv4.tcp_slow_start_after_idle=0
    
    # 保存配置到sysctl.conf（重启后依然生效）
    cat >> /etc/sysctl.conf << 'EOF'

# BBR + FQ + CAKE 三合一加速配置
net.ipv4.tcp_congestion_control=bbr
net.core.default_qdisc=fq
net.ipv4.tcp_bbr_min_rtt_win_sec=60
net.ipv4.tcp_slow_start_after_idle=0
EOF
    
    print_success "BBR + FQ + CAKE三合一加速配置完成（已免重启生效）"
}

# 第五步：优化TCP参数
optimize_tcp() {
    print_info "优化TCP参数..."
    
    # 增加TCP缓冲区大小（应对高延迟）
    sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
    sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"
    
    # 优化TCP连接参数
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
    
    # 保存配置到sysctl.conf
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

# 第七步：配置防火墙
configure_firewall() {
    print_info "配置防火墙..."
    
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
    
    # 检查队列规则
    NIC=$(ip route | grep default | awk '{print $5}' | head -n1)
    if [[ -z "$NIC" ]]; then
        NIC="eth0"
    fi
    echo "队列规则: $(tc qdisc show dev $NIC | head -n1)"
    
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
    update_sources
    update_system
    install_dependencies
    install_bbr_fq_cake
    optimize_tcp
    optimize_system_limits
    configure_firewall
    verify_optimization
}

# 运行主函数
main
