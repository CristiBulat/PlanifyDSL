# Import the components
from Parsing.Lexer import Lexer
from Parsing.Parser import Parser

# Sample input in the domain-specific language
input_text = """
Room {
    id: "living_room";
    size: 500cm;
    position: [0, 0];
}

Wall {
    id: "north_wall";
    start: [0, 0];
    end_on_wall: [500cm, 0];
}

Door {
    id: "main_door";
    width: 90cm;
    height: 210cm;
    wall: "north_wall";
    position: 200cm;
}

for (item in [1, 2]) {
    Room {
        id: "test";
        size: 500cm;
    }
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

# Print the resulting program
if program:
    print("Parsed program:")
    print(program.to_string())