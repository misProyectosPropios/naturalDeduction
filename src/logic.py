from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

class Prop:
    @abstractmethod
    def prettify(self):
        pass
    
    def implies(self, conclusion: 'Prop') -> 'IMPLIES':
        """Create an implication from this proposition to the conclusion."""
        return IMPLIES(self, conclusion)
    
    def or_with(self, other: 'Prop') -> 'OR':
        """Create a disjunction with another proposition."""
        return OR(self, other)
    
    def negate(self) -> 'NEG':
        """Create the negation of this proposition."""
        return NEG(self)


@dataclass(eq=True, frozen=True)
class NEG(Prop):
    prop: Prop
    
    def prettify(self):
        return f"¬({self.prop.prettify()})"


@dataclass(eq=True, frozen=True)
class AND(Prop):
    left: Prop
    right: Prop
    
    def prettify(self):
        return f"({self.left.prettify()} ∧ {self.right.prettify()})"


@dataclass(eq=True, frozen=True)
class OR(Prop):
    left: Prop
    right: Prop
    
    def prettify(self):
        return f"({self.left.prettify()} ∨ {self.right.prettify()})"


@dataclass(eq=True, frozen=True)
class IMPLIES(Prop):
    premise: Prop
    conclusion: Prop
    
    def prettify(self):
        return f"({self.premise.prettify()} → {self.conclusion.prettify()})"


@dataclass(eq=True, frozen=True)
class BOTTOM(Prop):
    def prettify(self):
        return "⊥"


@dataclass(eq=True, frozen=True)
class VAR(Prop):
    name: str

    def prettify(self):
        return self.name


class LogicRules(Enum):
    AXIOM = "Axiom"
    AND_INTRODUCTION = "∧I"
    AND_ELIMINATION_1 = "∧E1"
    AND_ELIMINATION_2 = "∧E2"
    IMPLICATION_INTRODUCTION = "→I"
    IMPLICATION_ELIMINATION = "→E"
    OR_INTRODUCTION_1 = "∨I1"
    OR_INTRODUCTION_2 = "∨I2"
    OR_ELIMINATION = "∨E"
    NEGATION_INTRODUCTION = "¬I"
    NEGATION_ELIMINATION = "¬E"
    BOTTOM_ELIMINATION = "⊥E"
    MODUS_TOLLENS = "MT"
    NEGATION_NEGATION_INTRODUCTION = "¬¬I"
    NEGATION_NEGATION_ELIMINATION = "¬¬E"
    EXCLUDED_MIDDLE = "LEM"
    PBC = "PBC"

def apply_logic_rule(context_strs, goal_str, rule_key):
    """
    Central entry point for rule application.
    Returns a dict with either 'error' or the new state.
    """
    from src.lexer import Lexer
    from src.parser import Parser

    def parse(s):
        return Parser(Lexer(s).tokenize()).parse()

    try:
        goal_ast = parse(goal_str)
        context_asts = [parse(c) for c in context_strs]

        if rule_key == "IMPLICATION_INTRODUCTION":
            if not isinstance(goal_ast, IMPLIES):
                return {"error": "The selected step is not an implication; →I cannot be applied."}
            
            return {
                "new_context": context_strs + [goal_ast.premise.prettify()],
                "new_goal": goal_ast.conclusion.prettify(),
                "resolved_by": "→I"
            }

        if rule_key == "AXIOM":
            # Deep equality check thanks to dataclass eq=True
            if any(ctx == goal_ast for ctx in context_asts):
                return {"resolved_by": "Axiom"}
            return {"error": "Axiom can only be applied when the goal is already in the context."}

        # Add other rules here as needed...
        return {"error": f"Rule '{rule_key}' is not yet implemented in Python logic."}

    except Exception as e:
        return {"error": f"Logic Error: {str(e)}"}
