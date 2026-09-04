import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import bush_pin
from mould_costing.gui.section_frame import SectionFrame


class BushPinFrame(SectionFrame):
    def __init__(self, parent, chart_loader, on_change):
        super().__init__(
            parent,
            "Bush Pin",
            ["Type", "Ø", "Length"],
            chart_loader,
            on_change,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.type_var = tk.StringVar(value="A")
        self.diameter_var = tk.StringVar()
        self.length_var = tk.StringVar()

        ttk.Label(frame, text="Type:").grid(row=0, column=0, sticky="w")
        self.type_combo = ttk.Combobox(
            frame, textvariable=self.type_var, values=["A", "B", "C"], width=8, state="readonly"
        )
        self.type_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Diameter (mm):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.diameter_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Total Length (mm):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.length_var, width=10).grid(row=2, column=1, sticky="w")

    def refresh_chart(self) -> None:
        types = self.chart_loader.unique_values("BushPin", "Type", ["A", "B", "C"])
        self.type_combo["values"] = types
        if self.type_var.get() not in types:
            self.type_var.set(types[0])

    def collect_line(self) -> tuple[dict, float]:
        type_ = self.type_var.get()
        try:
            diameter = float(self.diameter_var.get())
        except ValueError:
            raise ValueError("Diameter must be a number.")
        try:
            length = float(self.length_var.get())
        except ValueError:
            raise ValueError("Total Length must be a number.")

        result = bush_pin.calculate(self.chart_loader, type_, diameter, length)
        values = {"Type": type_, "Ø": diameter, "Length": length}
        return values, result.unit_cost
