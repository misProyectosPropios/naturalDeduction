import unittest
from lexer import TokenType
from main import AND, BOTTOM, IMPLIES, NEG, OR, VAR
from parser import Parser  # assuming your parser is in parser.py

def make_token(token_type, value=None):
    """Helper to create a token object (simple namedtuple or custom class)."""
    # Adjust if your token class has different attributes.
    class Token:
        def __init__(self, type, value=None):
            self.type = type
            self.value = value
        def __repr__(self):
            return f"Token({self.type}, {self.value})"
    return Token(token_type, value)

class TestParser(unittest.TestCase):
    def parse_expression(self, tokens):
        """Helper to run parser and return AST."""
        parser = Parser(tokens)
        return parser.parse()

    # ------------------- Required tests -------------------
    def test_implication(self):
        # "a" -> "b"
        tokens = [
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.IMPLIES),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = IMPLIES(VAR('a'), VAR('b'))
        self.assertEqual(ast, expected)

    def test_and(self):
        # "a" ^ "b"
        tokens = [
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.AND),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = AND(VAR('a'), VAR('b'))
        self.assertEqual(ast, expected)

    def test_or(self):
        # "a" v "b"
        tokens = [
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.OR),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = OR(VAR('a'), VAR('b'))
        self.assertEqual(ast, expected)

    def test_negation(self):
        # -"b"
        tokens = [
            make_token(TokenType.NOT),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = NEG(VAR('b'))
        self.assertEqual(ast, expected)

    def test_implication_bottom(self):
        # "a" -> _
        tokens = [
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.IMPLIES),
            make_token(TokenType.BOTTOM),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = IMPLIES(VAR('a'), BOTTOM())
        self.assertEqual(ast, expected)

    def test_right_associative_implication(self):
        # "a" -> "a" -> "a"  should parse as a -> (a -> a)
        tokens = [
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.IMPLIES),
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.IMPLIES),
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = IMPLIES(VAR('a'), IMPLIES(VAR('a'), VAR('a')))
        self.assertEqual(ast, expected)

    # ------------------- Edge cases -------------------
    def test_parentheses_override_precedence(self):
        # (a v b) ^ c   -> AND(OR(a,b), c)
        tokens = [
            make_token(TokenType.LPAREN),
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.OR),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.RPAREN),
            make_token(TokenType.AND),
            make_token(TokenType.VAR, 'c'),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = AND(OR(VAR('a'), VAR('b')), VAR('c'))
        self.assertEqual(ast, expected)

    def test_multiple_negations(self):
        # - - a
        tokens = [
            make_token(TokenType.NOT),
            make_token(TokenType.NOT),
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = NEG(NEG(VAR('a')))
        self.assertEqual(ast, expected)

    def test_precedence_and_over_or(self):
        # a v b ^ c   -> OR(a, AND(b,c))
        tokens = [
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.OR),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.AND),
            make_token(TokenType.VAR, 'c'),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = OR(VAR('a'), AND(VAR('b'), VAR('c')))
        self.assertEqual(ast, expected)

    def test_nested_parentheses(self):
        # (a -> (b ^ c))
        tokens = [
            make_token(TokenType.LPAREN),
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.IMPLIES),
            make_token(TokenType.LPAREN),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.AND),
            make_token(TokenType.VAR, 'c'),
            make_token(TokenType.RPAREN),
            make_token(TokenType.RPAREN),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = IMPLIES(VAR('a'), AND(VAR('b'), VAR('c')))
        self.assertEqual(ast, expected)

    def test_empty_input(self):
        # No formula given
        tokens = [make_token(TokenType.EOF)]
        parser = Parser(tokens)
        with self.assertRaises(ValueError):
            parser.parse()

    def test_invalid_syntax_missing_operand(self):
        # "a" ->   (no right operand)
        tokens = [
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.IMPLIES),
            make_token(TokenType.EOF)
        ]
        parser = Parser(tokens)
        with self.assertRaises(ValueError):
            parser.parse()

    def test_extra_tokens_after_expression(self):
        # a b 
        tokens = [
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.EOF)
        ]
        parser = Parser(tokens)
        # parse will consume 'a', then try to parse implication after 'a'
        # but 'b' will cause an unexpected token in parse_atom
        with self.assertRaises(ValueError):
            parser.parse()

    def test_unmatched_parenthesis(self):
        # (a v b
        tokens = [
            make_token(TokenType.LPAREN),
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.OR),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.EOF)
        ]
        parser = Parser(tokens)
        with self.assertRaises(ValueError):  # expects RPAREN but gets EOF
            parser.parse()

    # ------------------- Complex expression -------------------
    def test_complex_expression(self):
        # - (a -> b) v (c ^ - d)  (with proper precedence)
        tokens = [
            make_token(TokenType.NOT),
            make_token(TokenType.LPAREN),
            make_token(TokenType.VAR, 'a'),
            make_token(TokenType.IMPLIES),
            make_token(TokenType.VAR, 'b'),
            make_token(TokenType.RPAREN),
            make_token(TokenType.OR),
            make_token(TokenType.LPAREN),
            make_token(TokenType.VAR, 'c'),
            make_token(TokenType.AND),
            make_token(TokenType.NOT),
            make_token(TokenType.VAR, 'd'),
            make_token(TokenType.RPAREN),
            make_token(TokenType.EOF)
        ]
        ast = self.parse_expression(tokens)
        expected = OR(
            NEG(IMPLIES(VAR('a'), VAR('b'))),
            AND(VAR('c'), NEG(VAR('d')))
        )
        self.assertEqual(ast, expected)


if __name__ == '__main__':
    unittest.main()