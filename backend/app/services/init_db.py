from pathlib import Path

from backend.app.database import Base, engine
from backend.app.services.data_loader import DataLoader
from backend.app.services.data_cleaner import DataCleaner
from backend.app.services.field_mapper import FieldMapper


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

            # 数据表名称
            table_name = (
                file.stem.lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

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