# Q1 程序

- `model/q1_prepare_data.py`：从官方 Excel 生成 `q1_response_data.csv`。
- `validation/`：机理、单位、范围和证据边界检查。
- `plotting/q1_plot_results.py`：只读取 Q1 CSV 生成主效应、性能权衡和贡献图。

运行顺序：

```powershell
python 04_code/q1/model/q1_prepare_data.py
python 04_code/q1/plotting/q1_plot_results.py
```
