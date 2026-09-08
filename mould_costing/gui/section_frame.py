"""Reusable base for a costing section: inputs + Add + item list + subtotal."""

import tkinter as tk
from tkinter import ttk

from mould_costing.calculators import LookupMissError
from mould_costing.data.chart_loader import ChartLoader


class SectionFrame(ttk.LabelFrame):
    def __init__(
        self,
        parent,
        title: str,
        item_columns: list[str],
        chart_loader: ChartLoader,
        on_change,
        default_qty: int = 1,
        fixed_qty: int | None = None,
    ):
        super().__init__(parent, text=title, padding=8)
        self.title = title
        self.item_columns = item_columns
        self.full_columns = item_columns + ["Qty", "Unit Cost", "Total"]
        self.chart_loader = chart_loader
        self.on_change = on_change
        self.fixed_qty = fixed_qty
        self.items: list[dict] = []
        self._editing_index: int | None = None

        self._build_ui(default_qty)
        self.chart_loader.on_reload(self.refresh_chart)
        if self.chart_loader.is_loaded():
            self.refresh_chart()

    def _build_ui(self, default_qty: int) -> None:
        inputs_frame = ttk.Frame(self)
        inputs_frame.pack(fill="x")
        self.build_inputs(inputs_frame)

        qty_frame = ttk.Frame(self)
        qty_frame.pack(fill="x", pady=(4, 0))
        if self.fixed_qty is None:
            ttk.Label(qty_frame, text="Qty:").pack(side="left")
            self.qty_var = tk.StringVar(value=str(default_qty))
            ttk.Entry(qty_frame, textvariable=self.qty_var, width=6).pack(side="left", padx=(4, 0))
        else:
            self.qty_var = tk.StringVar(value=str(self.fixed_qty))
            ttk.Label(qty_frame, text=f"Qty: {self.fixed_qty} (fixed)").pack(side="left")
        self.add_button = ttk.Button(qty_frame, text="Add", command=self._on_add)
        self.add_button.pack(side="left", padx=(8, 0))
        ttk.Button(qty_frame, text="Edit Selected", command=self._on_edit).pack(side="left", padx=(4, 0))
        ttk.Button(qty_frame, text="Remove Selected", command=self._on_remove).pack(side="left", padx=(4, 0))
        ttk.Button(qty_frame, text="Clear", command=self.clear).pack(side="left", padx=(4, 0))

        self.status_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.status_var, foreground="red", wraplength=220).pack(fill="x")

        self.tree = ttk.Treeview(self, columns=self.full_columns, show="headings", height=4)
        for col in self.full_columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=70, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=(4, 0))

        self.subtotal_var = tk.StringVar(value="Subtotal: 0.00")
        ttk.Label(self, textvariable=self.subtotal_var, font=("Segoe UI", 9, "bold")).pack(
            fill="x", pady=(4, 0)
        )

    def build_inputs(self, frame: ttk.Frame) -> None:
        raise NotImplementedError

    def collect_line(self) -> tuple[dict, float]:
        """Return (display values for item_columns, unit_cost). Raise LookupMissError/ValueError on bad input."""
        raise NotImplementedError

    def populate_inputs(self, item: dict) -> None:
        """Subclasses override to load a stored item's values back into the input widgets for editing."""
        raise NotImplementedError

    def refresh_chart(self) -> None:
        """Subclasses override to repopulate chart-driven dropdowns after a reload."""

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _clear_status(self) -> None:
        self.status_var.set("")

    def _cancel_edit(self) -> None:
        if self._editing_index is not None:
            self._editing_index = None
            self.add_button.config(text="Add")

    def _on_add(self) -> None:
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError("Quantity must be a positive whole number.")
        except ValueError:
            self._set_status("Quantity must be a positive whole number.")
            return

        try:
            values, unit_cost = self.collect_line()
        except LookupMissError as exc:
            self._set_status(str(exc))
            return
        except ValueError as exc:
            self._set_status(f"Invalid input: {exc}")
            return

        if self._editing_index is not None:
            item = dict(values)
            item["Qty"] = qty
            item["Unit Cost"] = round(unit_cost, 2)
            item["Total"] = round(unit_cost * qty, 2)
            idx = self._editing_index
            self.items[idx] = item
            iid = self.tree.get_children()[idx]
            self.tree.item(iid, values=[item.get(c, "") for c in self.full_columns])
            self._cancel_edit()
            self._clear_status()
            self._recalc()
        else:
            self.add_item(values, unit_cost, qty)

    def add_item(self, values: dict, unit_cost: float, qty: int = 1) -> None:
        """Programmatically append a line item, bypassing the normal input
        fields/collect_line() -- e.g. a lump-sum total committed from elsewhere."""
        item = dict(values)
        item["Qty"] = qty
        item["Unit Cost"] = round(unit_cost, 2)
        item["Total"] = round(unit_cost * qty, 2)
        self.items.append(item)
        self.tree.insert("", "end", values=[item.get(c, "") for c in self.full_columns])
        self._clear_status()
        self._recalc()

    def load_items(self, items: list[dict]) -> None:
        """Replace current items with a previously-saved snapshot, bypassing
        collect_line() entirely -- e.g. reopening a machining window to edit."""
        self.items = [dict(item) for item in items]
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for item in self.items:
            self.tree.insert("", "end", values=[item.get(c, "") for c in self.full_columns])
        self._recalc()

    def _on_edit(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        item = self.items[idx]
        self.populate_inputs(item)
        if self.fixed_qty is None:
            self.qty_var.set(str(item["Qty"]))
        self._editing_index = idx
        self.add_button.config(text="Update")
        self._clear_status()

    def _on_remove(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        for iid in selected:
            idx = self.tree.index(iid)
            del self.items[idx]
            self.tree.delete(iid)
        self._cancel_edit()
        self._recalc()

    def clear(self) -> None:
        self.items.clear()
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._cancel_edit()
        self._clear_status()
        self._recalc()

    def _recalc(self) -> None:
        subtotal = self.get_subtotal()
        self.subtotal_var.set(f"Subtotal: {subtotal:,.2f}")
        self.on_change()

    def get_subtotal(self) -> float:
        return sum(item["Total"] for item in self.items)

    def get_export_rows(self) -> list[dict]:
        return [{"Section": self.title, **item} for item in self.items]
