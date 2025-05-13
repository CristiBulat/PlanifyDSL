class Room:
    """
    Represents a room in the floor plan
    """

    def __init__(self, id=None, x=0, y=0, width=0, height=0):
        """
        Initialize a room

        Args:
            id: Unique identifier
            x: X coordinate
            y: Y coordinate
            width: Width of the room
            height: Height of the room
        """
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Optional properties
        self.label = None
        self.color = None
        self.border_color = None
        self.border_width = None
        self.walls = []  # Custom wall configurations

        # Parent room (for nested rooms)
        self.parent_id = None

    @property
    def area(self):
        """Calculate area of the room in square meters with realistic scaling"""
        # Apply a scaling factor to get realistic values
        # Assuming units are in meters but need to be scaled down
        scale_factor = 0.01  # Adjust this value to get realistic areas
        return round(self.width * self.height * scale_factor, 2)

    def set_size(self, width, height):
        """
        Set the size of the room

        Args:
            width: Width of the room
            height: Height of the room
        """
        self.width = width
        self.height = height

    def set_position(self, x, y):
        """
        Set the position of the room

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y

    def add_wall(self, wall):
        """
        Add a custom wall to the room

        Args:
            wall: Wall object
        """
        self.walls.append(wall)

    def get_corners(self):
        """
        Get the coordinates of the four corners of the room

        Returns:
            List of (x, y) tuples for the corners
        """
        return [
            (self.x, self.y),  # Top-left
            (self.x + self.width, self.y),  # Top-right
            (self.x + self.width, self.y + self.height),  # Bottom-right
            (self.x, self.y + self.height)  # Bottom-left
        ]

    def contains_point(self, x, y):
        """
        Check if the room contains a point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if the point is inside the room, False otherwise
        """
        return (
                self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height
        )

    def from_dsl_structure(self, structure_node):
        """
        Create a Room from a DSL structure node

        Args:
            structure_node: StructureStatementNode from the AST

        Returns:
            Self for chaining
        """
        debug = True  # Enable debug output

        # Process each property
        for prop in structure_node.properties:
            # Get the literal token value (the property name as it appears in the DSL)
            prop_literal = prop.token.literal.lower() if hasattr(prop.token, 'literal') else ""

            if debug:
                print(f"Processing room property: {prop_literal}")

            if prop_literal == "id":
                if hasattr(prop.value, 'value'):
                    self.id = prop.value.value.strip('"\'')
                    self.label = self.id  # Use ID as default label
                    if debug:
                        print(f"Room ID: {self.id}")

            elif prop_literal == "id_parent":
                if hasattr(prop.value, 'value'):
                    self.parent_id = prop.value.value.strip('"\'')
                    if debug:
                        print(f"Room parent ID: {self.parent_id}")

            elif prop_literal == "size":
                if hasattr(prop.value, 'value_expr') and hasattr(prop.value, 'unit'):
                    # Handle measure literal
                    try:
                        size_value = float(prop.value.value_expr.value)
                        # For simplicity, make width = height for single size value
                        self.width = size_value
                        self.height = size_value
                        if debug:
                            print(f"Room size (from measure): {self.width}x{self.height}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing size: {e}")
                elif hasattr(prop.value, 'elements') and len(prop.value.elements) >= 2:
                    # Handle array like [width, height]
                    try:
                        self.width = float(prop.value.elements[0].value)
                        self.height = float(prop.value.elements[1].value)
                        if debug:
                            print(f"Room size (from array): {self.width}x{self.height}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing size array: {e}")

            elif prop_literal == "position":
                if hasattr(prop.value, 'elements') and len(prop.value.elements) >= 2:
                    try:
                        self.x = float(prop.value.elements[0].value)
                        self.y = float(prop.value.elements[1].value)
                        if debug:
                            print(f"Room position: ({self.x}, {self.y})")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing position: {e}")

            elif prop_literal == "label":
                if hasattr(prop.value, 'value'):
                    self.label = prop.value.value.strip('"\'')
                    if debug:
                        print(f"Room label: {self.label}")

            elif prop_literal == "border":
                if hasattr(prop.value, 'value'):
                    self.border_color = prop.value.value
                    if debug:
                        print(f"Room border color: {self.border_color}")

            elif prop_literal == "color":
                if hasattr(prop.value, 'value'):
                    self.color = prop.value.value
                    if debug:
                        print(f"Room color: {self.color}")

        return self