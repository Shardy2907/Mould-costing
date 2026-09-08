import tkinter as tk
from tkinter import ttk

from mould_costing.gui.section_frame import SectionFrame

# Direct fixed costs per bracket (not chart-driven, per spec).
BRACKETS = [(24.0, 30.0, 95.0), (30.0, 48.0, 105.0)]


class SprueBushHoleFrame(SectionFrame):
    """Thickness is read live from the Top Plate section's own Thickness
    input, same as Cavity Housing Drilling -- not re-entered here."""

    def __init__(
        self,
        parent,
        chart_loader,
        on_change,
        plate_thickness_var: tk.StringVar,
        title: str = "Sprue Bush Hole",
    ):
        self.plate_thickness_var = plate_thickness_var
        super().__init__(parent, title, ["Thickness"], chart_loader, on_change)

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.thickness_display_var = tk.StringVar()
        ttk.Label(frame, text="Top Plate Thickness:").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.thickness_display_var, font=("Segoe UI", 9, "bold")).grid(
            row=0, column=1, sticky="w"
        )
        self._sync_thickness_display()
        self.plate_thickness_var.trace_add("write", lambda *_args: self._sync_thickness_display())

    def _sync_thickness_display(self) -> None:
        value = self.plate_thickness_var.get()
        self.thickness_display_var.set(f"{value} mm" if value else "(not entered yet)")

    def populate_inputs(self, item: dict) -> None:
        pass

    def collect_line(self) -> tuple[dict, float]:
        thickness_str = self.plate_thickness_var.get()
        if not thickness_str:
            raise ValueError("Enter a Thickness in the Top Plate section first.")
        try:
            thickness = float(thickness_str)
        except ValueError:
            raise ValueError("Top Plate Thickness must be a number.")

        for low, high, cost in BRACKETS:
            if low <= thickness <= high:
                return {"Thickness": f"{low:g}-{high:g}"}, cost

        raise ValueError(f"No Sprue Bush Hole bracket covers {thickness}mm.")
