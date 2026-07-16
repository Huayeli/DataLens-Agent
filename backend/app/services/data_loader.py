from pathlib import Path
import pandas as pd
import chardet


class DataLoader:
    """工业级数据加载器（稳定增强版）"""

    SUPPORTED_EXTENSIONS = [".csv", ".xls", ".xlsx"]

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    # =========================
    # 数据集列表
    # =========================
    def list_datasets(self):
        if not self.data_dir.exists():
            return []

        return [
            f for f in self.data_dir.iterdir()
            if f.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]

    # =========================
    # 加载入口
    # =========================
    def load(self, file_path: Path):

        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            df = self._read_csv_safe(file_path)

        elif suffix in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path)

        else:
            raise ValueError(f"不支持格式: {suffix}")

        return self._basic_clean(df)

    # =========================
    # CSV 安全读取（核心）
    # =========================
    def _read_csv_safe(self, file_path: Path):

        encoding = self._detect_encoding(file_path)
        sep = self._detect_separator(file_path, encoding)

        # 1. 主读取
        df = self._try_read(file_path, encoding, sep)
        if df is not None:
            return df

        # 2. fallback 编码
        for enc in ["utf-8", "gbk", "cp1252", "latin1"]:
            df = self._try_read(file_path, enc, sep)
            if df is not None:
                return df

        # 3. 最终兜底（强制跳坏行）
        return pd.read_csv(
            file_path,
            encoding="latin1",
            sep=sep,
            on_bad_lines="skip",
            engine="python"
        )

    # =========================
    # 安全读取单次尝试
    # =========================
    def _try_read(self, file_path, encoding, sep):
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding,
                sep=sep,
                on_bad_lines="skip"
            )
        except Exception:
            return None

    # =========================
    # 编码检测（增强安全）
    # =========================
    def _detect_encoding(self, file_path: Path):

        with open(file_path, "rb") as f:
            raw = f.read(200000)

        result = chardet.detect(raw)

        encoding = result.get("encoding")

        if not encoding:
            return "utf-8"

        return encoding

    # =========================
    # 分隔符检测（更稳）
    # =========================
    def _detect_separator(self, file_path: Path, encoding: str):

        try:
            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                line = f.readline()

            if ";" in line:
                return ";"
            elif "\t" in line:
                return "\t"
            else:
                return ","

        except Exception:
            return ","

    # =========================
    # 基础清洗
    # =========================
    def _basic_clean(self, df: pd.DataFrame):

        # 去空行
        df = df.dropna(how="all")

        # 去重
        df = df.drop_duplicates()

        # 列名标准化
        df.columns = [
            str(col).strip().lower().replace(" ", "_")
            for col in df.columns
        ]

        return df