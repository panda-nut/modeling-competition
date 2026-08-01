# Q2—Q5 复现证据

本目录保存跨问题的 V1 可复现性检查，而非论文正式结果。

- `q2_q5_reproduction_checks.csv`：19 项可机器读取的不变量检查；
- `q2_q5_reproduction_evidence.json`：运行环境、命令、输入哈希和结论；
- `q2_q5_reproduction_report.md`：供人阅读的结论和限制。

当前状态：`progress=completed`、`stage=v1`、`review=pass_with_limits`。
该结论只表示当前登记入口在 Python 3.14 环境中能重建，并通过数据接口、设计域、收敛和风险边界检查；不代表已冻结、已获外部实验验证或可以直接写入 `08_results/`。
