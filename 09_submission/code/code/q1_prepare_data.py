"""把官方附件2转换为供分析和绘图读取的Q1 CSV。"""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "03_data" / "raw" / "apmcm-2026-b-appendix-2-data.xlsx"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "q1_response_data.csv"


def main() -> None:
    raw = pd.read_excel(SOURCE, header=1)
    raw.columns = ["id", "a", "b", "N", "R", "P", "U"]
    clean = raw.apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"wrote {len(clean)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
