import tkinter as tk
from tkinter import ttk

from mould_costing.calculators.bolt_counterbore import (
    STANDARD_BOLT_DEFAULTS,
    get_bolt_defaults,
    lookup_drilling_cost,
)
from mould_costing.data.chart_loader import _natural_sort_key
from mould_costing.gui.section_frame import SectionFrame

DEFAULT_BOLT_OPTIONS = list(STANDARD_BOLT_DEFAULTS.keys())


class SpacerBlockBoltFrame(SectionFrame):
    """Machining options for Spacer Blocks:
    Bolt diameter dropdown with default calculated clearance hole diameter,
    counterbore diameter, and counterbore depth that remain fully editable.
    """

    def __init__(
        self,
        parent,
        chart_loader,
        on_change,
        plate_thickness_var: tk.StringVar,
        title: str = "Clamping Bolt Machining",
    ):
        self.plate_thickness_var = plate_thickness_var
        self._is_populating = False
        super().__init__(
            parent,
            title,
            [
                "Bolt Diameter",
                "Clearance Dia (mm)",
                "Counterbore Dia (mm)",
                "Counterbore Depth (mm)",
            ],
            chart_loader,
            on_change,
            default_qty=4,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.bolt_var = tk.StringVar(value="M10")
        self.clearance_var = tk.StringVar()
        self.counterbore_dia_var = tk.StringVar()
        self.counterbore_depth_var = tk.StringVar()
        self.thickness_display_var = tk.StringVar()
        self.cost_var = tk.StringVar(value="0.0")

        # Row 0: Bolt diameter & Spacer block thickness
        ttk.Label(frame, text="Bolt Diameter:").grid(
            row=0, column=0, sticky="w", padx=(0, 4), pady=2)
        self.bolt_combo = ttk.Combobox(
            frame, textvariable=self.bolt_var, values=DEFAULT_BOLT_OPTIONS, width=10, state="readonly"
        )
        self.bolt_combo.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=2)

        ttk.Label(frame, text="Spacer Block Thickness:").grid(
            row=0, column=2, sticky="w", padx=(0, 4), pady=2)
        ttk.Label(frame, textvariable=self.thickness_display_var, font=("Segoe UI", 9, "bold")).grid(
            row=0, column=3, sticky="w", pady=2
        )

        # Row 1: Clearance Hole Dia & Counterbore Dia
        ttk.Label(frame, text="Clearance Hole Dia (mm):").grid(
            row=1, column=0, sticky="w", padx=(0, 4), pady=2)
        self.clearance_entry = ttk.Entry(
            frame, textvariable=self.clearance_var, width=10)
        self.clearance_entry.grid(
            row=1, column=1, sticky="w", padx=(0, 12), pady=2)

        ttk.Label(frame, text="Counterbore Dia (mm):").grid(
            row=1, column=2, sticky="w", padx=(0, 4), pady=2)
        self.cb_dia_entry = ttk.Entry(
            frame, textvariable=self.counterbore_dia_var, width=10)
        self.cb_dia_entry.grid(row=1, column=3, sticky="w", pady=2)

        # Row 2: Counterbore Depth & Unit Cost
        ttk.Label(frame, text="Counterbore Depth (mm):").grid(
            row=2, column=0, sticky="w", padx=(0, 4), pady=2)
        self.cb_depth_entry = ttk.Entry(
            frame, textvariable=self.counterbore_depth_var, width=10)
        self.cb_depth_entry.grid(
            row=2, column=1, sticky="w", padx=(0, 12), pady=2)

        ttk.Label(frame, text="Unit Cost (₹):").grid(
            row=2, column=2, sticky="w", padx=(0, 4), pady=2)
        self.cost_entry = ttk.Entry(
            frame, textvariable=self.cost_var, width=10)
        self.cost_entry.grid(row=2, column=3, sticky="w", pady=2)

        # Traces & event bindings
        self._sync_thickness_display()
        self.plate_thickness_var.trace_add(
            "write", lambda *_args: self._on_thickness_changed())
        self.bolt_var.trace_add(
            "write", lambda *_args: self._on_bolt_selected())

        # Set initial default values for the starting bolt (M10)
        self._apply_bolt_defaults(self.bolt_var.get())

    def _sync_thickness_display(self) -> None:
        value = self.plate_thickness_var.get()
        self.thickness_display_var.set(
            f"{value} mm" if value else "(not entered yet)")

    def _on_thickness_changed(self) -> None:
        self._sync_thickness_display()
        if not self._is_populating:
            self._try_auto_cost()

    def _on_bolt_selected(self) -> None:
        if self._is_populating:
            return
        bolt = self.bolt_var.get()
        self._apply_bolt_defaults(bolt)
        self._try_auto_cost()

    def _apply_bolt_defaults(self, bolt: str) -> None:
        defaults = get_bolt_defaults(bolt)
        self.clearance_var.set(str(defaults["clearance_hole"]))
        self.counterbore_dia_var.set(str(defaults["counterbore_dia"]))
        self.counterbore_depth_var.set(str(defaults["counterbore_depth"]))

    def _try_auto_cost(self) -> None:
        bolt = self.bolt_var.get()
        thickness_str = self.plate_thickness_var.get()
        try:
            thickness = float(thickness_str) if thickness_str else None
        except ValueError:
            thickness = None

        cost = lookup_drilling_cost(self.chart_loader, bolt, thickness)
        if cost is not None:
            self.cost_var.set(str(cost))

    def refresh_chart(self) -> None:
        chart_bolts = self.chart_loader.unique_values("Bolts", "D1", [])
        combined = sorted(
            set(DEFAULT_BOLT_OPTIONS + chart_bolts), key=_natural_sort_key)
        self.bolt_combo["values"] = combined
        if self.bolt_var.get() not in combined and combined:
            self.bolt_var.set(combined[0])
        self._try_auto_cost()

    def populate_inputs(self, item: dict) -> None:
        self._is_populating = True
        try:
            if "Bolt Diameter" in item:
                self.bolt_var.set(item["Bolt Diameter"])
            if "Clearance Dia (mm)" in item:
                self.clearance_var.set(str(item["Clearance Dia (mm)"]))
            if "Counterbore Dia (mm)" in item:
                self.counterbore_dia_var.set(str(item["Counterbore Dia (mm)"]))
            if "Counterbore Depth (mm)" in item:
                self.counterbore_depth_var.set(
                    str(item["Counterbore Depth (mm)"]))
            if "Unit Cost" in item:
                self.cost_var.set(str(item["Unit Cost"]))
            if "Qty" in item:
                self.qty_var.set(str(item["Qty"]))
        finally:
            self._is_populating = False

    def collect_line(self) -> tuple[dict, float]:
        bolt = self.bolt_var.get().strip()
        if not bolt:
            raise ValueError("Select a Bolt Diameter.")

        try:
            clearance = float(self.clearance_var.get())
            if clearance <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError(
                "Clearance Hole Diameter must be a positive number.")

        try:
            cb_dia = float(self.counterbore_dia_var.get())
            if cb_dia <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError("Counterbore Diameter must be a positive number.")

        try:
            cb_depth = float(self.counterbore_depth_var.get())
            if cb_depth <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError("Counterbore Depth must be a positive number.")

        try:
            cost = float(self.cost_var.get())
            if cost < 0:
                raise ValueError()
        except ValueError:
            raise ValueError("Unit Cost must be a non-negative number.")

        values = {
            "Bolt Diameter": bolt,
            "Clearance Dia (mm)": clearance,
            "Counterbore Dia (mm)": cb_dia,
            "Counterbore Depth (mm)": cb_depth,
        }
        return values, cost
