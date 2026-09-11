import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import bolt_standard_cost
from mould_costing.gui.section_frame import SectionFrame


class PunchHousingDrillingFrame(SectionFrame):
    """Bolt Diameter shares its variable with Spacer Blocks' Clamping Bolt
    Machining (and is populated from the same BoltStandards chart, so both
    stay in sync); Thickness is read live from the Bottom Plate section's own
    Thickness input, and cost is looked up from PunchHousingDrilling using
    Diameter + Thickness bracket -- same logic as Top Plate's Cavity Housing
    Drilling."""

    def __init__(
        self,
        parent,
        chart_loader,
        on_change,
        plate_thickness_var: tk.StringVar,
        bolt_diameter_var: tk.StringVar,
        title: str = "Punch Housing Drilling",
        default_qty: int = 1,
    ):
        self.plate_thickness_var = plate_thickness_var
        self.bolt_var = bolt_diameter_var
        super().__init__(
            parent,
            title,
            ["Bolt Diameter", "Thickness"],
            chart_loader,
            on_change,
            default_qty=default_qty,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.thickness_display_var = tk.StringVar()

        ttk.Label(frame, text="Bolt Diameter:").grid(row=0, column=0, sticky="w")
        self.bolt_combo = ttk.Combobox(frame, textvariable=self.bolt_var, values=[], width=10)
        self.bolt_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Bottom Plate Thickness:").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.thickness_display_var, font=("Segoe UI", 9, "bold")).grid(
            row=1, column=1, sticky="w"
        )
        self._sync_thickness_display()
        self.plate_thickness_var.trace_add("write", lambda *_args: self._sync_thickness_display())

    def _sync_thickness_display(self) -> None:
        value = self.plate_thickness_var.get()
        self.thickness_display_var.set(f"{value} mm" if value else "(not entered yet)")

    def refresh_chart(self) -> None:
        bolts = self.chart_loader.unique_values("BoltStandards", "Bolt Dia", [])
        self.bolt_combo["values"] = bolts
        if self.bolt_var.get() not in bolts:
            self.bolt_var.set(bolts[0] if bolts else "")

    def populate_inputs(self, item: dict) -> None:
        self.bolt_var.set(item["Bolt Diameter"])

    def collect_line(self) -> tuple[dict, float]:
        bolt = self.bolt_var.get()
        if not bolt:
            raise ValueError("No Bolt Diameter available in the BoltStandards chart.")

        thickness_str = self.plate_thickness_var.get()
        if not thickness_str:
            raise ValueError("Enter a Thickness in the Bottom Plate section first.")
        try:
            thickness = float(thickness_str)
        except ValueError:
            raise ValueError("Bottom Plate Thickness must be a number.")

        result = bolt_standard_cost.calculate(self.chart_loader, "PunchHousingDrilling", bolt, thickness)
        values = {"Bolt Diameter": bolt, "Thickness": result.extra["Bracket"]}
        return values, result.unit_cost
