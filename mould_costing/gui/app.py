import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from mould_costing import config
from mould_costing.data.chart_loader import ChartLoader, ChartLoadError
from mould_costing.export.excel_export import export_summary
from mould_costing.gui.bolt_frame import BoltFrame
from mould_costing.gui.guide_bush_frame import GuideBushFrame
from mould_costing.gui.guide_pin_frame import GuidePinFrame
from mould_costing.gui.plate_frame import PlateFrame
from mould_costing.gui.return_pin_frame import ReturnPinFrame
from mould_costing.gui.total_panel import TotalPanel


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mould Costing")
        self.geometry("1100x650")

        self.chart_loader = ChartLoader()

        self._build_layout()
        self._try_load_last_chart()

    def _build_layout(self) -> None:
        for col in range(3):
            self.columnconfigure(col, weight=1, uniform="col")
        for row in range(2):
            self.rowconfigure(row, weight=1, uniform="row")

        self.guide_pin_frame = GuidePinFrame(self, self.chart_loader, self._on_change)
        self.guide_bush_frame = GuideBushFrame(self, self.chart_loader, self._on_change)
        self.return_pin_frame = ReturnPinFrame(self, self.chart_loader, self._on_change)
        self.bolt_frame = BoltFrame(self, self.chart_loader, self._on_change)
        self.plate_frame = PlateFrame(self, self.chart_loader, self._on_change)
        self.total_panel = TotalPanel(self, self._on_load_chart, self._on_export)

        self.guide_pin_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.guide_bush_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.return_pin_frame.grid(row=0, column=2, sticky="nsew", padx=6, pady=6)
        self.bolt_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self.total_panel.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
        self.plate_frame.grid(row=1, column=2, sticky="nsew", padx=6, pady=6)

        self.sections = [
            self.guide_pin_frame,
            self.guide_bush_frame,
            self.return_pin_frame,
            self.bolt_frame,
            self.plate_frame,
        ]

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

    def _on_chart_reload(self) -> None:
        self.total_panel.set_chart_status(self.chart_loader.path)

    def _on_change(self) -> None:
        total = sum(section.get_subtotal() for section in self.sections)
        self.total_panel.set_total(total)

    def _on_export(self) -> None:
        if not any(section.items for section in self.sections):
            messagebox.showinfo("Export Summary", "No line items to export yet.")
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
            messagebox.showerror("Export Error", f"Could not save file:\n{exc}")
            return
        messagebox.showinfo("Export Summary", f"Summary exported to:\n{path}")
