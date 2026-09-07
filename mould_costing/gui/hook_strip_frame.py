import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import rate_lookup
from mould_costing.data.chart_loader import format_value
from mould_costing.gui.section_frame import SectionFrame


class HookStripFrame(SectionFrame):
    def __init__(self, parent, chart_loader, on_change):
        super().__init__(
            parent,
            "Hook Strip",
            ["W", "T", "Length"],
            chart_loader,
            on_change,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.w_var = tk.StringVar()
        self.t_var = tk.StringVar()
        self.length_var = tk.StringVar()

        ttk.Label(frame, text="W (mm):").grid(row=0, column=0, sticky="w")
        self.w_combo = ttk.Combobox(frame, textvariable=self.w_var, values=[], width=10, state="readonly")
        self.w_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="T (mm):").grid(row=1, column=0, sticky="w")
        self.t_combo = ttk.Combobox(frame, textvariable=self.t_var, values=[], width=10, state="readonly")
        self.t_combo.grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Length (mm):").grid(row=2, column=0, sticky="w")
        self.length_combo = ttk.Combobox(
            frame, textvariable=self.length_var, values=[], width=10, state="readonly"
        )
        self.length_combo.grid(row=2, column=1, sticky="w")

        self.w_var.trace_add("write", lambda *_args: self._refresh_t())
        self.t_var.trace_add("write", lambda *_args: self._refresh_lengths())

    def refresh_chart(self) -> None:
        w_values = self.chart_loader.unique_values("HookStrip", "W", [])
        self.w_combo["values"] = w_values
        if self.w_var.get() not in w_values:
            self.w_var.set(w_values[0] if w_values else "")
        else:
            self._refresh_t()

    def _refresh_t(self) -> None:
        t_values = self.chart_loader.filtered_unique_values(
            "HookStrip", "T", {"W": self.w_var.get()}, []
        )
        self.t_combo["values"] = t_values
        if self.t_var.get() not in t_values:
            self.t_var.set(t_values[0] if t_values else "")
        else:
            self._refresh_lengths()

    def _refresh_lengths(self) -> None:
        lengths = self.chart_loader.filtered_unique_values(
            "HookStrip", "Length", {"W": self.w_var.get(), "T": self.t_var.get()}, []
        )
        self.length_combo["values"] = lengths
        if self.length_var.get() not in lengths:
            self.length_var.set(lengths[0] if lengths else "")

    def populate_inputs(self, item: dict) -> None:
        self.w_var.set(format_value(item["W"]))
        self.t_var.set(format_value(item["T"]))
        self.length_var.set(format_value(item["Length"]))

    def collect_line(self) -> tuple[dict, float]:
        if not self.w_var.get() or not self.t_var.get() or not self.length_var.get():
            raise ValueError("No matching W/T/Length combination available in the chart.")

        w = float(self.w_var.get())
        t = float(self.t_var.get())
        length = float(self.length_var.get())

        result = rate_lookup.calculate(self.chart_loader, "HookStrip", self.title, W=w, T=t, Length=length)
        values = {"W": w, "T": t, "Length": length}
        return values, result.unit_cost
