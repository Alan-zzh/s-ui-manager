#!/bin/bash
# =============================================================
# 项目名: SimpleProxyManager
# 文件名: install.sh
# 功能: 一键部署 sing-box 代理服务
# 版本: v1.0.0
# 作者: Alan
# =============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

INSTALL_DIR="/opt/simple-proxy-manager"
CONFIG_DIR="/etc/simple-proxy-manager"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                SimpleProxyManager 安装脚本               ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[错误] 请使用 root 用户运行此脚本${NC}"
    exit 1
fi

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo -e "${RED}[错误] 无法检测操作系统${NC}"
    exit 1
fi

echo -e "${CYAN}[信息] 检测到系统: ${OS} ${VERSION}${NC}"

echo ""
echo -e "${YELLOW}[步骤 1/5] 更新系统包...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get update -y && apt-get upgrade -y
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum update -y
else
    echo -e "${RED}[错误] 不支持的系统: ${OS}${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[步骤 2/5] 安装依赖...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y curl wget git jq
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum install -y curl wget git jq
fi

echo ""
echo -e "${YELLOW}[步骤 3/5] 创建目录结构...${NC}"
mkdir -p ${INSTALL_DIR}
mkdir -p ${CONFIG_DIR}

echo ""
echo -e "${YELLOW}[步骤 4/5] 安装 sing-box...${NC}"
SB_VERSION=$(curl -s "https://api.github.com/repos/SagerNet/sing-box/releases/latest" | jq -r '.tag_name' | sed 's/v//')
if [ -z "$SB_VERSION" ]; then
    SB_VERSION="1.10.1"
fi

ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    SB_ARCH="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    SB_ARCH="arm64"
else
    echo -e "${RED}[错误] 不支持的架构: ${ARCH}${NC}"
    exit 1
fi

echo -e "${CYAN}[信息] 下载 sing-box v${SB_VERSION} (${SB_ARCH})${NC}"

curl -L "https://github.com/SagerNet/sing-box/releases/download/v${SB_VERSION}/sing-box-${SB_VERSION}-linux-${SB_ARCH}.tar.gz" -o /tmp/sing-box.tar.gz

if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] sing-box 下载失败${NC}"
    exit 1
fi

tar -xzf /tmp/sing-box.tar.gz -C /tmp
cp "/tmp/sing-box-${SB_VERSION}-linux-${SB_ARCH}/sing-box" /usr/local/bin/
chmod +x /usr/local/bin/sing-box

echo ""
echo -e "${YELLOW}[步骤 5/5] 生成配置...${NC}"

cat > ${CONFIG_DIR}/config.json << 'EOF'
{
  "log": {
    "level": "info",
    "output": "/var/log/singbox.log",
    "timestamp": true
  },
  "dns": {
    "servers": [
      {
        "tag": "cloudflare",
        "address": "https://1.1.1.1/dns-query",
        "detour": "direct"
      },
      {
        "tag": "google",
        "address": "https://8.8.8.8/dns-query",
        "detour": "direct"
      },
      {
        "tag": "ali",
        "address": "223.5.5.5",
        "detour": "direct"
      }
    ],
    "rules": [
      {
        "outbound": "direct",
        "server": "ali"
      },
      {
        "type": "default",
        "server": "cloudflare"
      }
    ]
  },
  "inbounds": [],
  "outbounds": [
    {
      "type": "direct",
      "tag": "direct"
    },
    {
      "type": "block",
      "tag": "block"
    }
  ],
  "route": {
    "rules": [],
    "final": "direct"
  }
}
EOF

cat > /etc/systemd/system/simple-proxy-manager.service << 'EOF'
[Unit]
Description=Simple Proxy Manager (sing-box)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/simple-proxy-manager
ExecStart=/usr/local/bin/sing-box run -c /etc/simple-proxy-manager/config.json
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable simple-proxy-manager

rm -rf /tmp/sing-box*

echo ""
echo "=" * 60
echo -e "${GREEN}安装完成！${NC}"
echo "=" * 60
echo ""
echo -e "${CYAN}下一步操作：${NC}"
echo "  1. 编辑配置文件: ${CONFIG_DIR}/config.json"
echo "  2. 添加你的节点配置"
echo "  3. 启动服务: systemctl start simple-proxy-manager"
echo ""
echo -e "${CYAN}常用命令：${NC}"
echo "  查看状态: systemctl status simple-proxy-manager"
echo "  查看日志: journalctl -u simple-proxy-manager -f"
echo "  重启服务: systemctl restart simple-proxy-manager"
echo ""
echo "=" * 60