import hashlib
import re
from pathlib import Path

from backend.app.database import Base, engine
from backend.app.services.data_cleaner import DataCleaner
from backend.app.services.data_loader import DataLoader
from backend.app.services.field_mapper import FieldMapper


def ascii_table_name(name: str) -> str:
    """将数据源文件名转换为纯 ASCII 的表名。

    中文描述（如“波兰房价portland_housing”）会被移除，
    避免生成含中文的表名导致 SQL 语句无法匹配。
    """
    text = name.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")

    if not text:
        # 纯中文文件名兜底：追加短散列，保证唯一且可读
        digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]
        text = f"dataset_{digest}"

    if text[0].isdigit():
        text = "t_" + text

    return text


class InitDB:

    def __init__(self):

        self.data_dir = Path(__file__).resolve().parents[3] / "data"

        self.loader = DataLoader(self.data_dir)
        self.cleaner = DataCleaner()
        self.mapper = FieldMapper()

    def run(self):

        print("开始初始化数据库...")

        # 创建 ORM 表
        Base.metadata.create_all(bind=engine)

        datasets = self.loader.list_datasets()

        if not datasets:
            print("未发现数据集")
            return

        print(f"发现 {len(datasets)} 个数据集")

        for file in datasets:

            print("-" * 50)
            print(f"正在处理：{file.name}")

            # 读取
            df = self.loader.load(file)
            print(f"原始数据：{df.shape}")

            # 清洗
            df = self.cleaner.clean(df)
            print(f"清洗完成：{df.shape}")

            # 字段统一
            df = self.mapper.map(df)
            print(f"字段统一完成：{df.shape}")

            # 数据表名称（仅保留 ASCII）
            table_name = ascii_table_name(file.stem)

            # 写入 SQLite
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
                index=False
            )

            print(f"已写入数据表：{table_name}")

        print("-" * 50)
        print("数据库初始化完成")


if __name__ == "__main__":
    InitDB().run()