from DSL.Rendering.SVGExporter import SVGExporter
from DSL.Rendering.StyleManager import StyleManager
from DSL.Models.FloorPlan import FloorPlan
import math


class Renderer:
    """
    Improved rendering engine that ensures proper layout of floor plan elements
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

        # Enhanced styling
        self.door_width = 10  # Default door width
        self.window_width = 8  # Default window width
        self.wall_thickness = 3  # Wall thickness
        self.use_grid_lines = False  # Whether to show grid lines
        self.grid_size = 100  # Grid size in pixels
        self.use_room_labels = True  # Whether to show room labels
        self.show_dimensions = True  # Whether to show room dimensions

        # Room color palette
        self.enhanced_colors = True  # Use enhanced color palette

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

        # Draw grid lines if enabled
        if self.use_grid_lines:
            self._draw_grid(exporter, width, height, offset_x, offset_y)

        # Order elements by layer: first rooms, then walls, then doors and windows, lastly furniture
        self._render_rooms(floor_plan.rooms, exporter, offset_x, offset_y)
        self._render_doors(floor_plan.doors, exporter, offset_x, offset_y)
        self._render_windows(floor_plan.windows, exporter, offset_x, offset_y)
        self._render_furniture(floor_plan.furniture, exporter, offset_x, offset_y)

        # Export the final SVG
        exporter.save(output_file)
        print(f"Saved SVG to {output_file}")

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

        # Apply scale and compute dimensions
        width = max(800, (max_x - min_x) * self.scale)
        height = max(600, (max_y - min_y) * self.scale)

        print(f"Canvas dimensions: {width}x{height}, min_pos: ({min_x}, {min_y}), max_pos: ({max_x}, {max_y})")

        return width, height, min_x, min_y

    def _draw_grid(self, exporter, width, height, offset_x, offset_y):
        """
        Draw grid lines on the canvas

        Args:
            exporter: SVGExporter
            width: Canvas width
            height: Canvas height
            offset_x: X offset
            offset_y: Y offset
        """
        # Draw horizontal grid lines
        for y in range(0, int(height) + self.grid_size, self.grid_size):
            exporter.add_line(
                offset_x, y + offset_y,
                          width + offset_x, y + offset_y,
                stroke="#DDDDDD",
                stroke_width=0.5
            )

        # Draw vertical grid lines
        for x in range(0, int(width) + self.grid_size, self.grid_size):
            exporter.add_line(
                x + offset_x, offset_y,
                x + offset_x, height + offset_y,
                stroke="#DDDDDD",
                stroke_width=0.5
            )

    def _render_rooms(self, rooms, exporter, offset_x=0, offset_y=0):
        """
        Render all rooms

        Args:
            rooms: List of Room objects
            exporter: SVGExporter
            offset_x: X offset
            offset_y: Y offset
        """
        # First render all room backgrounds
        for room in rooms:
            if room.width <= 0 or room.height <= 0:
                print(f"Warning: Room '{room.id}' has invalid dimensions: {room.width}x{room.height}")
                continue

            self._render_room_background(room, exporter, offset_x, offset_y)

        # Then render all room walls (so walls are on top of backgrounds)
        for room in rooms:
            if room.width <= 0 or room.height <= 0:
                continue

            self._render_room_walls(room, exporter, offset_x, offset_y)

        # Finally render room labels
        if self.use_room_labels:
            for room in rooms:
                if room.width <= 0 or room.height <= 0:
                    continue

                self._render_room_label(room, exporter, offset_x, offset_y)

    def _render_room_background(self, room, exporter, offset_x=0, offset_y=0):
        """
        Render a room's background

        Args:
            room: Room object
            exporter: SVGExporter
            offset_x: X offset
            offset_y: Y offset
        """
        # Get room style
        style = self.style_manager.get_room_style(room)

        # If enhanced colors is enabled, use more interesting colors
        if self.enhanced_colors:
            # Check room label to assign a logical color
            if room.label:
                label_lower = room.label.lower()
                if "living" in label_lower:
                    style['fill'] = "#F0FFF0"  # Honeydew
                    style['text_color'] = "#006400"  # DarkGreen
                elif "kitchen" in label_lower:
                    style['fill'] = "#FFF8DC"  # Cornsilk
                    style['text_color'] = "#8B4513"  # SaddleBrown
                elif "bath" in label_lower:
                    style['fill'] = "#E0FFFF"  # LightCyan
                    style['text_color'] = "#008B8B"  # DarkCyan
                elif "bed" in label_lower:
                    style['fill'] = "#FFF0F5"  # LavenderBlush
                    style['text_color'] = "#8B008B"  # DarkMagenta
                elif "guest" in label_lower:
                    style['fill'] = "#F0FFFF"  # Azure
                    style['text_color'] = "#4682B4"  # SteelBlue
                elif "dining" in label_lower:
                    style['fill'] = "#FFF5EE"  # Seashell
                    style['text_color'] = "#A0522D"  # Sienna
                elif "study" in label_lower or "office" in label_lower:
                    style['fill'] = "#F5F5DC"  # Beige
                    style['text_color'] = "#2F4F4F"  # DarkSlateGray
                elif "hallway" in label_lower or "corridor" in label_lower:
                    style['fill'] = "#F8F8FF"  # GhostWhite
                    style['text_color'] = "#708090"  # SlateGray

        # Calculate coordinates with scaling and offset
        x = room.x * self.scale + offset_x
        y = room.y * self.scale + offset_y
        width = room.width * self.scale
        height = room.height * self.scale

        print(f"Rendering room '{room.id}' at ({x}, {y}) with size {width}x{height}")

        # Add room rectangle with rounded corners for better visual appeal
        corner_radius = min(width, height) * 0.02  # 2% of smaller dimension

        # Add room rectangle - if enhanced styling, use rounded corners
        if corner_radius > 0 and corner_radius < min(width / 4, height / 4):
            # Create rounded rectangle path
            path = f'M {x + corner_radius} {y} '
            path += f'L {x + width - corner_radius} {y} '
            path += f'Q {x + width} {y} {x + width} {y + corner_radius} '
            path += f'L {x + width} {y + height - corner_radius} '
            path += f'Q {x + width} {y + height} {x + width - corner_radius} {y + height} '
            path += f'L {x + corner_radius} {y + height} '
            path += f'Q {x} {y + height} {x} {y + height - corner_radius} '
            path += f'L {x} {y + corner_radius} '
            path += f'Q {x} {y} {x + corner_radius} {y} Z'

            element = f'<path d="{path}" fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"]}" />'
            exporter.elements.append(element)
        else:
            # Standard rectangle for smaller rooms
            exporter.add_rectangle(
                x, y, width, height,
                fill=style['fill'],
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

    def _render_room_walls(self, room, exporter, offset_x=0, offset_y=0):
        """
        Render walls for a room

        Args:
            room: Room object
            exporter: SVGExporter
            offset_x: X offset
            offset_y: Y offset
        """
        # Get wall style
        style = self.style_manager.get_wall_style()

        # Calculate coordinates with scaling and offset
        x = room.x * self.scale + offset_x
        y = room.y * self.scale + offset_y
        width = room.width * self.scale
        height = room.height * self.scale

        # If room has explicit walls, render those
        if room.walls:
            for wall in room.walls:
                # Convert to pixels with scaling
                x1 = wall.start_x * self.scale + offset_x
                y1 = wall.start_y * self.scale + offset_y
                x2 = wall.end_x * self.scale + offset_x
                y2 = wall.end_y * self.scale + offset_y

                # Add wall line
                exporter.add_line(
                    x1, y1, x2, y2,
                    stroke=style['stroke'],
                    stroke_width=self.wall_thickness
                )
        else:
            # Otherwise, render the rectangular outer walls
            # Top wall
            exporter.add_line(
                x, y,
                x + width, y,
                stroke=style['stroke'],
                stroke_width=self.wall_thickness
            )

            # Right wall
            exporter.add_line(
                x + width, y,
                x + width, y + height,
                stroke=style['stroke'],
                stroke_width=self.wall_thickness
            )

            # Bottom wall
            exporter.add_line(
                x + width, y + height,
                x, y + height,
                stroke=style['stroke'],
                stroke_width=self.wall_thickness
            )

            # Left wall
            exporter.add_line(
                x, y + height,
                x, y,
                stroke=style['stroke'],
                stroke_width=self.wall_thickness
            )

    def _render_room_label(self, room, exporter, offset_x=0, offset_y=0):
        """
        Render a room's label

        Args:
            room: Room object
            exporter: SVGExporter
            offset_x: X offset
            offset_y: Y offset
        """
        # Get room style
        style = self.style_manager.get_room_style(room)

        # Calculate coordinates with scaling and offset
        x = room.x * self.scale + offset_x
        y = room.y * self.scale + offset_y
        width = room.width * self.scale
        height = room.height * self.scale

        # Add room label if provided
        if room.label:
            # Add room name with area information
            area_text = f"({room.area:.1f} m²)" if self.show_dimensions else ""
            label_text = f"{room.label}" if not area_text else f"{room.label} {area_text}"

            exporter.add_text(
                label_text,
                x + width / 2,
                y + height / 2,
                font_size=style['font_size'],
                fill=style['text_color']
            )

            # If showing dimensions, add width and height labels along the walls
            if self.show_dimensions and width > 100 and height > 100:
                # Width dimension on top
                exporter.add_text(
                    f"{room.width:.1f}",
                    x + width / 2,
                    y - 5,
                    font_size=style['font_size'] * 0.8,
                    fill=style['text_color']
                )

                # Height dimension on left
                exporter.add_text(
                    f"{room.height:.1f}",
                    x - 10,
                    y + height / 2,
                    font_size=style['font_size'] * 0.8,
                    fill=style['text_color']
                )

    def _render_doors(self, doors, exporter, offset_x=0, offset_y=0):
        """
        Render all doors

        Args:
            doors: List of Door objects
            exporter: SVGExporter
            offset_x: X offset
            offset_y: Y offset
        """
        for door in doors:
            if door.width <= 0 and door.height <= 0:
                print(f"Warning: Door '{door.id}' has invalid dimensions: {door.width}x{door.height}")
                continue

            self._render_door(door, exporter, offset_x, offset_y)

    def _render_door(self, door, exporter, offset_x=0, offset_y=0):
        """
        Render a door with improved styling

        Args:
            door: Door object
            exporter: SVGExporter
            offset_x: X offset
            offset_y: Y offset
        """
        # Get door style
        style = self.style_manager.get_door_style()

        # Convert to pixels with scaling
        x = door.x * self.scale + offset_x
        y = door.y * self.scale + offset_y
        width = max(self.door_width, door.width * self.scale)  # Ensure minimum visibility
        height = max(self.door_width, door.height * self.scale)  # Ensure minimum visibility

        print(f"Rendering door '{door.id}' at ({x}, {y}) with size {width}x{height}")

        # Add door with improved styling based on direction
        if door.direction == "left":
            # Vertical door opening left
            exporter.add_door_arc(
                x, y, width, height, "left",
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

            # Add handle on the right side
            handle_x = x + width * 0.75
            handle_y = y + height * 0.5
            exporter.add_rectangle(
                handle_x, handle_y - height * 0.05,
                          width * 0.1, height * 0.1,
                fill="#888888", stroke=style['stroke'], stroke_width=0.5
            )

        elif door.direction == "right":
            # Vertical door opening right
            exporter.add_door_arc(
                x, y, width, height, "right",
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

            # Add handle on the left side
            handle_x = x + width * 0.25
            handle_y = y + height * 0.5
            exporter.add_rectangle(
                handle_x - width * 0.05, handle_y - height * 0.05,
                width * 0.1, height * 0.1,
                fill="#888888", stroke=style['stroke'], stroke_width=0.5
            )

        elif door.direction == "up":
            # Horizontal door opening up
            exporter.add_door_arc(
                x, y, width, height, "up",
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

            # Add handle on the bottom side
            handle_x = x + width * 0.5
            handle_y = y + height * 0.75
            exporter.add_rectangle(
                handle_x - width * 0.05, handle_y - height * 0.05,
                width * 0.1, height * 0.1,
                fill="#888888", stroke=style['stroke'], stroke_width=0.5
            )

        elif door.direction == "down":
            # Horizontal door opening down
            exporter.add_door_arc(
                x, y, width, height, "down",
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

            # Add handle on the top side
            handle_x = x + width * 0.5
            handle_y = y + height * 0.25
            exporter.add_rectangle(
                handle_x - width * 0.05, handle_y - height * 0.05,
                width * 0.1, height * 0.1,
                fill="#888888", stroke=style['stroke'], stroke_width=0.5
            )

        else:
            # Default: just draw a line for the door
            exporter.add_line(
                x, y, x + width, y,
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

    def _render_windows(self, windows, exporter, offset_x=0, offset_y=0):
        """
        Render all windows

        Args:
            windows: List of Window objects
            exporter: SVGExporter
            offset_x: X offset
            offset_y: Y offset
        """
        for window in windows:
            if window.width <= 0 and window.height <= 0:
                print(f"Warning: Window '{window.id}' has invalid dimensions: {window.width}x{window.height}")
                continue

            self._render_window(window, exporter, offset_x, offset_y)

    def _render_window(self, window, exporter, offset_x=0, offset_y=0):
        """
        Render a window with improved styling

        Args:
            window: Window object
            exporter: SVGExporter
            offset_x: X offset
            offset_y: Y offset
        """
        # Get window style
        style = self.style_manager.get_window_style()

        # Convert to pixels with scaling
        x = window.x * self.scale + offset_x
        y = window.y * self.scale + offset_y
        width = max(self.window_width, window.width * self.scale)  # Ensure minimum visibility
        height = max(self.window_width, window.height * self.scale)  # Ensure minimum visibility

        print(f"Rendering window '{window.id}' at ({x}, {y}) with size {width}x{height}")

        # Determine if this is a horizontal or vertical window
        is_horizontal = width > height

        # Draw improved window representation
        if is_horizontal:
            # Draw window frame
            exporter.add_rectangle(
                x, y - height / 2, width, height,
                fill="#E6F7FF",  # Light blue for glass
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

            # Draw the main window line (sill)
            exporter.add_line(
                x, y,
                x + width, y,
                stroke=style['stroke'],
                stroke_width=style['stroke_width'] * 1.5
            )

            # Draw window panes
            num_panes = max(1, min(int(width / 30), 4))
            pane_width = width / num_panes

            for i in range(num_panes):
                # Vertical dividers
                if i > 0:
                    pane_x = x + i * pane_width
                    exporter.add_line(
                        pane_x, y - height / 2,
                        pane_x, y + height / 2,
                        stroke=style['stroke'],
                        stroke_width=style['stroke_width'] * 0.7
                    )

                # Horizontal divider for each pane
                mid_y = y - height / 4
                exporter.add_line(
                    x + i * pane_width, mid_y,
                    x + (i + 1) * pane_width, mid_y,
                    stroke=style['stroke'],
                    stroke_width=style['stroke_width'] * 0.7
                )
        else:
            # Vertical window
            # Draw window frame
            exporter.add_rectangle(
                x - width / 2, y, width, height,
                fill="#E6F7FF",  # Light blue for glass
                stroke=style['stroke'],
                stroke_width=style['stroke_width']
            )

            # Draw the main window line (edge)
            exporter.add_line(
                x, y,
                x, y + height,
                stroke=style['stroke'],
                stroke_width=style['stroke_width'] * 1.5
            )

            # Draw window panes
            num_panes = max(1, min(int(height / 30), 4))
            pane_height = height / num_panes

            for i in range(num_panes):
                # Horizontal dividers
                if i > 0:
                    pane_y = y + i * pane_height
                    exporter.add_line(
                        x - width / 2, pane_y,
                        x + width / 2, pane_y,
                        stroke=style['stroke'],
                        stroke_width=style['stroke_width'] * 0.7
                    )

                # Vertical divider for each pane
                mid_x = x - width / 4
                exporter.add_line(
                    mid_x, y + i * pane_height,
                    mid_x, y + (i + 1) * pane_height,
                    stroke=style['stroke'],
                    stroke_width=style['stroke_width'] * 0.7
                )

    def _render_furniture(self, furniture_items, exporter, offset_x=0, offset_y=0):
        """
        Render furniture items

        Args:
            furniture_items: List of Furniture objects
            exporter: SVGExporter
            offset_x: X-offset for positioning
            offset_y: Y-offset for positioning
        """
        # Sort furniture by type for consistent rendering
        sorted_furniture = sorted(furniture_items, key=lambda f: f.furniture_type)

        for furniture in sorted_furniture:
            # Skip rendering if furniture has zero dimensions
            if furniture.width <= 0 or furniture.height <= 0:
                print(
                    f"Warning: Furniture '{furniture.id}' has invalid dimensions: {furniture.width}x{furniture.height}")
                continue

            style = self.style_manager.get_furniture_style(furniture.furniture_type)

            # Convert to pixels with scaling
            x = furniture.x * self.scale + offset_x
            y = furniture.y * self.scale + offset_y
            width = max(10, furniture.width * self.scale)  # Ensure minimum visibility
            height = max(10, furniture.height * self.scale)  # Ensure minimum visibility

            print(f"Rendering furniture '{furniture.id}' at ({x}, {y}) with size {width}x{height}")

            # Apply rotation if specified
            rotation = furniture.rotation if hasattr(furniture, 'rotation') else 0

            # If rotation is applied, we need to transform the drawing
            transform = ""
            if rotation != 0:
                # Calculate center of furniture for rotation
                center_x = x + width / 2
                center_y = y + height / 2
                transform = f'transform="rotate({rotation} {center_x} {center_y})"'

            # Render based on furniture type with improved styling
            if furniture.furniture_type == "BED":
                # Enhanced bed rendering
                # Main bed rectangle
                bed_element = f'<g {transform}>'

                # Base rectangle
                bed_element += f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
                bed_element += f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"]}" />'

                # Mattress with rounded corners
                mattress_x = x + width * 0.05
                mattress_y = y + height * 0.1
                mattress_width = width * 0.9
                mattress_height = height * 0.8
                mattress_radius = min(mattress_width, mattress_height) * 0.1

                bed_element += f'<rect x="{mattress_x}" y="{mattress_y}" width="{mattress_width}" height="{mattress_height}" '
                bed_element += f'rx="{mattress_radius}" ry="{mattress_radius}" '
                bed_element += f'fill="#FFFFFF" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"] * 0.5}" />'

                # Pillows
                pillow_height = height * 0.2
                pillow_margin = width * 0.05
                pillow_width = (width - pillow_margin * 3) / 2
                pillow_radius = min(pillow_width, pillow_height) * 0.3

                # Left pillow
                bed_element += f'<rect x="{x + pillow_margin}" y="{y + pillow_margin}" '
                bed_element += f'width="{pillow_width}" height="{pillow_height}" '
                bed_element += f'rx="{pillow_radius}" ry="{pillow_radius}" '
                bed_element += f'fill="#F8F8F8" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"] * 0.5}" />'

                # Right pillow
                bed_element += f'<rect x="{x + pillow_width + pillow_margin * 2}" y="{y + pillow_margin}" '
                bed_element += f'width="{pillow_width}" height="{pillow_height}" '
                bed_element += f'rx="{pillow_radius}" ry="{pillow_radius}" '
                bed_element += f'fill="#F8F8F8" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"] * 0.5}" />'

                # Bed frame headboard
                bed_element += f'<rect x="{x - width * 0.03}" y="{y - height * 0.03}" '
                bed_element += f'width="{width * 1.06}" height="{height * 0.15}" '
                bed_element += f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"]}" />'

                bed_element += '</g>'
                exporter.elements.append(bed_element)

            elif furniture.furniture_type == "TABLE":
                # Use existing table rendering but with improved styling
                exporter.add_table(
                    x, y, width, height,
                    fill=style['fill'],
                    stroke=style['stroke'],
                    stroke_width=style['stroke_width']
                )

            elif furniture.furniture_type == "CHAIR":
                # Use existing chair rendering but with improved styling
                exporter.add_chair(
                    x, y, width, height,
                    fill=style['fill'],
                    stroke=style['stroke'],
                    stroke_width=style['stroke_width']
                )

            elif furniture.furniture_type == "STAIRS":
                # Use existing stairs rendering but with improved styling
                exporter.add_stairs(
                    x, y, width, height,
                    fill=style['fill'],
                    stroke=style['stroke'],
                    stroke_width=style['stroke_width']
                )

            elif furniture.furniture_type == "ELEVATOR":
                # Use existing elevator rendering but with improved styling
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