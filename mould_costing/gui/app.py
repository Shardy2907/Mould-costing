import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from mould_costing import config
from mould_costing.data.chart_loader import ChartLoader, ChartLoadError
from mould_costing.export.excel_export import export_summary
from mould_costing.gui.bolt_frame import BoltFrame
from mould_costing.gui.bottom_plate_machining_window import BottomPlateMachiningWindow
from mould_costing.gui.guide_bush_frame import GuideBushFrame
from mould_costing.gui.guide_pin_frame import GuidePinFrame
from mould_costing.gui.hook_strip_frame import HookStripFrame
from mould_costing.gui.locating_ring_frame import LocatingRingFrame
from mould_costing.gui.plate_frame import PlateFrame
from mould_costing.gui.punch_back_plate_machining_window import PunchBackPlateMachiningWindow
from mould_costing.gui.scrollable_frame import ScrollableFrame
from mould_costing.gui.simple_rate_frame import SimpleRateFrame
from mould_costing.gui.spacer_blocks_machining_window import SpacerBlocksMachiningWindow
from mould_costing.gui.top_plate_machining_window import TopPlateMachiningWindow
from mould_costing.gui.total_panel import TotalPanel


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mould Costing")
        self.geometry("1200x800")

        self.chart_loader = ChartLoader()

        ttk.Style(self).configure("TLabelframe.Label",
                                  font=("Segoe UI", 11, "bold"))

        self._build_layout()
        self._try_load_last_chart()

    def _build_layout(self) -> None:
        self.total_panel = TotalPanel(
            self, self._on_load_chart, self._on_export, self._on_clear_all)
        self.total_panel.pack(side="top", fill="x", padx=6, pady=6)

        scroll_area = ScrollableFrame(self)
        scroll_area.pack(side="top", fill="both", expand=True)
        grid = scroll_area.inner
        for col in range(3):
            grid.columnconfigure(col, weight=1, uniform="col")

        self.guide_pin_frame = GuidePinFrame(
            grid, self.chart_loader, self._on_change)
        self.guide_bush_frame = GuideBushFrame(
            grid, self.chart_loader, self._on_change, peer_side_var=self.guide_pin_frame.side_var
        )
        self.return_pin_frame = SimpleRateFrame(
            grid, "Return Pin", "ReturnPin", self.chart_loader, self._on_change, fixed_qty=4
        )
        self.bolt_frame = BoltFrame(grid, self.chart_loader, self._on_change)
        self.dowelling_sleeve_frame = SimpleRateFrame(
            grid, "Dowelling Sleeve", "DowellingSleeve", self.chart_loader, self._on_change, d1_column="Outer dia"
        )
        self.hook_strip_frame = HookStripFrame(
            grid, self.chart_loader, self._on_change)
        self.ejector_guide_pin_frame = SimpleRateFrame(
            grid, "Ejector Guide Pin", "EjectorGuidePin", self.chart_loader, self._on_change
        )
        self.ejector_guide_bush_frame = SimpleRateFrame(
            grid, "Ejector Guide Bush", "EjectorGuideBush", self.chart_loader, self._on_change
        )
        self.locating_ring_frame = LocatingRingFrame(
            grid, self.chart_loader, self._on_change)

        self.shared_bolt_diameter_var = tk.StringVar()

        plate_titles = [
            "Top Plate",
            "Cavity Plate",
            "Punch Plate",
            "Punch Back Plate",
            "Spacer Blocks",
            "Ejector Plate",
            "Ejector Back Plate",
            "Bottom Plate",
        ]
        self.plate_frames = []
        for title in plate_titles:
            factory = None
            default_qty = 1
            if title == "Top Plate":
                factory = self._open_top_plate_machining
            elif title == "Spacer Blocks":
                factory = self._open_spacer_blocks_machining
                default_qty = 2
            elif title == "Bottom Plate":
                factory = self._open_bottom_plate_machining
            elif title == "Punch Back Plate":
                factory = self._open_punch_back_plate_machining
            self.plate_frames.append(
                PlateFrame(
                    grid,
                    title,
                    self.chart_loader,
                    self._on_change,
                    machining_window_factory=factory,
                    default_qty=default_qty,
                )
            )

        self.sections = [
            self.guide_pin_frame,
            self.guide_bush_frame,
            self.return_pin_frame,
            self.bolt_frame,
            self.dowelling_sleeve_frame,
            self.hook_strip_frame,
            self.ejector_guide_pin_frame,
            self.ejector_guide_bush_frame,
            self.locating_ring_frame,
            *self.plate_frames,
        ]

        for index, section in enumerate(self.sections):
            row, col = divmod(index, 3)
            section.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        self.chart_loader.on_reload(self._on_chart_reload)

    def _try_load_last_chart(self) -> None:
        last_path = config.load_last_chart_path()
        if last_path:
            try:
                self.chart_loader.load(last_path)
            except ChartLoadError:
                pass

    def _on_load_chart(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Standard Chart Workbook",
            filetypes=[("Excel Workbook", "*.xlsx")],
        )
        if not path:
            return
        try:
            self.chart_loader.load(path)
        except ChartLoadError as exc:
            messagebox.showerror("Chart Load Error", str(exc))
            return
        config.save_last_chart_path(path)

    def _open_top_plate_machining(self, plate_frame, on_ok):
        return TopPlateMachiningWindow(self, self.chart_loader, plate_frame, on_ok)

    def _open_spacer_blocks_machining(self, plate_frame, on_ok):
        return SpacerBlocksMachiningWindow(
            self, self.chart_loader, plate_frame, on_ok, self.shared_bolt_diameter_var
        )

    def _open_bottom_plate_machining(self, plate_frame, on_ok):
        return BottomPlateMachiningWindow(
            self, self.chart_loader, plate_frame, on_ok, self.shared_bolt_diameter_var
        )

    def _open_punch_back_plate_machining(self, plate_frame, on_ok):
        return PunchBackPlateMachiningWindow(self, self.chart_loader, plate_frame, on_ok)

    def _on_chart_reload(self) -> None:
        self.total_panel.set_chart_status(self.chart_loader.path)

    def _on_change(self) -> None:
        total = sum(section.get_subtotal() for section in self.sections)
        self.total_panel.set_total(total)

    def _on_clear_all(self) -> None:
        if not any(section.items for section in self.sections):
            return
        if not messagebox.askyesno("Clear All", "Remove all line items from every section?"):
            return
        for section in self.sections:
            section.clear()

    def _on_export(self) -> None:
        if not any(section.items for section in self.sections):
            messagebox.showinfo(
                "Export Summary", "No line items to export yet.")
            return

        path = filedialog.asksaveasfilename(
            title="Export Costing Summary",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
        )
        if not path:
            return

        grand_total = sum(section.get_subtotal() for section in self.sections)
        try:
            export_summary(path, self.sections, grand_total)
        except OSError as exc:
            messagebox.showerror(
                "Export Error", f"Could not save file:\n{exc}")
            return
        messagebox.showinfo("Export Summary", f"Summary exported to:\n{path}")
