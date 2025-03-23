from enum import Enum


class AstNodeType(Enum):
    PROGRAM = "Program"
    ASSIGNMENT_STATEMENT = "AssignmentStatement"
    DECLARATION_STATEMENT = "DeclarationStatement"
    EXPRESSION_STATEMENT = "ExpressionStatement"
    HEADER_STATEMENT = "HeaderStatement"
    STRUCTURE = "Structure"
    PROPERTY = "Property"
    PREFIX_EXPRESSION = "PrefixExpression"
    INFIX_EXPRESSION = "InfixExpression"
    INDEX_EXPRESSION = "IndexExpression"
    CALL_EXPRESSION = "CallExpression"
    IDENTIFIER = "Identifier"
    INT_LITERAL = "IntLiteral"
    FLOAT_LITERAL = "FloatLiteral"
    MEASURE_LITERAL = "MeasureLiteral"
    COLOR_LITERAL = "ColorLiteral"
    ARRAY_LITERAL = "ArrayLiteral"
    STRING_LITERAL = "StringLiteral"
    IF_STATEMENT = "IfStatement"
    FOR_STATEMENT = "ForStatement"


# Base Node class
class Node:
    def __init__(self, token):
        self.token = token

    def token_literal(self):
        return self.token.literal

    def get_type(self):
        pass

    def to_string(self):
        pass


# Statement Node base class
class StatementNode(Node):
    def __init__(self, token):
        super().__init__(token)


# Expression Node base class
class ExpressionNode(Node):
    def __init__(self, token):
        super().__init__(token)


# Root Node
class ProgramNode(Node):
    def __init__(self, token):
        super().__init__(token)
        self.statements = []

    def get_type(self):
        return AstNodeType.PROGRAM

    def to_string(self):
        result = ""
        for i, stmt in enumerate(self.statements):
            result += stmt.to_string()
            if i < len(self.statements) - 1:
                result += "\n"
        return result


# Expressions

class IdentifierNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def get_type(self):
        return AstNodeType.IDENTIFIER

    def to_string(self):
        return self.value


class HeaderStatementNode(StatementNode):
    def __init__(self, token):
        super().__init__(token)
        self.width = 0
        self.height = 0

    def get_type(self):
        return AstNodeType.HEADER_STATEMENT

    def to_string(self):
        return f"# size: {self.width} x {self.height}"


class AssignmentStatementNode(StatementNode):
    def __init__(self, token):
        super().__init__(token)
        self.var_name = None
        self.value = None

    def get_type(self):
        return AstNodeType.ASSIGNMENT_STATEMENT

    def to_string(self):
        return f"{self.var_name.value} = {self.value.to_string()}"


class DeclarationStatementNode(StatementNode):
    def __init__(self, token):
        super().__init__(token)
        self.data_type = None
        self.var_name = None
        self.value = None

    def get_type(self):
        return AstNodeType.DECLARATION_STATEMENT

    def to_string(self):
        return f"{self.data_type} {self.var_name.value} = {self.value.to_string()}"


class ExpressionStatementNode(StatementNode):
    def __init__(self, token):
        super().__init__(token)
        self.expression = None

    def get_type(self):
        return AstNodeType.EXPRESSION_STATEMENT

    def to_string(self):
        return f"{self.expression.to_string()};"


class PropertyNode(ExpressionNode):
    def __init__(self, token, name):
        super().__init__(token)
        self.name = name
        self.value = None

    def get_type(self):
        return AstNodeType.PROPERTY

    def to_string(self):
        return f"\t{self.name}: {self.value.to_string()}"


class StructureStatementNode(StatementNode):
    def __init__(self, token, structure_type):
        super().__init__(token)
        self.structure_type = structure_type
        self.properties = []

    def get_type(self):
        return AstNodeType.STRUCTURE

    def to_string(self):
        result = f"{self.structure_type}(\n"
        for prop in self.properties:
            result += f"{prop.to_string()}\n"
        result += ")"
        return result


class IntegerLiteralNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def get_type(self):
        return AstNodeType.INT_LITERAL

    def to_string(self):
        return str(self.value)


class FloatLiteralNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def get_type(self):
        return AstNodeType.FLOAT_LITERAL

    def to_string(self):
        return str(self.value)


class MeasureLiteralNode(ExpressionNode):
    def __init__(self, token, value_expr, unit):
        super().__init__(token)
        self.value_expr = value_expr
        self.unit = unit

    def get_type(self):
        return AstNodeType.MEASURE_LITERAL

    def to_string(self):
        return f"{self.value_expr.to_string()}{self.unit}"


class ColorLiteralNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def get_type(self):
        return AstNodeType.COLOR_LITERAL

    def to_string(self):
        return self.token.literal


class StringLiteralNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def get_type(self):
        return AstNodeType.STRING_LITERAL

    def to_string(self):
        return f'"{self.value}"'


class ArrayLiteralNode(ExpressionNode):
    def __init__(self, token):
        super().__init__(token)
        self.elements = []

    def get_type(self):
        return AstNodeType.ARRAY_LITERAL

    def to_string(self):
        result = "{"
        for i, elem in enumerate(self.elements):
            result += elem.to_string()
            if i < len(self.elements) - 1:
                result += ", "
        result += "}"
        return result

class InfixExpressionNode(ExpressionNode):
    def __init__(self, token, op, left):
        super().__init__(token)
        self.op = op
        self.left = left
        self.right = None

    def get_type(self):
        return AstNodeType.INFIX_EXPRESSION

    def to_string(self):
        return f"({self.left.to_string()} {self.op} {self.right.to_string()})"


class PrefixExpressionNode(ExpressionNode):
    def __init__(self, token, op):
        super().__init__(token)
        self.op = op
        self.right = None

    def get_type(self):
        return AstNodeType.PREFIX_EXPRESSION

    def to_string(self):
        return f"({self.op}{self.right.to_string()})"


class IndexExpressionNode(ExpressionNode):
    def __init__(self, token, left):
        super().__init__(token)
        self.left = left
        self.index = None

    def get_type(self):
        return AstNodeType.INDEX_EXPRESSION

    def to_string(self):
        return f"{self.left.to_string()}[{self.index.to_string()}]"


class CallExpressionNode(ExpressionNode):
    def __init__(self, token, function):
        super().__init__(token)
        self.function = function
        self.arguments = []

    def get_type(self):
        return AstNodeType.CALL_EXPRESSION

    def to_string(self):
        result = f"{self.function.to_string()}("
        for i, arg in enumerate(self.arguments):
            if i > 0:
                result += ", "
            result += arg.to_string()
        result += ")"
        return result

class IfStatementNode(StatementNode):
    def __init__(self, token):
        super().__init__(token)
        self.condition = None
        self.consequence = []
        self.alternative = []

    def get_type(self):
        return AstNodeType.IF_STATEMENT

    def to_string(self):
        consequence_str = "\n".join(s.to_string() for s in self.consequence)
        alt = ""
        if self.alternative:
            alt_body = "\n".join(s.to_string() for s in self.alternative)
            alt = f"\nelse {{\n{alt_body}\n}}"
        condition_str = self.condition.to_string()
        if condition_str.startswith("(") and condition_str.endswith(")"):
            condition_str = condition_str[1:-1]
        return f"if ({condition_str}) {{\n{consequence_str}\n}}{alt}"


class ForStatementNode(StatementNode):
    def __init__(self, token):
        super().__init__(token)
        self.iterator = None
        self.iterable = None
        self.body = []

    def get_type(self):
        return AstNodeType.FOR_STATEMENT

    def to_string(self):
        body_str = "\n".join(s.to_string() for s in self.body)
        return f"for ({self.iterator.to_string()} in {self.iterable.to_string()}) {{\n{body_str}\n}}"