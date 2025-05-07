import math


class SVGExporter:
    """
    Handles exporting floor plans to SVG format
    """

    def __init__(self, width, height):
        """
        Initialize the SVG exporter

        Args:
            width: Width of the SVG canvas in pixels
            height: Height of the SVG canvas in pixels
        """
        self.width = width
        self.height = height
        self.elements = []

    def add_rectangle(self, x, y, width, height, fill="#FFFFFF", stroke="#000000", stroke_width=1):
        """
        Add a rectangle to the SVG

        Args:
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            width: Width of the rectangle
            height: Height of the rectangle
            fill: Fill color (hex code or name)
            stroke: Stroke color (hex code or name)
            stroke_width: Stroke width in pixels
        """
        element = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        element += f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
        self.elements.append(element)

    def add_line(self, x1, y1, x2, y2, stroke="#000000", stroke_width=1):
        """
        Add a line to the SVG

        Args:
            x1: X coordinate of the start point
            y1: Y coordinate of the start point
            x2: X coordinate of the end point
            y2: Y coordinate of the end point
            stroke: Stroke color (hex code or name)
            stroke_width: Stroke width in pixels
        """
        element = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        element += f'stroke="{stroke}" stroke-width="{stroke_width}" />'
        self.elements.append(element)

    def add_text(self, text, x, y, font_size=12, fill="#000000", text_anchor="middle"):
        """
        Add text to the SVG

        Args:
            text: Text content
            x: X coordinate of the text anchor point
            y: Y coordinate of the text anchor point
            font_size: Font size in pixels
            fill: Text color
            text_anchor: Text anchor position (start, middle, end)
        """
        element = f'<text x="{x}" y="{y}" font-size="{font_size}" fill="{fill}" '
        element += f'text-anchor="{text_anchor}" dominant-baseline="middle">{text}</text>'
        self.elements.append(element)

    def add_door_arc(self, x, y, width, height, direction, stroke="#000000", stroke_width=1):
        """
        Add a door arc to represent a door

        Args:
            x: X coordinate of the door position
            y: Y coordinate of the door position
            width: Width of the door
            height: Height of the door
            direction: Door opening direction (left, right, up, down)
            stroke: Stroke color
            stroke_width: Stroke width
        """
        if direction == "right":
            # Door opens to the right
            self.add_line(x, y, x, y + height, stroke=stroke, stroke_width=stroke_width)
            arc_path = f'M {x} {y} Q {x + width} {y + height / 2} {x} {y + height}'
            element = f'<path d="{arc_path}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" />'
            self.elements.append(element)
        elif direction == "left":
            # Door opens to the left
            self.add_line(x + width, y, x + width, y + height, stroke=stroke, stroke_width=stroke_width)
            arc_path = f'M {x + width} {y} Q {x} {y + height / 2} {x + width} {y + height}'
            element = f'<path d="{arc_path}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" />'
            self.elements.append(element)
        elif direction == "up":
            # Door opens upward
            self.add_line(x, y + height, x + width, y + height, stroke=stroke, stroke_width=stroke_width)
            arc_path = f'M {x} {y + height} Q {x + width / 2} {y} {x + width} {y + height}'
            element = f'<path d="{arc_path}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" />'
            self.elements.append(element)
        elif direction == "down":
            # Door opens downward
            self.add_line(x, y, x + width, y, stroke=stroke, stroke_width=stroke_width)
            arc_path = f'M {x} {y} Q {x + width / 2} {y + height} {x + width} {y}'
            element = f'<path d="{arc_path}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" />'
            self.elements.append(element)

    def add_window(self, x, y, width, height, stroke="#000000", stroke_width=1):
        """
        Add a window representation

        Args:
            x: X coordinate of the window
            y: Y coordinate of the window
            width: Width of the window
            height: Height of the window
            stroke: Stroke color
            stroke_width: Stroke width
        """
        # For horizontal windows (width > height)
        if width > height:
            # Draw the main window line
            self.add_line(x, y, x + width, y, stroke=stroke, stroke_width=stroke_width)

            # Draw the mullions (vertical dividers)
            num_mullions = max(1, min(int(width / 15), 3))
            spacing = width / (num_mullions + 1)

            for i in range(1, num_mullions + 1):
                mullion_x = x + i * spacing
                self.add_line(mullion_x, y - height / 2, mullion_x, y + height / 2,
                              stroke=stroke, stroke_width=stroke_width / 2)
        else:
            # For vertical windows (height >= width)
            self.add_line(x, y, x, y + height, stroke=stroke, stroke_width=stroke_width)

            # Draw the mullions (horizontal dividers)
            num_mullions = max(1, min(int(height / 15), 3))
            spacing = height / (num_mullions + 1)

            for i in range(1, num_mullions + 1):
                mullion_y = y + i * spacing
                self.add_line(x - width / 2, mullion_y, x + width / 2, mullion_y,
                              stroke=stroke, stroke_width=stroke_width / 2)

    def add_bed(self, x, y, width, height, fill="#FFFFFF", stroke="#000000", stroke_width=1):
        """Add a bed representation"""
        # Main bed rectangle
        self.add_rectangle(x, y, width, height, fill=fill, stroke=stroke, stroke_width=stroke_width)

        # Pillows (assuming bed headboard is at the top)
        pillow_height = height * 0.2
        pillow_spacing = width * 0.05
        pillow_width = (width - pillow_spacing) / 2

        # Left pillow
        self.add_rectangle(
            x, y,
            pillow_width, pillow_height,
            fill="#EEEEEE", stroke=stroke, stroke_width=stroke_width / 2
        )

        # Right pillow
        self.add_rectangle(
            x + pillow_width + pillow_spacing, y,
            pillow_width, pillow_height,
            fill="#EEEEEE", stroke=stroke, stroke_width=stroke_width / 2
        )

        # Headboard
        headboard_height = height * 0.1
        self.add_rectangle(
            x - headboard_height / 2, y - headboard_height / 2,
            width + headboard_height, headboard_height,
            fill=fill, stroke=stroke, stroke_width=stroke_width
        )

    def add_table(self, x, y, width, height, fill="#FFFFFF", stroke="#000000", stroke_width=1):
        """Add a table representation"""
        # Main table rectangle
        self.add_rectangle(x, y, width, height, fill=fill, stroke=stroke, stroke_width=stroke_width)

        # Table legs - assuming they're 10% of table size
        leg_size = min(width, height) * 0.1

        # Top-left leg
        self.add_rectangle(
            x, y,
            leg_size, leg_size,
            fill=fill, stroke=stroke, stroke_width=stroke_width
        )

        # Top-right leg
        self.add_rectangle(
            x + width - leg_size, y,
            leg_size, leg_size,
            fill=fill, stroke=stroke, stroke_width=stroke_width
        )

        # Bottom-right leg
        self.add_rectangle(
            x + width - leg_size, y + height - leg_size,
            leg_size, leg_size,
            fill=fill, stroke=stroke, stroke_width=stroke_width
        )

        # Bottom-left leg
        self.add_rectangle(
            x, y + height - leg_size,
            leg_size, leg_size,
            fill=fill, stroke=stroke, stroke_width=stroke_width
        )

    def add_chair(self, x, y, width, height, fill="#FFFFFF", stroke="#000000", stroke_width=1):
        """Add a chair representation"""
        # Chair seat
        self.add_rectangle(x, y, width, height, fill=fill, stroke=stroke, stroke_width=stroke_width)

        # Chair back (assuming it's at the top)
        back_height = height * 0.3
        self.add_rectangle(
            x, y - back_height,
            width, back_height,
            fill=fill, stroke=stroke, stroke_width=stroke_width
        )

    def add_stairs(self, x, y, width, height, fill="#FFFFFF", stroke="#000000", stroke_width=1):
        """Add a stairs representation"""
        # Main stairs rectangle
        self.add_rectangle(x, y, width, height, fill=fill, stroke=stroke, stroke_width=stroke_width)

        # Stair steps
        num_steps = min(10, max(3, int(math.sqrt(width * height) / 5)))

        if width > height:
            # Horizontal stairs
            step_width = width / num_steps
            for i in range(num_steps):
                step_x = x + i * step_width
                self.add_line(
                    step_x, y,
                    step_x, y + height,
                    stroke=stroke, stroke_width=stroke_width / 2
                )
        else:
            # Vertical stairs
            step_height = height / num_steps
            for i in range(num_steps):
                step_y = y + i * step_height
                self.add_line(
                    x, step_y,
                    x + width, step_y,
                    stroke=stroke, stroke_width=stroke_width / 2
                )

        # Add a diagonal arrow to show direction
        arrow_path = f'M {x + width * 0.2} {y + height * 0.8} L {x + width * 0.8} {y + height * 0.2}'
        element = f'<path d="{arrow_path}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" />'
        self.elements.append(element)

        # Arrowhead
        arrow_head = f'M {x + width * 0.75} {y + height * 0.25} L {x + width * 0.8} {y + height * 0.2} L {x + width * 0.85} {y + height * 0.3}'
        element = f'<path d="{arrow_head}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" />'
        self.elements.append(element)

    def add_elevator(self, x, y, width, height, fill="#FFFFFF", stroke="#000000", stroke_width=1):
        """Add an elevator representation"""
        # Main elevator rectangle
        self.add_rectangle(x, y, width, height, fill=fill, stroke=stroke, stroke_width=stroke_width)

        # Cross in the middle
        self.add_line(
            x + width / 4, y + height / 2,
            x + width * 3 / 4, y + height / 2,
            stroke=stroke, stroke_width=stroke_width
        )
        self.add_line(
            x + width / 2, y + height / 4,
            x + width / 2, y + height * 3 / 4,
            stroke=stroke, stroke_width=stroke_width
        )

        # Outer square
        inner_margin = min(width, height) * 0.15
        self.add_rectangle(
            x + inner_margin, y + inner_margin,
            width - 2 * inner_margin, height - 2 * inner_margin,
            fill="none", stroke=stroke, stroke_width=stroke_width / 2
        )

    def save(self, filename):
        """
        Save the SVG to a file

        Args:
            filename: Output file path
        """
        # Create the SVG header
        svg = f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        svg += f'<svg width="{self.width}" height="{self.height}" '
        svg += 'xmlns="http://www.w3.org/2000/svg" '
        svg += 'xmlns:svg="http://www.w3.org/2000/svg">\n'

        # Add a background rectangle
        svg += f'  <rect width="{self.width}" height="{self.height}" fill="white" />\n'

        # Add all elements
        for element in self.elements:
            svg += f'  {element}\n'

        # Close the SVG
        svg += '</svg>'

        # Write to file
        with open(filename, 'w') as f:
            f.write(svg)

    def add_rounded_rectangle(self, x, y, width, height, radius, fill="#FFFFFF", stroke="#000000", stroke_width=1):
        """
        Add a rectangle with rounded corners to the SVG

        Args:
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            width: Width of the rectangle
            height: Height of the rectangle
            radius: Corner radius
            fill: Fill color (hex code or name)
            stroke: Stroke color (hex code or name)
            stroke_width: Stroke width in pixels
        """
        path = f'M {x + radius} {y} '
        path += f'L {x + width - radius} {y} '
        path += f'Q {x + width} {y} {x + width} {y + radius} '
        path += f'L {x + width} {y + height - radius} '
        path += f'Q {x + width} {y + height} {x + width - radius} {y + height} '
        path += f'L {x + radius} {y + height} '
        path += f'Q {x} {y + height} {x} {y + height - radius} '
        path += f'L {x} {y + radius} '
        path += f'Q {x} {y} {x + radius} {y} Z'

        element = f'<path d="{path}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
        self.elements.append(element)

    def add_grid(self, width, height, grid_size, stroke="#DDDDDD", stroke_width=0.5):
        """
        Add a grid to the SVG

        Args:
            width: Total width of the grid
            height: Total height of the grid
            grid_size: Size of grid cells
            stroke: Grid line color
            stroke_width: Grid line width
        """
        # Horizontal grid lines
        for y in range(0, int(height) + grid_size, grid_size):
            self.add_line(0, y, width, y, stroke=stroke, stroke_width=stroke_width)

        # Vertical grid lines
        for x in range(0, int(width) + grid_size, grid_size):
            self.add_line(x, 0, x, height, stroke=stroke, stroke_width=stroke_width)

    def add_dimension_line(self, x1, y1, x2, y2, offset=10, text=None, stroke="#000000", stroke_width=0.5,
                           font_size=10):
        """
        Add a dimension line with optional text

        Args:
            x1, y1: Start point
            x2, y2: End point
            offset: Offset from the measured object
            text: Text to display
            stroke: Line color
            stroke_width: Line width
            font_size: Font size for text
        """
        # Draw the dimension line
        self.add_line(x1, y1, x2, y2, stroke=stroke, stroke_width=stroke_width)

        # Draw end ticks
        tick_size = 5
        if x1 == x2:  # Vertical dimension
            self.add_line(x1 - tick_size, y1, x1 + tick_size, y1, stroke=stroke, stroke_width=stroke_width)
            self.add_line(x2 - tick_size, y2, x2 + tick_size, y2, stroke=stroke, stroke_width=stroke_width)
        else:  # Horizontal dimension
            self.add_line(x1, y1 - tick_size, x1, y1 + tick_size, stroke=stroke, stroke_width=stroke_width)
            self.add_line(x2, y2 - tick_size, x2, y2 + tick_size, stroke=stroke, stroke_width=stroke_width)

        # Add text if provided
        if text:
            text_x = (x1 + x2) / 2
            text_y = (y1 + y2) / 2
            self.add_text(text, text_x, text_y, font_size=font_size, fill=stroke, text_anchor="middle")