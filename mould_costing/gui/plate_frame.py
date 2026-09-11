import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import LookupMissError, plate
from mould_costing.gui.section_frame import SectionFrame

MATERIAL_OPTIONS = ["C45", "P20", "OHNS"]


class PlateFrame(SectionFrame):
    """Generic material-cost section reused for all 8 plate types (Top Plate,
    Cavity Plate, Punch Plate, ... just pass a different title)."""

    def __init__(
        self,
        parent,
        title: str,
        chart_loader,
        on_change,
        machining_window_factory=None,
        bolt_diameter_var: tk.StringVar | None = None,
        default_qty: int = 1,
    ):
        self.machining_window_factory = machining_window_factory
        self.machining_window = None
        self._machining_edit_index = None
        self.bolt_diameter_var = bolt_diameter_var
        super().__init__(
            parent,
            title,
            ["Material", "Width", "Height", "Thickness", "Weight (kg)", "Rate"],
            chart_loader,
            on_change,
            default_qty=default_qty,
        )

    def _build_ui(self, default_qty: int) -> None:
        super()._build_ui(default_qty)
        self.tree.column("Material", width=210, minwidth=210, anchor="w", stretch=False)
        if self.machining_window_factory is not None:
            ttk.Button(self, text="Machining...", command=self._open_machining).pack(fill="x", pady=(4, 0))

    def _open_machining(self, edit_index: int | None = None) -> None:
        if self.machining_window is not None and self.machining_window.winfo_exists():
            self.machining_window.lift()
            self.machining_window.focus_force()
            return
        self._machining_edit_index = edit_index
        self.machining_window = self.machining_window_factory(self, self._commit_machining)
        if edit_index is not None:
            snapshot = self.items[edit_index].get("_machining_state")
            if snapshot:
                self.machining_window.load_state(snapshot)

    def _commit_machining(self, total: float, snapshot: list) -> None:
        idx = self._machining_edit_index
        if idx is not None:
            item = dict(self.items[idx])
            qty = item.get("Qty", 1)
            item["Unit Cost"] = round(total, 2)
            item["Total"] = round(total * qty, 2)
            item["_machining_state"] = snapshot
            self.items[idx] = item
            iid = self.tree.get_children()[idx]
            self.tree.item(iid, values=[item.get(c, "") for c in self.full_columns])
            self._recalc()
        else:
            self.add_item({"Material": "Total Machining Cost", "_machining_state": snapshot}, total)
        self.machining_window = None
        self._machining_edit_index = None

    def _on_edit(self) -> None:
        selected = self.tree.selection()
        if selected:
            idx = self.tree.index(selected[0])
            item = self.items[idx]
            if "_machining_state" in item:
                self._open_machining(edit_index=idx)
                return
            if "Width" not in item:
                self._set_status("Remove this row and re-add to change it.")
                return
        super()._on_edit()

    def _on_add(self) -> None:
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError("Quantity must be a positive whole number.")
        except ValueError:
            self._set_status("Quantity must be a positive whole number.")
            return

        try:
            values, unit_cost, area, sg_cost = self._collect_full_line()
        except LookupMissError as exc:
            self._set_status(str(exc))
            return
        except ValueError as exc:
            self._set_status(f"Invalid input: {exc}")
            return

        if self._editing_index is not None:
            item = dict(values)
            item["Qty"] = qty
            item["Unit Cost"] = round(unit_cost, 2)
            item["Total"] = round(unit_cost * qty, 2)
            idx = self._editing_index
            self.items[idx] = item
            iid = self.tree.get_children()[idx]
            self.tree.item(iid, values=[item.get(c, "") for c in self.full_columns])
            self._cancel_edit()
            self._clear_status()
            self._recalc()
        else:
            self.add_item(values, unit_cost, qty)
            self.add_item({"Material": f"Squaring Grinding (Area: {area:.2f} sq.in)"}, sg_cost, qty)

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.material_var = tk.StringVar(value=MATERIAL_OPTIONS[0])
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.thickness_var = tk.StringVar()
        self.rate_var = tk.StringVar()
        self.sg_rate_var = tk.StringVar()

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

        ttk.Label(frame, text="SG Rate:").grid(row=5, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.sg_rate_var, width=10).grid(row=5, column=1, sticky="w")

        if self.bolt_diameter_var is not None:
            ttk.Label(frame, text="Bolt Diameter:").grid(row=6, column=0, sticky="w")
            self.bolt_diameter_combo = ttk.Combobox(
                frame, textvariable=self.bolt_diameter_var, values=[], width=10
            )
            self.bolt_diameter_combo.grid(row=6, column=1, sticky="w")

    def refresh_chart(self) -> None:
        if self.bolt_diameter_var is None:
            return
        bolts = self.chart_loader.unique_values("BoltStandards", "Bolt Dia", [])
        self.bolt_diameter_combo["values"] = bolts
        if not self.bolt_diameter_var.get() and bolts:
            self.bolt_diameter_var.set(bolts[0])

    def populate_inputs(self, item: dict) -> None:
        if "Width" not in item:
            return
        self.material_var.set(item["Material"])
        self.width_var.set(str(item["Width"] - plate.STOCK_ALLOWANCE_MM))
        self.height_var.set(str(item["Height"] - plate.STOCK_ALLOWANCE_MM))
        self.thickness_var.set(str(item["Thickness"]))
        self.rate_var.set(str(item["Rate"]))

    def collect_line(self) -> tuple[dict, float]:
        values, unit_cost, _area, _sg_cost = self._collect_full_line()
        return values, unit_cost

    def _collect_full_line(self) -> tuple[dict, float, float, float]:
        """Returns (material values/cost, squaring-grinding area, squaring-grinding cost)."""
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
        try:
            sg_rate = float(self.sg_rate_var.get())
        except ValueError:
            raise ValueError("SG Rate must be a number.")

        result = plate.calculate(self.chart_loader, width_input, height_input, thickness_input, rate)
        area, sg_cost = plate.calculate_sg_cost(
            result.extra["Width"], result.extra["Height"], result.extra["Thickness"], sg_rate
        )
        values = {
            "Material": material,
            "Width": result.extra["Width"],
            "Height": result.extra["Height"],
            "Thickness": result.extra["Thickness"],
            "Weight (kg)": round(result.extra["Weight"], 3),
            "Rate": rate,
        }
        return values, result.unit_cost, area, sg_cost
