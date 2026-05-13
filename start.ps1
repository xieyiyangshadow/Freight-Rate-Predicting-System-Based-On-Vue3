# 一键启动脚本 - 同时启动 Django 后端和 Vue3 前端
# 使用方法: 在项目根目录运行 .\start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   多模型运价预测系统 - 一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录（项目根目录）
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "📁 项目根目录: $ProjectRoot" -ForegroundColor Green
Write-Host ""

# ======================== 后端设置 ========================
Write-Host "🔧 设置后端环境..." -ForegroundColor Yellow

$BackendDir = Join-Path $ProjectRoot "backend"
$VenvPath = Join-Path $BackendDir ".venv"

# 检查虚拟环境
if (!(Test-Path $VenvPath)) {
    Write-Host "⚠️  虚拟环境不存在，正在创建..." -ForegroundColor Yellow
    Set-Location $BackendDir
    python -m venv .venv
    Write-Host "✅ 虚拟环境创建完成" -ForegroundColor Green
} else {
    Write-Host "✅ 虚拟环境已存在" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host "🔌 激活虚拟环境..." -ForegroundColor Yellow
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "❌ 无法找到激活脚本，请手动激活虚拟环境" -ForegroundColor Red
    exit 1
}

# 检查依赖
$RequirementsFile = Join-Path $BackendDir "requirements.txt"
if (Test-Path $RequirementsFile) {
    Write-Host "📦 安装后端依赖..." -ForegroundColor Yellow
    pip install -q -r $RequirementsFile
    Write-Host "✅ 后端依赖已安装" -ForegroundColor Green
}

# 执行数据库迁移
Write-Host "🗄️  执行数据库迁移..." -ForegroundColor Yellow
Set-Location $BackendDir
python manage.py makemigrations --noinput 2>$null
python manage.py migrate --noinput 2>$null
Write-Host "✅ 数据库迁移完成" -ForegroundColor Green

Write-Host ""

# ======================== 前端设置 ========================
Write-Host "🔧 设置前端环境..." -ForegroundColor Yellow

$FrontendDir = Join-Path $ProjectRoot "frontend"
$NodeModulesPath = Join-Path $FrontendDir "node_modules"

# 检查 node_modules
if (!(Test-Path $NodeModulesPath)) {
    Write-Host "⚠️  依赖未安装，正在安装 npm 包..." -ForegroundColor Yellow
    Set-Location $FrontendDir
    npm install
    Write-Host "✅ npm 包已安装" -ForegroundColor Green
} else {
    Write-Host "✅ npm 包已安装" -ForegroundColor Green
}

Write-Host ""

# ======================== 启动服务 ========================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   启动服务..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 启动后端
Write-Host "🚀 启动后端服务 (127.0.0.1:8001)..." -ForegroundColor Magenta
Set-Location $BackendDir
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& `"$ActivateScript`"; python manage.py runserver 127.0.0.1:8001"
Write-Host "✅ 后端已启动 (新窗口)" -ForegroundColor Green

# 等待后端启动
Write-Host "⏳ 等待后端启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 启动前端
Write-Host "🚀 启动前端服务 (http://localhost:5173)..." -ForegroundColor Magenta
Set-Location $FrontendDir
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; npm run dev"
Write-Host "✅ 前端已启动 (新窗口)" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   服务启动成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 后端地址: http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host "📍 前端地址: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 提示: 两个新的 PowerShell 窗口将打开，分别运行后端和前端" -ForegroundColor Yellow
Write-Host "⏹️  要停止服务，关闭两个窗口或按 Ctrl+C" -ForegroundColor Yellow
Write-Host ""
