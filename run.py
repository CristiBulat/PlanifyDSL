#!/usr/bin/env python3
"""
Entry point for the Floor Plan DSL application.
This script should be run from the project root directory.
"""

import os
import sys

# Add the project root to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now we can import from DSL packages
from DSL.Parsing.Lexer import Lexer
from DSL.Parsing.Parser import Parser
from DSL.Visitors.RenderingVisitor import RenderingVisitor
from DSL.Rendering.Renderer import Renderer


def ensure_dir(directory):
    """Make sure the output directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def render_floor_plan(input_text, output_file):
    """
    Parse the DSL input and render the floor plan

    Args:
        input_text: DSL text input
        output_file: Path to save the output SVG
    """
    # Create the lexer and parser
    lexer = Lexer(input_text)
    parser = Parser(lexer)

    # Parse the input into an AST
    program = parser.parse()

    # Check for errors
    if parser.errors:
        print("Parsing errors:")
        for error in parser.errors:
            print(f"  {error}")
        return False

    # Create the visitor to build the model
    visitor = RenderingVisitor()
    floor_plan = visitor.visit_program(program)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        ensure_dir(output_dir)

    # Render the floor plan to SVG
    renderer = Renderer(scale=1)
    renderer.render(floor_plan, output_file)

    print(f"Floor plan rendered successfully to '{output_file}'")
    return True


def main():
    # Check for command line arguments
    if len(sys.argv) > 1:
        # If a file is specified, use that
        input_file = sys.argv[1]
        try:
            with open(input_file, 'r') as f:
                input_text = f.read()

            # Determine output file path
            if len(sys.argv) > 2:
                output_file = sys.argv[2]
            else:
                # Use the same name as input but with .svg extension
                base_name = os.path.splitext(input_file)[0]
                output_file = f"output/{os.path.basename(base_name)}.svg"

            render_floor_plan(input_text, output_file)

        except FileNotFoundError:
            print(f"Error: Could not find input file '{input_file}'")
            return
        except Exception as e:
            print(f"Error: {e}")
            return
    else:
        # Use the example from DSL/main.py
        from DSL.main import input_text
        render_floor_plan(input_text, "output/floor_plan.svg")


if __name__ == "__main__":
    main()