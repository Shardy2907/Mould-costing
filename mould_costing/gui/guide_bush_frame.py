import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import guide_bush
from mould_costing.data.chart_loader import format_value
from mould_costing.gui.section_frame import SectionFrame
from mould_costing.gui.side_options import opposite_side


class GuideBushFrame(SectionFrame):
    def __init__(self, parent, chart_loader, on_change, peer_side_var: tk.StringVar):
        self.peer_side_var = peer_side_var
        super().__init__(
            parent,
            "Guide Bush",
            ["Type", "Ø", "Length", "Side"],
            chart_loader,
            on_change,
            default_qty=4,
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        self.type_var = tk.StringVar(value="A")
        self.diameter_var = tk.StringVar()
        self.length_var = tk.StringVar()
        self.derived_side_var = tk.StringVar(value=opposite_side(self.peer_side_var.get()))

        ttk.Label(frame, text="Type:").grid(row=0, column=0, sticky="w")
        self.type_combo = ttk.Combobox(
            frame, textvariable=self.type_var, values=["A", "B", "C"], width=8, state="readonly"
        )
        self.type_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Diameter (mm):").grid(row=1, column=0, sticky="w")
        self.diameter_combo = ttk.Combobox(
            frame, textvariable=self.diameter_var, values=[], width=10, state="readonly"
        )
        self.diameter_combo.grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Total Length (mm):").grid(row=2, column=0, sticky="w")
        self.length_combo = ttk.Combobox(
            frame, textvariable=self.length_var, values=[], width=10, state="readonly"
        )
        self.length_combo.grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Side (auto):").grid(row=3, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.derived_side_var, font=("Segoe UI", 9, "bold")).grid(
            row=3, column=1, sticky="w"
        )
        self.peer_side_var.trace_add("write", self._on_peer_side_change)

        self.type_var.trace_add("write", lambda *_args: self._refresh_diameters())
        self.diameter_var.trace_add("write", lambda *_args: self._refresh_lengths())

    def _on_peer_side_change(self, *_args) -> None:
        self.derived_side_var.set(opposite_side(self.peer_side_var.get()))

    def refresh_chart(self) -> None:
        types = self.chart_loader.unique_values("GuideBush", "Type", ["A", "B", "C"])
        self.type_combo["values"] = types
        if self.type_var.get() not in types:
            self.type_var.set(types[0] if types else "")
        else:
            self._refresh_diameters()

    def _refresh_diameters(self) -> None:
        diameters = self.chart_loader.filtered_unique_values(
            "GuideBush", "Diameter C", {"Type": self.type_var.get()}, []
        )
        self.diameter_combo["values"] = diameters
        if self.diameter_var.get() not in diameters:
            self.diameter_var.set(diameters[0] if diameters else "")
        else:
            self._refresh_lengths()

    def _refresh_lengths(self) -> None:
        lengths = self.chart_loader.filtered_unique_values(
            "GuideBush",
            "Length",
            {"Type": self.type_var.get(), "Diameter C": self.diameter_var.get()},
            [],
        )
        self.length_combo["values"] = lengths
        if self.length_var.get() not in lengths:
            self.length_var.set(lengths[0] if lengths else "")

    def populate_inputs(self, item: dict) -> None:
        self.type_var.set(item["Type"])
        self.diameter_var.set(format_value(item["Ø"]))
        self.length_var.set(format_value(item["Length"]))

    def collect_line(self) -> tuple[dict, float]:
        type_ = self.type_var.get()
        if not self.diameter_var.get() or not self.length_var.get():
            raise ValueError("No matching Diameter/Length available in the chart for this Type.")

        diameter = float(self.diameter_var.get())
        length = float(self.length_var.get())

        result = guide_bush.calculate(self.chart_loader, type_, diameter, length)
        values = {
            "Type": type_,
            "Ø": diameter,
            "Length": length,
            "Side": self.derived_side_var.get(),
        }
        return values, result.unit_cost
