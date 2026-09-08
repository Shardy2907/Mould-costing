import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import cavity_housing_drilling
from mould_costing.gui.section_frame import SectionFrame


class CavityHousingDrillingFrame(SectionFrame):
    """Diameter is picked here; Thickness is read live from the Top Plate
    section's own Thickness input, not re-entered."""

    def __init__(
        self,
        parent,
        chart_loader,
        on_change,
        plate_thickness_var: tk.StringVar,
        title: str = "Cavity Housing Drilling",
    ):
        self.plate_thickness_var = plate_thickness_var
        super().__init__(
            parent,
            title,
            ["Diameter", "Thickness"],
            chart_loader,
            on_change,
            default_qty=4,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.diameter_var = tk.StringVar()
        self.thickness_display_var = tk.StringVar()

        ttk.Label(frame, text="Bolt Diameter:").grid(row=0, column=0, sticky="w")
        self.diameter_combo = ttk.Combobox(
            frame, textvariable=self.diameter_var, values=[], width=10, state="readonly"
        )
        self.diameter_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Top Plate Thickness:").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.thickness_display_var, font=("Segoe UI", 9, "bold")).grid(
            row=1, column=1, sticky="w"
        )
        self._sync_thickness_display()
        self.plate_thickness_var.trace_add("write", lambda *_args: self._sync_thickness_display())

    def _sync_thickness_display(self) -> None:
        value = self.plate_thickness_var.get()
        self.thickness_display_var.set(f"{value} mm" if value else "(not entered yet)")

    def refresh_chart(self) -> None:
        diameters = self.chart_loader.unique_values("Cavityhousingdrilling", "Diameter", [])
        self.diameter_combo["values"] = diameters
        if self.diameter_var.get() not in diameters:
            self.diameter_var.set(diameters[0] if diameters else "")

    def populate_inputs(self, item: dict) -> None:
        self.diameter_var.set(item["Diameter"])

    def collect_line(self) -> tuple[dict, float]:
        diameter = self.diameter_var.get()
        if not diameter:
            raise ValueError("No Diameter available in the chart.")

        thickness_str = self.plate_thickness_var.get()
        if not thickness_str:
            raise ValueError("Enter a Thickness in the Top Plate section first.")
        try:
            thickness = float(thickness_str)
        except ValueError:
            raise ValueError("Top Plate Thickness must be a number.")

        result = cavity_housing_drilling.calculate(self.chart_loader, diameter, thickness)
        values = {"Diameter": diameter, "Thickness": result.extra["Bracket"]}
        return values, result.unit_cost
