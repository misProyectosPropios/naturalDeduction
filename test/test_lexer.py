import unittest

from lexer import Lexer, Token, TokenType


class TestLexer(unittest.TestCase):

    def test_empty(self):
        lexer = Lexer("")
        self.assertEqual(
            lexer.tokenize(),
            [Token(TokenType.EOF)]
        )

    def test_var(self):
        lexer = Lexer('"P"')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.VAR, "P"),
                Token(TokenType.EOF)
            ]
        )

    def test_var_v_not_or(self):
        lexer = Lexer('"V"')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.VAR, "V"),
                Token(TokenType.EOF)
            ]
        )

    def test_or(self):
        lexer = Lexer('V')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.OR),
                Token(TokenType.EOF)
            ]
        )

    def test_implies(self):
        lexer = Lexer('->')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.IMPLIES),
                Token(TokenType.EOF)
            ]
        )

    def test_and(self):
        lexer = Lexer('^')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.AND),
                Token(TokenType.EOF)
            ]
        )

    def test_bottom(self):
        lexer = Lexer('_')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.BOTTOM),
                Token(TokenType.EOF)
            ]
        )

    def test_parentheses(self):
        lexer = Lexer('()')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.LPAREN),
                Token(TokenType.RPAREN),
                Token(TokenType.EOF)
            ]
        )

    def test_complex_expression(self):
        lexer = Lexer('("P" ^ -"Q") -> _')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.LPAREN),
                Token(TokenType.VAR, "P"),
                Token(TokenType.AND),
                Token(TokenType.NOT),
                Token(TokenType.VAR, "Q"),
                Token(TokenType.RPAREN),
                Token(TokenType.IMPLIES),
                Token(TokenType.BOTTOM),
                Token(TokenType.EOF)
            ]
        )

    def test_whitespace(self):
        lexer = Lexer('   "P"    V    "Q"   ')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.VAR, "P"),
                Token(TokenType.OR),
                Token(TokenType.VAR, "Q"),
                Token(TokenType.EOF)
            ]
        )

    def test_var_with_operator_symbols(self):
        lexer = Lexer('"P->Q"')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.VAR, "P->Q"),
                Token(TokenType.EOF)
            ]
        )

    def test_unterminated_string(self):
        lexer = Lexer('"P')

        with self.assertRaises(ValueError):
            lexer.tokenize()

    def test_invalid_character(self):
        lexer = Lexer('@')

        with self.assertRaises(ValueError):
            lexer.tokenize()

    def test_not_then_implies(self):
        lexer = Lexer('-->')

        self.assertEqual(
            lexer.tokenize(),
            [
                Token(TokenType.NOT),
                Token(TokenType.IMPLIES),
                Token(TokenType.EOF)
            ]
        )


if __name__ == "__main__":
    unittest.main()