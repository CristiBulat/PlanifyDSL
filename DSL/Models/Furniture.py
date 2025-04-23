class Furniture:
    """
    Base class for furniture items in the floor plan
    """

    def __init__(self, id=None, furniture_type=None, x=0, y=0, width=0, height=0):
        """
        Initialize a furniture item

        Args:
            id: Unique identifier
            furniture_type: Type of furniture (BED, TABLE, CHAIR, etc.)
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of the furniture
            height: Height of the furniture
        """
        self.id = id
        self.furniture_type = furniture_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Optional properties
        self.label = None
        self.color = None
        self.rotation = 0  # Rotation in degrees
        self.parent_id = None  # ID of the parent room
        self.layer = 0  # Layer for rendering order

    def set_position(self, x, y):
        """
        Set the position of the furniture

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y

    def set_size(self, width, height):
        """
        Set the size of the furniture

        Args:
            width: Width of the furniture
            height: Height of the furniture
        """
        self.width = width
        self.height = height

    def set_rotation(self, angle):
        """
        Set the rotation angle of the furniture

        Args:
            angle: Rotation angle in degrees
        """
        self.rotation = angle % 360

    def from_dsl_structure(self, structure_node):
        """
        Create a Furniture item from a DSL structure node

        Args:
            structure_node: StructureStatementNode from the AST

        Returns:
            Self for chaining
        """
        # Set furniture type based on structure type
        self.furniture_type = structure_node.structure_type
        debug = True  # Enable debug output

        if debug:
            print(f"Creating furniture of type: {self.furniture_type}")

        # Process each property
        for prop in structure_node.properties:
            # Get the literal token value (the property name as it appears in the DSL)
            prop_literal = prop.token.literal.lower() if hasattr(prop.token, 'literal') else ""

            if debug:
                print(f"Processing furniture property: {prop_literal}")

            if prop_literal == "id":
                if hasattr(prop.value, 'value'):
                    self.id = prop.value.value.strip('"\'')
                    if debug:
                        print(f"Furniture ID: {self.id}")

            elif prop_literal == "id_parent":
                if hasattr(prop.value, 'value'):
                    self.parent_id = prop.value.value.strip('"\'')
                    if debug:
                        print(f"Furniture parent ID: {self.parent_id}")

            elif prop_literal == "position":
                if hasattr(prop.value, 'elements') and len(prop.value.elements) >= 2:
                    try:
                        self.x = float(prop.value.elements[0].value)
                        self.y = float(prop.value.elements[1].value)
                        if debug:
                            print(f"Furniture position: ({self.x}, {self.y})")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing furniture position: {e}")

            elif prop_literal == "width":
                if hasattr(prop.value, 'value'):
                    try:
                        self.width = float(prop.value.value)
                        if debug:
                            print(f"Furniture width: {self.width}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing furniture width: {e}")

            elif prop_literal == "height":
                if hasattr(prop.value, 'value'):
                    try:
                        self.height = float(prop.value.value)
                        if debug:
                            print(f"Furniture height: {self.height}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing furniture height: {e}")

            elif prop_literal == "rotation":
                if hasattr(prop.value, 'value'):
                    try:
                        self.set_rotation(float(prop.value.value))
                        if debug:
                            print(f"Furniture rotation: {self.rotation}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing furniture rotation: {e}")

            elif prop_literal == "label":
                if hasattr(prop.value, 'value'):
                    self.label = prop.value.value.strip('"\'')
                    if debug:
                        print(f"Furniture label: {self.label}")

            elif prop_literal == "layer":
                if hasattr(prop.value, 'value'):
                    try:
                        self.layer = int(prop.value.value)
                        if debug:
                            print(f"Furniture layer: {self.layer}")
                    except (ValueError, AttributeError) as e:
                        if debug:
                            print(f"Error parsing furniture layer: {e}")

            elif prop_literal == "color":
                if hasattr(prop.value, 'value'):
                    self.color = prop.value.value
                    if debug:
                        print(f"Furniture color: {self.color}")

        return self

    @classmethod
    def create_from_structure(cls, structure_node):
        """
        Factory method to create furniture based on structure type

        Args:
            structure_node: StructureStatementNode from the AST

        Returns:
            Furniture object
        """
        structure_type = structure_node.structure_type
        furniture = cls(furniture_type=structure_type)
        return furniture.from_dsl_structure(structure_node)