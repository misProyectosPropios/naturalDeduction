from lexer import TokenType
from logic import AND, BOTTOM, IMPLIES, NEG, OR, VAR


class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def consume(self, expected=None):
        token = self.current()
        if expected is not None and token.type != expected:
            raise ValueError(
                f"Expected {expected}, got {token.type}"
            )
        self.pos += 1
        return token
    
    def parse(self):
        result = self.parse_implication()
        self.consume(TokenType.EOF)
        return result
    
    def parse_implication(self):
        left = self.parse_or()
        if self.current().type == TokenType.IMPLIES:
            self.consume(TokenType.IMPLIES)
            right = self.parse_implication()
            return IMPLIES(left, right)
        return left
    
    def parse_or(self):
        node = self.parse_and()
        while self.current().type == TokenType.OR:
            self.consume(TokenType.OR)
            right = self.parse_and()
            node = OR(node, right)
        return node
    
    def parse_and(self):
        node = self.parse_not()
        while self.current().type == TokenType.AND:
            self.consume(TokenType.AND)
            right = self.parse_not()
            node = AND(node, right)
        return node

    def parse_not(self):
        if self.current().type == TokenType.NOT:
            self.consume(TokenType.NOT)
            return NEG(
                self.parse_not()
            )
        return self.parse_atom()

    def parse_atom(self):
        token = self.current()
        if token.type == TokenType.VAR:
            self.consume(TokenType.VAR)
            return VAR(token.value)
        if token.type == TokenType.BOTTOM:
            self.consume(TokenType.BOTTOM)
            return BOTTOM()
        if token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            expr = self.parse_implication()
            self.consume(TokenType.RPAREN)
            return expr
        raise ValueError(
            f"Unexpected token {token.type}"
        )