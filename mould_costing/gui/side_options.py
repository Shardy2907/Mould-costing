"""Punch/Cavity side selection shared by the Guide Pin/Bush and Ejector Guide Pin/Bush pairs."""

SIDE_OPTIONS = ["Punch", "Cavity"]


def opposite_side(side: str) -> str:
    return "Cavity" if side == "Punch" else "Punch"
