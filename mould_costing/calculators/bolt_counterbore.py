"""Calculations and standard default specifications for bolt counterbore,
clearance hole diameter, and counterbore depth."""

import re

from mould_costing.data.chart_loader import ChartLoader

STANDARD_BOLT_DEFAULTS: dict[str, dict[str, float]] = {
    "M3": {"clearance_hole": 3.4, "counterbore_dia": 6.5, "counterbore_depth": 3.5},
    "M4": {"clearance_hole": 4.5, "counterbore_dia": 8.5, "counterbore_depth": 4.5},
    "M5": {"clearance_hole": 5.5, "counterbore_dia": 10.0, "counterbore_depth": 5.5},
    "M6": {"clearance_hole": 6.6, "counterbore_dia": 11.0, "counterbore_depth": 6.5},
    "M8": {"clearance_hole": 9.0, "counterbore_dia": 15.0, "counterbore_depth": 9.0},
    "M10": {"clearance_hole": 11.0, "counterbore_dia": 17.5, "counterbore_depth": 11.0},
    "M12": {"clearance_hole": 14.0, "counterbore_dia": 20.0, "counterbore_depth": 13.0},
    "M14": {"clearance_hole": 15.5, "counterbore_dia": 23.0, "counterbore_depth": 15.0},
    "M16": {"clearance_hole": 18.0, "counterbore_dia": 26.0, "counterbore_depth": 17.5},
    "M18": {"clearance_hole": 20.0, "counterbore_dia": 30.0, "counterbore_depth": 19.5},
    "M20": {"clearance_hole": 22.0, "counterbore_dia": 33.0, "counterbore_depth": 21.5},
    "M24": {"clearance_hole": 26.0, "counterbore_dia": 40.0, "counterbore_depth": 25.5},
}

_ANCHORS = [
    (3.0, 3.4, 6.5, 3.5),
    (4.0, 4.5, 8.5, 4.5),
    (5.0, 5.5, 10.0, 5.5),
    (6.0, 6.6, 11.0, 6.5),
    (8.0, 9.0, 15.0, 9.0),
    (10.0, 11.0, 17.5, 11.0),
    (12.0, 14.0, 20.0, 13.0),
    (14.0, 15.5, 23.0, 15.0),
    (16.0, 18.0, 26.0, 17.5),
    (18.0, 20.0, 30.0, 19.5),
    (20.0, 22.0, 33.0, 21.5),
    (24.0, 26.0, 40.0, 25.5),
]


def parse_nominal_diameter(bolt_name: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)", str(bolt_name))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def calculate_bolt_defaults(d: float) -> dict[str, float]:
    """Calculates clearance hole, counterbore diameter, and depth for an arbitrary
    metric bolt size using interpolation between standard anchor sizes."""
    if d <= _ANCHORS[0][0]:
        _, cl, cb, dp = _ANCHORS[0]
        return {"clearance_hole": cl, "counterbore_dia": cb, "counterbore_depth": dp}

    if d >= _ANCHORS[-1][0]:
        d_last, cl_last, cb_last, dp_last = _ANCHORS[-1]
        delta = d - d_last
        return {
            "clearance_hole": round(cl_last + delta, 1),
            "counterbore_dia": round(cb_last + delta * 1.5, 1),
            "counterbore_depth": round(dp_last + delta, 1),
        }

    for i in range(len(_ANCHORS) - 1):
        d0, cl0, cb0, dp0 = _ANCHORS[i]
        d1, cl1, cb1, dp1 = _ANCHORS[i + 1]
        if d0 <= d <= d1:
            ratio = (d - d0) / (d1 - d0) if d1 != d0 else 0.0
            return {
                "clearance_hole": round(cl0 + ratio * (cl1 - cl0), 1),
                "counterbore_dia": round(cb0 + ratio * (cb1 - cb0), 1),
                "counterbore_depth": round(dp0 + ratio * (dp1 - dp0), 1),
            }

    return {"clearance_hole": 0.0, "counterbore_dia": 0.0, "counterbore_depth": 0.0}


def get_bolt_defaults(bolt_diameter: str) -> dict[str, float]:
    """Returns a copy of the default dimensions dictionary for the given bolt diameter."""
    normalized = bolt_diameter.strip().upper()
    if normalized in STANDARD_BOLT_DEFAULTS:
        return dict(STANDARD_BOLT_DEFAULTS[normalized])

    d = parse_nominal_diameter(bolt_diameter)
    if d is not None:
        key = f"M{int(d) if d.is_integer() else d}"
        if key in STANDARD_BOLT_DEFAULTS:
            return dict(STANDARD_BOLT_DEFAULTS[key])
        return calculate_bolt_defaults(d)

    return {"clearance_hole": 0.0, "counterbore_dia": 0.0, "counterbore_depth": 0.0}


def lookup_drilling_cost(chart_loader: ChartLoader, diameter: str, thickness: float | None) -> float | None:
    """Attempts to look up cost from Cavityhousingdrilling sheet if chart and matching row exist."""
    if not chart_loader or not chart_loader.is_loaded() or thickness is None:
        return None
    try:
        from mould_costing.calculators import cavity_housing_drilling

        result = cavity_housing_drilling.calculate(chart_loader, diameter, thickness)
        return result.unit_cost
    except Exception:
        return None
