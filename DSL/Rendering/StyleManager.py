class StyleManager:
    """
    Manages styles for different elements in the floor plan
    """

    def __init__(self):
        """Initialize default styles"""
        self.default_room_style = {
            'fill': '#FFFFFF',
            'stroke': '#000000',
            'stroke_width': 2,
            'font_size': 14,
            'text_color': '#000000'
        }

        self.default_wall_style = {
            'stroke': '#000000',
            'stroke_width': 3
        }

        self.default_door_style = {
            'stroke': '#000000',
            'stroke_width': 1
        }

        self.default_window_style = {
            'stroke': '#000000',
            'stroke_width': 1
        }

        self.furniture_styles = {
            'BED': {
                'fill': '#EFEFEF',
                'stroke': '#000000',
                'stroke_width': 1
            },
            'TABLE': {
                'fill': '#DDDDDD',
                'stroke': '#000000',
                'stroke_width': 1
            },
            'CHAIR': {
                'fill': '#CCCCCC',
                'stroke': '#000000',
                'stroke_width': 1
            },
            'STAIRS': {
                'fill': '#DDDDDD',
                'stroke': '#000000',
                'stroke_width': 1
            },
            'ELEVATOR': {
                'fill': '#BBBBBB',
                'stroke': '#000000',
                'stroke_width': 1
            }
        }

        # Room styles based on room type
        self.room_styles = {
            'kitchen': {
                'fill': '#F0F8FF',  # Light blue
                'text_color': '#0000AA'
            },
            'bathroom': {
                'fill': '#E0FFFF',  # Light cyan
                'text_color': '#008B8B'
            },
            'bedroom': {
                'fill': '#FFF0F5',  # Lavender blush
                'text_color': '#8B008B'
            },
            'living': {
                'fill': '#F0FFF0',  # Honeydew
                'text_color': '#006400'
            },
            'dining': {
                'fill': '#FFF5EE',  # Seashell
                'text_color': '#8B4513'
            },
            'guest': {
                'fill': '#F0FFFF',  # Azure
                'text_color': '#4682B4'
            }
        }

    def get_room_style(self, room):
        """
        Get style for a room based on its type

        Args:
            room: Room object

        Returns:
            Dictionary with style properties
        """
        # Start with default style
        style = self.default_room_style.copy()

        # If room has specific room type, apply that style
        if room.label:
            label_lower = room.label.lower()

            # Check if any room style key is in the label
            for key, room_style in self.room_styles.items():
                if key in label_lower:
                    style.update(room_style)
                    break

        # If room has specific style properties, override defaults
        if hasattr(room, 'color') and room.color:
            style['fill'] = room.color

        if hasattr(room, 'border_color') and room.border_color:
            style['stroke'] = room.border_color

        if hasattr(room, 'border_width') and room.border_width:
            style['stroke_width'] = room.border_width

        return style

    def get_wall_style(self):
        """
        Get style for walls

        Returns:
            Dictionary with style properties
        """
        return self.default_wall_style.copy()

    def get_door_style(self):
        """
        Get style for doors

        Returns:
            Dictionary with style properties
        """
        return self.default_door_style.copy()

    def get_window_style(self):
        """
        Get style for windows

        Returns:
            Dictionary with style properties
        """
        return self.default_window_style.copy()

    def get_furniture_style(self, furniture_type):
        """
        Get style for furniture based on type

        Args:
            furniture_type: Type of furniture (e.g., BED, TABLE)

        Returns:
            Dictionary with style properties
        """
        if furniture_type in self.furniture_styles:
            return self.furniture_styles[furniture_type].copy()
        else:
            # Default style if type not found
            return {
                'fill': '#EEEEEE',
                'stroke': '#000000',
                'stroke_width': 1
            }