"""
Loft Language -- Lexer
=======================

The lexer (tokenizer) is the first stage of the Loft interpreter pipeline.
It reads raw Loft source code and converts it into a flat stream of
Token objects that the Week 2 parser will consume.

Pipeline: source code -> [Lexer] -> tokens -> [Parser] -> AST -> [Evaluator] -> result

Run this file directly to see a demo:
    python lexer.py
"""

from enum import Enum, auto


class TokenType(Enum):
    # Literals
    INTEGER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords
    LET = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    END = auto()
    PRINT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    TRUE = auto()
    FALSE = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()      # =
    EQEQ = auto()     # ==
    NEQ = auto()      # !=
    LT = auto()       # <
    GT = auto()       # >
    LE = auto()       # <=
    GE = auto()       # >=

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    NEWLINE = auto()
    EOF = auto()


KEYWORDS = {
    "let": TokenType.LET,
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "else": TokenType.ELSE,
    "end": TokenType.END,
    "print": TokenType.PRINT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

_SIMPLE_SYMBOLS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
}

_ESCAPES = {
    "n": "\n",
    "t": "\t",
    '"': '"',
    "\\": "\\",
}


class Token:
    __slots__ = ("type", "value", "line", "column")

    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return (self.type, self.value) == (other.type, other.value)


class LexerError(Exception):
    """Raised for any malformed input so the caller can report a clean
    diagnostic instead of letting a raw Python traceback crash the program."""

    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")


class Lexer:
    """Converts Loft source text into a list of Tokens."""

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    # -- low-level cursor helpers ------------------------------------

    def _peek(self, offset=0):
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else None

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _emit(self, type_, value, line, column):
        self.tokens.append(Token(type_, value, line, column))

    def _error(self, message, line=None, column=None):
        raise LexerError(message, line if line is not None else self.line,
                          column if column is not None else self.column)

    # -- main entry point ----------------------------------------------

    def tokenize(self):
        while self.pos < len(self.source):
            ch = self._peek()

            if ch in " \t\r":
                self._advance()
                continue

            if ch == "#":
                self._skip_comment()
                continue

            if ch == "\n":
                line, col = self.line, self.column
                self._advance()
                self._emit(TokenType.NEWLINE, "\n", line, col)
                continue

            if ch.isdigit():
                self._read_integer()
                continue

            if ch == '"':
                self._read_string()
                continue

            if ch.isalpha() or ch == "_":
                self._read_word()
                continue

            if ch in _SIMPLE_SYMBOLS:
                line, col = self.line, self.column
                self._advance()
                self._emit(_SIMPLE_SYMBOLS[ch], ch, line, col)
                continue

            if ch in "=!<>":
                self._read_operator()
                continue

            self._error(f"Illegal character {ch!r}")

        self._emit(TokenType.EOF, None, self.line, self.column)
        return self.tokens

    # -- token readers ---------------------------------------------------

    def _skip_comment(self):
        while self._peek() is not None and self._peek() != "\n":
            self._advance()

    def _read_integer(self):
        line, col = self.line, self.column
        digits = []
        while self._peek() is not None and self._peek().isdigit():
            digits.append(self._advance())
        self._emit(TokenType.INTEGER, int("".join(digits)), line, col)

    def _read_string(self):
        line, col = self.line, self.column
        self._advance()  # consume opening quote
        chars = []
        while True:
            ch = self._peek()
            if ch is None or ch == "\n":
                self._error("Unterminated string literal", line, col)
            if ch == '"':
                self._advance()
                break
            if ch == "\\":
                self._advance()
                esc = self._peek()
                if esc not in _ESCAPES:
                    self._error(f"Unknown escape sequence '\\{esc}'")
                chars.append(_ESCAPES[esc])
                self._advance()
                continue
            chars.append(self._advance())
        self._emit(TokenType.STRING, "".join(chars), line, col)

    def _read_word(self):
        line, col = self.line, self.column
        chars = []
        while self._peek() is not None and (self._peek().isalnum() or self._peek() == "_"):
            chars.append(self._advance())
        text = "".join(chars)
        self._emit(KEYWORDS.get(text, TokenType.IDENTIFIER), text, line, col)

    def _read_operator(self):
        """Handles =, ==, !, !=, <, <=, >, >=."""
        line, col = self.line, self.column
        first = self._advance()
        if self._peek() == "=":
            self._advance()
            two_char = {"=": TokenType.EQEQ, "!": TokenType.NEQ,
                        "<": TokenType.LE, ">": TokenType.GE}
            self._emit(two_char[first], first + "=", line, col)
            return
        if first == "=":
            self._emit(TokenType.EQ, "=", line, col)
        elif first == "<":
            self._emit(TokenType.LT, "<", line, col)
        elif first == ">":
            self._emit(TokenType.GT, ">", line, col)
        else:  # bare '!' with no following '='
            self._error("Unexpected character '!' (did you mean '!='?)", line, col)


def tokenize(source):
    """Convenience wrapper: source string -> list[Token]."""
    return Lexer(source).tokenize()


if __name__ == "__main__":
    demo_source = '''# demo: area of a rectangle
let width = 6
let height = 3
let area = width * height
print area

let name = "Loft" + "Lang"
if area >= 10 and not (width == height) then
    print name
else
    print "small"
end
'''

    print("=== Tokens ===")
    for tok in tokenize(demo_source):
        print(tok)

    print("\n=== Illegal character handled gracefully ===")
    try:
        tokenize("let x = 5 @ 2")
    except LexerError as e:
        print(f"Caught cleanly: {e}")
