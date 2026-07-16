from openai import OpenAI
from dotenv import load_dotenv
import os
import time


# ======================
# 加载 .env
# ======================
load_dotenv()


class LLMService:

    def __init__(self):

        # ======================
        # 读取配置
        # ======================
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置")

        # ======================
        # OpenAI兼容客户端
        # ======================
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    # ======================
    # 核心调用（带重试+容错）
    # ======================
    def chat(self, messages, max_retries=3):

        last_error = None

        for i in range(max_retries):

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    timeout=30
                )

                # ======================
                # 防止空返回
                # ======================
                if not response or not response.choices:
                    raise ValueError("空响应")

                content = response.choices[0].message.content

                if not content:
                    raise ValueError("空内容")

                return content


            except Exception as e:
                last_error = e
                print(f"[LLM重试 {i+1}/{max_retries}] 失败：{e}")
                time.sleep(1.5)

        # ======================
        # 最终失败兜底
        # ======================
        return f"LLM调用失败：{str(last_error)}"