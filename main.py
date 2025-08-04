from dataclasses import dataclass
from typing import Union, List, Set, Tuple
from enum import Enum

# --- Proposition Types ---
# Note: Added 'IMPLIES' to the Union for Prop type hint.
Prop = Union["NEG", "AND", "OR", "BOTTOM", "VAR", "IMPLIES"]

@dataclass(eq=True, frozen=True) # Added eq=True, frozen=True for easy comparison and use in sets/dicts
class NEG:
    prop: Prop

@dataclass(eq=True, frozen=True)
class AND:
    left: Prop
    right: Prop

@dataclass(eq=True, frozen=True)
class OR:
    left: Prop
    right: Prop

@dataclass(eq=True, frozen=True)
class IMPLIES:
    premise: Prop
    conclusion: Prop

@dataclass(eq=True, frozen=True)
class BOTTOM:
    pass

@dataclass(eq=True, frozen=True)
class VAR:
    name: str

# --- Pretty Print Function ---
def pretty_print(p: Prop) -> str:
    match p:
        case VAR(name):
            return name
        case NEG(expr):
            return f"¬({pretty_print(expr)})"
        case AND(left, right):
            return f"({pretty_print(left)} ∧ {pretty_print(right)})"
        case OR(left, right):
            return f"({pretty_print(left)} ∨ {pretty_print(right)})"
        case IMPLIES(premise, conclusion):
            return f"({pretty_print(premise)} → {pretty_print(conclusion)})" # Changed ⇒ to → for consistency
        case BOTTOM():
            return "⊥"
        case _:
            return "UNKNOWN_PROP_TYPE" # Fallback for unexpected types

# --- Logic Rules Enum ---
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

    # Reglas derivadas
    MODUS_TOLLENS = "MT"
    NEGATION_NEGATION_INTRODUCTION = "¬¬I"

    # Classical-specific axiom/rule
    NEGATION_NEGATION_ELIMINATION = "¬¬E"

    # Reglas Derivadas Comunes
    EXCLUDED_MIDDLE = "LEM"
    PBC = "PBC"

# --- Helper Functions for User Input Parsing (from previous interactions) ---
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
    try:
        # eval is powerful but can be risky if input is not controlled.
        # For a production system, consider a dedicated parsing library.
        return eval(expr, {"__builtins__": None}, allowed_globals)
    except Exception as e:
        raise ValueError(f"Error parsing formula '{expr}': {e}")

# Placeholder for user input functions - you'll connect these to actual input later
def getContext() -> List[Prop]:
    print("Enter context propositions (e.g., 'VAR(\"P\")', 'IMPLIES(VAR(\"P\"), VAR(\"Q\"))'). Empty line to finish:")
    context = []
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                break
            prop = parse_formula(user_input)
            context.append(prop)
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")
    return context

def getResolvent() -> Prop:
    print("Enter the resolvent proposition (e.g., 'VAR(\"R\")', 'AND(VAR(\"A\"), NEG(VAR(\"B\")))':")
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                print("Resolvent cannot be empty.")
                continue
            prop = parse_formula(user_input)
            return prop
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")

# --- esReglaAplicable Function (corrected and modified for Resolver class) ---
# This version assumes 'contexto' will be passed from the Resolver instance.
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

# --- Paso Class (as per your previous context) ---
@dataclass
class Paso:
    contexto: List[Prop]
    resolvente: Prop
    # Adding an optional 'rule_applied' and 'references' for better representation in the proof
    rule_applied: LogicRules = None
    references: Tuple[int, ...] = tuple() # Indices of steps this step depends on

    def __post_init__(self):
        # Ensure context elements are Props
        if not all(isinstance(item, Prop) for item in self.contexto):
            raise TypeError("All elements in 'contexto' must be instances of Prop.")
        # Ensure resolvente is a Prop
        if not isinstance(self.resolvente, Prop):
            raise TypeError("'resolvente' must be an instance of Prop.")

    def toString(self) -> str:
        contexto_str = ', '.join(pretty_print(prop) for prop in self.contexto)
        return f"{contexto_str} ⊢ {pretty_print(self.resolvente)}"

    def isInTheContext(self, proposition: Prop) -> bool:
        # Devuelve true si la proposición está en el contexto
        # Using the __eq__ method from dataclass (if eq=True is set)
        return proposition in self.contexto

