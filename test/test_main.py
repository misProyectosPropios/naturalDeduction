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
    
    def test_paso_toString(self):
        p = VAR("P")
        q = VAR("Q")
        context = [p, q]
        goal = AND(p, q)
        
        paso = Proof(context, goal)
        result = paso.toString()
        
        self.assertIn("P", result)
        self.assertIn("Q", result)
        self.assertIn("⊢", result)
    """
    def test_paso_isInTheContext(self):
        p = VAR("P")
        q = VAR("Q")
        context = [p]
        goal = q
        
        paso = Proof(context, goal)
        self.assertTrue(paso.isInTheContext(p))
        self.assertFalse(paso.isInTheContext(q))
    """
    """
    def test_paso_type_checking(self):
        p = VAR("P")
        
        # Valid creation
        paso = Proof([p], p)
        self.assertIsNotNone(paso)
        
        # Invalid context
        with self.assertRaises(TypeError):
            Paso(["not a prop"], p)
        
        # Invalid resolvente
        with self.assertRaises(TypeError):
            Paso([p], "not a prop")
    """
    def test_and_introduction_applicable(self):
        """Test AND_INTRODUCTION applicability."""
        p = VAR("P")
        q = VAR("Q")
        and_pq = AND(p, q)
        
        paso = Goal([], and_pq)
        rule = AndIntro()
        self.assertTrue(rule.applicable(paso))
        
        paso_fail = Proof([], p)
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
        paso_fail = Proof([], VAR("P"))
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
    
    """def test_excluded_middle_applicable(self):
        #TODO
        p = VAR("P")
        or_formula = OR(p, NEG(p))
        paso = Goal([], or_formula)
        rule = self._get_default_rule("EXCLUDED_MIDDLE")
        self.assertTrue(rule.applicable(paso))
        
        # Not applicable if not of form (A ∨ ¬A)
        or_bad = OR(p, VAR("Q"))
        paso_fail = Goal([], or_bad)
        self.assertFalse(rule.applicable(paso_fail))
    """
    
    """"def test_negation_negation_introduction_applicable(self):
        
        neg_neg = NEG(NEG(VAR("P")))
        paso = Goal([], neg_neg)
        rule = self._get_default_rule("NEGATION_NEGATION_INTRODUCTION")
        self.assertTrue(rule.applicable(paso))
    """

