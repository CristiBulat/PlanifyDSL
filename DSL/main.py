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

if (id == "kitchen") {
    Room {
        id: "test_room";
        size: 300cm;
    }
} else {
    Room {
        id: "alternative_room";
        size: 400cm;
    }
}

for (i in [1, 2, 3]) {
    Room {
        id: "room_" + i;
        size: 200cm;
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