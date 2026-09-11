import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import bolt_standard_cost
from mould_costing.data.chart_loader import format_value
from mould_costing.gui.section_frame import SectionFrame


class SpacerBlockBoltFrame(SectionFrame):
    """Bolt Diameter shares its variable with the Bottom Plate section's own
    Bolt Diameter field, so picking one updates the other; Clearance Hole/
    Counterbore Dia/Counterbore Depth come straight from the BoltStandards
    chart (read-only), and cost is looked up from SpacerBlocksCosting using
    the Spacer Blocks section's own Thickness input (not re-entered)."""

    def __init__(
        self,
        parent,
        chart_loader,
        on_change,
        plate_thickness_var: tk.StringVar,
        bolt_diameter_var: tk.StringVar,
        title: str = "Clamping Bolt Machining",
        default_qty: int = 2,
    ):
        self.plate_thickness_var = plate_thickness_var
        self.bolt_var = bolt_diameter_var
        super().__init__(
            parent,
            title,
            [
                "Bolt Diameter",
                "Clearance Dia (mm)",
                "Counterbore Dia (mm)",
                "Counterbore Depth (mm)",
                "Thickness",
            ],
            chart_loader,
            on_change,
            default_qty=default_qty,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.clearance_display_var = tk.StringVar()
        self.counterbore_dia_display_var = tk.StringVar()
        self.counterbore_depth_display_var = tk.StringVar()
        self.thickness_display_var = tk.StringVar()

        ttk.Label(frame, text="Bolt Diameter:").grid(row=0, column=0, sticky="w")
        self.bolt_combo = ttk.Combobox(frame, textvariable=self.bolt_var, values=[], width=10)
        self.bolt_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Clearance Hole Dia (mm):").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.clearance_display_var, font=("Segoe UI", 9, "bold")).grid(
            row=1, column=1, sticky="w"
        )

        ttk.Label(frame, text="Counterbore Dia (mm):").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.counterbore_dia_display_var, font=("Segoe UI", 9, "bold")).grid(
            row=2, column=1, sticky="w"
        )

        ttk.Label(frame, text="Counterbore Depth (mm):").grid(row=3, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.counterbore_depth_display_var, font=("Segoe UI", 9, "bold")).grid(
            row=3, column=1, sticky="w"
        )

        ttk.Label(frame, text="Spacer Block Thickness:").grid(row=4, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.thickness_display_var, font=("Segoe UI", 9, "bold")).grid(
            row=4, column=1, sticky="w"
        )

        self._sync_thickness_display()
        self.plate_thickness_var.trace_add("write", lambda *_args: self._sync_thickness_display())
        self.bolt_var.trace_add("write", lambda *_args: self._sync_bolt_standards())

    def _sync_thickness_display(self) -> None:
        value = self.plate_thickness_var.get()
        self.thickness_display_var.set(f"{value} mm" if value else "(not entered yet)")

    def _sync_bolt_standards(self) -> None:
        bolt = self.bolt_var.get()
        df = self.chart_loader.get("BoltStandards")
        if df is None or not bolt:
            self.clearance_display_var.set("")
            self.counterbore_dia_display_var.set("")
            self.counterbore_depth_display_var.set("")
            return

        match = df[df["Bolt Dia"].astype(str) == bolt]
        if match.empty:
            self.clearance_display_var.set("(not in chart)")
            self.counterbore_dia_display_var.set("(not in chart)")
            self.counterbore_depth_display_var.set("(not in chart)")
            return

        row = match.iloc[0]
        self.clearance_display_var.set(format_value(row["Clearance hole dia"]))
        self.counterbore_dia_display_var.set(format_value(row["Counter bore dia"]))
        self.counterbore_depth_display_var.set(format_value(row["Counter bore depth"]))

    def refresh_chart(self) -> None:
        bolts = self.chart_loader.unique_values("BoltStandards", "Bolt Dia", [])
        self.bolt_combo["values"] = bolts
        if self.bolt_var.get() not in bolts:
            self.bolt_var.set(bolts[0] if bolts else "")
        else:
            self._sync_bolt_standards()

    def populate_inputs(self, item: dict) -> None:
        self.bolt_var.set(item["Bolt Diameter"])

    def collect_line(self) -> tuple[dict, float]:
        bolt = self.bolt_var.get()
        if not bolt:
            raise ValueError("No Bolt Diameter available in the BoltStandards chart.")

        thickness_str = self.plate_thickness_var.get()
        if not thickness_str:
            raise ValueError("Enter a Thickness in the Spacer Blocks section first.")
        try:
            thickness = float(thickness_str)
        except ValueError:
            raise ValueError("Spacer Blocks Thickness must be a number.")

        result = bolt_standard_cost.calculate_by_thickness(self.chart_loader, "SpacerBlocksCosting", thickness)
        values = {
            "Bolt Diameter": bolt,
            "Clearance Dia (mm)": self.clearance_display_var.get(),
            "Counterbore Dia (mm)": self.counterbore_dia_display_var.get(),
            "Counterbore Depth (mm)": self.counterbore_depth_display_var.get(),
            "Thickness": result.extra["Bracket"],
        }
        return values, result.unit_cost
