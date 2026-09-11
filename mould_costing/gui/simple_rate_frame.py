"""Reusable D1 -> Length -> Rate section (Return Pin, Dowelling Sleeve,
Ejector Guide Pin/Bush all share this exact shape)."""

import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import rate_lookup
from mould_costing.data.chart_loader import format_value
from mould_costing.gui.section_frame import SectionFrame


class SimpleRateFrame(SectionFrame):
    def __init__(
        self,
        parent,
        title: str,
        sheet_name: str,
        chart_loader,
        on_change,
        fixed_qty: int | None = None,
        default_qty: int = 1,
        d1_column: str = "D1",
    ):
        self.sheet_name = sheet_name
        self.d1_column = d1_column
        super().__init__(
            parent,
            title,
            ["D1", "Length"],
            chart_loader,
            on_change,
            default_qty=default_qty,
            fixed_qty=fixed_qty,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.d1_var = tk.StringVar()
        self.length_var = tk.StringVar()

        ttk.Label(frame, text="D1 (mm):").grid(row=0, column=0, sticky="w")
        self.d1_combo = ttk.Combobox(frame, textvariable=self.d1_var, values=[], width=10, state="readonly")
        self.d1_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Length (mm):").grid(row=1, column=0, sticky="w")
        self.length_combo = ttk.Combobox(
            frame, textvariable=self.length_var, values=[], width=10, state="readonly"
        )
        self.length_combo.grid(row=1, column=1, sticky="w")

        self.d1_var.trace_add("write", lambda *_args: self._refresh_lengths())

    def refresh_chart(self) -> None:
        d1_values = self.chart_loader.unique_values(self.sheet_name, self.d1_column, [])
        self.d1_combo["values"] = d1_values
        if self.d1_var.get() not in d1_values:
            self.d1_var.set(d1_values[0] if d1_values else "")
        else:
            self._refresh_lengths()

    def _refresh_lengths(self) -> None:
        lengths = self.chart_loader.filtered_unique_values(
            self.sheet_name, "Length", {self.d1_column: self.d1_var.get()}, []
        )
        self.length_combo["values"] = lengths
        if self.length_var.get() not in lengths:
            self.length_var.set(lengths[0] if lengths else "")

    def populate_inputs(self, item: dict) -> None:
        self.d1_var.set(format_value(item["D1"]))
        self.length_var.set(format_value(item["Length"]))

    def collect_line(self) -> tuple[dict, float]:
        if not self.d1_var.get() or not self.length_var.get():
            raise ValueError("No matching D1/Length available in the chart.")

        d1 = float(self.d1_var.get())
        length = float(self.length_var.get())

        result = rate_lookup.calculate(
            self.chart_loader, self.sheet_name, self.title, **{self.d1_column: d1, "Length": length}
        )
        values = {"D1": d1, "Length": length}
        return values, result.unit_cost
