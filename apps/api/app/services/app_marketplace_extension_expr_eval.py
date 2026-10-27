"""Expression Evaluator — safe recursive descent parser for math/logic expressions.

Implements:
- Tokenizer: numbers, operators, parentheses, variables, functions
- Recursive descent parser: respects operator precedence
- Operators: +, -, *, /, %, **, ==, !=, <, >, <=, >=, and, or, not
- Built-in functions: min, max, abs, round, len, if
- Variable substitution from context
- NO eval/exec — completely safe
"""
from __future__ import annotations
import re
import math


class ExprError(Exception):
    pass


# Token types
class T:
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENT = "IDENT"
    OP = "OP"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA = "COMMA"
    EOF = "EOF"


TOKEN_RE = re.compile(r'''
    (\d+\.?\d*) |       # numbers
    ("(?:[^"\\]|\\.)*") | # strings
    (and|or|not) |       # logical ops (must be before ident)
    ([a-zA-Z_]\w*) |     # identifiers
    (==|!=|<=|>=|[+\-*/%<>]) | # operators
    (\*\*) |             # power
    (\() | (\)) | (,) |  # parens, comma
    (\s+)                # whitespace (skip)
''', re.VERBOSE)

BUILTIN_FNS = {"min", "max", "abs", "round", "len", "if", "int", "float"}


class ExprEvaluatorService:
    def __init__(self):
        self._functions: dict[str, callable] = {
            "min": lambda args: min(args),
            "max": lambda args: max(args),
            "abs": lambda args: abs(args[0]),
            "round": lambda args: round(args[0], int(args[1]) if len(args) > 1 else 0),
            "len": lambda args: len(args[0]) if isinstance(args[0], (str, list)) else 0,
            "int": lambda args: int(args[0]),
            "float": lambda args: float(args[0]),
            "if": lambda args: args[1] if args[0] else (args[2] if len(args) > 2 else None),
        }

    def evaluate(self, expression: str, context: dict | None = None) -> object:
        """Evaluate an expression with optional variable context."""
        tokens = self._tokenize(expression)
        parser = _Parser(tokens, context or {}, self._functions)
        result = parser.parse_expr()
        if parser.pos < len(parser.tokens) and parser.tokens[parser.pos][0] != T.EOF:
            raise ExprError(f"Unexpected token: {parser.tokens[parser.pos]}")
        return result

    def _tokenize(self, expr: str) -> list[tuple]:
        tokens = []
        for m in TOKEN_RE.finditer(expr):
            if m.group(1):  # number
                val = float(m.group(1)) if '.' in m.group(1) else int(m.group(1))
                tokens.append((T.NUMBER, val))
            elif m.group(2):  # string
                tokens.append((T.STRING, m.group(2)[1:-1]))
            elif m.group(3):  # logical op
                tokens.append((T.OP, m.group(3)))
            elif m.group(4):  # identifier
                tokens.append((T.IDENT, m.group(4)))
            elif m.group(5):  # operator
                tokens.append((T.OP, m.group(5)))
            elif m.group(6):  # **
                tokens.append((T.OP, "**"))
            elif m.group(7):
                tokens.append((T.LPAREN, "("))
            elif m.group(8):
                tokens.append((T.RPAREN, ")"))
            elif m.group(9):
                tokens.append((T.COMMA, ","))
            # skip whitespace
        tokens.append((T.EOF, None))
        return tokens


class _Parser:
    def __init__(self, tokens, context, functions):
        self.tokens = tokens
        self.pos = 0
        self.context = context
        self.functions = functions

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (T.EOF, None)

    def consume(self, expected_type=None):
        tok = self.peek()
        if expected_type and tok[0] != expected_type:
            raise ExprError(f"Expected {expected_type}, got {tok}")
        self.pos += 1
        return tok

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek() == (T.OP, "or"):
            self.consume()
            right = self.parse_and()
            left = bool(left) or bool(right)
        return left

    def parse_and(self):
        left = self.parse_comparison()
        while self.peek() == (T.OP, "and"):
            self.consume()
            right = self.parse_comparison()
            left = bool(left) and bool(right)
        return left

    def parse_comparison(self):
        left = self.parse_add()
        ops = {"==", "!=", "<", ">", "<=", ">="}
        while self.peek()[0] == T.OP and self.peek()[1] in ops:
            op = self.consume()[1]
            right = self.parse_add()
            if op == "==": left = left == right
            elif op == "!=": left = left != right
            elif op == "<": left = left < right
            elif op == ">": left = left > right
            elif op == "<=": left = left <= right
            elif op == ">=": left = left >= right
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek()[0] == T.OP and self.peek()[1] in ("+", "-"):
            op = self.consume()[1]
            right = self.parse_mul()
            left = left + right if op == "+" else left - right
        return left

    def parse_mul(self):
        left = self.parse_power()
        while self.peek()[0] == T.OP and self.peek()[1] in ("*", "/", "%"):
            op = self.consume()[1]
            right = self.parse_power()
            if op == "*": left = left * right
            elif op == "/":
                if right == 0: raise ExprError("Division by zero")
                left = left / right
            elif op == "%": left = left % right
        return left

    def parse_power(self):
        left = self.parse_unary()
        if self.peek() == (T.OP, "**"):
            self.consume()
            right = self.parse_unary()
            left = left ** right
        return left

    def parse_unary(self):
        if self.peek() == (T.OP, "-"):
            self.consume()
            return -self.parse_unary()
        if self.peek() == (T.OP, "not"):
            self.consume()
            return not self.parse_unary()
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok[0] == T.NUMBER:
            self.consume()
            return tok[1]
        if tok[0] == T.STRING:
            self.consume()
            return tok[1]
        if tok[0] == T.LPAREN:
            self.consume()
            val = self.parse_expr()
            self.consume(T.RPAREN)
            return val
        if tok[0] == T.IDENT:
            name = tok[1]
            self.consume()
            # Function call
            if self.peek()[0] == T.LPAREN and name in self.functions:
                self.consume()  # (
                args = []
                if self.peek()[0] != T.RPAREN:
                    args.append(self.parse_expr())
                    while self.peek()[0] == T.COMMA:
                        self.consume()
                        args.append(self.parse_expr())
                self.consume(T.RPAREN)
                return self.functions[name](args)
            # Variable
            if name in self.context:
                return self.context[name]
            raise ExprError(f"Unknown variable: {name}")
        raise ExprError(f"Unexpected: {tok}")
