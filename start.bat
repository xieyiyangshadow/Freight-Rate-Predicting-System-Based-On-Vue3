@echo off
REM 一键启动脚本 - Windows Batch 版本
REM 使用方法: 双击运行 start.bat

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    多模型运价预测系统 - 一键启动
echo ========================================
echo.

REM 获取当前目录
set PROJECT_ROOT=%~dp0
echo 项目根目录: %PROJECT_ROOT%
echo.

REM ======================== 后端设置 ========================
echo 设置后端环境...

set BACKEND_DIR=%PROJECT_ROOT%backend
set VENV_PATH=%BACKEND_DIR%\.venv

REM 检查虚拟环境
if not exist "%VENV_PATH%" (
    echo 虚拟环境不存在，正在创建...
    cd /d "%BACKEND_DIR%"
    python -m venv .venv
    echo 虚拟环境创建完成
) else (
    echo 虚拟环境已存在
)

REM 激活虚拟环境
set ACTIVATE_SCRIPT=%VENV_PATH%\Scripts\activate.bat
if exist "%ACTIVATE_SCRIPT%" (
    call "%ACTIVATE_SCRIPT%"
    echo 虚拟环境已激活
) else (
    echo 无法找到激活脚本
    pause
    exit /b 1
)

REM 检查并安装依赖
set REQUIREMENTS_FILE=%BACKEND_DIR%\requirements.txt
if exist "%REQUIREMENTS_FILE%" (
    echo 安装后端依赖...
    pip install -q -r "%REQUIREMENTS_FILE%"
    echo 后端依赖已安装
)

REM 执行数据库迁移
echo 执行数据库迁移...
cd /d "%BACKEND_DIR%"
python manage.py makemigrations --noinput >nul 2>&1
python manage.py migrate --noinput >nul 2>&1
echo 数据库迁移完成

echo.

REM ======================== 前端设置 ========================
echo 设置前端环境...

set FRONTEND_DIR=%PROJECT_ROOT%frontend
set NODE_MODULES=%FRONTEND_DIR%\node_modules

REM 检查 node_modules
if not exist "%NODE_MODULES%" (
    echo 依赖未安装，正在安装 npm 包...
    cd /d "%FRONTEND_DIR%"
    call npm install
    echo npm 包已安装
) else (
    echo npm 包已安装
)

echo.

REM ======================== 启动服务 ========================
echo ========================================
echo    启动服务...
echo ========================================
echo.

REM 启动后端
echo 启动后端服务 (127.0.0.1:8001)...
cd /d "%BACKEND_DIR%"
start "Django Backend" cmd /k "call "%ACTIVATE_SCRIPT%" && python manage.py runserver 127.0.0.1:8001"

timeout /t 3 /nobreak

REM 启动前端
echo 启动前端服务 (http://localhost:5173)...
cd /d "%FRONTEND_DIR%"
start "Vue3 Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo    服务启动成功！
echo ========================================
echo.
echo 后端地址: http://127.0.0.1:8001
echo 前端地址: http://localhost:5173
echo.
echo 提示: 两个新的命令窗口将打开，分别运行后端和前端
echo 要停止服务，关闭这两个窗口或按 Ctrl+C
echo.

pause
