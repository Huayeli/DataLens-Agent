# DataLens Agent
基于大模型 + SQL 的智能数据分析 Agent 系统。
本项目实现了对企业数据的自动读取、清洗、数据库存储以及自然语言数据分析功能。

## 项目介绍
DataLens Agent 是一个面向数据分析场景的智能分析系统。

用户可以通过自然语言提问，例如：
- 销售额最高的产品是什么？
- 哪个地区销售情况最好？
- 最近几个月销售趋势如何？

系统会自动理解用户需求，并结合数据库中的业务数据生成分析结果。

## 技术架构
- 后端框架：FastAPI
- 数据库：SQLite
- ORM框架：SQLAlchemy
- 数据处理：Pandas
- 大语言模型：DeepSeek API
- 数据接口：RESTful API

## 项目功能
### 1. 数据加载
支持：
- CSV
- XLS
- XLSX
文件自动读取并转换为结构化数据。

### 2. 数据清洗
实现：
- 缺失值处理
- 重复数据删除
- 字段标准化
- 类型转换

### 3. 数据库存储
使用 SQLite 保存业务数据。
数据表包含：
- 时间
- 产品
- 数量
- 金额
- 地区

### 4. 智能问答分析
用户输入自然语言问题：
例如：
"销售额最高的地区"
系统调用大模型进行分析，并返回结果。

## 系统运行截图
### API接口文档
<img width="1917" height="1015" alt="FastAPI接口界面" src="https://github.com/user-attachments/assets/97a34631-c0fd-4249-bbfe-185cab3ed512" />

### 数据分析效果
<img width="1902" height="1020" alt="分析结果1" src="https://github.com/user-attachments/assets/795bed09-f4aa-4fb4-b6b0-f172b1c42c03" />
<img width="1905" height="1017" alt="分析结果2" src="https://github.com/user-attachments/assets/11a50be3-f771-44b6-9d56-ad821db8f90f" />


### 系统运行界面
<img width="1918" height="1015" alt="运行界面1" src="https://github.com/user-attachments/assets/237a9455-31ab-4071-acfc-53d7dda43882" />
<img width="1918" height="1012" alt="运行界面2" src="https://github.com/user-attachments/assets/f5030667-42ce-4736-92a8-503cf4d01b0a" />
<img width="1917" height="1013" alt="运行界面3" src="https://github.com/user-attachments/assets/582529c1-4308-4a66-b4c4-1e03fe4949eb" />
<img width="1918" height="1010" alt="运行界面4" src="https://github.com/user-attachments/assets/f7336682-eed1-4389-977a-9ca12464ffe2" />

## 运行方式

安装依赖：

```bash
pip install -r requirements.txt

初始化数据库：
python -m backend.app.services.init_db

启动服务：python -m backend.main

访问：http://127.0.0.1:8000/docs