class TestResolver(unittest.TestCase):
    """Test Resolver class."""
    """
    def test_resolver_initialization(self):

        p = VAR("P")
        context = [p]
        goal = p
        
        resolver = Proof(context, goal)
        
        self.assertEqual(resolver.contexto_inicial, context)
        self.assertEqual(resolver.resolvente_final, goal)
        self.assertEqual(len(resolver.lista_de_pasos), 1)
        self.assertEqual(resolver.pasos_a_resolver, {0})
    """

    def test_proof_not_complete_initially(self):
        """Test that proof is not complete initially."""
        p = VAR("P")
        context = [p]
        goal = p
        
        resolver = Proof(context, goal)
        self.assertFalse(resolver.isProofComplete())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_proof_complete_after_axiom(self, mock_stdout):
        """Test that proof is complete after applying axiom."""
        p = VAR("P")
        context = [p]
        goal = p
        
        resolver = Proof(context, goal)
        result = resolver.aplicarRegla(0, Axiom())
        
        self.assertTrue(result)
        self.assertTrue(resolver.isProofComplete())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_and_introduction(self, mock_stdout):
        """Test applying AND_INTRODUCTION rule."""
        p = VAR("P")
        q = VAR("Q")
        context = [p, q]
        goal = AND(p, q)
        
        resolver = Proof(context, goal)
        result = resolver.aplicarRegla(0, LogicRules.AND_INTRODUCTION)
        
        self.assertTrue(result)
        # Should create two substeps
        self.assertEqual(len(resolver.lista_de_pasos), 3)
        # Should remove step 0 from pasos_a_resolver
        self.assertNotIn(0, resolver.pasos_a_resolver)
        # Should add steps 1 and 2 to pasos_a_resolver
        self.assertIn(1, resolver.pasos_a_resolver)
        self.assertIn(2, resolver.pasos_a_resolver)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_implication_introduction(self, mock_stdout):
        """Test applying IMPLICATION_INTRODUCTION rule."""
        p = VAR("P")
        q = VAR("Q")
        impl = IMPLIES(p, q)
        
        resolver = Proof([], impl)
        result = resolver.aplicarRegla(0, LogicRules.IMPLICATION_INTRODUCTION)
        
        self.assertTrue(result)
        # Should create one substep with p added to context
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertIn(p, new_paso.contexto)
        self.assertEqual(new_paso.resolvente, q)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_negation_introduction(self, mock_stdout):
        """Test applying NEGATION_INTRODUCTION rule."""
        p = VAR("P")
        neg_p = NEG(p)
        
        resolver = Proof([], neg_p)
        result = resolver.aplicarRegla(0, LogicRules.NEGATION_INTRODUCTION)
        
        self.assertTrue(result)
        # Should create one substep with p added to context and goal BOTTOM
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertIn(p, new_paso.contexto)
        self.assertIsInstance(new_paso.resolvente, BOTTOM)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_rule_to_invalid_step(self, mock_stdout):
        """Test applying rule to invalid step."""
        p = VAR("P")
        resolver = Proof([p], p)
        
        # Apply axiom to step 0
        resolver.aplicarRegla(0, LogicRules.AXIOM)
        
        # Try to apply rule to resolved step 0
        result = resolver.aplicarRegla(0, LogicRules.AND_INTRODUCTION)
        self.assertFalse(result)
        
        # Try to apply rule to non-existent step
        result = resolver.aplicarRegla(999, LogicRules.AXIOM)
        self.assertFalse(result)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_structurally_inapplicable_rule(self, mock_stdout):
        """Test applying structurally inapplicable rule."""
        p = VAR("P")
        resolver = Proof([], p)
        
        # Try to apply AND_INTRODUCTION to non-AND proposition
        result = resolver.aplicarRegla(0, LogicRules.AND_INTRODUCTION)
        self.assertFalse(result)


