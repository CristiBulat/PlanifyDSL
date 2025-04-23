from enum import Enum


class ElementType(Enum):
    """Enum for different types of elements in the floor plan"""
    ROOM = "Room"
    WALL = "Wall"
    DOOR = "Door"
    WINDOW = "Window"
    BED = "Bed"
    TABLE = "Table"
    CHAIR = "Chair"
    STAIRS = "Stairs"
    ELEVATOR = "Elevator"

    @staticmethod
    def from_dsl_type(dsl_type):
        """
        Convert a DSL type string to an ElementType

        Args:
            dsl_type: String from the DSL token type

        Returns:
            ElementType enum value
        """
        type_map = {
            "ROOM": ElementType.ROOM,
            "WALL": ElementType.WALL,
            "DOOR": ElementType.DOOR,
            "WINDOW": ElementType.WINDOW,
            "BED": ElementType.BED,
            "TABLE": ElementType.TABLE,
            "CHAIR": ElementType.CHAIR,
            "STAIRS": ElementType.STAIRS,
            "ELEVATOR": ElementType.ELEVATOR
        }

        return type_map.get(dsl_type, None)