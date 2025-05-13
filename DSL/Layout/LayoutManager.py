from DSL.Models.FloorPlan import FloorPlan
from DSL.Models.Room import Room
from DSL.Models.Wall import Wall
from DSL.Models.Door import Door
from DSL.Models.Window import Window
from DSL.Models.Furniture import Furniture
import math


class LayoutManager:
    """
    Layout Manager for floor plans that handles:
    - Room positioning without overlaps while preserving original coordinates when possible
    - Placing windows and doors on walls
    """

    def __init__(self, floor_plan):
        """
        Initialize the layout manager

        Args:
            floor_plan: FloorPlan object to optimize
        """
        self.floor_plan = floor_plan
        self.wall_thickness = 20

        # Default dimensions if header not provided
        self.max_width = 1000
        self.max_height = 1000

        # Minimum door dimensions (only used if door has no dimensions)
        self.min_door_width = 1
        self.min_door_height = 1

        # Use header dimensions if available
        if self.floor_plan.header:
            if 'width' in self.floor_plan.header:
                self.max_width = self.floor_plan.header['width']
            if 'height' in self.floor_plan.header:
                self.max_height = self.floor_plan.header['height']

    def optimize_layout(self):
        """
        Main method to optimize the floor plan layout

        Returns:
            Optimized FloorPlan object
        """
        # Step 1: Position rooms without overlaps while preserving coordinates
        self._prevent_room_intersections()

        # Step 2: Place windows on walls
        self._place_windows_on_walls()

        # Step 3: Place doors on walls
        self._place_doors_on_walls()

        return self.floor_plan

    def _prevent_room_intersections(self):
        """
        Adjusts room positions to prevent intersections while trying to keep
        rooms close to their original positions
        """
        # Sort rooms by area (largest first) for processing order
        sorted_rooms = sorted(self.floor_plan.rooms,
                              key=lambda r: r.width * r.height,
                              reverse=True)

        # Keep track of placed rooms
        placed_rooms = []

        for room in sorted_rooms:
            # Check if this room intersects with any already placed room
            while self._has_intersection(room, placed_rooms):
                # Resolve the intersection by moving the room
                self._resolve_intersection(room, placed_rooms)

            # Make sure room is within floor plan boundaries
            self._ensure_within_boundaries(room)

            # Add to placed rooms
            placed_rooms.append(room)

    def _has_intersection(self, room, other_rooms):
        """
        Check if a room intersects with any other room

        Args:
            room: The room to check
            other_rooms: List of other rooms to check against

        Returns:
            True if there's an intersection, False otherwise
        """
        for other in other_rooms:
            # Check if rooms overlap
            if (room.x < other.x + other.width and
                    room.x + room.width > other.x and
                    room.y < other.y + other.height and
                    room.y + room.height > other.y):
                return True

        return False

    def _resolve_intersection(self, room, other_rooms):
        """
        Resolve room intersection by moving the room

        Args:
            room: Room to move
            other_rooms: List of placed rooms
        """
        # Find the room that this room intersects with
        for other in other_rooms:
            # Check if rooms overlap
            if (room.x < other.x + other.width and
                    room.x + room.width > other.x and
                    room.y < other.y + other.height and
                    room.y + room.height > other.y):

                # Calculate overlap in both directions
                overlap_x = min(room.x + room.width, other.x + other.width) - max(room.x, other.x)
                overlap_y = min(room.y + room.height, other.y + other.height) - max(room.y, other.y)

                # Determine which direction requires less movement
                if overlap_x < overlap_y:
                    # Move horizontally
                    if room.x < other.x:
                        # Move left
                        room.x = other.x - room.width - 1  # 1px gap
                    else:
                        # Move right
                        room.x = other.x + other.width + 1  # 1px gap
                else:
                    # Move vertically
                    if room.y < other.y:
                        # Move up
                        room.y = other.y - room.height - 1  # 1px gap
                    else:
                        # Move down
                        room.y = other.y + other.height + 1  # 1px gap

                # Only resolve one intersection at a time
                break

    def _ensure_within_boundaries(self, room):
        """
        Make sure the room stays within floor plan boundaries

        Args:
            room: Room to check
        """
        # Check and adjust x coordinate
        if room.x < 0:
            room.x = 0
        elif room.x + room.width > self.max_width:
            room.x = max(0, self.max_width - room.width)

        # Check and adjust y coordinate
        if room.y < 0:
            room.y = 0
        elif room.y + room.height > self.max_height:
            room.y = max(0, self.max_height - room.height)

    def _place_windows_on_walls(self):
        """
        Place each window on a wall of the closest room
        """
        for window in self.floor_plan.windows:
            self._place_window_on_wall(window)

    def _place_window_on_wall(self, window):
        """
        Place a window on a wall of the closest room

        Args:
            window: Window object to place
        """
        # Find closest room to the window
        closest_room = None
        min_distance = float('inf')

        window_center_x = window.x + window.width / 2
        window_center_y = window.y + window.height / 2

        for room in self.floor_plan.rooms:
            # Calculate room center
            room_center_x = room.x + room.width / 2
            room_center_y = room.y + room.height / 2

            # Calculate distance between centers
            distance = math.sqrt((room_center_x - window_center_x) ** 2 +
                                 (room_center_y - window_center_y) ** 2)

            if distance < min_distance:
                min_distance = distance
                closest_room = room

        if not closest_room:
            return  # No rooms to place window on

        # Calculate distances to each wall
        dist_to_left = abs(window_center_x - closest_room.x)
        dist_to_right = abs(window_center_x - (closest_room.x + closest_room.width))
        dist_to_top = abs(window_center_y - closest_room.y)
        dist_to_bottom = abs(window_center_y - (closest_room.y + closest_room.height))

        # Find the closest wall
        min_dist = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)

        # Simple offset for visibility
        offset = 0  # Place directly on the wall

        # Bounds for the other coordinate to keep window within room limits
        min_x = closest_room.x + self.wall_thickness
        max_x = closest_room.x + closest_room.width - window.width - self.wall_thickness
        min_y = closest_room.y + self.wall_thickness
        max_y = closest_room.y + closest_room.height - window.height - self.wall_thickness

        if min_dist == dist_to_left:
            # Left wall
            window.x = closest_room.x + offset
            # Keep y coordinate within room bounds
            window.y = min(max(window.y, min_y), max_y)
        elif min_dist == dist_to_right:
            # Right wall
            window.x = closest_room.x + closest_room.width - window.width - offset
            # Keep y coordinate within room bounds
            window.y = min(max(window.y, min_y), max_y)
        elif min_dist == dist_to_top:
            # Top wall
            window.y = closest_room.y + offset
            # Keep x coordinate within room bounds
            window.x = min(max(window.x, min_x), max_x)
        elif min_dist == dist_to_bottom:
            # Bottom wall
            window.y = closest_room.y + closest_room.height - window.height - offset
            # Keep x coordinate within room bounds
            window.x = min(max(window.x, min_x), max_x)

    def _place_doors_on_walls(self):
        """
        Place each door on a wall of the closest room
        """
        for door in self.floor_plan.doors:
            self._place_door_on_wall(door)

    def _place_door_on_wall(self, door):
        """
        Place a door on a wall of the closest room

        Args:
            door: Door object to place
        """
        # Find closest room to the door
        closest_room = None
        min_distance = float('inf')

        # Ensure door has valid dimensions
        door_width = max(door.width, self.min_door_width) if door.width > 0 else self.min_door_width
        door_height = max(door.height, self.min_door_height) if door.height > 0 else self.min_door_height

        # Update door dimensions if needed
        if door.width != door_width:
            door.width = door_width
        if door.height != door_height:
            door.height = door_height

        door_center_x = door.x + door.width / 2
        door_center_y = door.y + door.height / 2

        for room in self.floor_plan.rooms:
            # Calculate room center
            room_center_x = room.x + room.width / 2
            room_center_y = room.y + room.height / 2

            # Calculate distance between centers
            distance = math.sqrt((room_center_x - door_center_x) ** 2 +
                                 (room_center_y - door_center_y) ** 2)

            if distance < min_distance:
                min_distance = distance
                closest_room = room

        if not closest_room:
            return  # No rooms to place door on

        # Calculate distances to each wall
        dist_to_left = abs(door_center_x - closest_room.x)
        dist_to_right = abs(door_center_x - (closest_room.x + closest_room.width))
        dist_to_top = abs(door_center_y - closest_room.y)
        dist_to_bottom = abs(door_center_y - (closest_room.y + closest_room.height))

        # Find the closest wall
        min_dist = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)

        # Offset for placement
        offset = 0  # Place directly on the wall

        # Bounds for the other coordinate to keep door within room limits
        min_x = closest_room.x + self.wall_thickness
        max_x = closest_room.x + closest_room.width - door.width - self.wall_thickness
        min_y = closest_room.y + self.wall_thickness
        max_y = closest_room.y + closest_room.height - door.height - self.wall_thickness

        if min_dist == dist_to_left:
            # Left wall
            door.x = closest_room.x + offset
            # Keep y coordinate within room bounds
            door.y = min(max(door.y, min_y), max_y)
            # Set door direction
            door.direction = "right"
        elif min_dist == dist_to_right:
            # Right wall
            door.x = closest_room.x + closest_room.width - door.width - offset
            # Keep y coordinate within room bounds
            door.y = min(max(door.y, min_y), max_y)
            # Set door direction
            door.direction = "left"
        elif min_dist == dist_to_top:
            # Top wall
            door.y = closest_room.y + offset
            # Keep x coordinate within room bounds
            door.x = min(max(door.x, min_x), max_x)
            # Set door direction
            door.direction = "down"
        elif min_dist == dist_to_bottom:
            # Bottom wall
            door.y = closest_room.y + closest_room.height - door.height - offset
            # Keep x coordinate within room bounds
            door.x = min(max(door.x, min_x), max_x)
            # Set door direction
            door.direction = "up"