import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import locating_ring
from mould_costing.data.chart_loader import format_value
from mould_costing.gui.section_frame import SectionFrame


class LocatingRingFrame(SectionFrame):
    """There's only ever one standard Locating Ring, so this section has no
    input dropdowns -- just the fixed part's info and an Add button."""

    def __init__(self, parent, chart_loader, on_change):
        super().__init__(
            parent,
            "Locating Ring",
            ["D1", "Thickness"],
            chart_loader,
            on_change,
            fixed_qty=1,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.info_var = tk.StringVar(value="No chart loaded")
        ttk.Label(frame, textvariable=self.info_var, justify="left").grid(row=0, column=0, sticky="w")

    def refresh_chart(self) -> None:
        df = self.chart_loader.get("LocatingRing")
        if df is None or df.empty:
            self.info_var.set("No Locating Ring data in chart yet.")
            return
        row = df.iloc[0]
        self.info_var.set(
            f"D1: {format_value(row['D1'])}   Thickness: {format_value(row['thickness'])}   "
            f"Cost: {format_value(row['cost'])}"
        )

    def collect_line(self) -> tuple[dict, float]:
        result = locating_ring.calculate(self.chart_loader)
        values = {"D1": result.extra["D1"], "Thickness": result.extra["Thickness"]}
        return values, result.unit_cost

    def populate_inputs(self, item: dict) -> None:
        pass
