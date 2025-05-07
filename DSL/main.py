# Import the components
from DSL.Parsing.Lexer import Lexer
from DSL.Parsing.Parser import Parser
from DSL.Visitors.RenderingVisitor import RenderingVisitor
from DSL.Rendering.Renderer import Renderer
from DSL.Layout.LayoutManager import LayoutManager
import os


def ensure_dir(directory):
    """Make sure the output directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    # Sample input in the domain-specific language
    input_text = """
# size: 1000 x 1000

// Bedroom
Room {
    id: "bedroom";
    label: "Bedroom";
    size: [300, 250];
    position: [0, 0];
}


Room {
    id: "living";
    label: "Living-Room";
    size: [400, 300];
    position: [0, 250];
}


Room {
    id: "bathroom";
    label: "Bathroom";
    size: [200, 150];
    position: [300, 0];
}


Room {
    id: "kitchen";
    label: "kitchen";
    size: [300, 100];
    position: [300, 150];
}


Window {
    id: "window_east";
    position: [0, 100];
    width: 10;
    height: 40;
}

// Bed
Bed {
    id: "bed";
    position: [100, 10];
    width: 100;
    height: 150;
}

// Door
Door {
    id: "bedroom_door";
    position: [70, 250];
    width: 40;
    height: 15;
    direction: "up";
}

// Bedside Table
Table {
    id: "bedside_table";
    position: [25, 10];
    width: 50;
    height: 50;
}

Chair {
    id: "sofa";
    position: [35, 70];
    width: 30;
    height: 15;
}

Stairs {
    id: "stairs";
    position: [400, 400];
    width: 30;
    height: 15;tatust
}

Elevator {
    id: "stairs";
    position: [500, 500];
    width: 30;
    height: 15;
}


    """

    # Create the lexer and parser
    lexer = Lexer(input_text)
    parser = Parser(lexer)

    # Parse the input into an AST
    program = parser.parse()

    # Print any errors
    if parser.errors:
        print("Parsing errors:")
        for error in parser.errors:
            print(f"  {error}")
        return

    # Create the visitor to build the model
    visitor = RenderingVisitor()
    floor_plan = visitor.visit_program(program)

    # Apply layout optimization
    layout_manager = LayoutManager(floor_plan)
    optimized_floor_plan = layout_manager.optimize_layout()

    # Ensure output directory exists
    ensure_dir("output")

    # Render the floor plan to SVG using improved rendering
    renderer = Renderer(scale=10)


    # Create the lexer and parser
    lexer = Lexer(input_text)
    parser = Parser(lexer)

    # Parse the input into an AST
    program = parser.parse()

    # Print any errors
    if parser.errors:
        print("Parsing errors:")
        for error in parser.errors:
            print(f"  {error}")
        return

    # Create the visitor to build the model
    visitor = RenderingVisitor()
    floor_plan = visitor.visit_program(program)

    # Apply layout optimization
    layout_manager = LayoutManager(floor_plan)
    optimized_floor_plan = layout_manager.optimize_layout()

    # Ensure output directory exists
    ensure_dir("output")

    # Render the floor plan to SVG using improved rendering
    renderer = Renderer(scale=10)
    renderer.enhanced_rendering = True  # Enable enhanced rendering features
    renderer.use_room_labels = True
    renderer.show_dimensions = True
    renderer.enhanced_colors = True
    renderer.wall_thickness = 3
    renderer.render(optimized_floor_plan, "output/floor_plan.svg")

    print("Floor plan rendered successfully to 'output/floor_plan.svg'")

    # Print the AST as a string if needed
    # print("Parsed program:")
    # print(program.to_string())


if __name__ == "__main__":
    main()