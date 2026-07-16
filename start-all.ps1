# ==============================
# DataLens Agent 一键启动脚本（终极稳定修复版）
# ==============================

$ErrorActionPreference = "Stop"

# ==============================
# UTF-8 & 控制台环境修复
# ==============================
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host " DataLens Agent 启动中..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# ==============================
# 进入项目目录
# ==============================
Set-Location "D:\Project\Datalens Agent"

# ==============================
# 清理旧 Python 进程（防止端口占用）
# ==============================
Write-Host "清理旧 Python 进程..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# ==============================
# 激活虚拟环境
# ==============================
Write-Host "激活虚拟环境..."
& ".\.venv\Scripts\Activate.ps1"

# ==============================
# 安装依赖
# ==============================
Write-Host "安装依赖..."
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
# 启动 FastAPI
# ==============================
Write-Host "启动 FastAPI..."

Start-Process powershell -ArgumentList "-NoExit", "-Command", `
"uvicorn backend.main:app --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 3

# ==============================
# 打开 Swagger
# ==============================
Start-Process "http://127.0.0.1:8000/docs"

Write-Host "==================================" -ForegroundColor Green
Write-Host " 启动完成" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green