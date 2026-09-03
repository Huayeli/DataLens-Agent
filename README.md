# 数镜 · DataLens

**对话式数据分析 Agent** —— 上传一份 CSV，用自然语言提问，自动生成 SQL、图表与结论。

数镜（DataLens）是一款本地运行的智能数据分析工具。界面采用深色纸墨与黄铜点缀的 Academia 学术风格，前端基于 Vue 3，后端基于 FastAPI + SQLite，模型默认使用 DeepSeek（OpenAI 兼容接口）。

---

## 功能亮点

- **自然语言问数**：如「哪个地区销售额最高？」「每月销售额变化趋势如何？」无需手写 SQL。
- **智能意图识别**：
  - 与数据相关 → 语义映射真实字段 → 自动生成并执行 SQL（失败时按真实字段自动纠错重试一次）。
  - 与数据无关 → 直接调用大模型以助手身份回答。
- **图表自适应**：
  - 趋势类问题绘制折线图，分类比较绘制柱状图，普通查询展示表格。
  - 横轴名称过长时显示可辨识的短词，悬浮或点击查看全称。
  - 分类过多时默认精简为 20 个并提示，可要求展示完整数据。
- **明细与原始数据**：每条数据回答可切换到「明细」查看本次 SQL 返回的行；底部另有「查看原始数据」可展开数据集的原始行列（前 200 行）。
- **对话记忆**：Agent 保留最近 30 条消息（约 15 轮问答），并自动滚动到最新问答区域。
- **多数据集管理**：支持上传、统计、预览、切换与删除多个数据集。
- **运行时模型配置**：设置页可修改 API 地址 / 模型名 / API Key，保存后写入 `.env` 并热生效，无需重启。

---

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3 · Vite · Pinia · ECharts |
| 后端 | FastAPI · SQLAlchemy · pandas |
| 数据库 | SQLite（默认 `data/datalens.db`，可用 `.env` 切换） |
| 模型 | DeepSeek / 任意 OpenAI 兼容 API |

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 1. 安装依赖

```powershell
# 创建并激活虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Python 依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
cd ..
```

### 2. 配置模型

复制 `.env.example` 为 `.env`，填写 DeepSeek API Key：

```ini
DEEPSEEK_API_KEY=sk-xxxx
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

之后也可以在界面「设置」页修改 API 地址 / 模型 / 密钥，保存即热生效，无需重启。

### 3. 导入数据（可选）

将 CSV 放入 `data/` 目录后执行：

```powershell
python -m backend.app.services.init_db
```

脚本会清洗数据并建立以 ASCII 命名的数据表。也可以直接在网页左侧「载入数据」上传 CSV。

### 4. 启动

方式一：后端直接托管前端（推荐）

```powershell
# 先构建前端
cd frontend
npm run build
cd ..

# 启动后端
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

打开 `http://127.0.0.1:8000/` 即可使用；接口文档见 `http://127.0.0.1:8000/docs`。

方式二：前端开发模式（前后端分离、热更新）

```powershell
# 终端 A：后端
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 终端 B：前端（Vite 开发服务器，自动代理 API 到 8000）
cd frontend
npm run dev
```

打开 `http://localhost:5173/`。

方式三：Windows 一键启动

```powershell
.\start-all.ps1
```

> 注意：一键脚本会先清理所有 `python` 进程（避免端口占用），再安装依赖、初始化数据库、构建前端并启动服务。

---

## 数据与存储

| 项 | 位置 / 说明 |
| --- | --- |
| SQLite 数据库 | `data/datalens.db`（`.env` 中 `DATABASE_URL` 可改为其它路径或 PostgreSQL） |
| 网页上传的 CSV | 临时保存于 `uploads/`，随后写入 SQLite 数据表 |
| 数据表命名 | 中文文件名会自动转为纯 ASCII 表名（如「波兰房价 portland_housing.csv」→ `portland_housing`） |
| 编码 | 上传 CSV 自动兼容 UTF-8 / GBK |

运行期上传的新数据集会成为一张表并加入数据集列表；删除数据集即删除对应表。

---

## API 一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/chat` | 智能问答（`{"message": "...", "dataset": "表名"}`） |
| GET | `/datasets` | 数据集列表与当前数据集 |
| POST | `/switch/{name}` | 切换当前数据集 |
| GET | `/datasets/{name}/stats` | 数据集统计（行数 / 字段 / 预览） |
| GET | `/data/{name}` | 读取数据（最多前 200 行，NaN 已转 null） |
| POST | `/upload` | 上传 CSV 并建表 |
| DELETE | `/datasets/{name}` | 删除数据集 |
| GET | `/settings` / POST `/settings` | 读取 / 保存模型配置（热生效） |
| GET | `/health` · `/info` · `/current` | 健康检查、信息、当前数据集 |

`/chat` 返回：

```json
{
  "answer": "分析结论文字",
  "sql": "实际执行的 SQL",
  "data": [ { "行": "数据对象" } ],
  "chart": "table | bar | line",
  "x": "横轴字段",
  "y": "纵轴字段",
  "dataset": "本次使用的数据表"
}
```

---

## 常见问题

- **`no such table` 错误**：确认当前选中了正确的数据集；若 CSV 刚放入 `data/`，先运行 `python -m backend.app.services.init_db` 导入。
- **回答与数据不符 / 图表为空**：检查 `DEEPSEEK_API_KEY` 是否有效（设置页可改并测试保存）。
- **前端修改不生效**：改的是 `frontend/src`，需要 `npm run build`（生产模式）或在开发模式下访问 `5173` 端口。
- **端口被占用**：确认 8000 / 5173 无残留进程后重启，或修改 `.env` 的 `PORT` / `frontend/vite.config.js`。
