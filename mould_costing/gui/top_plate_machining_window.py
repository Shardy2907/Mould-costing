import tkinter as tk
from tkinter import ttk

from mould_costing.gui.cavity_housing_drilling_frame import CavityHousingDrillingFrame
from mould_costing.gui.fixed_cost_frame import FixedCostFrame
from mould_costing.gui.scrollable_frame import ScrollableFrame
from mould_costing.gui.sprue_bush_hole_frame import SprueBushHoleFrame


class TopPlateMachiningWindow(tk.Toplevel):
    """Configure machining features here; clicking OK commits the total as a
    single line item on the Top Plate section and closes this window."""

    def __init__(self, parent, chart_loader, top_plate_frame, on_ok):
        super().__init__(parent)
        self.title("Top Plate - Machining")
        self.geometry("480x760")
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

        prefix = "Top Plate - "
        self.sub_frames = [
            CavityHousingDrillingFrame(
                container,
                chart_loader,
                self._recalc,
                top_plate_frame.thickness_var,
                title=prefix + "Cavity Housing Drilling",
            ),
            FixedCostFrame(container, prefix + "Locating Ring Counter", 400.0, chart_loader, self._recalc),
            SprueBushHoleFrame(
                container,
                chart_loader,
                self._recalc,
                top_plate_frame.thickness_var,
                title=prefix + "Sprue Bush Hole",
            ),
            FixedCostFrame(container, prefix + "Sprue Bush Counter", 200.0, chart_loader, self._recalc),
            FixedCostFrame(container, prefix + "Locating Ring Bolt", 50.0, chart_loader, self._recalc),
            FixedCostFrame(container, prefix + "Cavity Insert Bolt", 55.0, chart_loader, self._recalc),
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
