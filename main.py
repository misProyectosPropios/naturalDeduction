from dataclasses import dataclass
from typing import Union
from enum import Enum

# Tipo forward para la recursividad
Prop = Union["NEG", "AND", "OR", "BOTTOM", "VAR"]

@dataclass
class NEG:
    prop: Prop

@dataclass
class AND:
    left: Prop
    right: Prop

@dataclass
class OR:
    left: Prop
    right: Prop

@dataclass
class IMPLIES:
    premise: Prop
    conclusion: Prop

@dataclass
class BOTTOM:
    pass

@dataclass
class VAR:
    name: str

def pretty_print(p: Prop) -> str:
    match p:
        case VAR(name):
            return name
        case NOT(expr):
            return f"¬({pretty_print(expr)})"
        case AND(left, right):
            return f"({pretty_print(left)} ∧ {pretty_print(right)})"
        case OR(left, right):
            return f"({pretty_print(left)} ∨ {pretty_print(right)})"
        case IMPLIES(premise, conclusion):
            return f"({pretty_print(premise)} ⇒ {pretty_print(conclusion)})"
        case BOTTOM():
            return "⊥"

class LogicRules(Enum):
    AXIOM: "Axiom"
    AND_INTRODUCTION: "∧I"
    AND_ELIMINATION_1: "∧E1"
    AND_ELIMINATION_2: "∧E2"
    IMPLICATION_INTRODUCTION: "→I"
    IMPLICATION_ELIMINATION: "→E" 
    OR_INTRODUCTION_1: "∨I1"
    OR_INTRODUCTION_2: "∨I2" 
    OR_ELIMINATION: "∨E"
    NEGATION_INTRODUCTION: "¬I" 
    NEGATION_ELIMINATION: "¬E"  
    BOTTOM_ELIMINATION: "⊥E"

    #Reglas derivadas
    MODUS_TOLLENS: "MT" 
    NEGATION_NEGATION_INTRODUCTION: "¬¬I"

    #Classical-specific axiom/rule
    NEGATION_NEGATION_ELIMINATION: "¬¬E",

    #Reglas Derivadas Comunes
    EXCLUDED_MIDDLE: "LEM",
    PBC: "PBC"

def parse_formula(expr: str) -> Prop:
    # Ambiente seguro con solo los constructores disponibles
    allowed_globals = {
        'VAR': VAR,
        'AND': AND,
        'OR': OR,
        'NEG': NEG,
        'IMPLIES': IMPLIES,
        'BOTTOM': BOTTOM
    }
    return eval(expr, allowed_globals)

def getContext() -> list(Prop):
    pass

def getFormula() -> Prop:
    pass

def getResolvent() -> Prop:
    pass

class Resolver:
    pass

def esReglaAplicable(prop: Prop, regla: LogicRules, context: List[Prop]) -> bool:
    """
    Checks if a given proposition 'prop' has the correct structure
    to be the conclusion of the specified 'regla' (rule).
    It also checks if the proposition 'prop' itself is an axiom within the given context.
    """
    match regla:
        case LogicRules.AXIOM:
            return prop in context # Check if the proposition is in the provided context

        case LogicRules.AND_INTRODUCTION:
            return isinstance(prop, AND)

        case LogicRules.AND_ELIMINATION_1 | LogicRules.AND_ELIMINATION_2 | \
             LogicRules.IMPLICATION_ELIMINATION | LogicRules.OR_ELIMINATION | \
             LogicRules.BOTTOM_ELIMINATION | LogicRules.NEGATION_NEGATION_ELIMINATION | \
             LogicRules.PBC:
            # These rules can conclude any proposition type, so their conclusion's structure
            # itself doesn't restrict applicability. The actual premises are key.
            return True

        case LogicRules.IMPLICATION_INTRODUCTION:
            return isinstance(prop, IMPLIES)

        case LogicRules.OR_INTRODUCTION_1 | LogicRules.OR_INTRODUCTION_2:
            return isinstance(prop, OR)

        case LogicRules.NEGATION_INTRODUCTION | LogicRules.MODUS_TOLLENS:
            return isinstance(prop, NEG)

        case LogicRules.NEGATION_ELIMINATION:
            return isinstance(prop, BOTTOM)

        case LogicRules.NEGATION_NEGATION_INTRODUCTION:
            return isinstance(prop, NEG) and isinstance(prop.prop, NEG)

        case LogicRules.EXCLUDED_MIDDLE:
            return isinstance(prop, OR) and \
                   isinstance(prop.right, NEG) and \
                   prop.left == prop.right.prop
        case _:
            raise ValueError(f"Regla no reconocida o no implementada: {regla.value}")