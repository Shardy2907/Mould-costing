"""Cavity Housing (bolt) Drilling: cost depends on the bolt Diameter and which
Thickness bracket (e.g. "24-30") the Cavity Plate's thickness falls into."""

import pandas as pd

from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader, column_matches

SHEET_NAME = "Cavityhousingdrilling"


def _parse_bracket(bracket: str) -> tuple[float, float] | None:
    parts = str(bracket).split("-")
    if len(parts) != 2:
        return None
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        return None


def calculate(chart_loader: ChartLoader, diameter: str, thickness: float) -> LineResult:
    df = chart_loader.get(SHEET_NAME)
    if df is None or df.empty:
        raise LookupMissError("Cavity Housing Drilling chart is not loaded or has no rows.")

    subset = df[column_matches(df["Diameter"], diameter)]
    if subset.empty:
        raise LookupMissError(f"No chart match for Cavity Housing Drilling Diameter={diameter}")

    for _, row in subset.iterrows():
        bracket = _parse_bracket(row["Thickness"])
        if bracket is None:
            continue
        low, high = bracket
        if low <= thickness <= high:
            if pd.isna(row["Cost"]):
                raise LookupMissError(
                    f"Chart has no Cost yet for Cavity Housing Drilling "
                    f"Diameter={diameter}, Thickness={thickness}"
                )
            return LineResult(unit_cost=float(row["Cost"]), extra={"Bracket": row["Thickness"]})

    raise LookupMissError(
        f"No thickness bracket in the chart covers {thickness}mm for Diameter={diameter}"
    )
