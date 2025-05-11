import os
import uuid
from typing import Dict, List, Any, Tuple

# Import DSL components
from DSL.Parsing.Lexer import Lexer
from DSL.Parsing.Parser import Parser
from DSL.Visitors.RenderingVisitor import RenderingVisitor
from DSL.Rendering.Renderer import Renderer
from DSL.Layout.LayoutManager import LayoutManager

from ..config import SVG_OUTPUT_DIR


class DSLService:
    """Service for processing DSL code and generating floor plans"""

    def __init__(self):
        """Initialize the DSL service"""
        # Ensure output directory exists
        self.SVG_OUTPUT_DIR = SVG_OUTPUT_DIR
        os.makedirs(self.SVG_OUTPUT_DIR, exist_ok=True)
        print(f"DSL Service initialized with output directory: {self.SVG_OUTPUT_DIR}")

    def process_dsl_code(self, dsl_code: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Process DSL code and generate a floor plan

        Args:
            dsl_code: DSL code to parse

        Returns:
            Tuple of (elements list, svg_path)
            - elements: List of floor plan elements in JSON format
            - svg_path: Path to the generated SVG file
        """
        try:
            print("Processing DSL code...")
            # Create the lexer and parser
            lexer = Lexer(dsl_code)
            parser = Parser(lexer)

            # Parse the input into an AST
            program = parser.parse()

            # Check for parsing errors
            if parser.errors:
                error_msg = "\n".join(parser.errors)
                raise ValueError(f"Parsing errors: {error_msg}")

            # Create the visitor to build the model
            visitor = RenderingVisitor()
            floor_plan = visitor.visit_program(program)

            # Apply layout optimization
            layout_manager = LayoutManager(floor_plan)
            optimized_floor_plan = layout_manager.optimize_layout()

            # Generate a unique filename for the SVG
            file_id = uuid.uuid4().hex[:8]
            svg_filename = os.path.join(self.SVG_OUTPUT_DIR, f"floor_plan_{file_id}.svg")

            # Render the floor plan to SVG
            renderer = Renderer(scale=10)
            renderer.enhanced_rendering = True
            renderer.use_room_labels = True
            renderer.show_dimensions = True
            renderer.enhanced_colors = True
            renderer.wall_thickness = 3
            renderer.render(optimized_floor_plan, svg_filename)

            print(f"Floor plan rendered to: {svg_filename}")

            # Convert floor plan to JSON format
            elements = self._floor_plan_to_json(optimized_floor_plan)

            return elements, svg_filename

        except Exception as e:
            print(f"Error processing DSL code: {str(e)}")
            raise Exception(f"Error processing DSL code: {str(e)}")

    def _floor_plan_to_json(self, floor_plan) -> List[Dict[str, Any]]:
        """
        Convert a floor plan object to JSON format for the frontend

        Args:
            floor_plan: FloorPlan object

        Returns:
            List of elements in JSON format
        """
        elements = []

        # Add rooms
        for room in floor_plan.rooms:
            room_json = {
                "id": room.id or f"room_{len(elements)}",
                "type": "room",
                "position": [room.x, room.y],
                "size": [room.width, room.height]
            }
            elements.append(room_json)

        # Add walls
        for wall in floor_plan.walls:
            wall_json = {
                "id": wall.id or f"wall_{len(elements)}",
                "type": "wall",
                "start": [wall.start_x, wall.start_y],
                "end": [wall.end_x, wall.end_y]
            }
            elements.append(wall_json)

        # Add doors
        for door in floor_plan.doors:
            door_json = {
                "id": door.id or f"door_{len(elements)}",
                "type": "door",
                "position": [door.x, door.y],
                "width": door.width,
                "height": door.height,
                "direction": door.direction
            }
            elements.append(door_json)

        # Add windows
        for window in floor_plan.windows:
            window_json = {
                "id": window.id or f"window_{len(elements)}",
                "type": "window",
                "position": [window.x, window.y],
                "width": window.width,
                "height": window.height
            }
            elements.append(window_json)

        # Add furniture
        for furniture in floor_plan.furniture:
            furniture_json = {
                "id": furniture.id or f"furniture_{len(elements)}",
                "type": furniture.furniture_type.lower(),
                "position": [furniture.x, furniture.y],
                "width": furniture.width,
                "height": furniture.height
            }
            elements.append(furniture_json)

        return elements