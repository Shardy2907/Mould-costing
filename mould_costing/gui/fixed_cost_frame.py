from tkinter import ttk

from mould_costing.gui.section_frame import SectionFrame


class FixedCostFrame(SectionFrame):
    """A machining feature with one fixed, chart-independent cost (e.g. a
    standard counter-bore or bolt) -- just Add with a quantity."""

    def __init__(self, parent, title: str, cost: float, chart_loader, on_change):
        self.cost = cost
        super().__init__(parent, title, [], chart_loader, on_change)

    def build_inputs(self, frame: ttk.Frame) -> None:
        ttk.Label(frame, text=f"Fixed cost: {self.cost:,.2f}").grid(row=0, column=0, sticky="w")

    def populate_inputs(self, item: dict) -> None:
        pass

    def collect_line(self) -> tuple[dict, float]:
        return {}, self.cost