class TestResolverRuleHandlers(unittest.TestCase):
    """Test the implementation of every default rule handler."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_and_elimination_1(self, mock_stdout):
        p = VAR("P")
        q = VAR("Q")
        resolver = Proof([], AND(p, q))

        result = resolver.aplicarRegla(0, LogicRules.AND_ELIMINATION_1)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        self.assertNotIn(0, resolver.pasos_a_resolver)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertEqual(new_paso.resolvente, p)

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_and_elimination_2(self, mock_stdout):
        p = VAR("P")
        q = VAR("Q")
        resolver = Proof([], AND(p, q))

        result = resolver.aplicarRegla(0, LogicRules.AND_ELIMINATION_2)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        self.assertNotIn(0, resolver.pasos_a_resolver)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertEqual(new_paso.resolvente, q)

    @patch('main.getFormula')
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_implication_elimination(self, mock_stdout, mock_get_formula):
        p = VAR("P")
        q = VAR("Q")
        mock_get_formula.return_value = p
        resolver = Proof([], q)

        result = resolver.aplicarRegla(0, LogicRules.IMPLICATION_ELIMINATION)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 3)
        new_paso1, _, _ = resolver.lista_de_pasos[1]
        new_paso2, _, _ = resolver.lista_de_pasos[2]
        self.assertEqual(new_paso1.resolvente, p)
        self.assertEqual(new_paso2.resolvente, p.implies(q))

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_or_introduction_1(self, mock_stdout):
        p = VAR("P")
        q = VAR("Q")
        resolver = Proof([], OR(p, q))

        result = resolver.aplicarRegla(0, LogicRules.OR_INTRODUCTION_1)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertEqual(new_paso.resolvente, p)

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_or_introduction_2(self, mock_stdout):
        p = VAR("P")
        q = VAR("Q")
        resolver = Proof([], OR(p, q))

        result = resolver.aplicarRegla(0, LogicRules.OR_INTRODUCTION_2)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertEqual(new_paso.resolvente, q)

    @patch('main.getFormula')
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_or_elimination(self, mock_stdout, mock_get_formula):
        p = VAR("P")
        q = VAR("Q")
        r = VAR("R")
        mock_get_formula.side_effect = [p, q]
        resolver = Proof([], r)

        result = resolver.aplicarRegla(0, LogicRules.OR_ELIMINATION)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 4)
        new_paso1, _, _ = resolver.lista_de_pasos[1]
        new_paso2, _, _ = resolver.lista_de_pasos[2]
        new_paso3, _, _ = resolver.lista_de_pasos[3]
        self.assertEqual(new_paso1.resolvente, p.or_with(q))
        self.assertEqual(new_paso2.contexto, [p])
        self.assertEqual(new_paso2.resolvente, r)
        self.assertEqual(new_paso3.contexto, [q])
        self.assertEqual(new_paso3.resolvente, r)

    @patch('main.getFormula')
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_negation_elimination(self, mock_stdout, mock_get_formula):
        p = VAR("P")
        q = VAR("Q")
        mock_get_formula.return_value = p
        resolver = Proof([], q)

        result = resolver.aplicarRegla(0, LogicRules.NEGATION_ELIMINATION)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 3)
        new_paso1, _, _ = resolver.lista_de_pasos[1]
        new_paso2, _, _ = resolver.lista_de_pasos[2]
        self.assertEqual(new_paso1.resolvente, p)
        self.assertEqual(new_paso2.resolvente, p.negate())

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_bottom_elimination(self, mock_stdout):
        p = VAR("P")
        resolver = Proof([], p)

        result = resolver.aplicarRegla(0, LogicRules.BOTTOM_ELIMINATION)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertIsInstance(new_paso.resolvente, BOTTOM)

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_modus_tollens(self, mock_stdout):
        p = VAR("P")
        resolver = Proof([], NEG(p))

        result = resolver.aplicarRegla(0, LogicRules.MODUS_TOLLENS)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertEqual(new_paso.resolvente, p.implies(BOTTOM()))

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_negation_negation_introduction(self, mock_stdout):
        p = VAR("P")
        resolver = Proof([], NEG(NEG(p)))

        result = resolver.aplicarRegla(0, LogicRules.NEGATION_NEGATION_INTRODUCTION)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertIsInstance(new_paso.resolvente, BOTTOM)
        self.assertIn(NEG(p), new_paso.contexto)

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_negation_negation_elimination(self, mock_stdout):
        p = VAR("P")
        resolver = Proof([], NEG(NEG(p)))

        result = resolver.aplicarRegla(0, LogicRules.NEGATION_NEGATION_ELIMINATION)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertEqual(new_paso.resolvente, p)

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_excluded_middle(self, mock_stdout):
        p = VAR("P")
        resolver = Proof([], OR(p, p.negate()))

        result = resolver.aplicarRegla(0, LogicRules.EXCLUDED_MIDDLE)

        self.assertTrue(result)
        self.assertTrue(resolver.isProofComplete())
        self.assertEqual(len(resolver.lista_de_pasos), 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_pbc(self, mock_stdout):
        p = VAR("P")
        resolver = Proof([], p)

        result = resolver.aplicarRegla(0, LogicRules.PBC)

        self.assertTrue(result)
        self.assertEqual(len(resolver.lista_de_pasos), 2)
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertIsInstance(new_paso.resolvente, BOTTOM)
        self.assertEqual(new_paso.contexto, [p.negate()])


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


class TestUserInput(unittest.TestCase):
    """Test user input functions."""
    
    @patch('builtins.input')
    def test_getContext_single_proposition(self, mock_input):
        """Test getContext with single proposition."""
        mock_input.side_effect = ['"P"', '']
        
        context = getContext()
        
        self.assertEqual(len(context), 1)
        self.assertIsInstance(context[0], VAR)
        self.assertEqual(context[0].name, "P")
    
    @patch('builtins.input')
    def test_getContext_multiple_propositions(self, mock_input):
        """Test getContext with multiple propositions."""
        mock_input.side_effect = ['"P"', '"Q"', '"P" ^ "Q"', '']
        
        context = getContext()
        
        self.assertEqual(len(context), 3)
        self.assertIsInstance(context[0], VAR)
        self.assertIsInstance(context[1], VAR)
        self.assertIsInstance(context[2], AND)
    
    @patch('builtins.input')
    def test_getContext_empty(self, mock_input):
        """Test getContext with no propositions."""
        mock_input.side_effect = ['']
        
        context = getContext()
        
        self.assertEqual(len(context), 0)
    
    @patch('builtins.input')
    def test_getContext_invalid_then_valid(self, mock_input):
        """Test getContext with invalid input then valid."""
        mock_input.side_effect = ['invalid @@@', '"P"', '']
        
        context = getContext()
        
        self.assertEqual(len(context), 1)
        self.assertIsInstance(context[0], VAR)
    
    @patch('builtins.input')
    def test_getResolvent_valid(self, mock_input):
        """Test getResolvent with valid input."""
        mock_input.side_effect = ['"P"']
        
        resolvente = getResolvent()
        
        self.assertIsInstance(resolvente, VAR)
        self.assertEqual(resolvente.name, "P")
    
    @patch('builtins.input')
    def test_getResolvent_complex(self, mock_input):
        """Test getResolvent with complex formula."""
        mock_input.side_effect = ['("P" -> "Q") ^ "R"']
        
        resolvente = getResolvent()
        
        self.assertIsInstance(resolvente, AND)
        self.assertIsInstance(resolvente.left, IMPLIES)
        self.assertIsInstance(resolvente.right, VAR)
    
    @patch('builtins.input')
    def test_getResolvent_rejects_empty(self, mock_input):
        """Test getResolvent rejects empty input."""
        mock_input.side_effect = ['', '"P"']
        
        resolvente = getResolvent()
        
        self.assertIsInstance(resolvente, VAR)
    
    @patch('builtins.input')
    def test_getFormula_valid(self, mock_input):
        """Test getFormula with valid input."""
        mock_input.side_effect = ['"P" -> "Q"']
        
        formula = getFormula()
        
        self.assertIsInstance(formula, IMPLIES)
    
    @patch('builtins.input')
    def test_getFormula_rejects_empty(self, mock_input):
        """Test getFormula rejects empty input."""
        mock_input.side_effect = ['', '"P"']
        
        formula = getFormula()
        
        self.assertIsInstance(formula, VAR)


class TestResolverIntegration(unittest.TestCase):
    """Integration tests for Resolver with multiple rules."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_prove_simple_tautology(self, mock_stdout):
        """Test proving P from [P]."""
        p = VAR("P")
        resolver = Proof([p], p)
        
        self.assertFalse(resolver.isProofComplete())
        resolver.aplicarRegla(0, LogicRules.AXIOM)
        self.assertTrue(resolver.isProofComplete())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_prove_and_from_components(self, mock_stdout):
        """Test proving P ∧ Q from [P, Q]."""
        p = VAR("P")
        q = VAR("Q")
        and_pq = AND(p, q)
        
        resolver = Proof([p, q], and_pq)
        
        # Apply AND_INTRODUCTION
        self.assertTrue(resolver.aplicarRegla(0, LogicRules.AND_INTRODUCTION))
        self.assertEqual(len(resolver.pasos_a_resolver), 2)
        
        # Apply AXIOM to both substeps
        self.assertTrue(resolver.aplicarRegla(1, LogicRules.AXIOM))
        self.assertTrue(resolver.aplicarRegla(2, LogicRules.AXIOM))
        self.assertTrue(resolver.isProofComplete())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_prove_implication_introduction(self, mock_stdout):
        """Test proving P → Q from [Q]."""
        p = VAR("P")
        q = VAR("Q")
        impl = IMPLIES(p, q)
        
        resolver = Proof([q], impl)
        
        # Apply IMPLICATION_INTRODUCTION
        self.assertTrue(resolver.aplicarRegla(0, LogicRules.IMPLICATION_INTRODUCTION))
        self.assertEqual(len(resolver.pasos_a_resolver), 1)
        
        # The substep should have p in context and q as goal
        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertIn(p, new_paso.contexto)
        
        # Apply AXIOM to the substep
        self.assertTrue(resolver.aplicarRegla(1, LogicRules.AXIOM))
        self.assertTrue(resolver.isProofComplete())

    @patch('sys.stdout', new_callable=StringIO)
    def test_register_custom_rule_and_infer_truth(self, mock_stdout):
        """Test adding a custom rule to infer Q from P and P → Q."""
        p = VAR("P")
        q = VAR("Q")
        implication = IMPLIES(p, q)

        resolver = Proof([p, implication], q)

        def custom_applicable(paso: Proof) -> bool:
            return paso.resolvente == q and any(
                isinstance(item, IMPLIES) and item.premise == p and item.conclusion == q
                for item in paso.contexto
            )

        def custom_handler(self, num_pos: int, current_paso: Proof) -> bool:
            self._mark_resolved(num_pos, custom_rule)
            return True

        custom_rule = Rule(
            key="MPQ",
            value="MPQ",
            applicable=custom_applicable,
            handler=custom_handler,
            description="Infer Q from P and P → Q in the context."
        )
        resolver.register_rule(custom_rule)

        self.assertTrue(resolver.aplicarRegla(0, custom_rule))
        self.assertTrue(resolver.isProofComplete())

    @patch('sys.stdout', new_callable=StringIO)
    def test_prove_identity_implication(self, mock_stdout):
        """Test proving P → P with implication introduction and axiom."""
        p = VAR("P")
        goal = IMPLIES(p, p)

        resolver = Proof([], goal)
        self.assertFalse(resolver.isProofComplete())

        # Apply IMPLICATION_INTRODUCTION to create a substep P |- P
        self.assertTrue(resolver.aplicarRegla(0, LogicRules.IMPLICATION_INTRODUCTION))
        self.assertEqual(len(resolver.lista_de_pasos), 2)

        new_paso, _, _ = resolver.lista_de_pasos[1]
        self.assertEqual(new_paso.contexto, [p])
        self.assertEqual(new_paso.resolvente, p)

        # Apply AXIOM to discharge the substep and complete the proof
        self.assertTrue(resolver.aplicarRegla(1, LogicRules.AXIOM))
        self.assertTrue(resolver.isProofComplete())

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_displays_proof_complete_feedback(self, mock_stdout, mock_input):
        mock_input.side_effect = ['"P"', '', '"P"', '0', 'Axiom']

        main()

        output = mock_stdout.getvalue()
        self.assertIn("SUCCESS! PROOF COMPLETE!", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_prove_negation(self, mock_stdout):
        """Test proving ¬P from context with P leading to bottom."""
        p = VAR("P")
        neg_p = NEG(p)
        initial_goal = Goal(set(), neg_p)
        proof = Proof(initial_goal)

        # Apply NEGATION_INTRODUCTION
        applied_not_intro, _ = proof.aplicarRegla(0, _get_rule_instance(LogicRules.NEGATION_INTRODUCTION))
        self.assertTrue(applied_not_intro)
        self.assertEqual(len(proof.steps), 2) # Original + 1 subgoal
        self.assertFalse(proof.isCompleted())
        
        new_goal_step = proof.steps[1]
        self.assertIn(p, new_goal_step.context)
        self.assertIsInstance(new_goal_step.formula, BOTTOM)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_deeply_nested_formulas(self):
        """Test handling deeply nested formulas."""
        formula = VAR("P")
        for _ in range(5):
            formula = NEG(formula)
        
        self.assertIsNotNone(formula.prettify())
    
    def test_wide_nested_formulas(self):
        """Test handling wide nested formulas."""
        formulas = [VAR(f"P{i}") for i in range(10)]
        
        result = formulas[0]
        for f in formulas[1:]:
            result = AND(result, f)
        
        self.assertIsNotNone(result.prettify())
    
    def test_paso_with_large_context(self):
        """Test Paso with large context."""
        context = [VAR(f"P{i}") for i in range(100)]
        goal = VAR("Goal")
        
        paso = Goal(context, goal)
        self.assertEqual(len(paso.contexto), 100)
    
    def test_resolver_with_empty_context(self):
        """Test Resolver with empty context."""
        goal = IMPLIES(VAR("P"), VAR("P"))
        resolver = Proof([], goal)
        
        self.assertFalse(resolver.isProofComplete())
        self.assertEqual(len(resolver.lista_de_pasos), 1)


if __name__ == '__main__':
    unittest.main()
