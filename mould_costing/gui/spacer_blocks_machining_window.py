import tkinter as tk
from tkinter import ttk

from mould_costing.gui.scrollable_frame import ScrollableFrame
from mould_costing.gui.spacer_block_bolt_frame import SpacerBlockBoltFrame


class SpacerBlocksMachiningWindow(tk.Toplevel):
    """Configure machining features for Spacer Blocks; clicking OK commits the total
    as a single line item on the Spacer Blocks section and closes this window."""

    def __init__(self, parent, chart_loader, spacer_blocks_frame, on_ok, bolt_diameter_var):
        super().__init__(parent)
        self.title("Spacer Blocks - Machining")
        self.geometry("540x760")
        self._on_ok = on_ok

        self.total_var = tk.StringVar()
        ttk.Label(self, textvariable=self.total_var, font=("Segoe UI", 11, "bold")).pack(
            side="top", fill="x", padx=8, pady=8
        )
        ttk.Button(self, text="OK", command=self._on_ok_clicked).pack(
            side="bottom", fill="x", padx=8, pady=8)

        scroll_area = ScrollableFrame(self)
        scroll_area.pack(side="top", fill="both", expand=True)
        container = scroll_area.inner
        container.columnconfigure(0, weight=1)

        try:
            spacer_qty = int(spacer_blocks_frame.qty_var.get())
        except ValueError:
            spacer_qty = 1
        bolt_default_qty = spacer_qty * 2 if spacer_qty > 0 else 2

        prefix = "Spacer Blocks - "
        self.sub_frames = [
            SpacerBlockBoltFrame(
                container,
                chart_loader,
                self._recalc,
                spacer_blocks_frame.thickness_var,
                bolt_diameter_var,
                title=prefix + "Clamping Bolt Machining",
                default_qty=bolt_default_qty,
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
