import pandas as pd
import re
import os
import keyword

from sqlalchemy import text, inspect

from backend.app.database import engine




class SQLTool:



    # ==========================
    # SQL执行
    # ==========================

    def run(self, sql:str):
        
        sql = sql.replace(
            "`",
            ""
        )


        try:


            # 防止返回过大数据

            if "limit" not in sql.lower():

                sql = sql.rstrip(";") + " LIMIT 500"



            with engine.connect() as conn:


                result = conn.execute(
                    text(sql)
                )



                if result.returns_rows:


                    rows=result.fetchall()

                    columns=result.keys()



                    df=pd.DataFrame(
                        rows,
                        columns=columns
                    )



                    return {


                        "success":True,


                        "data":
                        df.to_dict(
                            orient="records"
                        ),


                        "sql":sql


                    }



                return {


                    "success":True,


                    "data":[],


                    "sql":sql

                }



        except Exception as e:


            return {


                "success":False,


                "error":str(e),


                "data":[],


                "sql":sql

            }









    # ==========================
    # CSV自动建表
    # ==========================


    def create_table_from_csv(
        self,
        file_path,
        table_name
    ):


        try:


            # 自动编码

            try:

                df=pd.read_csv(
                    file_path,
                    encoding="utf-8-sig"
                )


            except:


                df=pd.read_csv(
                    file_path,
                    encoding="gbk"
                )




            # ======================
            # 清洗字段
            # ======================


            df.columns=[

                self.clean_name(c)

                for c in df.columns

            ]




            # ======================
            # 清洗表名
            # ======================


            table_name=self.clean_name(
                table_name
            )




            # ======================
            # 避免重复
            # ======================


            base=table_name

            count=1



            tables=self.get_tables()



            while table_name in tables:


                table_name=f"{base}_{count}"

                count+=1







            # ======================
            # 入库
            # ======================


            df.to_sql(

                table_name,

                engine,

                if_exists="replace",

                index=False

            )



            return {


                "success":True,


                "table":table_name,


                "rows":len(df),


                "columns":
                list(df.columns)

            }




        except Exception as e:


            return {


                "success":False,


                "error":str(e)

            }









    # ==========================
    # 字段清洗
    # ==========================


    def clean_name(self,name):


        name=str(name)


        name=re.sub(
            r"[^\w]",
            "_",
            name
        )


        name=name.lower()


        if name in [

            "left",
            "right",
            "order",
            "group",
            "select"

        ]:

            name=name+"_col"



        return name






    # ==========================
    # 获取所有表
    # ==========================


    def get_tables(self):


        inspector=inspect(
            engine
        )


        return inspector.get_table_names()









    # ==========================
    # 获取字段
    # ==========================


    def get_columns(
        self,
        table_name
    ):


        inspector=inspect(
            engine
        )



        columns=inspector.get_columns(
            table_name
        )



        return [

            c["name"]

            for c in columns

        ]








    # ==========================
    # 获取完整数据库结构
    # ==========================


    def get_schema(self):


        inspector=inspect(
            engine
        )


        result=""



        tables=self.get_tables()



        for table in tables:


            result+=f"\n表名:{table}\n"



            columns=inspector.get_columns(
                table
            )



            for c in columns:


                result+=(
                    f"{c['name']}"
                    f"({c['type']}) "
                )



            result+="\n"



        return result