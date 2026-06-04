from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    VAR = auto()
    IMPLIES = auto()
    OR = auto()
    AND = auto()
    NOT = auto()
    BOTTOM = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str | None = None

class Lexer:

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def current(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def advance(self):
        self.pos += 1

    def tokenize(self):
        tokens = []

        while self.current() is not None:

            c = self.current()

            if c.isspace():
                self.advance()
                continue

            # "P", "Q", "foo"
            if c == '"':
                self.advance()

                start = self.pos

                while self.current() is not None and self.current() != '"':
                    self.advance()

                if self.current() is None:
                    raise ValueError("Unterminated string")

                value = self.text[start:self.pos]

                self.advance()

                tokens.append(Token(TokenType.VAR, value))
                continue

            
            if c == '-':
                # ->
                if (
                    self.pos + 1 < len(self.text)
                    and self.text[self.pos + 1] == '>'
                ):
                    self.pos += 2
                    tokens.append(Token(TokenType.IMPLIES))
                else:
                    self.advance()
                    tokens.append(Token(TokenType.NOT))
                continue
            if c == 'V':
                self.advance()
                tokens.append(Token(TokenType.OR))
                continue
            if c == '^':
                self.advance()
                tokens.append(Token(TokenType.AND))
                continue
            if c == '_':
                self.advance()
                tokens.append(Token(TokenType.BOTTOM))
                continue
            if c == '(':
                self.advance()
                tokens.append(Token(TokenType.LPAREN))
                continue
            if c == ')':
                self.advance()
                tokens.append(Token(TokenType.RPAREN))
                continue
            raise ValueError(f"Unexpected character: {c}")

        tokens.append(Token(TokenType.EOF))

        return tokens