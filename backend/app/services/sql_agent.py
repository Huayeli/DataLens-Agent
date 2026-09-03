import json
import re

from backend.app.services.llm import LLMService
from backend.app.services.sql_tool import SQLTool


class SQLAgent:

    # 对话记忆条数（最近 30 条消息，约 15 轮问答）
    MEMORY_SIZE = 30

    def __init__(self):
        self.llm = LLMService()
        self.sql_tool = SQLTool()
        self.history = []
        self.current_table = None

    # ======================
    # JSON 解析
    # ======================
    def _extract_json(self, text):
        try:
            return json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
        return None

    # ======================
    # 获取当前表结构
    # ======================
    def get_table_schema(self, table):
        if not table:
            return ""
        try:
            cols = self.sql_tool.get_columns(table)
            schema = f"当前数据表:\n{table}\n\n字段:\n"
            for col in cols:
                schema += col + "\n"
            return schema
        except Exception:
            return ""

    # ======================
    # 图表类型判断（兜底）
    # ======================
    def detect_chart(self, question):
        line_words = ["趋势", "变化", "增长", "下降", "每月", "每年", "时间"]
        bar_words = ["最高", "最低", "最多", "最好", "排名", "比较", "分别", "各个", "分类"]
        for word in line_words:
            if word in question:
                return "line"
        for word in bar_words:
            if word in question:
                return "bar"
        return "table"

    # ======================
    # 构建 SQL/意图识别提示词
    # ======================
    def _build_prompt(self, user_question, schema):
        return f"""
你是DataLens智能数据分析Agent，根据当前数据卷回答用户问题。

=================
数据库信息:
{schema}
=================

用户问题:
{user_question}

【第一步：判断意图】
判断该问题是否与当前数据表的字段或数据相关：
- 相关：统计、对比、排名、趋势、筛选、数值、字段含义等问题。
- 不相关：常识、计算、闲聊、写作、翻译等与表格数据无关的问题，或表中没有任何字段能对应用户需求的问题。

【字段语义映射（关键）】
用户往往用中文口语提问，而字段名是英文，请先理解语义，再在下方“字段”清单中找出最相近的真实字段，禁止生造字段。
通用对应关系（仅当清单中存在相似字段时参考）：
- 价格/售价/市值 → price、lastsoldprice、zestimate 等含 price 的字段
- 类型/房型/户型/种类 → hometype、type 等字段（本房产数据中 hometype 即房屋类型）
- 卧室/卫生间/面积/大小 → bedrooms、bathrooms、livingarea 等
- 日期/时间/挂牌/成交 → date、datesold、onmarketdate 等
- 城市/地区/地址/邮编 → city、address/city、zipcode 等
- 部门/团队/地区/类别 → 表格中表达分类含义的字段（例如 sales、region、category）
- 薪资/离职/满意度 等管理类词 → 若表格含 salary、left、satisfaction_level 等则使用，否则不必套用
判断标准：
只要问题是想从这张表里了解某种数量、排行、比较、趋势、筛选或某个字段的统计含义，就必须映射到最近字段并返回 type=sql。
只有当问题与表中内容完全无关（如闲聊、常识、写作、数学计算、与表无关的其他话题）时才返回 type=general。

【输出】
只返回一个JSON，两种情况二选一：

1) 与数据相关，返回 SQL 请求：
{{"type":"sql","sql":"","chart":"","x":"","y":""}}

2) 与数据无关，直接以助手身份回答（自然中文，不用Markdown符号）：
{{"type":"general","answer":""}}

【SQL规则】（仅 type=sql 时需遵守）
1. 只能 SELECT；禁止 delete、update、insert、drop、alter。
2. 必须使用 schema 中真实存在的字段；字段含特殊字符时用双引号包裹。
3. 数值聚合按字段语义：数量/金额用 SUM，评分/比例用 AVG，时间字段按时间粒度 GROUP BY。
4. 比较/排名问题（哪个最好/最高/最多/最少）必须返回全部分类，禁止 LIMIT 1；
   正确写法: SELECT 分类字段, SUM(金额) FROM 当前表 GROUP BY 分类字段 ORDER BY 汇总列 DESC
5. 图表: 趋势→line；分类比较→bar；普通查询→table。
6. 返回大量数据时最多 500 行。
只返回JSON。
"""

    # ======================
    # SQL 执行失败时按真实字段纠错重试
    # ======================
    def _retry_sql(self, sql, error, schema, user_question):
        prompt = f"""
之前生成的SQL执行失败。
错误信息:
{error}

数据库信息:
{schema}

用户问题:
{user_question}

失败SQL:
{sql}

请分析失败原因（通常是字段名不存在或拼写不同），把SQL改成使用schema中真实存在的字段。
只返回JSON: {{"sql":""}}
若无法修复则返回 {{"sql":""}}
"""
        try:
            response = self.llm.chat([
                {"role": "system", "content": "你是SQL专家，负责修正SQL。"},
                {"role": "user", "content": prompt},
            ])
            data = self._extract_json(response)
            if data and data.get("sql"):
                fixed = data["sql"].strip()
                if "delete" not in fixed.lower() and "drop" not in fixed.lower():
                    return fixed
        except Exception:
            pass
        return None

    # ======================
    # 主流程
    # ======================
    def run(self, user_question, current_table=None):
        self.current_table = current_table
        schema = self.get_table_schema(current_table)
        chart = self.detect_chart(user_question)

        prompt = self._build_prompt(user_question, schema)

        messages = [{"role": "system", "content": "你是DataLens智能数据分析Agent。"}]
        messages.extend(self.history[-self.MEMORY_SIZE:])
        messages.append({"role": "user", "content": prompt})

        response = self.llm.chat(messages)
        data = self._extract_json(response)

        # LLM 未返回 JSON 时，把原文当作普通回答返回
        if not data:
            self._remember(user_question, response)
            return {"answer": response, "sql": None, "data": [], "chart": "table"}

        answer_type = data.get("type", "sql")

        # ============ 与数据无关 → 普通对话回答 ============
        if answer_type == "general":
            answer = (data.get("answer") or "").strip()
            if not answer:
                answer = "这个问题与当前数据卷无关，暂时无法用数据分析回答，请换一个关于数据的问题。"
            self._remember(user_question, answer)
            return {"answer": answer, "sql": None, "data": [], "chart": "table"}

        # ============ 数据相关 → 生成并执行 SQL ============
        sql = (data.get("sql") or "").strip()
        x = data.get("x", "")
        y = data.get("y", "")

        if not sql:
            answer = "无法根据当前数据卷生成 SQL，请尝试用更明确的字段描述提问。"
            self._remember(user_question, answer)
            return {"answer": answer, "sql": None, "data": [], "chart": chart}

        # SQL 安全
        danger = ["delete", "update", "insert", "drop", "alter"]
        if any(word in sql.lower() for word in danger):
            answer = "检测到非法 SQL，已拦截执行。"
            self._remember(user_question, answer)
            return {"answer": answer, "sql": sql, "data": [], "chart": "table"}

        # 自动限制数量
        if "limit" not in sql.lower():
            sql = sql.rstrip(";") + " LIMIT 500"

        # 执行（失败时按真实字段自动纠错重试一次）
        result = self.sql_tool.run(sql)
        if not result.get("success"):
            fixed = self._retry_sql(sql, result.get("error", ""), schema, user_question)
            if fixed:
                sql = fixed
                if "limit" not in sql.lower():
                    sql = sql.rstrip(";") + " LIMIT 500"
                result = self.sql_tool.run(sql)

        if not result.get("success"):
            answer = (
                "SQL执行失败:"
                + str(result.get("error", ""))
                + "\n\n（已尝试按真实字段自动修正，仍无法执行。请检查字段名或重新描述问题。）"
            )
            self._remember(user_question, answer)
            return {"answer": answer, "sql": sql, "data": [], "chart": "table"}

        table = result.get("data", [])

        # 自动补齐坐标字段
        if table:
            keys = list(table[0].keys())
            if len(keys) >= 2:
                if not x:
                    x = keys[0]
                if not y:
                    y = keys[1]

        summary = f"""
用户问题:
{user_question}

查询结果:
{json.dumps(table, ensure_ascii=False)}

请直接回答:
1.结果
2.排名
3.关键数据

回答要求:
不要使用Markdown符号。
不要使用**加粗**。
不要使用#标题。
直接输出普通中文文本。
"""
        answer = self.llm.chat([
            {"role": "system", "content": "你是数据分析师。"},
            {"role": "user", "content": summary},
        ])

        self._remember(user_question, answer)

        return {
            "answer": answer,
            "sql": sql,
            "data": table,
            "chart": chart,
            "x": x,
            "y": y,
            "dataset": current_table,
        }

    # ======================
    # 记忆最近对话
    # ======================
    def _remember(self, question, answer):
        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": answer})