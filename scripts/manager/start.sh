#!/bin/bash
# =============================================================
# 启动脚本: start.sh
# 功能: 启动傻瓜式Web规则管理器
# 作者: Alan
# =============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}          傻瓜式Web规则管理器 - 启动脚本                 ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未找到Python3，请先安装${NC}"
    exit 1
fi

# 检查Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}[提示] 正在安装Flask...${NC}"
    pip3 install flask
fi

echo -e "${GREEN}[启动] Web界面...${NC}"
echo ""
echo -e "  访问地址: http://127.0.0.1:5000"
echo -e "  按 Ctrl+C 停止服务"
echo ""

python3 app.py