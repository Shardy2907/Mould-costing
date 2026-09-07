import pandas as pd

from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader


def calculate(chart_loader: ChartLoader, type_: str, diameter: float, length: float) -> LineResult:
    df = chart_loader.get("GuideBush")
    if df is None:
        raise LookupMissError("Guide Bush chart is not loaded.")

    match = df[
        (df["Type"].astype(str) == str(type_))
        & (df["Diameter C"].astype(float) == float(diameter))
        & (df["Length"].astype(float) == float(length))
    ]
    if match.empty:
        raise LookupMissError(
            f"No chart match for Guide Bush Type={type_}, Ø{diameter}, L={length}"
        )

    row = match.iloc[0]
    if pd.isna(row["Total Cost"]):
        raise LookupMissError(
            f"Chart has no Total Cost yet for Guide Bush Type={type_}, Ø{diameter}, L={length}"
        )

    return LineResult(
        unit_cost=float(row["Total Cost"]),
        extra={
            "DiameterD": row["Diameter D"],
            "DiameterE": row["Diameter E"],
        },
    )
