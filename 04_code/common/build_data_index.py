"""生成 03_data/processed 下 CSV 的可审计 Markdown 索引。"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "03_data" / "processed"
OUTPUT = DATA_ROOT / "file-index.md"


def describe_csv(path: Path) -> tuple[int, int, str, str]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader, [])
        rows = sum(1 for _ in reader)
    fields = "、".join(header) if header else "（无表头）"
    return rows, len(header), fields, digest


def main() -> None:
    lines = [
        "# 处理数据逐文件索引",
        "",
        "> 由 `04_code/common/build_data_index.py` 生成。SHA-256 用于迁移和复现核对；",
        "> 本索引不等同于技术复核通过或冻结批准。",
        "",
        "| 路径 | 数据行 | 列数 | 字段 | SHA-256 |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for path in sorted(DATA_ROOT.rglob("*.csv")):
        rows, columns, fields, digest = describe_csv(path)
        relative = path.relative_to(DATA_ROOT).as_posix()
        fields = fields.replace("|", r"\|")
        lines.append(
            f"| `{relative}` | {rows} | {columns} | {fields} | `{digest}` |"
        )
    lines.extend(
        [
            "",
            "重新生成：",
            "",
            "```bat",
            ".venv\\Scripts\\python.exe 04_code\\common\\build_data_index.py",
            "```",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"indexed {len(list(DATA_ROOT.rglob('*.csv')))} CSV files -> {OUTPUT}")


if __name__ == "__main__":
    main()
