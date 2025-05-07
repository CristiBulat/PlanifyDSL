import math


class Wall:
    """
    Represents a wall in the floor plan
    """

    def __init__(self, id=None, start_x=0, start_y=0, end_x=0, end_y=0):
        """
        Initialize a wall

        Args:
            id: Unique identifier
            start_x: X coordinate of start point
            start_y: Y coordinate of start point
            end_x: X coordinate of end point
            end_y: Y coordinate of end point
        """
        self.id = id
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

        # Optional properties
        self.thickness = 1
        self.color = None
        self.parent_id = None  # ID of the parent room

    @property
    def length(self):
        """Calculate length of the wall"""
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        return math.sqrt(dx * dx + dy * dy)

    @property
    def angle(self):
        """Calculate angle of the wall in degrees from horizontal"""
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        return math.degrees(math.atan2(dy, dx))

    def set_start_point(self, x, y):
        """
        Set the start point of the wall

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.start_x = x
        self.start_y = y

    def set_end_point(self, x, y):
        """
        Set the end point of the wall

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.end_x = x
        self.end_y = y

    def point_at_distance(self, distance):
        """
        Get point at a certain distance from start

        Args:
            distance: Distance from start point

        Returns:
            (x, y) tuple representing the point
        """
        total_length = self.length
        if total_length == 0:
            return (self.start_x, self.start_y)

        ratio = min(1.0, distance / total_length)
        x = self.start_x + ratio * (self.end_x - self.start_x)
        y = self.start_y + ratio * (self.end_y - self.start_y)

        return (x, y)

    def from_dsl_structure(self, structure_node):
        """
        Create a Wall from a DSL structure node

        Args:
            structure_node: StructureStatementNode from the AST

        Returns:
            Self for chaining
        """
        # Process each property
        for prop in structure_node.properties:
            prop_name = prop.name

            if prop_name == "ID_PROP":
                if hasattr(prop.value, 'value'):
                    self.id = prop.value.value.strip('"\'')

            elif prop_name == "ID_PARENT_PROP":
                if hasattr(prop.value, 'value'):
                    self.parent_id = prop.value.value.strip('"\'')

            elif prop_name == "START_PROPERTY":
                if hasattr(prop.value, 'elements') and len(prop.value.elements) >= 2:
                    self.start_x = float(prop.value.elements[0].value)
                    self.start_y = float(prop.value.elements[1].value)

            elif prop_name == "END_PROP":
                if hasattr(prop.value, 'elements') and len(prop.value.elements) >= 2:
                    self.end_x = float(prop.value.elements[0].value)
                    self.end_y = float(prop.value.elements[1].value)

            elif prop_name == "LENGTH_PROP":
                if hasattr(prop.value, 'value'):
                    # If only length is given, assume horizontal wall
                    length = float(prop.value.value)
                    self.end_x = self.start_x + length
                    self.end_y = self.start_y

            elif prop_name == "BORDER_PROP":
                if hasattr(prop.value, 'value'):
                    self.color = prop.value.value

        return self