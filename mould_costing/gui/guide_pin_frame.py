import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import guide_pin
from mould_costing.data.chart_loader import format_value
from mould_costing.gui.section_frame import SectionFrame
from mould_costing.gui.side_options import SIDE_OPTIONS


class GuidePinFrame(SectionFrame):
    def __init__(self, parent, chart_loader, on_change):
        super().__init__(
            parent,
            "Guide Pin",
            ["Type", "Main Ø", "Length", "Side"],
            chart_loader,
            on_change,
            default_qty=4,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.type_var = tk.StringVar(value="A")
        self.diameter_var = tk.StringVar()
        self.length_var = tk.StringVar()
        self.side_var = tk.StringVar(value=SIDE_OPTIONS[0])

        ttk.Label(frame, text="Type:").grid(row=0, column=0, sticky="w")
        self.type_combo = ttk.Combobox(
            frame, textvariable=self.type_var, values=["A", "B", "C"], width=8, state="readonly"
        )
        self.type_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Main Ø (mm):").grid(row=1, column=0, sticky="w")
        self.diameter_combo = ttk.Combobox(
            frame, textvariable=self.diameter_var, values=[], width=10, state="readonly"
        )
        self.diameter_combo.grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Total Length (mm):").grid(row=2, column=0, sticky="w")
        self.length_combo = ttk.Combobox(
            frame, textvariable=self.length_var, values=[], width=10, state="readonly"
        )
        self.length_combo.grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Which Side:").grid(row=3, column=0, sticky="w")
        ttk.Combobox(
            frame, textvariable=self.side_var, values=SIDE_OPTIONS, width=8, state="readonly"
        ).grid(row=3, column=1, sticky="w")

        self.type_var.trace_add("write", lambda *_args: self._refresh_diameters())
        self.diameter_var.trace_add("write", lambda *_args: self._refresh_lengths())

    def refresh_chart(self) -> None:
        types = self.chart_loader.unique_values("GuidePin", "Type", ["A", "B", "C"])
        self.type_combo["values"] = types
        if self.type_var.get() not in types:
            self.type_var.set(types[0] if types else "")
        else:
            self._refresh_diameters()

    def _refresh_diameters(self) -> None:
        diameters = self.chart_loader.filtered_unique_values(
            "GuidePin", "Diameter C", {"Type": self.type_var.get()}, []
        )
        self.diameter_combo["values"] = diameters
        if self.diameter_var.get() not in diameters:
            self.diameter_var.set(diameters[0] if diameters else "")
        else:
            self._refresh_lengths()

    def _refresh_lengths(self) -> None:
        lengths = self.chart_loader.filtered_unique_values(
            "GuidePin",
            "Length",
            {"Type": self.type_var.get(), "Diameter C": self.diameter_var.get()},
            [],
        )
        self.length_combo["values"] = lengths
        if self.length_var.get() not in lengths:
            self.length_var.set(lengths[0] if lengths else "")

    def populate_inputs(self, item: dict) -> None:
        self.type_var.set(item["Type"])
        self.diameter_var.set(format_value(item["Main Ø"]))
        self.length_var.set(format_value(item["Length"]))
        self.side_var.set(item["Side"])

    def collect_line(self) -> tuple[dict, float]:
        type_ = self.type_var.get()
        if not self.diameter_var.get() or not self.length_var.get():
            raise ValueError("No matching Diameter/Length available in the chart for this Type.")

        diameter = float(self.diameter_var.get())
        length = float(self.length_var.get())
        side = self.side_var.get()

        result = guide_pin.calculate(self.chart_loader, type_, diameter, length, side)
        values = {"Type": type_, "Main Ø": diameter, "Length": length, "Side": side}
        return values, result.unit_cost
