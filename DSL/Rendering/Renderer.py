from DSL.Rendering.SVGExporter import SVGExporter
from DSL.Rendering.StyleManager import StyleManager
from DSL.Models.FloorPlan import FloorPlan
import math


class Renderer:
    """
    Main rendering engine that converts model objects into visual representation
    """

    def __init__(self, scale=10.0, padding=50):
        """
        Initialize the renderer

        Args:
            scale: Scale factor for measurements (1 unit = scale pixels)
            padding: Padding around the floor plan in pixels
        """
        self.scale = scale
        self.padding = padding
        self.style_manager = StyleManager()

    def render(self, floor_plan, output_file):
        """
        Render the floor plan to an SVG file

        Args:
            floor_plan: FloorPlan object containing all elements
            output_file: Path to save the SVG file
        """
        # Print summary of what we're rendering
        print(f"Rendering floor plan with:")
        print(f"- {len(floor_plan.rooms)} rooms")
        print(f"- {len(floor_plan.doors)} doors")
        print(f"- {len(floor_plan.windows)} windows")
        print(f"- {len(floor_plan.furniture)} furniture items")

        # Calculate canvas size with padding
        width, height, min_x, min_y = self._calculate_canvas_size(floor_plan)

        # Create SVG exporter
        exporter = SVGExporter(
            width + self.padding * 2,
            height + self.padding * 2
        )

        print(f"Created SVG canvas with dimensions {width + self.padding * 2}x{height + self.padding * 2}")

        # Calculate offsets to ensure all elements are visible within the canvas
        offset_x = self.padding - min_x * self.scale
        offset_y = self.padding - min_y * self.scale

        print(f"Using offsets: ({offset_x}, {offset_y})")

        # Render each room
        valid_rooms = 0
        for room in floor_plan.rooms:
            if room.width <= 0 or room.height <= 0:
                print(f"Skipping room '{room.id}' with invalid dimensions: {room.width}x{room.height}")
                continue

            self._render_room(room, exporter, offset_x, offset_y)
            valid_rooms += 1

        print(f"Rendered {valid_rooms} valid rooms")

        # Render doors
        valid_doors = 0
        for door in floor_plan.doors:
            if door.width <= 0 and door.height <= 0:
                print(f"Skipping door '{door.id}' with invalid dimensions: {door.width}x{door.height}")
                continue

            self._render_door(door, exporter, offset_x, offset_y)
            valid_doors += 1

        print(f"Rendered {valid_doors} valid doors")

        # Render windows
        valid_windows = 0
        for window in floor_plan.windows:
            if window.width <= 0 and window.height <= 0:
                print(f"Skipping window '{window.id}' with invalid dimensions: {window.width}x{window.height}")
                continue

            self._render_window(window, exporter, offset_x, offset_y)
            valid_windows += 1

        print(f"Rendered {valid_windows} valid windows")

        # Render furniture
        valid_furniture = 0
        for furniture in floor_plan.furniture:
            if furniture.width <= 0 or furniture.height <= 0:
                print(
                    f"Skipping furniture '{furniture.id}' with invalid dimensions: {furniture.width}x{furniture.height}")
                continue

            self._render_furniture(furniture, exporter, offset_x, offset_y)
            valid_furniture += 1

        print(f"Rendered {valid_furniture} valid furniture items")

        # Export the final SVG
        exporter.save(output_file)
        print(f"Saved SVG to {output_file}")

        # If nothing valid was rendered, warn the user
        if valid_rooms == 0 and valid_doors == 0 and valid_windows == 0 and valid_furniture == 0:
            print("WARNING: No valid elements were rendered. Check your DSL input for proper dimensions.")

        return True

    def _calculate_canvas_size(self, floor_plan):
        """
        Calculate the canvas size based on the floor plan

        Returns:
            Tuple of (width, height, min_x, min_y)
        """
        if not floor_plan.rooms:
            return 800, 600, 0, 0

        # Set default values in case there are no valid coordinates
        min_x = 0
        min_y = 0
        max_x = 1000
        max_y = 800

        # Check if there are rooms with valid dimensions
        valid_rooms = [room for room in floor_plan.rooms if room.width > 0 and room.height > 0]
        if valid_rooms:
            min_x = min(room.x for room in valid_rooms)
            min_y = min(room.y for room in valid_rooms)
            max_x = max(room.x + room.width for room in valid_rooms)
            max_y = max(room.y + room.height for room in valid_rooms)

        # Check doors with valid dimensions
        valid_doors = [door for door in floor_plan.doors if door.width > 0 or door.height > 0]
        if valid_doors:
            if not valid_rooms or min([door.x for door in valid_doors]) < min_x:
                min_x = min(door.x for door in valid_doors)
            if not valid_rooms or min([door.y for door in valid_doors]) < min_y:
                min_y = min(door.y for door in valid_doors)
            if not valid_rooms or max([door.x + door.width for door in valid_doors]) > max_x:
                max_x = max(door.x + door.width for door in valid_doors)
            if not valid_rooms or max([door.y + door.height for door in valid_doors]) > max_y:
                max_y = max(door.y + door.height for door in valid_doors)

        # Check windows with valid dimensions
        valid_windows = [window for window in floor_plan.windows if window.width > 0 or window.height > 0]
        if valid_windows:
            if not valid_rooms and not valid_doors or min([window.x for window in valid_windows]) < min_x:
                min_x = min(window.x for window in valid_windows)
            if not valid_rooms and not valid_doors or min([window.y for window in valid_windows]) < min_y:
                min_y = min(window.y for window in valid_windows)
            if not valid_rooms and not valid_doors or max(
                    [window.x + window.width for window in valid_windows]) > max_x:
                max_x = max(window.x + window.width for window in valid_windows)
            if not valid_rooms and not valid_doors or max(
                    [window.y + window.height for window in valid_windows]) > max_y:
                max_y = max(window.y + window.height for window in valid_windows)

        # Check furniture with valid dimensions
        valid_furniture = [furniture for furniture in floor_plan.furniture if
                           furniture.width > 0 or furniture.height > 0]
        if valid_furniture:
            if (not valid_rooms and not valid_doors and not valid_windows) or min(
                    [furniture.x for furniture in valid_furniture]) < min_x:
                min_x = min(furniture.x for furniture in valid_furniture)
            if (not valid_rooms and not valid_doors and not valid_windows) or min(
                    [furniture.y for furniture in valid_furniture]) < min_y:
                min_y = min(furniture.y for furniture in valid_furniture)
            if (not valid_rooms and not valid_doors and not valid_windows) or max(
                    [furniture.x + furniture.width for furniture in valid_furniture]) > max_x:
                max_x = max(furniture.x + furniture.width for furniture in valid_furniture)
            if (not valid_rooms and not valid_doors and not valid_windows) or max(
                    [furniture.y + furniture.height for furniture in valid_furniture]) > max_y:
                max_y = max(furniture.y + furniture.height for furniture in valid_furniture)

        # Apply scale and compute dimensions
        width = max(800, (max_x - min_x) * self.scale)
        height = max(600, (max_y - min_y) * self.scale)

        print(f"Canvas dimensions: {width}x{height}, min_pos: ({min_x}, {min_y}), max_pos: ({max_x}, {max_y})")

        return width, height, min_x, min_y

    def _render_room(self, room, exporter, offset_x=0, offset_y=0):
        """
        Render a single room

        Args:
            room: Room object
            exporter: SVGExporter
            offset_x: X-offset for positioning
            offset_y: Y-offset for positioning
        """
        # Skip rendering if room has zero dimensions
        if room.width <= 0 or room.height <= 0:
            print(f"Warning: Room '{room.id}' has invalid dimensions: {room.width}x{room.height}")
            return

        # Get room style
        style = self.style_manager.get_room_style(room)

        # Calculate coordinates with scaling and offset
        x = room.x * self.scale + offset_x
        y = room.y * self.scale + offset_y
        width = room.width * self.scale
        height = room.height * self.scale

        print(f"Rendering room '{room.id}' at ({x}, {y}) with size {width}x{height}")

        # Add room rectangle
        exporter.add_rectangle(
            x, y, width, height,
            fill=style['fill'],
            stroke=style['stroke'],
            stroke_width=style['stroke_width']
        )

        # Add room label if provided
        if room.label:
            exporter.add_text(
                f"{room.label} ({room.area} m²)",
                x + width / 2,
                y + height / 2,
                font_size=style['font_size'],
                fill=style['text_color']
            )

        # Render walls
        self._render_walls(room, exporter, offset_x, offset_y)

    def _render_walls(self, room, exporter, offset_x=0, offset_y=0):
        """
        Render walls for a room

        Args:
            room: Room object
            exporter: SVGExporter
            offset_x: X-offset for positioning
            offset_y: Y-offset for positioning
        """
        # If room has explicit walls, render those
        if room.walls:
            for wall in room.walls:
                self._render_wall(wall, exporter, offset_x, offset_y)
            return

        # Otherwise, render the rectangular outer walls
        style = self.style_manager.get_wall_style()

        x = room.x * self.scale + offset_x
        y = room.y * self.scale + offset_y
        width = room.width * self.scale
        height = room.height * self.scale

        # Top wall
        exporter.add_line(
            x, y,
            x + width, y,
            stroke=style['stroke'],
            stroke_width=style['stroke_width']
        )

        # Right wall
        exporter.add_line(
            x + width, y,
            x + width, y + height,
            stroke=style['stroke'],
            stroke_width=style['stroke_width']
        )

        # Bottom wall
        exporter.add_line(
            x + width, y + height,
            x, y + height,
            stroke=style['stroke'],
            stroke_width=style['stroke_width']
        )

        # Left wall
        exporter.add_line(
            x, y + height,
            x, y,
            stroke=style['stroke'],
            stroke_width=style['stroke_width']
        )

    def _render_wall(self, wall, exporter, offset_x=0, offset_y=0):
        """
        Render a single wall

        Args:
            wall: Wall object
            exporter: SVGExporter
            offset_x: X-offset for positioning
            offset_y: Y-offset for positioning
        """
        style = self.style_manager.get_wall_style()

        # Convert to pixels with scaling
        x1 = wall.start_x * self.scale + offset_x
        y1 = wall.start_y * self.scale + offset_y
        x2 = wall.end_x * self.scale + offset_x
        y2 = wall.end_y * self.scale + offset_y

        # Add wall line
        exporter.add_line(
            x1, y1, x2, y2,
            stroke=style['stroke'],
            stroke_width=style['stroke_width']
        )

    def _render_door(self, door, exporter, offset_x=0, offset_y=0):
        """
        Render a door

        Args:
            door: Door object
            exporter: SVGExporter
            offset_x: X-offset for positioning
            offset_y: Y-offset for positioning
        """
        # Skip rendering if door has zero dimensions
        if door.width <= 0 and door.height <= 0:
            print(f"Warning: Door '{door.id}' has invalid dimensions: {door.width}x{door.height}")
            return

        style = self.style_manager.get_door_style()

        # Convert to pixels with scaling
        x = door.x * self.scale + offset_x
        y = door.y * self.scale + offset_y
        width = max(10, door.width * self.scale)  # Ensure minimum visibility
        height = max(10, door.height * self.scale)  # Ensure minimum visibility

        print(f"Rendering door '{door.id}' at ({x}, {y}) with size {width}x{height}")

        # Add door arc based on direction
        if door.direction == "left":
            exporter.add_door_arc(
                x, y, width, height, "left",
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        elif door.direction == "right":
            exporter.add_door_arc(
                x, y, width, height, "right",
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        elif door.direction == "up":
            exporter.add_door_arc(
                x, y, width, height, "up",
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        elif door.direction == "down":
            exporter.add_door_arc(
                x, y, width, height, "down",
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        else:
            # Default: just draw a line for the door
            exporter.add_line(
                x, y, x + width, y,
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

    def _render_window(self, window, exporter, offset_x=0, offset_y=0):
        """
        Render a window

        Args:
            window: Window object
            exporter: SVGExporter
            offset_x: X-offset for positioning
            offset_y: Y-offset for positioning
        """
        # Skip rendering if window has zero dimensions
        if window.width <= 0 and window.height <= 0:
            print(f"Warning: Window '{window.id}' has invalid dimensions: {window.width}x{window.height}")
            return

        style = self.style_manager.get_window_style()

        # Convert to pixels with scaling
        x = window.x * self.scale + offset_x
        y = window.y * self.scale + offset_y
        width = max(10, window.width * self.scale)  # Ensure minimum visibility
        height = max(10, window.height * self.scale)  # Ensure minimum visibility

        print(f"Rendering window '{window.id}' at ({x}, {y}) with size {width}x{height}")

        # Add window rectangle with style
        exporter.add_window(
            x, y, width, height,
            stroke=style['stroke'],
            stroke_width=style['stroke_width']
        )

    def _render_furniture(self, furniture, exporter, offset_x=0, offset_y=0):
        """
        Render a furniture item

        Args:
            furniture: Furniture object
            exporter: SVGExporter
            offset_x: X-offset for positioning
            offset_y: Y-offset for positioning
        """
        # Skip rendering if furniture has zero dimensions
        if furniture.width <= 0 or furniture.height <= 0:
            print(f"Warning: Furniture '{furniture.id}' has invalid dimensions: {furniture.width}x{furniture.height}")
            return

        style = self.style_manager.get_furniture_style(furniture.furniture_type)

        # Convert to pixels with scaling
        x = furniture.x * self.scale + offset_x
        y = furniture.y * self.scale + offset_y
        width = max(10, furniture.width * self.scale)  # Ensure minimum visibility
        height = max(10, furniture.height * self.scale)  # Ensure minimum visibility

        print(f"Rendering furniture '{furniture.id}' at ({x}, {y}) with size {width}x{height}")

        # Render based on furniture type
        if furniture.furniture_type == "BED":
            exporter.add_bed(
                x, y, width, height,
                fill=style['fill'],
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        elif furniture.furniture_type == "TABLE":
            exporter.add_table(
                x, y, width, height,
                fill=style['fill'],
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        elif furniture.furniture_type == "CHAIR":
            exporter.add_chair(
                x, y, width, height,
                fill=style['fill'],
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        elif furniture.furniture_type == "STAIRS":
            exporter.add_stairs(
                x, y, width, height,
                fill=style['fill'],
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        elif furniture.furniture_type == "ELEVATOR":
            exporter.add_elevator(
                x, y, width, height,
                fill=style['fill'],
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )
        else:
            # Default: just a rectangle
            exporter.add_rectangle(
                x, y, width, height,
                fill=style['fill'],
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )