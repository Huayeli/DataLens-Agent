# =====================
# DataLens Agent Dockerfile
# 用于部署到 Render 等云平台
# =====================

# 使用 Python 3.10 精简镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（pandas 需要底层 C 库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件（利用 Docker 缓存层加速构建）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录（SQLite 数据库存放位置）
RUN mkdir -p /app/data

# 暴露端口（Render 默认使用 10000 端口）
EXPOSE 10000

# 启动命令
# 使用 gunicorn + uvicorn workers 实现生产级部署
# workers=4 表示 4 个 worker 进程处理并发
# timeout=120 给 LLM 调用留足时间
CMD ["gunicorn", "backend.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:10000", \
     "--workers", "4", \
     "--timeout", "120"]
