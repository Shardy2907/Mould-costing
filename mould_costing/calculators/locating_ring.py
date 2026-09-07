"""Locating Ring has exactly one standard part (fixed D1/thickness), so there is
no lookup key to choose from -- just the single row's cost."""

import pandas as pd

from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader


def calculate(chart_loader: ChartLoader) -> LineResult:
    df = chart_loader.get("LocatingRing")
    if df is None or df.empty:
        raise LookupMissError("Locating Ring chart has no data yet.")

    row = df.iloc[0]
    if pd.isna(row["cost"]):
        raise LookupMissError("Chart has no cost yet for Locating Ring.")

    return LineResult(
        unit_cost=float(row["cost"]),
        extra={"D1": row["D1"], "Thickness": row["thickness"]},
    )
