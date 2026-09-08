import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import plate
from mould_costing.gui.section_frame import SectionFrame

MATERIAL_OPTIONS = ["C45", "P20", "OHNS"]


class PlateFrame(SectionFrame):
    """Generic material-cost section reused for all 8 plate types (Top Plate,
    Cavity Plate, Punch Plate, ... just pass a different title)."""

    def __init__(self, parent, title: str, chart_loader, on_change):
        super().__init__(
            parent,
            title,
            ["Material", "Width", "Height", "Thickness", "Weight (kg)", "Rate"],
            chart_loader,
            on_change,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.material_var = tk.StringVar(value=MATERIAL_OPTIONS[0])
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.thickness_var = tk.StringVar()
        self.rate_var = tk.StringVar()

        ttk.Label(frame, text="Material:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            frame, textvariable=self.material_var, values=MATERIAL_OPTIONS, width=8, state="readonly"
        ).grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Width (mm):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.width_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Height (mm):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.height_var, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Thickness (mm):").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.thickness_var, width=10).grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Rate:").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.rate_var, width=10).grid(row=4, column=1, sticky="w")

    def populate_inputs(self, item: dict) -> None:
        self.material_var.set(item["Material"])
        self.width_var.set(str(item["Width"] - plate.STOCK_ALLOWANCE_MM))
        self.height_var.set(str(item["Height"] - plate.STOCK_ALLOWANCE_MM))
        self.thickness_var.set(str(item["Thickness"]))
        self.rate_var.set(str(item["Rate"]))

    def collect_line(self) -> tuple[dict, float]:
        material = self.material_var.get()
        try:
            width_input = float(self.width_var.get())
            height_input = float(self.height_var.get())
            thickness_input = float(self.thickness_var.get())
        except ValueError:
            raise ValueError("Width, Height, and Thickness must be numbers.")
        try:
            rate = float(self.rate_var.get())
        except ValueError:
            raise ValueError("Rate must be a number.")

        result = plate.calculate(self.chart_loader, width_input, height_input, thickness_input, rate)
        values = {
            "Material": material,
            "Width": result.extra["Width"],
            "Height": result.extra["Height"],
            "Thickness": result.extra["Thickness"],
            "Weight (kg)": round(result.extra["Weight"], 3),
            "Rate": rate,
        }
        return values, result.unit_cost
