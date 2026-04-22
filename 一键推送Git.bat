@echo off
chcp 65001 >nul
title 一键Git推送脚本
echo ========================================
echo    Git 一键自动推送工具
echo ========================================
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 第一步：检查Git状态
echo [1/4] 检查仓库状态...
git status --short
echo.

:: 第二步：添加所有变更
echo [2/4] 添加所有文件变更...
git add -A
if errorlevel 1 (
    echo [错误] 文件添加失败，请检查权限或文件锁定
    pause
    exit /b 1
)
echo [成功] 所有文件已添加到暂存区
echo.

:: 第三步：自动生成提交信息并提交
echo [3/4] 创建提交...
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"

set "commit_msg=自动更新: %YY%-%MM%-%DD% %HH%:%Min%:%Sec%"

git commit -m "%commit_msg%"
if errorlevel 1 (
    echo [提示] 没有需要提交的变更，或存在冲突
    echo 如果提示"nothing to commit"，说明已经是最新状态
    pause
    exit /b 0
)
echo [成功] 提交已创建: %commit_msg%
echo.

:: 第四步：推送到远程仓库
echo [4/4] 推送到远程仓库...
git push origin master
if errorlevel 1 (
    echo [错误] 推送失败，可能原因：
    echo 1. 网络连接问题
    echo 2. 远程仓库权限变更
    echo 3. 需要强制推送(git push -f)
    pause
    exit /b 1
)
echo.
echo ========================================
echo    Git 推送完成！
echo ========================================
echo 提交信息: %commit_msg%
echo.
pause
