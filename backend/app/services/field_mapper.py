import pandas as pd


class FieldMapper:
    """
    统一不同数据集的字段名称，并补充标准分析字段
    """

    def map(self, df: pd.DataFrame) -> pd.DataFrame:

        # ---------- Global Superstore ----------
        if "order_date" in df.columns:

            if "product_name" not in df.columns and "product" in df.columns:
                df["product_name"] = df["product"]

            return df

        # ---------- Online Retail ----------
        if "invoicedate" in df.columns or "invoice_date" in df.columns:

            # 字段重命名
            rename_dict = {
                "invoicedate": "order_date",
                "invoice_date": "order_date",
                "description": "product_name",
                "country": "region",
                "unitprice": "unit_price",
                "unit_price": "unit_price"
            }

            df = df.rename(columns=rename_dict)

            # 自动生成 sales
            if "sales" not in df.columns:

                if "quantity" in df.columns and "unit_price" in df.columns:
                    df["sales"] = df["quantity"] * df["unit_price"]

            # Online Retail 没有利润字段
            if "profit" not in df.columns:
                df["profit"] = None

            if "category" not in df.columns:
                df["category"] = None

            return df

        return df