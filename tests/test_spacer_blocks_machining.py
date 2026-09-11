import tkinter as tk
import unittest

from mould_costing.calculators.bolt_counterbore import (
    calculate_bolt_defaults,
    get_bolt_defaults,
    lookup_drilling_cost,
    parse_nominal_diameter,
)
from mould_costing.data.chart_loader import ChartLoader
from mould_costing.gui.spacer_block_bolt_frame import SpacerBlockBoltFrame
from mould_costing.gui.spacer_blocks_machining_window import SpacerBlocksMachiningWindow


class TestBoltCounterboreCalculator(unittest.TestCase):
    def test_user_specified_defaults(self):
        m10 = get_bolt_defaults("M10")
        self.assertEqual(m10["clearance_hole"], 11.0)
        self.assertEqual(m10["counterbore_dia"], 18)
        self.assertEqual(m10["counterbore_depth"], 11.0)

        m12 = get_bolt_defaults("M12")
        self.assertEqual(m12["clearance_hole"], 14.0)
        self.assertEqual(m12["counterbore_dia"], 20.0)
        self.assertEqual(m12["counterbore_depth"], 13.0)

        m16 = get_bolt_defaults("M16")
        self.assertEqual(m16["clearance_hole"], 18.0)
        self.assertEqual(m16["counterbore_dia"], 26.0)
        self.assertEqual(m16["counterbore_depth"], 18)

    def test_calculated_defaults_for_other_sizes(self):
        m3 = get_bolt_defaults("M3")
        self.assertEqual(m3["clearance_hole"], 3.5)
        self.assertEqual(m3["counterbore_dia"], 6)
        self.assertEqual(m3["counterbore_depth"], 3.5)

        m4 = get_bolt_defaults("M4")
        self.assertEqual(m4["clearance_hole"], 4.5)
        self.assertEqual(m4["counterbore_dia"], 7)
        self.assertEqual(m4["counterbore_depth"], 4.5)

        m5 = get_bolt_defaults("M5")
        self.assertEqual(m5["clearance_hole"], 5.5)
        self.assertEqual(m5["counterbore_dia"], 8.5)
        self.assertEqual(m5["counterbore_depth"], 5.5)

        m6 = get_bolt_defaults("M6")
        self.assertEqual(m6["clearance_hole"], 6.5)
        self.assertEqual(m6["counterbore_dia"], 11.0)
        self.assertEqual(m6["counterbore_depth"], 6.5)

        m8 = get_bolt_defaults("M8")
        self.assertEqual(m8["clearance_hole"], 9.0)
        self.assertEqual(m8["counterbore_dia"], 13.0)
        self.assertEqual(m8["counterbore_depth"], 9.0)

        m20 = get_bolt_defaults("M20")
        self.assertEqual(m20["clearance_hole"], 22.0)
        self.assertEqual(m20["counterbore_dia"], 32.0)
        self.assertEqual(m20["counterbore_depth"], 21)

    def test_case_insensitivity_and_formatting(self):
        self.assertEqual(get_bolt_defaults("m10"), get_bolt_defaults("M10"))
        self.assertEqual(get_bolt_defaults(" 10 "), get_bolt_defaults("M10"))

    def test_dynamic_fallback(self):
        calc = calculate_bolt_defaults(17.0)
        self.assertEqual(calc["clearance_hole"], 19.0)
        self.assertEqual(calc["counterbore_dia"], 28.0)
        self.assertEqual(calc["counterbore_depth"], 18.5)


class TestSpacerBlockBoltGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except tk.TclError:
            cls.root = None

    @classmethod
    def tearDownClass(cls):
        if cls.root is not None:
            cls.root.destroy()

    def setUp(self):
        if self.root is None:
            self.skipTest("Tkinter display not available in this environment")
        self.chart_loader = ChartLoader()
        self.thickness_var = tk.StringVar(value="40.0")

    def test_frame_initialization_and_bolt_selection(self):
        frame = SpacerBlockBoltFrame(
            self.root, self.chart_loader, lambda: None, self.thickness_var
        )
        # Default starting bolt is M10
        self.assertEqual(frame.bolt_var.get(), "M10")
        self.assertEqual(frame.clearance_var.get(), "11.0")
        self.assertEqual(frame.counterbore_dia_var.get(), "17.5")
        self.assertEqual(frame.counterbore_depth_var.get(), "11.0")

        # Switching to M12 updates defaults
        frame.bolt_var.set("M12")
        self.assertEqual(frame.clearance_var.get(), "14.0")
        self.assertEqual(frame.counterbore_dia_var.get(), "20.0")
        self.assertEqual(frame.counterbore_depth_var.get(), "13.0")

        # Switching to M16 updates defaults
        frame.bolt_var.set("M16")
        self.assertEqual(frame.clearance_var.get(), "18.0")
        self.assertEqual(frame.counterbore_dia_var.get(), "26.0")
        self.assertEqual(frame.counterbore_depth_var.get(), "17.5")

    def test_editable_inputs_and_collect_line(self):
        frame = SpacerBlockBoltFrame(
            self.root, self.chart_loader, lambda: None, self.thickness_var
        )
        frame.bolt_var.set("M10")
        # User manually edits clearance and counterbore
        frame.clearance_var.set("11.5")
        frame.counterbore_dia_var.set("18.0")
        frame.counterbore_depth_var.set("12.0")
        frame.cost_var.set("150.0")
        frame.qty_var.set("4")

        values, unit_cost = frame.collect_line()
        self.assertEqual(values["Bolt Diameter"], "M10")
        self.assertEqual(values["Clearance Dia (mm)"], 11.5)
        self.assertEqual(values["Counterbore Dia (mm)"], 18.0)
        self.assertEqual(values["Counterbore Depth (mm)"], 12.0)
        self.assertEqual(unit_cost, 150.0)

    def test_populate_inputs_restores_custom_values(self):
        frame = SpacerBlockBoltFrame(
            self.root, self.chart_loader, lambda: None, self.thickness_var
        )
        item = {
            "Bolt Diameter": "M12",
            "Clearance Dia (mm)": 14.2,
            "Counterbore Dia (mm)": 21.0,
            "Counterbore Depth (mm)": 13.5,
            "Unit Cost": 220.0,
            "Qty": 6,
        }
        frame.populate_inputs(item)
        self.assertEqual(frame.bolt_var.get(), "M12")
        self.assertEqual(frame.clearance_var.get(), "14.2")
        self.assertEqual(frame.counterbore_dia_var.get(), "21.0")
        self.assertEqual(frame.counterbore_depth_var.get(), "13.5")
        self.assertEqual(frame.cost_var.get(), "220.0")
        self.assertEqual(frame.qty_var.get(), "6")

    def test_machining_window_total_and_state(self):
        class DummyPlateFrame:
            def __init__(self, thickness_var):
                self.thickness_var = thickness_var

        dummy_plate = DummyPlateFrame(self.thickness_var)
        committed = {}

        def on_ok(total, snapshot):
            committed["total"] = total
            committed["snapshot"] = snapshot

        win = SpacerBlocksMachiningWindow(
            self.root, self.chart_loader, dummy_plate, on_ok
        )
        # Add item to the subframe
        subframe = win.sub_frames[0]
        subframe.add_item(
            {
                "Bolt Diameter": "M10",
                "Clearance Dia (mm)": 11.0,
                "Counterbore Dia (mm)": 17.5,
                "Counterbore Depth (mm)": 11.0,
            },
            unit_cost=100.0,
            qty=4,
        )
        self.assertEqual(win.get_subtotal(), 400.0)

        # Trigger OK
        win._on_ok_clicked()
        self.assertEqual(committed["total"], 400.0)
        self.assertEqual(len(committed["snapshot"]), 1)
        self.assertEqual(len(committed["snapshot"][0]), 1)

    def test_app_spacer_blocks_machining_flow(self):
        from mould_costing.gui.app import App

        app = App()
        try:
            # Find Spacer Blocks frame
            spacer_frame = None
            for pf in app.plate_frames:
                if pf.title == "Spacer Blocks":
                    spacer_frame = pf
                    break
            self.assertIsNotNone(spacer_frame)
            self.assertIsNotNone(spacer_frame.machining_window_factory)

            # Open machining window via the factory
            win = spacer_frame.machining_window_factory(
                spacer_frame, spacer_frame._commit_machining)
            self.assertIsInstance(win, SpacerBlocksMachiningWindow)

            # Add an item to the bolt machining subframe
            bolt_frame = win.sub_frames[0]
            bolt_frame.bolt_var.set("M12")
            self.assertEqual(bolt_frame.clearance_var.get(), "14.0")
            self.assertEqual(bolt_frame.counterbore_dia_var.get(), "20.0")
            self.assertEqual(bolt_frame.counterbore_depth_var.get(), "13.0")
            bolt_frame.cost_var.set("185.0")
            bolt_frame.qty_var.set("4")
            bolt_frame._on_add()

            # Confirm row is in the subframe
            self.assertEqual(len(bolt_frame.items), 1)
            self.assertEqual(win.get_subtotal(), 740.0)

            # Commit OK
            win._on_ok_clicked()

            # Check that Spacer Blocks now has the Total Machining Cost item
            self.assertEqual(len(spacer_frame.items), 1)
            machining_item = spacer_frame.items[0]
            self.assertEqual(
                machining_item["Material"], "Total Machining Cost")
            self.assertEqual(machining_item["Unit Cost"], 740.0)
            self.assertEqual(machining_item["Total"], 740.0)
            self.assertIn("_machining_state", machining_item)

            # Check reopening and loading state
            spacer_frame.tree.selection_set(
                spacer_frame.tree.get_children()[0])
            spacer_frame._on_edit()
            self.assertIsNotNone(spacer_frame.machining_window)
            reopened_bolt_frame = spacer_frame.machining_window.sub_frames[0]
            self.assertEqual(len(reopened_bolt_frame.items), 1)
            saved_bolt_row = reopened_bolt_frame.items[0]
            self.assertEqual(saved_bolt_row["Bolt Diameter"], "M12")
            self.assertEqual(saved_bolt_row["Clearance Dia (mm)"], 14.0)
            self.assertEqual(saved_bolt_row["Counterbore Dia (mm)"], 20.0)
            self.assertEqual(saved_bolt_row["Counterbore Depth (mm)"], 13.0)

            spacer_frame.machining_window.destroy()
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
