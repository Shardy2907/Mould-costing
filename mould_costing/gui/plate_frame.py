import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import plate
from mould_costing.gui.section_frame import SectionFrame

DEFAULT_MATERIALS = ["Material A"]


class PlateFrame(SectionFrame):
    def __init__(self, parent, chart_loader, on_change):
        super().__init__(
            parent,
            "Plates",
            ["Material", "X", "Y", "Z", "Density", "Weight (kg)"],
            chart_loader,
            on_change,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.material_var = tk.StringVar(value=DEFAULT_MATERIALS[0])
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.z_var = tk.StringVar()
        self.density_var = tk.StringVar()

        ttk.Label(frame, text="Material:").grid(row=0, column=0, sticky="w")
        self.material_combo = ttk.Combobox(
            frame, textvariable=self.material_var, values=DEFAULT_MATERIALS, width=12, state="readonly"
        )
        self.material_combo.grid(row=0, column=1, sticky="w")
        self.material_combo.bind("<<ComboboxSelected>>", self._on_material_change)

        ttk.Label(frame, text="X (mm):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.x_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Y (mm):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.y_var, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Z (mm):").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.z_var, width=10).grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Density:").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.density_var, width=10).grid(row=4, column=1, sticky="w")

    def _on_material_change(self, _event=None) -> None:
        default_density = plate.default_density(self.chart_loader, self.material_var.get())
        if default_density is not None:
            self.density_var.set(str(default_density))

    def refresh_chart(self) -> None:
        materials = self.chart_loader.unique_values("Plates", "Material", DEFAULT_MATERIALS)
        self.material_combo["values"] = materials
        if self.material_var.get() not in materials:
            self.material_var.set(materials[0])
        self._on_material_change()

    def collect_line(self) -> tuple[dict, float]:
        material = self.material_var.get()
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            z = float(self.z_var.get())
        except ValueError:
            raise ValueError("X, Y, and Z must be numbers.")
        try:
            density = float(self.density_var.get())
        except ValueError:
            raise ValueError("Density must be a number.")

        result = plate.calculate(self.chart_loader, material, x, y, z, density)
        values = {
            "Material": material,
            "X": x,
            "Y": y,
            "Z": z,
            "Density": density,
            "Weight (kg)": round(result.extra["WeightKg"], 3),
        }
        return values, result.unit_cost
