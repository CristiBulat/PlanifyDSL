import re
from .Token import Token, TokenType, look_up_ident


class Lexer:
    def __init__(self, input_str):
        self.input = input_str
        self.position = 0
        self.read_position = 0
        self.ch = ''
        self.line = 0
        self.col = 0
        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = '\0'
        else:
            self.ch = self.input[self.read_position]

        if self.ch == '\n':
            self.line += 1
            self.col = 0
        else:
            self.col += 1

        self.position = self.read_position
        self.read_position += 1

    def peek_char(self):
        return self.input[self.read_position] if self.read_position < len(self.input) else '\0'

    def seek(self, offset):
        self.col = offset
        self.read_position = offset
        self.ch = self.input[self.read_position] if self.read_position < len(self.input) else '\0'
        self.position = self.read_position
        self.read_position += 1

    def read_identifier(self):
        start = self.position
        while self.ch.isalpha() or self.ch == '_':
            self.read_char()
        return self.input[start: self.position]

    def read_number(self):
        start = self.position
        tok = Token("", "INT_LITERAL", self.line, self.col)

        while self.ch.isdigit():
            self.read_char()

        if self.ch == '.':
            self.read_char()
            while self.ch.isdigit():
                self.read_char()
            tok.type = "FLOAT_LITERAL"

        tok.literal = self.input[start:self.position]
        return tok

    def read_hex_code(self):
        start = self.position
        if self.ch == '#':
            self.read_char()
        while self.ch.isalnum():
            self.read_char()
        return self.input[start:self.position]

    def skip_whitespace(self):
        while self.ch in (' ', '\n', '\t', '\r'):
            self.read_char()
        if self.ch == '/' and self.peek_char() == '/':
            while self.ch != '\n' and self.ch != '\0':
                self.read_char()
            self.skip_whitespace()

    def set_input(self, input_str):
        self.input = input_str
        self.position = 0
        self.read_position = 0
        self.line = 0
        self.col = 0
        self.read_char()

    def next_token(self):
        self.skip_whitespace()
        tok = Token("", "ILLEGAL", self.line, self.col)

        single_char_tokens = {
            '=': "ASSIGN",
            '+': "PLUS",
            '-': "MINUS",
            '/': "SLASH",
            '*': "ASTERISK",
            ',': "COMMA",
            ';': "SEMICOLON",
            ':': "COLON",
            '(': "LPAREN",
            ')': "RPAREN",
            '{': "LBRACE",
            '}': "RBRACE",
            '[': "LBRACKET",
            ']': "RBRACKET",
            '!': "EXCLAM_MARK"
        }

        if self.ch in single_char_tokens:
            tok = Token(self.ch, single_char_tokens[self.ch], self.line, self.col)
            self.read_char()
        elif self.ch == '"':
            # Handle string literals
            start_pos = self.position
            self.read_char()  # Skip opening quote
            str_content = ""
            while self.ch != '"' and self.ch != '\0':
                str_content += self.ch
                self.read_char()

            if self.ch == '"':
                tok = Token(str_content, "STRING_LITERAL", self.line, self.col)
                self.read_char()  # Skip closing quote
            else:
                tok = Token(self.input[start_pos:self.position], "ILLEGAL", self.line, self.col)
                self.errors.append(f"Unterminated string literal at line {self.line}, column {self.col}")
        elif self.ch == '#':
            tok = Token(self.read_hex_code(), "COLOR_LITERAL", self.line, self.col)
            if len(tok.literal) not in (4, 7):
                tok.type = "ILLEGAL"
        elif self.ch.isalpha() or self.ch == '_':
            ident = self.read_identifier()
            # Look up keywords
            tok_type = look_up_ident(ident)
            tok = Token(ident, tok_type, self.line, self.col)
        elif self.ch.isdigit():
            tok = self.read_number()
        elif self.ch == '\0':
            tok = Token("", "END", self.line, self.col)
        else:
            tok = Token(self.ch, "ILLEGAL", self.line, self.col)
            self.read_char()

        return tok