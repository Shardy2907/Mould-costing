"""Plate material cost: pad width/height for machining stock, round thickness
up to the nearest standard stock size, then price by weight."""

from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader

STOCK_ALLOWANCE_MM = 10
DENSITY = 0.008


def _round_up_thickness(chart_loader: ChartLoader, thickness_input: float) -> float:
    df = chart_loader.get("PlateThickness")
    if df is None or df.empty:
        raise LookupMissError("Plate Thickness chart is not loaded or has no rows.")

    candidates = df["Thickness"].dropna().astype(float)
    valid = candidates[candidates >= thickness_input]
    if valid.empty:
        raise LookupMissError(f"No standard thickness in the chart is >= {thickness_input}mm.")
    return float(valid.min())


def calculate(
    chart_loader: ChartLoader,
    width_input: float,
    height_input: float,
    thickness_input: float,
    rate: float,
) -> LineResult:
    width = width_input + STOCK_ALLOWANCE_MM
    height = height_input + STOCK_ALLOWANCE_MM
    thickness = _round_up_thickness(chart_loader, thickness_input)

    volume = width * height * thickness
    weight = (volume * DENSITY)/1000
    cost = weight * rate

    return LineResult(
        unit_cost=cost,
        extra={"Width": width, "Height": height, "Thickness": thickness, "Weight": weight},
    )
