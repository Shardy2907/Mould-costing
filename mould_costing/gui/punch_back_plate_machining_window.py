import tkinter as tk
from tkinter import ttk

from mould_costing.gui.cavity_housing_drilling_frame import CavityHousingDrillingFrame
from mould_costing.gui.scrollable_frame import ScrollableFrame


class PunchBackPlateMachiningWindow(tk.Toplevel):
    """Configure machining for Punch Back Plate -- almost identical to Bottom
    Plate's machining window: a single Diameter + Thickness bracket cost
    feature (own independent Bolt Diameter, not shared with Spacer Blocks/
    Bottom Plate), looked up from the PunchBackPlate chart. Clicking OK
    commits the total as a single line item on the Punch Back Plate section
    and closes this window."""

    def __init__(self, parent, chart_loader, punch_back_plate_frame, on_ok):
        super().__init__(parent)
        self.title("Punch Back Plate - Machining")
        self.geometry("480x360")
        self._on_ok = on_ok

        self.total_var = tk.StringVar()
        ttk.Label(self, textvariable=self.total_var, font=("Segoe UI", 11, "bold")).pack(
            side="top", fill="x", padx=8, pady=8
        )
        ttk.Button(self, text="OK", command=self._on_ok_clicked).pack(side="bottom", fill="x", padx=8, pady=8)

        scroll_area = ScrollableFrame(self)
        scroll_area.pack(side="top", fill="both", expand=True)
        container = scroll_area.inner
        container.columnconfigure(0, weight=1)

        try:
            plate_qty = int(punch_back_plate_frame.qty_var.get())
        except ValueError:
            plate_qty = 1
        drilling_default_qty = plate_qty if plate_qty > 0 else 1

        prefix = "Punch Back Plate - "
        self.sub_frames = [
            CavityHousingDrillingFrame(
                container,
                chart_loader,
                self._recalc,
                punch_back_plate_frame.thickness_var,
                sheet_name="PunchBackPlate",
                title=prefix + "Housing Drilling",
                plate_label="Punch Back Plate",
                default_qty=drilling_default_qty,
            ),
        ]
        for index, frame in enumerate(self.sub_frames):
            frame.grid(row=index, column=0, sticky="nsew", padx=4, pady=4)

        self._recalc()

    def get_subtotal(self) -> float:
        return sum(frame.get_subtotal() for frame in self.sub_frames)

    def get_export_rows(self) -> list[dict]:
        rows = []
        for frame in self.sub_frames:
            rows.extend(frame.get_export_rows())
        return rows

    def load_state(self, snapshot: list[list[dict]]) -> None:
        for frame, items in zip(self.sub_frames, snapshot):
            frame.load_items(items)

    def _recalc(self) -> None:
        self.total_var.set(f"Machining Total: {self.get_subtotal():,.2f}")

    def _on_ok_clicked(self) -> None:
        total = self.get_subtotal()
        snapshot = [list(frame.items) for frame in self.sub_frames]
        self.destroy()
        self._on_ok(total, snapshot)
