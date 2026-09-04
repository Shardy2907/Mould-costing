from mould_costing.calculators import LineResult, LookupMissError
from mould_costing.data.chart_loader import ChartLoader


def calculate(
    chart_loader: ChartLoader,
    material: str,
    x: float,
    y: float,
    z: float,
    density: float,
) -> LineResult:
    df = chart_loader.get("Plates")
    if df is None:
        raise LookupMissError("Plates chart is not loaded.")

    match = df[df["Material"].astype(str) == str(material)]
    if match.empty:
        raise LookupMissError(f"No chart match for Plate Material={material}")

    row = match.iloc[0]
    rate = float(row["Rate"])
    weight_kg = float(x) * float(y) * float(z) * float(density)
    price = weight_kg * rate

    return LineResult(unit_cost=price, extra={"WeightKg": weight_kg, "Rate": rate})


def default_density(chart_loader: ChartLoader, material: str) -> float | None:
    df = chart_loader.get("Plates")
    if df is None:
        return None
    match = df[df["Material"].astype(str) == str(material)]
    if match.empty:
        return None
    return float(match.iloc[0]["Density"])
