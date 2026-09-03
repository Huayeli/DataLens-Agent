# ==============================
# DataLens Agent 一键启动脚本
# ==============================

$ErrorActionPreference = "Stop"

# ==============================
# UTF-8 & 控制台环境修复
# ==============================
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$Root = "D:\Project\Datalens Agent"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host " DataLens Agent 启动中..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

Set-Location $Root

# ==============================
# 清理旧 Python 进程（防止端口占用）
# ==============================
Write-Host "清理旧 Python 进程..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# ==============================
# 激活虚拟环境
# ==============================
Write-Host "激活虚拟环境..."
& "$Root\.venv\Scripts\Activate.ps1"

# ==============================
# 安装 Python 依赖
# ==============================
Write-Host "安装 Python 依赖..."
pip install -r requirements.txt

# ==============================
# 初始化数据库
# ==============================
Write-Host "初始化数据库..."
python -m backend.app.services.init_db

if ($LASTEXITCODE -ne 0) {
    Write-Host "数据库初始化失败" -ForegroundColor Red
    exit 1
}

# ==============================
# 构建前端（Vue 3 + Vite）
# ==============================
Write-Host "构建前端..."
Set-Location "$Root\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "安装前端依赖（首次运行需要几分钟）..."
    npm install
}

npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "前端构建失败" -ForegroundColor Red
    exit 1
}

Set-Location $Root

# ==============================
# 启动 FastAPI（同时托管前端）
# ==============================
Write-Host "启动 FastAPI..."

Start-Process powershell -ArgumentList "-NoExit", "-Command", `
"uvicorn backend.main:app --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 3

# ==============================
# 打开前端页面
# ==============================
Start-Process "http://127.0.0.1:8000/"
Write-Host "==================================" -ForegroundColor Green
Write-Host " 启动完成" -ForegroundColor Green
Write-Host " 访问地址：" -ForegroundColor Green -NoNewline
Write-Host "http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host " API文档：http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green