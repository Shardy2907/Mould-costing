import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import return_pin
from mould_costing.gui.section_frame import SectionFrame


class ReturnPinFrame(SectionFrame):
    def __init__(self, parent, chart_loader, on_change):
        super().__init__(
            parent,
            "Return Pin",
            ["D1", "Length"],
            chart_loader,
            on_change,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.d1_var = tk.StringVar()
        self.length_var = tk.StringVar()

        ttk.Label(frame, text="D1 (mm):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.d1_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Length (mm):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.length_var, width=10).grid(row=1, column=1, sticky="w")

    def collect_line(self) -> tuple[dict, float]:
        try:
            d1 = float(self.d1_var.get())
        except ValueError:
            raise ValueError("D1 must be a number.")
        try:
            length = float(self.length_var.get())
        except ValueError:
            raise ValueError("Length must be a number.")

        result = return_pin.calculate(self.chart_loader, d1, length)
        values = {"D1": d1, "Length": length}
        return values, result.unit_cost
