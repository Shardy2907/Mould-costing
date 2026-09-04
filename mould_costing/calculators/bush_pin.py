from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader


def calculate(chart_loader: ChartLoader, type_: str, diameter: float, length: float) -> LineResult:
    df = chart_loader.get("BushPin")
    if df is None:
        raise LookupMissError("Bush Pin chart is not loaded.")

    match = df[
        (df["Type"].astype(str) == str(type_))
        & (df["Diameter"].astype(float) == float(diameter))
        & (df["TotalLength"].astype(float) == float(length))
    ]
    if match.empty:
        raise LookupMissError(
            f"No chart match for Bush Pin Type={type_}, Ø{diameter}, L={length}"
        )

    row = match.iloc[0]
    return LineResult(
        unit_cost=float(row["Cost"]),
        extra={
            "OtherDiameter": row["OtherDiameter"],
            "Hours": row["Hours"],
        },
    )
