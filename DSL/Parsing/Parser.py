from .AST import *
from .Token import TokenType


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.peek_token = None

        # Initialize both tokens
        self.next_token()
        self.next_token()

        # Precedence levels for operators
        self.precedences = {
            TokenType.PLUS: 4,
            TokenType.MINUS: 4,
            TokenType.SLASH: 5,
            TokenType.ASTERISK: 5,
            TokenType.LBRACKET: 6,
            TokenType.EQUAL: 3,
        }

        # Error tracking
        self.errors = []

    def next_token(self):
        """Advance the current and peek tokens"""
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def current_token_is(self, token_type):
        """Check if current token is of given type"""
        return self.current_token.type == token_type

    def peek_token_is(self, token_type):
        """Check if peek token is of given type"""
        return self.peek_token.type == token_type

    def expect_peek(self, token_type):
        """Check if peek token is of expected type and advance if it is"""
        if self.peek_token_is(token_type):
            self.next_token()
            return True
        else:
            self.peek_error(token_type)
            return False

    def peek_error(self, token_type):
        """Report error when peek token is not of expected type"""
        error_msg = f"Expected next token to be {token_type}, got {self.peek_token.type} instead"
        self.errors.append(error_msg)

    def get_errors(self):
        """Return the list of errors"""
        return self.errors

    def current_precedence(self):
        """Get precedence of current token"""
        if self.current_token.type in self.precedences:
            return self.precedences[self.current_token.type]
        return 0

    def peek_precedence(self):
        """Get precedence of peek token"""
        if self.peek_token.type in self.precedences:
            return self.precedences[self.peek_token.type]
        return 0

    # Parsing methods
    def parse_program(self):
        """Parse the entire program"""
        program = ProgramNode(self.current_token)

        while not self.current_token_is(TokenType.END):
            stmt = self.parse_statement()
            if stmt:
                program.statements.append(stmt)
            self.next_token()

        return program

    def parse_statement(self):
        """Parse a statement based on token type"""
        if self.current_token.type == TokenType.IDENTIFIER:
            return self.parse_assignment_statement()
        elif self.current_token.type in TokenType.dataTypes:
            return self.parse_declaration_statement()
        elif self.current_token.type in TokenType.structures:
            return self.parse_structure_statement()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for_statement()
        else:
            return self.parse_expression_statement()

    def parse_assignment_statement(self):
        """Parse assignment: identifier = expression;"""
        stmt = AssignmentStatementNode(self.current_token)

        stmt.var_name = IdentifierNode(self.current_token, self.current_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()

        stmt.value = self.parse_expression()

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return stmt

    def parse_declaration_statement(self):
        """Parse declaration: type identifier = expression;"""
        stmt = DeclarationStatementNode(self.current_token)
        stmt.data_type = self.current_token.type

        if not self.expect_peek(TokenType.IDENTIFIER):
            return None

        stmt.var_name = IdentifierNode(self.current_token, self.current_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()

        stmt.value = self.parse_expression()

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return stmt

    def parse_structure_statement(self):
        stmt = StructureStatementNode(self.current_token, self.current_token.type)

        if not self.expect_peek(TokenType.LBRACE):  # Use expect_peek to advance if correct
            return None

        self.next_token()  # Move into the block, now on first property or `}`

        while not self.current_token_is(TokenType.RBRACE) and not self.current_token_is(TokenType.END):
            prop = self.parse_property()
            if prop:
                stmt.properties.append(prop)
            else:
                # Optional: recover if parsing fails by skipping one token
                self.next_token()
                continue

            self.next_token()  # Move to next property (or RBRACE)

        return stmt

    def parse_property(self):
        """Parse property within a structure"""
        if not (self.current_token.type in TokenType.roomProps or self.current_token.type == TokenType.IDENTIFIER):
            self.errors.append(f"Expected property name, got {self.current_token.type}")
            return None

        prop = PropertyNode(self.current_token, self.current_token.type)

        if not self.expect_peek(TokenType.COLON):
            return None

        self.next_token()

        prop.value = self.parse_expression()

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return prop

    def parse_expression_statement(self):
        """Parse expression statement"""
        stmt = ExpressionStatementNode(self.current_token)

        stmt.expression = self.parse_expression()

        if stmt.expression is None:
            return None

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return stmt

    def parse_expression(self, precedence=0):
        """Parse an expression with precedence climbing."""
        prefix = None

        # Handle prefix expressions (identifiers, literals, grouped expressions, etc.)
        if self.current_token.type == TokenType.IDENTIFIER:
            prefix = self.parse_identifier()
        elif self.current_token.type == TokenType.INT_LITERAL:
            prefix = self.parse_integer_literal()
        elif self.current_token.type == TokenType.FLOAT_LITERAL:
            prefix = self.parse_float_literal()
        elif self.current_token.type == TokenType.STRING_LITERAL:
            prefix = self.parse_string_literal()
        elif self.current_token.type == TokenType.COLOR_LITERAL:
            prefix = self.parse_color_literal()
        elif self.current_token.type == TokenType.LPAREN:
            prefix = self.parse_grouped_expression()
        elif self.current_token.type == TokenType.LBRACKET:
            prefix = self.parse_array_literal()
        elif self.current_token.type == TokenType.MINUS or self.current_token.type == TokenType.EXCLAM_MARK:
            prefix = self.parse_prefix_expression()
        else:
            # Handle unexpected tokens by creating a default expression node
            prefix = IdentifierNode(self.current_token, self.current_token.literal)

        # Handle measure literals (e.g., 500cm)
        if self.current_token.type in [TokenType.INT_LITERAL, TokenType.FLOAT_LITERAL] and \
                self.peek_token.type in TokenType.measureUnits:
            return self.parse_measure_literal_from_value(prefix)

        # Handle infix expressions with precedence climbing
        while not self.peek_token_is(TokenType.SEMICOLON) and precedence < self.peek_precedence():
            if self.peek_token.type == TokenType.PLUS or \
                    self.peek_token.type == TokenType.MINUS or \
                    self.peek_token.type == TokenType.SLASH or \
                    self.peek_token.type == TokenType.ASTERISK or \
                    self.peek_token.type == TokenType.EQUAL:  # Handle ==
                self.next_token()
                prefix = self.parse_infix_expression(prefix)
            elif self.peek_token.type == TokenType.LBRACKET:
                self.next_token()
                prefix = self.parse_index_expression(prefix)
            elif self.peek_token.type == TokenType.LPAREN:
                self.next_token()
                prefix = self.parse_call_expression(prefix)
            elif self.peek_token.type in TokenType.measureUnits and self.current_token.type in [TokenType.INT_LITERAL,
                                                                                                TokenType.FLOAT_LITERAL]:
                prefix = self.parse_measure_literal_from_value(prefix)
            else:
                break

        return prefix

    def parse_identifier(self):
        """Parse identifier"""
        return IdentifierNode(self.current_token, self.current_token.literal)

    def parse_integer_literal(self):
        """Parse integer literal"""
        try:
            value = int(self.current_token.literal)
            return IntegerLiteralNode(self.current_token, value)
        except ValueError:
            self.errors.append(f"Could not parse {self.current_token.literal} as integer")
            return None

    def parse_float_literal(self):
        """Parse float literal"""
        try:
            value = float(self.current_token.literal)
            return FloatLiteralNode(self.current_token, value)
        except ValueError:
            self.errors.append(f"Could not parse {self.current_token.literal} as float")
            return None

    def parse_string_literal(self):
        """Parse string literal"""
        return StringLiteralNode(self.current_token, self.current_token.literal)

    def parse_color_literal(self):
        """Parse color literal"""
        return ColorLiteralNode(self.current_token, self.current_token.literal)

    def parse_grouped_expression(self):
        """Parse grouped expression: (expression)"""
        self.next_token()

        exp = self.parse_expression()

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return exp

    def parse_array_literal(self):
        """Parse array literal: [expr1, expr2, ...]"""
        array = ArrayLiteralNode(self.current_token)

        array.elements = self.parse_expression_list(TokenType.RBRACKET)

        return array

    def parse_expression_list(self, end):
        elements = []

        self.next_token()

        expr = self.parse_expression()
        if expr is None:
            self.errors.append(f"Invalid expression in list at token: {self.current_token.type}")
            return None
        elements.append(expr)

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()  # skip comma
            self.next_token()  # move to next expression
            expr = self.parse_expression()
            if expr is None:
                self.errors.append(f"Invalid expression in list at token: {self.current_token.type}")
                return None
            elements.append(expr)

        if not self.expect_peek(end):
            self.errors.append(f"Expected end of list token {end}, got {self.peek_token.type}")
            return None

        return elements

    def parse_prefix_expression(self):
        """Parse prefix expression: operator expression"""
        expression = PrefixExpressionNode(self.current_token, self.current_token.type)

        self.next_token()

        expression.right = self.parse_expression(1)

        return expression

    def parse_infix_expression(self, left):
        """Parse infix expression: expression operator expression"""
        expression = InfixExpressionNode(self.current_token, self.current_token.type, left)

        precedence = self.current_precedence()
        self.next_token()

        expression.right = self.parse_expression(precedence)

        return expression

    def parse_index_expression(self, left):
        """Parse index expression: expression[expression]"""
        expression = IndexExpressionNode(self.current_token, left)

        self.next_token()
        expression.index = self.parse_expression()

        if not self.expect_peek(TokenType.RBRACKET):
            return None

        return expression

    def parse_call_expression(self, function):
        """Parse function call: expression(arg1, arg2, ...)"""
        expression = CallExpressionNode(self.current_token, function)

        expression.arguments = self.parse_expression_list(TokenType.RPAREN)

        return expression

    def parse_measure_literal(self):
        """Parse measure literal: value unit"""
        value_expr = self.parse_expression()

        if not self.peek_token_is(TokenType.MEASURE_UNIT_MM) and \
                not self.peek_token_is(TokenType.MEASURE_UNIT_CM) and \
                not self.peek_token_is(TokenType.MEASURE_UNIT_DM) and \
                not self.peek_token_is(TokenType.MEASURE_UNIT_M) and \
                not self.peek_token_is(TokenType.MEASURE_UNIT_KM):
            self.errors.append(f"Expected measure unit, got {self.peek_token.type}")
            return None

        self.next_token()

        return MeasureLiteralNode(self.current_token, value_expr, self.current_token.type)

    def parse_measure_literal_from_value(self, value_expr):
        """Parse measure literal when we already have the value expression"""
        self.next_token()  # Move to unit
        return MeasureLiteralNode(self.current_token, value_expr, self.current_token.type)

    def parse_if_statement(self):
        stmt = IfStatementNode(self.current_token)

        if not self.expect_peek(TokenType.LPAREN):
            return None

        self.next_token()  # Move to first token of condition
        stmt.condition = self.parse_expression()

        if not self.expect_peek(TokenType.RPAREN):
            return None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        self.next_token()  # Move into the block, now on first statement or `}`
        while not self.current_token_is(TokenType.RBRACE) and not self.current_token_is(TokenType.END):
            body_stmt = self.parse_statement()
            if body_stmt:
                stmt.consequence.append(body_stmt)
            self.next_token()

        if self.peek_token_is(TokenType.ELSE):
            self.next_token()  # Move to 'else'
            if not self.expect_peek(TokenType.LBRACE):
                return None
            self.next_token()  # Move into the else block, now on first statement or `}`
            while not self.current_token_is(TokenType.RBRACE) and not self.current_token_is(TokenType.END):
                alt_stmt = self.parse_statement()
                if alt_stmt:
                    stmt.alternative.append(alt_stmt)
                self.next_token()

        return stmt

    def parse_for_statement(self):
        stmt = ForStatementNode(self.current_token)

        if not self.expect_peek(TokenType.LPAREN):
            return None
        self.next_token()

        if self.current_token.type != TokenType.IDENTIFIER:
            self.errors.append(f"Expected identifier in for loop, got {self.current_token.type}")
            return None

        stmt.iterator = IdentifierNode(self.current_token, self.current_token.literal)

        if not self.expect_peek(TokenType.IN):
            return None
        self.next_token()

        stmt.iterable = self.parse_expression()

        if not self.expect_peek(TokenType.RPAREN):
            return None
        if not self.expect_peek(TokenType.LBRACE):
            return None

        self.next_token()
        while not self.current_token_is(TokenType.RBRACE):
            body_stmt = self.parse_statement()
            if body_stmt:
                stmt.body.append(body_stmt)
            self.next_token()

        return stmt
    def parse(self):
        """Main entry point for parsing"""
        program = self.parse_program()
        if len(self.errors) > 0:
            for error in self.errors:
                print(f"Parser error: {error}")
        return program