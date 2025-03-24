from typing import Dict


class TokenType:
    IDENTIFIER = "IDENT"

    # Literals
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    COLOR_LITERAL = "COLOR_LITERAL"

    # Operators
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    ASTERISK = "*"
    SLASH = "/"

    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"

    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    EXCLAM_MARK = "!"

    # Keywords
    INT = "INT"
    STRING = "STRING"
    MEASURE = "MEASURE"
    COLOR = "COLOR"
    FLOAT = "FLOAT"
    LIST = "LIST"

    ROOM = "ROOM"
    WINDOW = "WINDOW"
    WALL = "WALL"
    DOOR = "DOOR"
    ELEVATOR = "ELEVATOR"
    STAIRS = "STAIRS"
    BED = "BED"
    TABLE = "TABLE"
    CHAIR = "CHAIR"

    # Properties
    ID_PROP = "ID_PROPERTY"
    ID_PARENT_PROP = "ID_PARENT_PROPERTY"
    WALL_PROP = "WALL_PROPERTY"
    END_ON_WALL = "END_ON_WALL_PROPERTY"
    SIZE_PROP = "SIZE_PROPERTY"
    ANGLES_PROP = "ANGLES_PROPERTY"
    BORDER_PROP = "BORDER_PROPERTY"
    POSITION_PROP = "POSITION"
    START_ON_WALL_PROP = "START_ON_WALL"
    LENGTH_PROP = "LENGTH"
    DIRECTION_PROP = "DIRECTION"
    START_PROPERTY = "START"
    END_PROP = "END"
    WIDTH_PROP = "WIDTH"
    HEIGHT_PROP = "HEIGHT"
    DISTANCE_WALL_PROP = "DISTANCE_WALL"
    LAYER_PROP = "LAYER"
    ROTATION_PROP = "ROTATION"
    LABEL_PROP = "LABEL"

    VISIBILITY_PROP_VALUE = "VISIBILITY"
    HIDDEN_PROP_VALUE = "HIDDEN"
    VISIBLE_PROP_VALUE = "VISIBLE"

    # Measure units
    MEASURE_UNIT_MM = "MEASURE_MM"
    MEASURE_UNIT_CM = "MEASURE_CM"
    MEASURE_UNIT_DM = "MEASURE_DM"
    MEASURE_UNIT_M = "MEASURE_M"
    MEASURE_UNIT_KM = "MEASURE_KM"

    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    IN = "IN"

    ILLEGAL = "ILLEGAL"
    END = "END"

    dataTypes = {INT, STRING, MEASURE, COLOR, FLOAT, LIST}
    structures = {ROOM, WINDOW, WALL, DOOR, ELEVATOR, STAIRS, BED, TABLE, CHAIR}
    roomProps = {
        ID_PROP, ID_PARENT_PROP, WALL_PROP, END_ON_WALL, SIZE_PROP,
        ANGLES_PROP, BORDER_PROP, POSITION_PROP, START_ON_WALL_PROP,
        LENGTH_PROP, DIRECTION_PROP, START_PROPERTY, END_PROP,
        WIDTH_PROP, HEIGHT_PROP, DISTANCE_WALL_PROP, LAYER_PROP,
        ROTATION_PROP, LABEL_PROP
    }
    measureUnits = {MEASURE_UNIT_MM, MEASURE_UNIT_CM, MEASURE_UNIT_DM, MEASURE_UNIT_M, MEASURE_UNIT_KM}


keywords: Dict[str, str] = {
    "int": TokenType.INT,
    "string": TokenType.STRING,
    "measure": TokenType.MEASURE,
    "color": TokenType.COLOR,
    "float": TokenType.FLOAT,
    "list": TokenType.LIST,
    "Room": TokenType.ROOM,
    "Window": TokenType.WINDOW,
    "Wall": TokenType.WALL,
    "Door": TokenType.DOOR,
    "Elevator": TokenType.ELEVATOR,
    "Stairs": TokenType.STAIRS,
    "Bed": TokenType.BED,
    "Table": TokenType.TABLE,
    "Chair": TokenType.CHAIR,
    "id": TokenType.ID_PROP,
    "id_parent": TokenType.ID_PARENT_PROP,
    "size": TokenType.SIZE_PROP,
    "angles": TokenType.ANGLES_PROP,
    "border": TokenType.BORDER_PROP,
    "position": TokenType.POSITION_PROP,
    "start_on_wall": TokenType.START_ON_WALL_PROP,
    "wall": TokenType.WALL_PROP,
    "end_on_wall": TokenType.END_ON_WALL,
    "length": TokenType.LENGTH_PROP,
    "direction": TokenType.DIRECTION_PROP,
    "start": TokenType.START_PROPERTY,
    "end": TokenType.END_PROP,
    "width": TokenType.WIDTH_PROP,
    "height": TokenType.HEIGHT_PROP,
    "distance_wall": TokenType.DISTANCE_WALL_PROP,
    "rotation": TokenType.ROTATION_PROP,
    "label": TokenType.LABEL_PROP,
    "layer": TokenType.LAYER_PROP,
    "hidden": TokenType.HIDDEN_PROP_VALUE,
    "visible": TokenType.VISIBILITY_PROP_VALUE,
    "mm": TokenType.MEASURE_UNIT_MM,
    "cm": TokenType.MEASURE_UNIT_CM,
    "dm": TokenType.MEASURE_UNIT_DM,
    "m": TokenType.MEASURE_UNIT_M,
    "km": TokenType.MEASURE_UNIT_KM,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
}


class Token:
    def __init__(self, literal: str, type_: str, line: int, col: int):
        self.literal = literal
        self.type = type_
        self.line = line
        self.col = col

    def __str__(self):
        return f"{self.literal}, type: {self.type}, line: {self.line}, col: {self.col}"


def look_up_ident(ident: str) -> str:
    return keywords.get(ident, TokenType.IDENTIFIER)