# --- Resolver Class ---
class Resolver:
    """
    Manages the state of a natural deduction proof.
    """
    def __init__(self, contexto_inicial: List[Prop], resolvente_final: Prop):
        """
        Initializes the Resolver with the initial context (axioms/assumptions)
        and the final proposition to be proven (resolvent).
        """
        self.contexto_inicial = contexto_inicial
        self.resolvente_final = resolvente_final

        # listaDePasos will store tuples: (Paso object, step_index, rule_applied)
        # The first step represents the goal to be proven.
        initial_goal_paso = Paso(contexto_inicial, resolvente_final, rule_applied=LogicRules.AXIOM, references=())
        self.lista_de_pasos: List[Tuple[Paso, int, LogicRules]] = [
            (initial_goal_paso, 0, LogicRules.AXIOM) # Or a custom "GOAL" rule
        ]

        # pasos_a_resolver stores indices of steps that still need a rule applied
        # to justify them. Initially, only the goal needs to be justified.
        self.pasos_a_resolver: Set[int] = {0} # Use 0-based indexing for the first step

        # You might also want a way to keep track of established/proven propositions
        # based on the steps already completed. This is crucial for rule application.
        self.proposiciones_probadas: List[Prop] = [] # List of propositions already derived

    def isProofComplete(self) -> bool:
        """
        Checks if the proof is complete.
        A proof is complete if there are no more steps left to resolve.
        """
        return len(self.pasos_a_resolver) == 0

    def aplicarRegla(self, num_pos: int, regla: LogicRules, *referencias_indices: int) -> bool:
        """
        Attempts to apply a given rule to the step at `num_pos`.
        If successful, it updates `pasos_a_resolver` and `lista_de_pasos`.

        Args:
            num_pos (int): The 0-based index of the step to which the rule is being applied.
            regla (LogicRules): The rule to attempt to apply.
            *referencias_indices (int): Optional, indices of previous steps this rule depends on.

        Returns:
            bool: True if the rule was successfully applied, False otherwise.
        """
        if num_pos not in self.pasos_a_resolver:
            print(f"Error: Paso {num_pos} ya está resuelto o no existe como paso a resolver.")
            return False

        if num_pos >= len(self.lista_de_pasos):
            print(f"Error: El número de posición {num_pos} está fuera de los límites de la lista de pasos.")
            return False

        current_paso, _, _ = self.lista_de_pasos[num_pos]
        
        # 1. Check if the rule is structurally applicable to the resolvent of this step
        #    Note: This is only a structural check. It does not check premises.
        if not esReglaAplicable(current_paso.resolvente, regla, self.contexto_inicial):
            print(f"Error: La regla '{regla.value}' no es estructuralmente aplicable a la proposición {pretty_print(current_paso.resolvente)}.")
            return False

        # 2. Implement the rule logic. This is where the complexity lies.
        #    This section needs to be expanded significantly based on each rule.
        #    For now, it's a placeholder.
        #    For each rule:
        #    a. Check if the required premises (from `self.lista_de_pasos` or `self.contexto_inicial`)
        #       are available. This will involve using `referencias_indices`.
        #    b. If premises are available and the rule's conditions are met:
        #       i. Create new `Paso` objects (new sub-goals to resolve) if the rule introduces them.
        #          e.g., for Implication Introduction, you'd add a new step assuming the premise.
        #       ii. Add new steps to `self.lista_de_pasos`.
        #       iii. Add the indices of new steps to `self.pasos_a_resolver`.
        #       iv. Remove `num_pos` from `self.pasos_a_resolver`.
        #       v. Update the `rule_applied` and `references` of `current_paso` in `self.lista_de_pasos`.

        print(f"Aplicando regla '{regla.value}' al paso {num_pos} (Prop: {pretty_print(current_paso.resolvente)})...")

        # Placeholder logic for successful application for AXIOM only for demonstration
        if regla == LogicRules.AXIOM:
            if current_paso.resolvente in self.contexto_inicial:
                self.pasos_a_resolver.remove(num_pos)
                # Update the rule and references for the completed step
                # A new tuple is created because tuples are immutable
                self.lista_de_pasos[num_pos] = (
                    Paso(current_paso.contexto, current_paso.resolvente, rule_applied=regla, references=references_indices),
                    num_pos,
                    regla
                )
                self.proposiciones_probadas.append(current_paso.resolvente)
                print(f"Paso {num_pos} (AXIOM) resuelto: {pretty_print(current_paso.resolvente)}")
                return True
            else:
                print(f"Error: {pretty_print(current_paso.resolvente)} no es un axioma en el contexto.")
                return False
        
        # For other rules, you'd need specific logic for checking premises and adding new steps
        print("Logic for this rule is not yet fully implemented.")
        return False # Placeholder

    def mostrar_prueba(self):
        """
        Displays the current state of the proof, showing steps from last to first.
        """
        print("\n--- Current Proof State (Last to First) ---")
        if not self.lista_de_pasos:
            print("No steps in the proof yet.")
            return

        # Create a copy and reverse it for display
        reversed_steps = list(reversed(self.lista_de_pasos))
        for i, (paso, original_idx, rule) in enumerate(reversed_steps):
            status = " (UNRESOLVED)" if original_idx in self.pasos_a_resolver else ""
            references_str = f" [{', '.join(map(str, paso.references))}]" if paso.references else ""
            print(f"[{original_idx}]{status}: {paso.toString()} by {rule.value}{references_str}")
        print("------------------------------------------")
        print(f"Steps to resolve: {sorted(list(self.pasos_a_resolver))}")
        print(f"Proven propositions: {[pretty_print(p) for p in self.proposiciones_probadas]}")