import unittest
import os
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

# Add the project root to sys.path to allow importing from 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import (
    Rule, Goal, Proof, Axiom, AndIntro, AndElim1, AndElim2, OrIntro1, OrIntro2, OrElim, ImpIntro, ImpElimination, NotIntro, NotElimination, BottomElimination,
    parse_formula_with_lexer,
    getContext, getResolvent, getFormula, main,
    # Paso and Resolver are no longer in src.main.py, they have been refactored into Goal and Proof.
)
from src.logic import VAR, AND, OR, NEG, IMPLIES, BOTTOM, LogicRules

class TestPropClasses(unittest.TestCase):
    """Test Prop subclasses and their prettify methods."""
    
    def test_var_prettify(self):
        """Test VAR prettification."""
        var_p = VAR("P")
        self.assertEqual(var_p.prettify(), "P")
        
        var_long = VAR("LongVariable")
        self.assertEqual(var_long.prettify(), "LongVariable")
    
    def test_bottom_prettify(self):
        """Test BOTTOM prettification."""
        bottom = BOTTOM()
        self.assertEqual(bottom.prettify(), "⊥")
    
    def test_neg_prettify(self):
        """Test NEG prettification."""
        var_p = VAR("P")
        neg_p = NEG(var_p)
        self.assertEqual(neg_p.prettify(), "¬(P)")
        
        # Nested negation
        neg_neg_p = NEG(neg_p)
        self.assertEqual(neg_neg_p.prettify(), "¬(¬(P))")
    
    def test_and_prettify(self):
        """Test AND prettification."""
        var_p = VAR("P")
        var_q = VAR("Q")
        and_pq = AND(var_p, var_q)
        self.assertEqual(and_pq.prettify(), "(P ∧ Q)")
    
    def test_or_prettify(self):
        """Test OR prettification."""
        var_p = VAR("P")
        var_q = VAR("Q")
        or_pq = OR(var_p, var_q)
        self.assertEqual(or_pq.prettify(), "(P ∨ Q)")
    
    def test_implies_prettify(self):
        """Test IMPLIES prettification."""
        var_p = VAR("P")
        var_q = VAR("Q")
        impl_pq = IMPLIES(var_p, var_q)
        self.assertEqual(impl_pq.prettify(), "(P → Q)")
    
    def test_complex_prettify(self):
        """Test prettification of complex nested formulas."""
        # (P ∧ Q) → (¬R ∨ S)
        p = VAR("P")
        q = VAR("Q")
        r = VAR("R")
        s = VAR("S")
        
        left = AND(p, q)
        right = OR(NEG(r), s)
        formula = IMPLIES(left, right)
        
        expected = "((P ∧ Q) → (¬(R) ∨ S))"
        self.assertEqual(formula.prettify(), expected)


class TestPropMethods(unittest.TestCase):
    """Test helper methods on Prop classes."""
    
    def test_implies_method(self):
        """Test implies() method."""
        p = VAR("P")
        q = VAR("Q")
        
        impl = p.implies(q)
        self.assertIsInstance(impl, IMPLIES)
        self.assertEqual(impl.premise, p)
        self.assertEqual(impl.conclusion, q)
    
    def test_or_with_method(self):
        """Test or_with() method."""
        p = VAR("P")
        q = VAR("Q")
        
        or_formula = p.or_with(q)
        self.assertIsInstance(or_formula, OR)
        self.assertEqual(or_formula.left, p)
        self.assertEqual(or_formula.right, q)
    
    def test_negate_method(self):
        """Test negate() method."""
        p = VAR("P")
        
        neg = p.negate()
        self.assertIsInstance(neg, NEG)
        self.assertEqual(neg.prop, p)


class TestPaso(unittest.TestCase):
    """Test Paso class."""

    def test_and_introduction_applicable(self):
        """Test AND_INTRODUCTION applicability."""
        p = VAR("P")
        q = VAR("Q")
        and_pq = AND(p, q)
        
        paso = Goal([], and_pq)
        rule = AndIntro()
        self.assertTrue(rule.applicable(paso))
        
        paso_fail = Goal([], p)
        self.assertFalse(rule.applicable(paso_fail))
    
    def test_and_elimination_1_applicable(self):
        """Test AND_ELIMINATION_1 applicability."""
        and_formula = AND(VAR("P"), VAR("Q"))
        paso = Goal([], and_formula)
        rule = AndElim1()
        self.assertTrue(rule.applicable(paso))
    
    def test_and_elimination_2_applicable(self):
        """Test AND_ELIMINATION_2 applicability."""
        and_formula = AND(VAR("P"), VAR("Q"))
        paso = Goal([], and_formula)
        rule = AndElim2()
        self.assertTrue(rule.applicable(paso))
    
    def test_implication_introduction_applicable(self):
        """Test IMPLICATION_INTRODUCTION applicability."""
        impl = IMPLIES(VAR("P"), VAR("Q"))
        paso = Goal([], impl)
        rule = ImpIntro()
        self.assertTrue(rule.applicable(paso))
        
        # Not applicable to non-IMPLIES
        paso_fail = Goal([], VAR("P"))
        self.assertFalse(rule.applicable(paso_fail))
    
    def test_or_introduction_1_applicable(self):
        """Test OR_INTRODUCTION_1 applicability."""
        or_formula = OR(VAR("P"), VAR("Q"))
        paso = Goal([], or_formula)
        rule = OrIntro1()
        self.assertTrue(rule.applicable(paso))
    
    def test_or_introduction_2_applicable(self):
        """Test OR_INTRODUCTION_2 applicability."""
        or_formula = OR(VAR("P"), VAR("Q"))
        paso = Goal([], or_formula)
        rule = OrIntro2()
        self.assertTrue(rule.applicable(paso))
    
    def test_negation_introduction_applicable(self):
        """Test NEGATION_INTRODUCTION applicability."""
        neg_formula = NEG(VAR("P"))
        paso = Goal([], neg_formula)
        rule = NotIntro()
        self.assertTrue(rule.applicable(paso))
    
    def test_negation_elimination_applicable(self):
        """Test NEGATION_ELIMINATION applicability."""
        bottom = BOTTOM()
        paso = Goal([], bottom)
        rule = NotElimination()
        self.assertTrue(rule.applicable(paso))
    
