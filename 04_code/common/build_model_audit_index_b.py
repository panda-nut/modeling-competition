"""为 [B] 平行模型产物生成独立 Markdown 索引和机器可读元数据。"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "03_data" / "processed"
FIGURES = ROOT / "05_figures"
INDEX = PROCESSED / "model-audit-index-b.md"
METADATA = PROCESSED / "model-audit-metadata-b.json"
EVIDENCE_ID = "E-Q1-Q5-B-ALT-001"
GENERATORS = {
    "q1": "04_code/q1/model/q1_effect_analysis_b.py",
    "q2": "04_code/q2/model/q2_surrogate_audit_b.py",
    "q3": "04_code/q3/model/q3_optimization_audit_b.py",
    "q4": "04_code/q4/model/q4_preference_audit_b.py",
    "q5": "04_code/q5/model/q5_robustness_audit_b.py",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def question_for(path: Path) -> str:
    for part in path.parts:
        if part in GENERATORS:
            return part
    raise ValueError(f"Cannot infer question for {path}")


def main() -> None:
    data_rows = []
    for path in sorted(PROCESSED.glob("q*/**/*_b.csv")):
        frame = pd.read_csv(path)
        question = question_for(path)
        data_rows.append(
            {
                "question": question.upper(),
                "path": path.relative_to(ROOT).as_posix(),
                "rows": len(frame),
                "columns": len(frame.columns),
                "fields": "、".join(map(str, frame.columns)),
                "sha256": sha256(path),
                "generator": GENERATORS[question],
            }
        )

    figure_rows = []
    for path in sorted(FIGURES.glob("q*/**/*_b.*")):
        figure_rows.append(
            {
                "question": question_for(path).upper(),
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "generator": "04_code/q1/plotting/q1_plot_results_b.py" if "q1" in path.parts else "",
            }
        )

    lines = [
        "# [B] 平行模型产物索引",
        "",
        f"> Evidence ID：`{EVIDENCE_ID}`；阶段：`v0`；复核：`pending`。本索引不改变原主模型及其正式状态。",
        "",
        "## 数据文件",
        "",
        "| 问题 | 路径 | 行 | 列 | 字段 | SHA-256 | 生成程序 |",
        "| --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in data_rows:
        lines.append(
            f"| {row['question']} | `{row['path']}` | {row['rows']} | {row['columns']} | {row['fields']} | `{row['sha256']}` | `{row['generator']}` |"
        )
    lines.extend(
        [
            "",
            "## 图表文件",
            "",
            "| 问题 | 路径 | SHA-256 | 生成程序 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in figure_rows:
        lines.append(f"| {row['question']} | `{row['path']}` | `{row['sha256']}` | `{row['generator']}` |")
    lines.extend(
        [
            "",
            "## 统一运行口径",
            "",
            "- 输入：官方原始数据的现有只读处理结果与原模型工作产物。",
            "- 单位：`R`、`P`、`U` 延续附件无量纲口径；结构参数延续题面定义。",
            "- 缺失值：生成程序发现关键字段缺失时停止，不做静默填补。",
            "- 随机种子：程序内固定为 `20260730` 及明确偏移值。",
            "- 当前环境：本机 Python 3.14.0 系统解释器；项目 `.venv` 因中文路径启动问题尚未完成复核。",
            "- 当前结论：仅为 `[B]` 平行候选与审计结果，不得写入冻结结果或替换主模型。",
            "",
        ]
    )
    INDEX.write_text("\n".join(lines), encoding="utf-8")

    metadata = {
        "question": "Q1-Q5",
        "progress": "completed",
        "stage": "v0",
        "review": "pending",
        "evidence_id": EVIDENCE_ID,
        "source_commit": source_commit(),
        "updated_at": "2026-07-30",
        "machine": "B",
        "data_files": data_rows,
        "figure_files": figure_rows,
        "environment_limit": "Executed with system Python 3.14.0 because project .venv cannot start from the current Unicode path.",
    }
    METADATA.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {INDEX}")
    print(f"wrote {METADATA}")


if __name__ == "__main__":
    main()
