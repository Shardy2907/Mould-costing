"""Thickness-bracket cost lookups (e.g. "24-30") used by Top Plate's Cavity
Housing Drilling (Cavityhousingdrilling chart, keyed by Diameter + Thickness)
and Spacer Blocks' Clamping Bolt Machining (SpacerBlocksCosting chart, keyed
by Thickness alone) -- each passes its own sheet name since the two charts
are independent and have different shapes."""

import pandas as pd

from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader, column_matches


def _parse_bracket(bracket: str) -> tuple[float, float] | None:
    parts = str(bracket).split("-")
    if len(parts) != 2:
        return None
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        return None


def calculate(chart_loader: ChartLoader, sheet_name: str, diameter: str, thickness: float) -> LineResult:
    df = chart_loader.get(sheet_name)
    if df is None or df.empty:
        raise LookupMissError(f"{sheet_name} chart is not loaded or has no rows.")

    subset = df[column_matches(df["Diameter"], diameter)]
    if subset.empty:
        raise LookupMissError(f"No chart match in {sheet_name} for Diameter={diameter}")

    for _, row in subset.iterrows():
        bracket = _parse_bracket(row["Thickness"])
        if bracket is None:
            continue
        low, high = bracket
        if low <= thickness <= high:
            if pd.isna(row["Cost"]):
                raise LookupMissError(
                    f"Chart has no Cost yet in {sheet_name} for Diameter={diameter}, Thickness={thickness}"
                )
            return LineResult(unit_cost=float(row["Cost"]), extra={"Bracket": row["Thickness"]})

    raise LookupMissError(
        f"No thickness bracket in {sheet_name} covers {thickness}mm for Diameter={diameter}"
    )


def calculate_by_thickness(chart_loader: ChartLoader, sheet_name: str, thickness: float) -> LineResult:
    """Same bracket lookup as `calculate`, but for charts with no Diameter column
    -- cost depends only on which Thickness bracket the value falls into."""
    df = chart_loader.get(sheet_name)
    if df is None or df.empty:
        raise LookupMissError(f"{sheet_name} chart is not loaded or has no rows.")

    for _, row in df.iterrows():
        bracket = _parse_bracket(row["Thickness"])
        if bracket is None:
            continue
        low, high = bracket
        if low <= thickness <= high:
            if pd.isna(row["Cost"]):
                raise LookupMissError(f"Chart has no Cost yet in {sheet_name} for Thickness={thickness}")
            return LineResult(unit_cost=float(row["Cost"]), extra={"Bracket": row["Thickness"]})

    raise LookupMissError(f"No thickness bracket in {sheet_name} covers {thickness}mm")
