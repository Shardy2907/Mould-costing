"""Loads the standardized cost-chart workbook into per-sheet DataFrames."""

import re

import pandas as pd

REQUIRED_SHEETS: dict[str, list[str]] = {
    "GuidePin": ["Type", "Diameter C", "Diameter F", "Diameter G", "Length", "Total Cost"],
    "GuideBush": ["Type", "Diameter C", "Diameter D", "Diameter E", "Length", "Total Cost"],
    "ReturnPin": ["D1", "Length", "Rate"],
    "Bolts": ["D1", "Length", "Rate"],
    "DowellingSleeve": ["Outer dia", "Length", "Rate"],
    "HookStrip": ["W", "T", "Length", "Rate"],
    "EjectorGuidePin": ["D1", "Length", "Rate"],
    "EjectorGuideBush": ["D1", "Length", "Rate"],
    "LocatingRing": ["D1", "thickness", "cost"],
    "PlateThickness": ["Thickness"],
    "Cavityhousingdrilling": ["Diameter", "Thickness", "Cost"],
    "BoltStandards": ["Bolt Dia", "Clearance hole dia", "Counter bore dia", "Counter bore depth"],
    "SpacerBlocksCosting": ["Thickness", "Cost"],
}


def _natural_sort_key(value: str):
    match = re.search(r"(\d+)$", value)
    if match:
        return (value[: match.start()], int(match.group(1)))
    return (value, -1)


def format_value(value) -> str:
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return str(value)
    if as_float.is_integer():
        return str(int(as_float))
    return str(as_float)


def column_matches(series: pd.Series, value) -> pd.Series:
    """Compares a chart column to a value, using numeric or string equality
    depending on the column's own dtype (so a dropdown-selected string like
    "25" still matches a numeric 25.0 chart cell)."""
    if pd.api.types.is_numeric_dtype(series):
        try:
            return series.astype(float) == float(value)
        except (TypeError, ValueError):
            return pd.Series(False, index=series.index)
    return series.astype(str) == str(value)


class ChartLoadError(Exception):
    pass


class ChartLoader:
    """Holds the currently loaded chart workbook and notifies listeners on reload."""

    def __init__(self) -> None:
        self.path: str | None = None
        self.sheets: dict[str, pd.DataFrame] = {}
        self._listeners: list[callable] = []

    def on_reload(self, callback) -> None:
        self._listeners.append(callback)

    def load(self, path: str) -> None:
        try:
            raw = pd.read_excel(path, sheet_name=None, engine="openpyxl")
        except Exception as exc:
            raise ChartLoadError(f"Could not open workbook:\n{exc}") from exc

        sheets: dict[str, pd.DataFrame] = {}
        missing_sheets = []
        for sheet_name, columns in REQUIRED_SHEETS.items():
            if sheet_name not in raw:
                missing_sheets.append(sheet_name)
                continue
            df = raw[sheet_name]
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                raise ChartLoadError(
                    f"Sheet '{sheet_name}' is missing column(s): {', '.join(missing_cols)}"
                )
            sheets[sheet_name] = df

        if missing_sheets:
            raise ChartLoadError(
                "Workbook is missing sheet(s): " + ", ".join(missing_sheets)
            )

        self.path = path
        self.sheets = sheets
        for callback in self._listeners:
            try:
                callback()
            except Exception:
                import traceback

                traceback.print_exc()

    def is_loaded(self) -> bool:
        return bool(self.sheets)

    def get(self, sheet_name: str) -> pd.DataFrame | None:
        return self.sheets.get(sheet_name)

    def unique_values(self, sheet_name: str, column: str, fallback: list[str]) -> list[str]:
        df = self.get(sheet_name)
        if df is None or column not in df.columns:
            return fallback
        values = sorted({format_value(v) for v in df[column].dropna().unique()}, key=_natural_sort_key)
        return values or fallback

    def filtered_unique_values(
        self, sheet_name: str, column: str, filters: dict, fallback: list[str]
    ) -> list[str]:
        """Like unique_values, but restricted to rows matching `filters`
        (other column -> currently-selected-value pairs), for cascading dropdowns."""
        df = self.get(sheet_name)
        if df is None or column not in df.columns:
            return fallback
        subset = df
        for filter_column, filter_value in filters.items():
            if filter_column not in subset.columns or not filter_value:
                continue
            subset = subset[column_matches(subset[filter_column], filter_value)]
        values = sorted({format_value(v) for v in subset[column].dropna().unique()}, key=_natural_sort_key)
        return values or fallback
