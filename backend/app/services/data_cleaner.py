import pandas as pd


class DataCleaner:
    """
    通用数据清洗模块
    适用于 Global Superstore / Online Retail 等数据集
    """

    def __init__(self):
        pass

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        主清洗入口
        """

        # 1. 删除全空行
        df = df.dropna(how="all")

        # 2. 删除重复数据
        df = df.drop_duplicates()

        # 3. 统一列名（标准化）
        df.columns = [
            self._normalize_col(col) 
            for col in df.columns]
        # 去掉重复列
        df = df.loc[:, ~df.columns.duplicated()]

        # 4. 去掉字符串首尾空格
        obj_cols = df.select_dtypes(include="object").columns
        for col in obj_cols:
            df[col] = df[col].astype(str).str.strip()

        # 5. 日期字段处理
        df = self._parse_dates(df)

        # 6. 数值字段处理
        df = self._convert_numeric(df)

        return df

    def _normalize_col(self, col: str) -> str:
        """
        列名标准化：
        Order Date -> order_date
        Product Name -> product_name
        """
        col = str(col).strip().lower()
        col = col.replace(" ", "_")
        col = col.replace("-", "_")
        return col

    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        自动识别日期字段（避免 future warning）
        """

        for col in df.columns:
            if "date" in col:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

        return df

    def _convert_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        自动转换数值字段（安全版）
        """

        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_numeric(df[col])
                except Exception:
                    pass

        return df