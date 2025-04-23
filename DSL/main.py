# Import the components
from DSL.Parsing.Lexer import Lexer
from DSL.Parsing.Parser import Parser
from DSL.Visitors.RenderingVisitor import RenderingVisitor
from DSL.Rendering.Renderer import Renderer
import os


def ensure_dir(directory):
    """Make sure the output directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    # Sample input in the domain-specific language
    input_text = """
    # size: 1000 x 800

    Room {
        id: "living_room";
        label: "Living Room";
        size: 1000cm;
        position: [0, 0];
    }

    Room {
        id: "bathroom";
        label: "Bathroom";
        size: [300, 300];
        position: [700, 300];
    }

    Room {
        id: "kitchen";
        label: "kitchen";
        size: [200, 200];
        position: [0, 400];
    }

    Room {
        id: "guest_room";
        label: "Guest Room";
        size: [400, 350];
        position: [550, 0];
    }

    // Doors
    Door {
        id: "main_door";
        position: [350, 750];
        width: 100;
        height: 20;
        direction: "up";
    }

    Door {
        id: "kitchen_door";
        position: [230, 580];
        width: 80;
        height: 20;
        direction: "down";
    }

    Door {
        id: "bathroom_door";
        position: [600, 450];
        width: 20;
        height: 80;
        direction: "left";
    }

    // Windows
    Window {
        id: "living_window";
        position: [350, 0];
        width: 150;
        height: 20;
    }

    Window {
        id: "kitchen_window";
        position: [0, 500];
        width: 20;
        height: 100;
    }

    Window {
        id: "bathroom_window";
        position: [950, 450];
        width: 20;
        height: 100;
    }

    Window {
        id: "guest_window";
        position: [800, 0];
        width: 100;
        height: 20;
    }

    // Furniture
    Bed {
        id: "guest_bed";
        position: [600, 100];
        width: 150;
        height: 200;
    }

    Table {
        id: "dining_table";
        position: [300, 300];
        width: 150;
        height: 120;
    }

    Chair {
        id: "chair1";
        position: [270, 270];
        width: 40;
        height: 40;
    }

    Chair {
        id: "chair2";
        position: [440, 270];
        width: 40;
        height: 40;
    }

    Chair {
        id: "chair3";
        position: [270, 410];
        width: 40;
        height: 40;
    }

    Chair {
        id: "chair4";
        position: [440, 410];
        width: 40;
        height: 40;
    }

    // Adding stairs and elevator
    Stairs {
        id: "main_stairs";
        position: [150, 450];
        width: 100;
        height: 150;
    }

    Elevator {
        id: "main_elevator";
        position: [150, 150];
        width: 80;
        height: 80;
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

    # Ensure output directory exists
    ensure_dir("output")

    # Render the floor plan to SVG
    renderer = Renderer(scale=10)
    renderer.render(floor_plan, "output/floor_plan.svg")

    print("Floor plan rendered successfully to 'output/floor_plan.svg'")

    # Print the AST as a string if needed
    # print("Parsed program:")
    # print(program.to_string())


if __name__ == "__main__":
    main()