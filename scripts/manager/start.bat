@echo off
chcp 65001 >nul
title 傻瓜式Web规则管理器

echo ========================================
echo   傻瓜式Web规则管理器 - 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装
    pause
    exit /b 1
)

REM 检查Flask
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 正在安装Flask...
    pip install flask
)

echo [启动] Web界面...
echo.
echo   访问地址: http://127.0.0.1:5000
echo   按 Ctrl+C 停止服务
echo.

python app.py

pause