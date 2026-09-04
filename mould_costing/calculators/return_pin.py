from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader


def calculate(chart_loader: ChartLoader, d1: float, length: float) -> LineResult:
    df = chart_loader.get("ReturnPin")
    if df is None:
        raise LookupMissError("Return Pin chart is not loaded.")

    match = df[
        (df["D1"].astype(float) == float(d1)) & (df["Length"].astype(float) == float(length))
    ]
    if match.empty:
        raise LookupMissError(f"No chart match for Return Pin D1={d1}, L={length}")

    row = match.iloc[0]
    return LineResult(unit_cost=float(row["Rate"]))
