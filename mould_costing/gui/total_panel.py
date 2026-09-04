import tkinter as tk
from tkinter import ttk


class TotalPanel(ttk.LabelFrame):
    def __init__(self, parent, on_load_chart, on_export):
        super().__init__(parent, text="Mould Cost Summary", padding=12)

        self.chart_status_var = tk.StringVar(value="No chart loaded")
        ttk.Label(self, textvariable=self.chart_status_var, wraplength=220, justify="center").pack(
            pady=(0, 8)
        )

        ttk.Label(self, text="TOTAL COST", font=("Segoe UI", 11, "bold")).pack()
        self.total_var = tk.StringVar(value="0.00")
        ttk.Label(self, textvariable=self.total_var, font=("Segoe UI", 24, "bold")).pack(pady=(0, 12))

        ttk.Button(self, text="Load Chart File...", command=on_load_chart).pack(fill="x", pady=2)
        ttk.Button(self, text="Export Summary...", command=on_export).pack(fill="x", pady=2)

    def set_total(self, value: float) -> None:
        self.total_var.set(f"{value:,.2f}")

    def set_chart_status(self, path: str | None) -> None:
        self.chart_status_var.set(f"Chart: {path}" if path else "No chart loaded")
