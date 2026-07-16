import json
import re

from backend.app.services.llm import LLMService
from backend.app.services.sql_tool import SQLTool



class SQLAgent:


    def __init__(self):

        self.llm=LLMService()

        self.sql_tool=SQLTool()

        self.history=[]



        # 当前表

        self.current_table=None





    # ======================
    # JSON解析
    # ======================

    def _extract_json(self,text):


        try:

            return json.loads(text)


        except:


            match=re.search(
                r"\{.*\}",
                text,
                re.S
            )


            if match:

                try:

                    return json.loads(
                        match.group()
                    )

                except:

                    pass


        return None





    # ======================
    # 获取当前表结构
    # ======================

    def get_table_schema(
        self,
        table
    ):


        if not table:

            return ""



        try:


            cols=self.sql_tool.get_columns(
                table
            )


            schema=""


            schema+=f"""

当前数据表:

{table}


字段:

"""


            for c in cols:


                schema+=c+"\n"



            return schema



        except:


            return ""






    # ======================
    # 图表判断
    # ======================

    def detect_chart(self,q):


        words_line=[

            "趋势",
            "变化",
            "增长",
            "下降",
            "每月",
            "每年",
            "时间"

        ]



        words_bar=[

            "最高",
            "最低",
            "最多",
            "最好",
            "排名",
            "比较",
            "分别",
            "各个",
            "分类"


        ]


        for w in words_line:

            if w in q:

                return "line"



        for w in words_bar:

            if w in q:

                return "bar"



        return "table"






    # ======================
    # 主流程
    # ======================


    def run(
        self,
        user_question,
        current_table=None
    ):



        self.current_table=current_table



        schema=self.get_table_schema(
            current_table
        )



        chart=self.detect_chart(
            user_question
        )





        prompt=f"""


你是DataLens智能数据分析Agent。


你的任务:

根据当前数据表生成SQL并分析。


=================

数据库信息:

{schema}


=================


用户问题:

{user_question}



必须返回JSON:


{{
"sql":"",
"chart":"",
"x":"",
"y":"",
"analysis":""
}}



SQL规则:


1.
只能SELECT。


禁止:

delete
update
insert
drop
alter



2.

必须严格使用提供字段。


禁止创造不存在字段。


3.

根据字段含义判断:


数量:

SUM


金额:

SUM


评分:

AVG


时间:

GROUP BY 时间字段



4.

比较问题:


例如:

哪个商品最好

哪个地区最高


必须返回全部分类。


禁止:

LIMIT 1



正确:


SELECT
类别,
SUM(金额)
FROM 当前表
GROUP BY 类别



5.

图表:

趋势:

line


分类比较:

bar


普通:

table



6.

如果返回大量数据:

最多500条。



只返回JSON。
"""






        messages=[


            {

                "role":
                "system",

                "content":
                "你是SQL专家"

            }

        ]



        messages.extend(
            self.history[-6:]
        )



        messages.append(

            {

                "role":
                "user",

                "content":
                prompt

            }

        )





        response=self.llm.chat(
            messages
        )



        data=self._extract_json(
            response
        )



        if not data:


            return {

                "answer":response,

                "sql":None,

                "data":[],

                "chart":"table"

            }





        sql=data.get(
            "sql",
            ""
        )



        chart=data.get(
            "chart",
            chart
        )


        x=data.get(
            "x",
            ""
        )


        y=data.get(
            "y",
            ""
        )





        if not sql:


            return {

                "answer":
                "无法生成SQL",

                "sql":None,

                "data":[],

                "chart":chart

            }







        # ======================
        # SQL安全
        # ======================


        danger=[

            "delete",
            "update",
            "insert",
            "drop",
            "alter"

        ]


        for d in danger:


            if d in sql.lower():


                return {

                    "answer":
                    "检测到非法SQL",

                    "sql":sql,

                    "data":[],

                    "chart":"table"

                }







        # ======================
        # 自动限制数量
        # ======================


        if "limit" not in sql.lower():


            sql=sql.rstrip(";")

            sql+=" LIMIT 500"







        # ======================
        # 执行
        # ======================


        result=self.sql_tool.run(
            sql
        )



        if not result.get(
            "success"
        ):


            return {


                "answer":
                "SQL执行失败:"+
                result.get(
                    "error",
                    ""
                ),


                "sql":sql,

                "data":[],

                "chart":"table"

            }






        table=result.get(
            "data",
            []
        )





        # 自动生成坐标字段


        if table:


            keys=list(
                table[0].keys()
            )


            if len(keys)>=2:


                if not x:

                    x=keys[0]


                if not y:

                    y=keys[1]







        summary=f"""

用户问题:

{user_question}



查询结果:

{json.dumps(
table,
ensure_ascii=False
)}



请直接回答:

1.结果

2.排名

3.关键数据


不要说:

分析完成

回答要求：

不要使用Markdown符号。
不要使用**加粗**。
不要使用#标题。
直接输出普通中文文本。

"""




        answer=self.llm.chat([


            {

                "role":
                "system",

                "content":
                "你是数据分析师"

            },


            {

                "role":
                "user",

                "content":
                summary

            }


        ])







        self.history.append(

            {

                "role":
                "user",

                "content":
                user_question

            }

        )


        self.history.append(

            {

                "role":
                "assistant",

                "content":
                answer

            }

        )






        return {


            "answer":
            answer,


            "sql":
            sql,


            "data":
            table,


            "chart":
            chart,


            "x":
            x,


            "y":
            y,


            "dataset":
            current_table


        }