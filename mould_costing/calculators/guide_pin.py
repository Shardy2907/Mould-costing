from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader


def calculate(chart_loader: ChartLoader, type_: str, main_diameter: float, length: float, side: str) -> LineResult:
    df = chart_loader.get("GuidePin")
    if df is None:
        raise LookupMissError("Guide Pin chart is not loaded.")

    match = df[
        (df["Type"].astype(str) == str(type_))
        & (df["MainDiameter"].astype(float) == float(main_diameter))
        & (df["TotalLength"].astype(float) == float(length))
    ]
    if match.empty:
        raise LookupMissError(
            f"No chart match for Guide Pin Type={type_}, Ø{main_diameter}, L={length}"
        )

    row = match.iloc[0]
    return LineResult(
        unit_cost=float(row["Cost"]),
        extra={
            "OtherDiameter": row["OtherDiameter"],
            "Hours": row["Hours"],
            "Side": side,
        },
    )
