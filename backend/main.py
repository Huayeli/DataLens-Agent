import os


from fastapi import (
    FastAPI,
    UploadFile,
    File
)


from fastapi.middleware.cors import CORSMiddleware


from pydantic import BaseModel


from backend.app.services.sql_agent import SQLAgent
from backend.app.services.sql_tool import SQLTool





app=FastAPI(

    title="DataLens Agent",

    description="智能数据分析Agent",

    version="3.0"

)





# ======================
# CORS
# ======================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)





# ======================
# 初始化
# ======================


agent=SQLAgent()

sql_tool=SQLTool()



CURRENT_DATASET={

    "name":None

}





# ======================
# 启动自动选择数据表
# ======================


@app.on_event("startup")
def startup():


    tables=sql_tool.get_tables()


    if tables:


        CURRENT_DATASET["name"]=tables[0]


    else:


        CURRENT_DATASET["name"]=""








# ======================
# 请求
# ======================


class ChatRequest(BaseModel):

    message:str

    dataset:str|None=None







# ======================
# Chat
# ======================


@app.post("/chat")
def chat(req:ChatRequest):


    # 如果前端传数据集

    if req.dataset:


        CURRENT_DATASET["name"]=req.dataset



    current=CURRENT_DATASET["name"]



    result = agent.run(

        req.message,

        CURRENT_DATASET["name"]

    )





    return {


        "answer":
        result.get(
            "answer",
            ""
        ),



        "sql":
        result.get(
            "sql"
        ),



        "data":
        result.get(
            "data",
            []
        ),



        "chart":
        result.get(
            "chart",
            "table"
        ),



        "x":
        result.get(
            "x",
            ""
        ),



        "y":
        result.get(
            "y",
            ""
        ),



        "dataset":
        current


    }










# ======================
# 上传CSV
# ======================


@app.post("/upload")
async def upload(
    file:UploadFile=File(...)
):


    os.makedirs(

        "uploads",

        exist_ok=True

    )



    path=os.path.join(

        "uploads",

        file.filename

    )



    content=await file.read()



    with open(
        path,
        "wb"
    ) as f:


        f.write(content)






    table_name=(

        file.filename

        .replace(".csv","")

        .replace("-","_")

        .replace(" ","_")

    )




    result=sql_tool.create_table_from_csv(

        path,

        table_name

    )




    CURRENT_DATASET["name"]=table_name





    return {


        "success":True,


        "message":
        "上传成功",


        "table":
        table_name,


        "rows":
        result.get(
            "rows",
            0
        )


    }









# ======================
# 数据集列表
# ======================


@app.get("/datasets")
def datasets():


    return {


        "datasets":
        sql_tool.get_tables(),



        "current":
        CURRENT_DATASET["name"]


    }









# ======================
# 切换数据集
# ======================


@app.post("/switch/{name}")
def switch(name:str):


    tables=sql_tool.get_tables()



    if name not in tables:


        return {


            "success":False,


            "msg":
            "不存在"


        }



    CURRENT_DATASET["name"]=name




    return {


        "success":True,


        "current":
        name


    }








# ======================
# 查看数据
# ======================


@app.get("/data/{name}")
def data(name:str):


    result=sql_tool.run(

        f"""

        SELECT *

        FROM {name}

        LIMIT 200

        """

    )


    return {


        "data":
        result.get(
            "data",
            []
        )

    }









@app.get("/current")
def current():


    return {


        "current":
        CURRENT_DATASET["name"]

    }








@app.get("/")
def root():


    return {


        "status":
        "running",


        "dataset":
        CURRENT_DATASET["name"]

    }