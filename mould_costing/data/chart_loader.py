"""Loads the standardized cost-chart workbook into per-sheet DataFrames."""

import pandas as pd

REQUIRED_SHEETS: dict[str, list[str]] = {
    "GuidePin": ["Type", "MainDiameter", "OtherDiameter", "TotalLength", "Hours", "Cost"],
    "BushPin": ["Type", "Diameter", "OtherDiameter", "TotalLength", "Hours", "Cost"],
    "ReturnPin": ["D1", "Length", "Rate"],
    "Bolts": ["D1", "Length", "Rate"],
    "Plates": ["Material", "Density", "Rate"],
}


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
            callback()

    def is_loaded(self) -> bool:
        return bool(self.sheets)

    def get(self, sheet_name: str) -> pd.DataFrame | None:
        return self.sheets.get(sheet_name)

    def unique_values(self, sheet_name: str, column: str, fallback: list[str]) -> list[str]:
        df = self.get(sheet_name)
        if df is None or column not in df.columns:
            return fallback
        values = sorted(str(v) for v in df[column].dropna().unique())
        return values or fallback
