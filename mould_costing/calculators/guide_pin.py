import pandas as pd

from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader


def calculate(chart_loader: ChartLoader, type_: str, main_diameter: float, length: float, side: str) -> LineResult:
    df = chart_loader.get("GuidePin")
    if df is None:
        raise LookupMissError("Guide Pin chart is not loaded.")

    match = df[
        (df["Type"].astype(str) == str(type_))
        & (df["Diameter C"].astype(float) == float(main_diameter))
        & (df["Length"].astype(float) == float(length))
    ]
    if match.empty:
        raise LookupMissError(
            f"No chart match for Guide Pin Type={type_}, Ø{main_diameter}, L={length}"
        )

    row = match.iloc[0]
    if pd.isna(row["Total Cost"]):
        raise LookupMissError(
            f"Chart has no Total Cost yet for Guide Pin Type={type_}, Ø{main_diameter}, L={length}"
        )

    return LineResult(
        unit_cost=float(row["Total Cost"]),
        extra={
            "DiameterF": row["Diameter F"],
            "DiameterG": row["Diameter G"],
            "Side": side,
        },
    )
