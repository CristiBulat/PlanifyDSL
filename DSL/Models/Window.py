class Window:
    """
    Represents a window in the floor plan
    """

    def __init__(self, id=None, x=0, y=0, width=0, height=0):
        """
        Initialize a window

        Args:
            id: Unique identifier
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of the window
            height: Height of the window
        """
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Optional properties
        self.parent_id = None  # ID of the parent wall or room
        self.wall_id = None  # ID of the wall this window is on
        self.distance_wall = 0  # Distance from start of wall

    def set_position(self, x, y):
        """
        Set the position of the window

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y

    def set_size(self, width, height):
        """
        Set the size of the window

        Args:
            width: Width of the window
            height: Height of the window
        """
        self.width = width
        self.height = height

    def set_on_wall(self, wall_id, distance=0):
        """
        Place the window on a wall at specified distance

        Args:
            wall_id: ID of the wall
            distance: Distance from start of the wall
        """
        self.wall_id = wall_id
        self.distance_wall = distance

    def from_dsl_structure(self, structure_node):
        """
        Create a Window from a DSL structure node

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
                print(f"Processing window property: {prop_literal}")

            if prop_literal == "id":
                if hasattr(prop.value, 'value'):
                    self.id = prop.value.value.strip('"\'')
                    if debug:
                        print(f"Window ID: {self.id}")

            elif prop_literal == "id_parent":
                if hasattr(prop.value, 'value'):
                    self.parent_id = prop.value.value.strip('"\'')
                    if debug:
                        print(f"Window parent ID: {self.parent_id}")

            elif prop_literal == "wall":
                if hasattr(prop.value, 'value'):
                    self.wall_id = prop.value.value.strip('"\'')
                    if debug:
                        print(f"Window wall ID: {self.wall_id}")

            elif prop_literal == "position":
                if hasattr(prop.value, 'elements') and len(prop.value.elements) >= 2:
                    try:
                        self.x = float(prop.value.elements[0].value)
                        self.y = float(prop.value.elements[1].value)
                        if debug:
                            print(f"Window position: ({self.x}, {self.y})")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing window position: {e}")

            elif prop_literal == "width":
                if hasattr(prop.value, 'value'):
                    try:
                        self.width = float(prop.value.value)
                        if debug:
                            print(f"Window width: {self.width}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing window width: {e}")

            elif prop_literal == "height":
                if hasattr(prop.value, 'value'):
                    try:
                        self.height = float(prop.value.value)
                        if debug:
                            print(f"Window height: {self.height}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing window height: {e}")

            elif prop_literal == "distance_wall":
                if hasattr(prop.value, 'value'):
                    try:
                        self.distance_wall = float(prop.value.value)
                        if debug:
                            print(f"Window distance from wall start: {self.distance_wall}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing window distance: {e}")

        return self