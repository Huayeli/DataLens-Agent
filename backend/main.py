import os
from pathlib import Path

from dotenv import set_key
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.app import config
from backend.app.services.llm import LLMService
from backend.app.services.sql_agent import SQLAgent
from backend.app.services.sql_tool import SQLTool

app = FastAPI(
    title="DataLens Agent",
    description="智能数据分析 Agent（Academia 学术风格）",
    version="3.0",
)


# ======================
# CORS（开发模式下 Vite 需要跨域）
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================
# 初始化
# ======================
agent = SQLAgent()
sql_tool = SQLTool()

CURRENT_DATASET = {"name": None}

ENV_PATH = config.BASE_DIR / ".env"


# ======================
# 启动自动选择数据表
# ======================
@app.on_event("startup")
def startup():
    tables = sql_tool.get_tables()
    CURRENT_DATASET["name"] = tables[0] if tables else ""


class ChatRequest(BaseModel):
    message: str
    dataset: str | None = None


class SettingsRequest(BaseModel):
    api_key: str | None = None
    api_base: str | None = None
    model: str | None = None


# ======================
# 运行时可编辑的模型配置
# 优先读取环境变量（load_dotenv 在启动时已注入 .env 的值）
# ======================
def mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "***"
    return "***" + key[-4:]


def current_settings() -> dict:
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    return {
        "model": os.getenv("DEEPSEEK_MODEL", config.DEEPSEEK_MODEL),
        "api_base": os.getenv("DEEPSEEK_API_BASE", config.DEEPSEEK_API_BASE),
        "has_api_key": bool(api_key),
        "key_tail": mask_key(api_key),
    }


def refresh_llm() -> bool:
    """按最新配置重建 LLM 客户端（agent 复用，仅替换底层模型客户端）"""
    try:
        agent.llm = LLMService()
        return True
    except ValueError:
        return False


# ======================
# Chat（智能问答）
# ======================
@app.post("/chat")
def chat(req: ChatRequest):
    if req.dataset:
        CURRENT_DATASET["name"] = req.dataset
    current = CURRENT_DATASET["name"]
    result = agent.run(req.message, CURRENT_DATASET["name"])
    return {
        "answer": result.get("answer", ""),
        "sql": result.get("sql"),
        "data": result.get("data", []),
        "chart": result.get("chart", "table"),
        "x": result.get("x", ""),
        "y": result.get("y", ""),
        "dataset": current,
    }


# ======================
# 上传 CSV
# ======================
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    # 防止路径穿越：仅保留文件名
    safe_name = Path(file.filename or "upload.csv").name
    path = os.path.join("uploads", safe_name)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    table_name = Path(safe_name).stem.replace("-", "_").replace(" ", "_")
    result = sql_tool.create_table_from_csv(path, table_name)

    if result.get("success"):
        CURRENT_DATASET["name"] = result["table"]

    return {
        "success": bool(result.get("success")),
        "message": "上传成功" if result.get("success") else result.get("error", "上传失败"),
        "table": result.get("table", ""),
        "rows": result.get("rows", 0),
    }


# ======================
# 数据集列表
# ======================
@app.get("/datasets")
def datasets():
    return {
        "datasets": sql_tool.get_tables(),
        "current": CURRENT_DATASET["name"],
    }


# ======================
# 数据集统计（行数/字段/预览）
# ======================
@app.get("/datasets/{name}/stats")
def dataset_stats(name: str):
    if name not in sql_tool.get_tables():
        return {"success": False, "msg": "数据集不存在"}
    result = sql_tool.get_stats(name)
    result["name"] = name
    return result


# ======================
# 删除数据集
# ======================
@app.delete("/datasets/{name}")
def delete_dataset(name: str):
    tables = sql_tool.get_tables()
    if name not in tables:
        return {"success": False, "msg": "数据集不存在"}
    result = sql_tool.drop_table(name)
    if result.get("success") and CURRENT_DATASET["name"] == name:
        remaining = sql_tool.get_tables()
        CURRENT_DATASET["name"] = remaining[0] if remaining else ""
    return result


# ======================
# 切换数据集
# ======================
@app.post("/switch/{name}")
def switch(name: str):
    tables = sql_tool.get_tables()
    if name not in tables:
        return {"success": False, "msg": "不存在"}
    CURRENT_DATASET["name"] = name
    return {"success": True, "current": name}


# ======================
# 查看数据（预览）
# ======================
@app.get("/data/{name}")
def data(name: str):
    result = sql_tool.run(f'SELECT * FROM "{name}" LIMIT 200')
    return {"data": result.get("data", [])}


# ======================
# 当前数据集
# ======================
@app.get("/current")
def current():
    return {"current": CURRENT_DATASET["name"]}


# ======================
# 健康检查
# ======================
@app.get("/health")
def health():
    return {
        "status": "running",
        "dataset": CURRENT_DATASET["name"],
        "tables": sql_tool.get_tables(),
    }


# ======================
# 系统信息（兼容旧版）
# ======================
@app.get("/info")
def info():
    return {
        "name": config.APP_NAME,
        "model": os.getenv("DEEPSEEK_MODEL", config.DEEPSEEK_MODEL),
        "api_base": os.getenv("DEEPSEEK_API_BASE", config.DEEPSEEK_API_BASE),
        "has_api_key": bool(os.getenv("DEEPSEEK_API_KEY", "")),
    }


# ======================
# 读取模型配置（设置页可编辑项）
# ======================
@app.get("/settings")
def get_settings():
    return current_settings()


# ======================
# 保存模型配置（写入 .env 并热更新，无需重启）
# api_key 为空时保持不变
# ======================
@app.post("/settings")
def save_settings(req: SettingsRequest):
    updates: dict = {}

    model = (req.model or "").strip()
    api_base = (req.api_base or "").strip()
    api_key = (req.api_key or "").strip()

    if model:
        updates["DEEPSEEK_MODEL"] = model
    if api_base:
        updates["DEEPSEEK_API_BASE"] = api_base
    if req.api_key is not None and req.api_key.strip():
        updates["DEEPSEEK_API_KEY"] = api_key

    if updates:
        if not ENV_PATH.exists():
            ENV_PATH.write_text("", encoding="utf-8")
        for key, value in updates.items():
            set_key(str(ENV_PATH), key, value)
            os.environ[key] = value

    llm_ok = refresh_llm()

    return {
        "success": True,
        "llm_ok": llm_ok,
        "updated": list(updates.keys()),
        "config": current_settings(),
    }


# ======================
# 托管前端构建产物（frontend/dist）
# 仅在生产构建存在时挂载；开发模式请使用 Vite dev server
# ======================
DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="frontend")