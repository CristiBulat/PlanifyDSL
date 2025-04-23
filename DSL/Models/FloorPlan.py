class FloorPlan:
    """
    Container for all elements in a floor plan
    """

    def __init__(self):
        """Initialize an empty floor plan"""
        self.rooms = []
        self.walls = []
        self.doors = []
        self.windows = []
        self.furniture = []
        self.header = None

        # Store elements by ID for quick lookup
        self.elements_by_id = {}

    def add_room(self, room):
        """
        Add a room to the floor plan

        Args:
            room: Room object
        """
        self.rooms.append(room)
        if room.id:
            self.elements_by_id[room.id] = room

    def add_wall(self, wall):
        """
        Add a wall to the floor plan

        Args:
            wall: Wall object
        """
        self.walls.append(wall)
        if wall.id:
            self.elements_by_id[wall.id] = wall

    def add_door(self, door):
        """
        Add a door to the floor plan

        Args:
            door: Door object
        """
        self.doors.append(door)
        if door.id:
            self.elements_by_id[door.id] = door

    def add_window(self, window):
        """
        Add a window to the floor plan

        Args:
            window: Window object
        """
        self.windows.append(window)
        if window.id:
            self.elements_by_id[window.id] = window

    def add_furniture(self, furniture):
        """
        Add a furniture item to the floor plan

        Args:
            furniture: Furniture object
        """
        self.furniture.append(furniture)
        if furniture.id:
            self.elements_by_id[furniture.id] = furniture

    def get_element_by_id(self, element_id):
        """
        Get an element by its ID

        Args:
            element_id: ID of the element

        Returns:
            Element object or None if not found
        """
        return self.elements_by_id.get(element_id, None)

    def get_all_elements(self):
        """
        Get all elements in the floor plan

        Returns:
            List of all elements
        """
        return self.rooms + self.walls + self.doors + self.windows + self.furniture

    def set_header(self, width, height):
        """
        Set the header information (size of the floor plan)

        Args:
            width: Width of the floor plan
            height: Height of the floor plan
        """
        self.header = {
            'width': width,
            'height': height
        }