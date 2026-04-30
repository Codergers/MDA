@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set LANG=zh_CN.UTF-8
set LC_ALL=zh_CN.UTF-8

if "%~1"=="" (
    cmd /k
) else (
    %*
)
