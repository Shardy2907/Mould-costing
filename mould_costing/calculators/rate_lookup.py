"""Generic exact-match chart lookup for parts whose cost is simply a chart `Rate`
(Return Pin, Bolts, Dowelling Sleeve, Hook Strip, Ejector Guide Pin/Bush, Locating Ring)."""

import pandas as pd

from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader, column_matches


def calculate(chart_loader: ChartLoader, sheet_name: str, part_label: str, **filters) -> LineResult:
    df = chart_loader.get(sheet_name)
    if df is None:
        raise LookupMissError(f"{part_label} chart is not loaded.")

    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        mask &= column_matches(df[column], value)
    match = df[mask]

    if match.empty:
        description = ", ".join(f"{key}={value}" for key, value in filters.items())
        raise LookupMissError(f"No chart match for {part_label} {description}")

    row = match.iloc[0]
    if pd.isna(row["Rate"]):
        description = ", ".join(f"{key}={value}" for key, value in filters.items())
        raise LookupMissError(f"Chart has no Rate yet for {part_label} {description}")

    return LineResult(unit_cost=float(row["Rate"]))
