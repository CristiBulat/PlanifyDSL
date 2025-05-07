from DSL.Models.FloorPlan import FloorPlan
from DSL.Models.Room import Room
from DSL.Models.Wall import Wall
from DSL.Models.Door import Door
from DSL.Models.Window import Window
from DSL.Models.Furniture import Furniture
from DSL.Parsing.AST import AstNodeType


class RenderingVisitor:
    """
    Visitor that traverses an AST and converts it to model objects
    for rendering
    """

    def __init__(self):
        """Initialize the visitor"""
        self.floor_plan = FloorPlan()
        self.variables = {}  # Store variables for reference
        self.debug = True  # Enable debug output

    def visit_program(self, program_node):
        """
        Visit the program node (root of the AST)

        Args:
            program_node: ProgramNode from the AST

        Returns:
            FloorPlan object
        """
        if self.debug:
            print("Starting AST traversal...")

        for statement in program_node.statements:
            self.visit_statement(statement)

        if self.debug:
            print(f"Finished AST traversal. Created {len(self.floor_plan.rooms)} rooms, "
                  f"{len(self.floor_plan.doors)} doors, "
                  f"{len(self.floor_plan.windows)} windows, "
                  f"{len(self.floor_plan.furniture)} furniture items.")

        return self.floor_plan

    def visit_statement(self, statement):
        """
        Visit a statement node

        Args:
            statement: StatementNode from the AST
        """
        node_type = statement.get_type()

        if self.debug:
            print(f"Processing statement of type: {node_type}")

        if node_type == AstNodeType.HEADER_STATEMENT:
            self.visit_header(statement)
        elif node_type == AstNodeType.STRUCTURE:
            self.visit_structure(statement)
        elif node_type == AstNodeType.ASSIGNMENT_STATEMENT:
            self.visit_assignment(statement)
        elif node_type == AstNodeType.DECLARATION_STATEMENT:
            self.visit_declaration(statement)
        elif node_type == AstNodeType.IF_STATEMENT:
            self.visit_if_statement(statement)
        elif node_type == AstNodeType.FOR_STATEMENT:
            self.visit_for_statement(statement)
        elif node_type == AstNodeType.EXPRESSION_STATEMENT:
            self.visit_expression_statement(statement)
        else:
            if self.debug:
                print(f"Unknown statement type: {node_type}")

    def visit_header(self, header_node):
        """
        Visit a header statement

        Args:
            header_node: HeaderStatementNode from the AST
        """
        if self.debug:
            print(f"Processing header with dimensions: {header_node.width} x {header_node.height}")

        self.floor_plan.set_header(header_node.width, header_node.height)

    def visit_structure(self, structure_node):
        """
        Visit a structure statement (Room, Wall, etc.)

        Args:
            structure_node: StructureStatementNode from the AST
        """
        structure_type = structure_node.structure_type

        if self.debug:
            print(f"Processing structure of type: {structure_type}")
            print(f"Number of properties: {len(structure_node.properties)}")
            for i, prop in enumerate(structure_node.properties):
                literal = prop.token.literal if hasattr(prop.token, 'literal') else 'Unknown'
                print(f"  Property {i}: {literal}")
                if hasattr(prop.value, 'token') and hasattr(prop.value.token, 'literal'):
                    print(f"    Value literal: {prop.value.token.literal}")
                if hasattr(prop.value, 'value'):
                    print(f"    Value: {prop.value.value}")
                elif hasattr(prop.value, 'elements') and len(prop.value.elements) > 0:
                    print(
                        f"    Elements: {[e.value if hasattr(e, 'value') else 'Unknown' for e in prop.value.elements]}")

        if structure_type == "ROOM":
            room = Room().from_dsl_structure(structure_node)
            if self.debug:
                print(f"Created room '{room.id}' at ({room.x}, {room.y}) with size {room.width}x{room.height}")
            self.floor_plan.add_room(room)

        elif structure_type == "WALL":
            wall = Wall().from_dsl_structure(structure_node)
            if self.debug:
                print(f"Created wall '{wall.id}' from ({wall.start_x}, {wall.start_y}) to ({wall.end_x}, {wall.end_y})")
            self.floor_plan.add_wall(wall)

        elif structure_type == "DOOR":
            door = Door().from_dsl_structure(structure_node)
            if self.debug:
                print(f"Created door '{door.id}' at ({door.x}, {door.y}) with size {door.width}x{door.height}")
            self.floor_plan.add_door(door)

        elif structure_type == "WINDOW":
            window = Window().from_dsl_structure(structure_node)
            if self.debug:
                print(
                    f"Created window '{window.id}' at ({window.x}, {window.y}) with size {window.width}x{window.height}")
            self.floor_plan.add_window(window)

        elif structure_type in ["BED", "TABLE", "CHAIR", "STAIRS", "ELEVATOR"]:
            furniture = Furniture.create_from_structure(structure_node)
            if self.debug:
                print(
                    f"Created furniture '{furniture.id}' of type {structure_type} at ({furniture.x}, {furniture.y}) with size {furniture.width}x{furniture.height}")
            self.floor_plan.add_furniture(furniture)
        else:
            if self.debug:
                print(f"Unknown structure type: {structure_type}")

    def visit_assignment(self, assignment_node):
        """
        Visit an assignment statement

        Args:
            assignment_node: AssignmentStatementNode from the AST
        """
        var_name = assignment_node.var_name.value
        value = self.evaluate_expression(assignment_node.value)

        self.variables[var_name] = value

        if self.debug:
            print(f"Assigned variable '{var_name}' = {value}")

    def visit_declaration(self, declaration_node):
        """
        Visit a declaration statement

        Args:
            declaration_node: DeclarationStatementNode from the AST
        """
        var_name = declaration_node.var_name.value
        value = self.evaluate_expression(declaration_node.value)

        self.variables[var_name] = value

        if self.debug:
            print(f"Declared variable '{var_name}' of type {declaration_node.data_type} = {value}")

    def visit_if_statement(self, if_statement):
        """
        Visit an if statement

        Args:
            if_statement: IfStatementNode from the AST
        """
        condition_value = self.evaluate_expression(if_statement.condition)

        if self.debug:
            print(f"Evaluating if condition: {condition_value}")

        if condition_value:
            # Execute the consequence statements
            if self.debug:
                print(f"Condition is true, executing {len(if_statement.consequence)} consequence statements")
            for statement in if_statement.consequence:
                self.visit_statement(statement)
        else:
            # Execute the alternative statements (else block)
            if self.debug:
                print(f"Condition is false, executing {len(if_statement.alternative)} alternative statements")
            for statement in if_statement.alternative:
                self.visit_statement(statement)

    def visit_for_statement(self, for_statement):
        """
        Visit a for statement

        Args:
            for_statement: ForStatementNode from the AST
        """
        iterator_name = for_statement.iterator.value
        iterable = self.evaluate_expression(for_statement.iterable)

        if not isinstance(iterable, (list, tuple)):
            # If not a list, convert to one
            iterable = [iterable]

        if self.debug:
            print(f"Executing for loop with iterator '{iterator_name}' over {iterable}")

        for item in iterable:
            # Set the iterator variable
            self.variables[iterator_name] = item

            if self.debug:
                print(f"  Loop iteration: {iterator_name} = {item}")

            # Execute the loop body
            for statement in for_statement.body:
                self.visit_statement(statement)

    def visit_expression_statement(self, expression_statement):
        """
        Visit an expression statement

        Args:
            expression_statement: ExpressionStatementNode from the AST
        """
        result = self.evaluate_expression(expression_statement.expression)

        if self.debug:
            print(f"Evaluated expression statement result: {result}")

    def evaluate_expression(self, expression):
        """
        Evaluate an expression and return its value

        Args:
            expression: ExpressionNode from the AST

        Returns:
            Evaluated value of the expression
        """
        if expression is None:
            return None

        node_type = expression.get_type()

        if node_type == AstNodeType.INT_LITERAL:
            return expression.value

        elif node_type == AstNodeType.FLOAT_LITERAL:
            return expression.value

        elif node_type == AstNodeType.STRING_LITERAL:
            return expression.value

        elif node_type == AstNodeType.COLOR_LITERAL:
            return expression.value

        elif node_type == AstNodeType.IDENTIFIER:
            # Look up variable value
            if expression.value in self.variables:
                return self.variables[expression.value]
            else:
                if self.debug:
                    print(f"Warning: Variable '{expression.value}' not found, returning as string")
                return expression.value  # Return as string if not found

        elif node_type == AstNodeType.ARRAY_LITERAL:
            # Evaluate each element in the array
            return [self.evaluate_expression(elem) for elem in expression.elements]

        elif node_type == AstNodeType.MEASURE_LITERAL:
            # For simplicity, just return the numeric value
            # In a real implementation, you might want to handle units
            return self.evaluate_expression(expression.value_expr)

        elif node_type == AstNodeType.PREFIX_EXPRESSION:
            right = self.evaluate_expression(expression.right)

            if expression.op == "-":
                return -right
            elif expression.op == "!":
                return not right
            else:
                return right

        elif node_type == AstNodeType.INFIX_EXPRESSION:
            left = self.evaluate_expression(expression.left)
            right = self.evaluate_expression(expression.right)

            if expression.op == "+":
                return left + right
            elif expression.op == "-":
                return left - right
            elif expression.op == "*":
                return left * right
            elif expression.op == "/":
                return left / right if right != 0 else 0
            elif expression.op == "==":
                return left == right
            else:
                if self.debug:
                    print(f"Unknown operator: {expression.op}")
                return None

        elif node_type == AstNodeType.INDEX_EXPRESSION:
            array = self.evaluate_expression(expression.left)
            index = self.evaluate_expression(expression.index)

            if isinstance(array, (list, tuple)) and 0 <= index < len(array):
                return array[index]
            else:
                if self.debug:
                    print(f"Array index out of bounds or invalid: {array} at index {index}")
                return None

        elif node_type == AstNodeType.CALL_EXPRESSION:
            # Function calls not implemented yet
            if self.debug:
                print(f"Function calls not implemented yet")
            return None

        else:
            if self.debug:
                print(f"Unknown expression type: {node_type}")
            return None

    def extract_position_and_size(self, structure_node, element):
        """
        Extract position and size from a structure node

        Args:
            structure_node: Structure node from the AST
            element: Element object to update
        """
        for prop in structure_node.properties:
            prop_name = prop.name

            if prop_name == "POSITION_PROP":
                if hasattr(prop.value, 'elements') and len(prop.value.elements) >= 2:
                    try:
                        element.x = float(prop.value.elements[0].value)
                        element.y = float(prop.value.elements[1].value)
                        if self.debug:
                            print(f"Set position: ({element.x}, {element.y})")
                    except (ValueError, AttributeError) as e:
                        if self.debug:
                            print(f"Error extracting position: {e}")

            elif prop_name == "SIZE_PROP":
                if hasattr(prop.value, 'value_expr') and hasattr(prop.value, 'unit'):
                    # Handle measure literal
                    try:
                        size_value = float(prop.value.value_expr.value)
                        # For simplicity, make width = height for single size value
                        element.width = size_value
                        element.height = size_value
                        if self.debug:
                            print(f"Set size from measure: {size_value}x{size_value}")
                    except (ValueError, AttributeError) as e:
                        if self.debug:
                            print(f"Error extracting measure size: {e}")
                elif hasattr(prop.value, 'elements') and len(prop.value.elements) >= 2:
                    # Handle array like [width, height]
                    try:
                        element.width = float(prop.value.elements[0].value)
                        element.height = float(prop.value.elements[1].value)
                        if self.debug:
                            print(f"Set size from array: {element.width}x{element.height}")
                    except (ValueError, AttributeError) as e:
                        if self.debug:
                            print(f"Error extracting array size: {e}")

            elif prop_name == "WIDTH_PROP":
                if hasattr(prop.value, 'value'):
                    try:
                        element.width = float(prop.value.value)
                        if self.debug:
                            print(f"Set width: {element.width}")
                    except (ValueError, AttributeError) as e:
                        if self.debug:
                            print(f"Error extracting width: {e}")

            elif prop_name == "HEIGHT_PROP":
                if hasattr(prop.value, 'value'):
                    try:
                        element.height = float(prop.value.value)
                        if self.debug:
                            print(f"Set height: {element.height}")
                    except (ValueError, AttributeError) as e:
                        if self.debug:
                            print(f"Error extracting height: {e}")

            # Add more extraction logic as needed