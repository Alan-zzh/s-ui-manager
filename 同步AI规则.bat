@echo off
chcp 65001 >nul
title 同步个人AI规则到所有项目
echo ========================================
echo    同步AI规则到各项目
echo ========================================
echo.

set "RULES_SOURCE=%~dp0.trae\rules\git-push-rules.md"

:: 查找所有.git目录并复制规则
echo 正在扫描项目...
for /r %%d in (.) do (
    if exist "%%d\.git" (
        echo 找到项目: %%d
        if not exist "%%d\.trae\rules" (
            mkdir "%%d\.trae\rules"
        )
        copy "%RULES_SOURCE%" "%%d\.trae\rules\git-push-rules.md" >nul
        if exist "%%d\.trae\rules\git-push-rules.md" (
            echo   ✓ 规则已同步
        )
    )
)

echo.
echo ========================================
echo    同步完成！
echo ========================================
echo.
pause
