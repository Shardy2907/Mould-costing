"""Generates a small sample chart workbook matching the schema in chart_loader.py,
purely for development/testing until the real standardized chart is ready.

Run with: uv run tests/fixtures/make_sample_chart.py
"""

from pathlib import Path

from openpyxl import Workbook

OUTPUT_PATH = Path(__file__).parent / "sample_chart.xlsx"


def build() -> None:
    wb = Workbook()

    guide_pin = wb.active
    guide_pin.title = "GuidePin"
    guide_pin.append(["Type", "MainDiameter", "OtherDiameter", "TotalLength", "Hours", "Cost"])
    guide_pin.append(["A", 10, 16, 50, 0.5, 120.0])
    guide_pin.append(["A", 10, 16, 100, 0.8, 160.0])
    guide_pin.append(["B", 12, 18, 50, 0.6, 140.0])
    guide_pin.append(["C", 16, 22, 100, 1.0, 200.0])

    bush_pin = wb.create_sheet("BushPin")
    bush_pin.append(["Type", "Diameter", "OtherDiameter", "TotalLength", "Hours", "Cost"])
    bush_pin.append(["A", 10, 16, 50, 0.4, 90.0])
    bush_pin.append(["A", 10, 16, 100, 0.6, 130.0])
    bush_pin.append(["B", 12, 18, 50, 0.5, 110.0])

    return_pin = wb.create_sheet("ReturnPin")
    return_pin.append(["D1", "Length", "Rate"])
    return_pin.append([10, 50, 60.0])
    return_pin.append([12, 63, 75.0])
    return_pin.append([16, 100, 110.0])

    bolts = wb.create_sheet("Bolts")
    bolts.append(["D1", "Length", "Rate"])
    bolts.append([6, 20, 5.0])
    bolts.append([8, 25, 7.5])
    bolts.append([10, 30, 10.0])

    plates = wb.create_sheet("Plates")
    plates.append(["Material", "Density", "Rate"])
    plates.append(["Mild Steel", 0.00000785, 120.0])
    plates.append(["Aluminium", 0.0000027, 250.0])

    wb.save(OUTPUT_PATH)
    print(f"Sample chart written to {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