class TestParseFormulaWithLexer(unittest.TestCase):
    """Test parse_formula_with_lexer function."""
    
    def test_parse_single_variable(self):
        """Test parsing single variable."""
        result = parse_formula_with_lexer('"P"')
        self.assertIsInstance(result, VAR)
        self.assertEqual(result.name, "P")
    
    def test_parse_bottom(self):
        """Test parsing bottom."""
        result = parse_formula_with_lexer('_')
        self.assertIsInstance(result, BOTTOM)
    
    def test_parse_negation(self):
        """Test parsing negation."""
        result = parse_formula_with_lexer('-"P"')
        self.assertIsInstance(result, NEG)
        self.assertIsInstance(result.prop, VAR)
        self.assertEqual(result.prop.name, "P")
    
    def test_parse_conjunction(self):
        """Test parsing conjunction."""
        result = parse_formula_with_lexer('"P" ^ "Q"')
        self.assertIsInstance(result, AND)
        self.assertIsInstance(result.left, VAR)
        self.assertIsInstance(result.right, VAR)
    
    def test_parse_disjunction(self):
        """Test parsing disjunction."""
        result = parse_formula_with_lexer('"P" V "Q"')
        self.assertIsInstance(result, OR)
        self.assertIsInstance(result.left, VAR)
        self.assertIsInstance(result.right, VAR)
    
    def test_parse_implication(self):
        """Test parsing implication."""
        result = parse_formula_with_lexer('"P" -> "Q"')
        self.assertIsInstance(result, IMPLIES)
        self.assertIsInstance(result.premise, VAR)
        self.assertIsInstance(result.conclusion, VAR)
    
    def test_parse_complex_formula(self):
        """Test parsing complex nested formula."""
        result = parse_formula_with_lexer('("P" ^ "Q") -> -"R"')
        self.assertIsInstance(result, IMPLIES)
        self.assertIsInstance(result.premise, AND)
        self.assertIsInstance(result.conclusion, NEG)
    
    def test_parse_invalid_syntax(self):
        """Test parsing invalid syntax."""
        with self.assertRaises(ValueError):
            parse_formula_with_lexer('invalid syntax @@@')
    
    def test_parse_unterminated_string(self):
        """Test parsing unterminated string."""
        with self.assertRaises(ValueError):
            parse_formula_with_lexer('"P')
    
    def test_parse_empty_string(self):
        """Test parsing empty string."""
        with self.assertRaises(ValueError):
            parse_formula_with_lexer('')

class TestResolver(unittest.TestCase):
    """Test Resolver class."""

    def test_proof_not_complete_initially(self):
        """Test that proof is not complete initially."""
        p = VAR("P")
        context = [Goal({p}, p)]
        goal = p
        
        resolver = Proof(goal, context)
        self.assertFalse(resolver.isCompleted())

        resolver.aplicarRegla(Axiom(), 0)
        self.assertTrue(resolver.isCompleted())
    
    def test_proof_and_intro_complete(self):
        """Test that proof is not complete initially."""
        p = VAR("P")
        q = VAR("Q")
        pAndQ = AND(p, q)

        context = [Goal({}, p)]
        goal = Goal({}, pAndQ)
        
        resolver = Proof(goal, context)
        resolver.aplicarRegla(AndIntro(), 0)
        self.assertFalse(resolver.isCompleted())
        resolver.aplicarRegla(Axiom(), 1)
        resolver.aplicarRegla(Axiom(), 2)
        self.assertTrue(resolver.isCompleted())
    
    def test_proof_and_intro_complete(self):
        """Test that proof is not complete initially."""
        p = VAR("P")
        context = []
        goal = Goal({}, IMPLIES(p, p))
        
        resolver = Proof(goal, context)
        resolver.aplicarRegla(ImpIntro(), 0)
        self.assertFalse(resolver.isCompleted())
        self.assertFalse(resolver.isCompleted())

if __name__ == '__main__':
    unittest.main()
