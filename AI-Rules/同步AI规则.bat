@echo off
chcp 65001 >nul
title 同步AI规则到所有项目
echo ========================================
echo    同步AI规则到各项目
echo ========================================
echo.

set "RULES_SOURCE=%~dp0"

:: 查找所有.git目录并复制规则
echo 正在扫描项目...
for /r %%d in (.) do (
    if exist "%%d\.git" (
        echo 找到项目: %%d
        
        :: 创建目标目录
        if not exist "%%d\.trae\rules" mkdir "%%d\.trae\rules" 2>nul
        
        :: 复制规则文件
        copy "%RULES_SOURCE%personal.md" "%%d\.trae\rules\personal.md" >nul 2>&1
        copy "%RULES_SOURCE%git-push-rules.md" "%%d\.trae\rules\git-push-rules.md" >nul 2>&1
        copy "%RULES_SOURCE%CLAUDE.md" "%%d\CLAUDE.md" >nul 2>&1
        copy "%RULES_SOURCE%.cursorrules" "%%d\.cursorrules" >nul 2>&1
        copy "%RULES_SOURCE%.ai-rules.md" "%%d\.ai-rules.md" >nul 2>&1
        
        echo   ✓ 规则已同步
        echo.
    )
)

echo ========================================
echo    同步完成！
echo ========================================
echo.
pause
