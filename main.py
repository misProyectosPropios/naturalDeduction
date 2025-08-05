from dataclasses import dataclass
from typing import Union, List, Set, Tuple
from enum import Enum

class Prop: pass

@dataclass(eq=True, frozen=True)
class NEG(Prop):
    prop: Prop

@dataclass(eq=True, frozen=True)
class AND(Prop):
    left: Prop
    right: Prop

@dataclass(eq=True, frozen=True)
class OR(Prop):
    left: Prop
    right: Prop

@dataclass(eq=True, frozen=True)
class IMPLIES(Prop):
    premise: Prop
    conclusion: Prop

@dataclass(eq=True, frozen=True)
class BOTTOM(Prop):
    pass

@dataclass(eq=True, frozen=True)
class VAR(Prop):
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
        return eval(expr, {"__builtins__": None}, allowed_globals)
    except Exception as e:
        raise ValueError(f"Error parsing formula '{expr}': {e}")

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

def getFormula() -> Prop:
    """
    Prompts the user to input a formula and parses it into a Prop object.
    """
    print("Enter a formula (e.g., 'VAR(\"P\")', 'AND(VAR(\"A\"), VAR(\"B\"))'):")
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                print("Formula cannot be empty.")
                continue
            return parse_formula(user_input)
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")

# --- Paso Class (as per your previous context) ---
@dataclass
class Paso:
    contexto: List[Prop]
    resolvente: Prop

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
        return proposition in self.contexto

def esReglaAplicable(paso: Paso, regla: LogicRules) -> bool:
    """
    Checks if a given step 'paso' has the correct structure
    to be the conclusion of the specified 'regla' (rule).
    It also checks if the proposition in 'paso.resolvente' itself is an axiom within the given context.
    """
    prop = paso.resolvente
    context = paso.contexto

    match regla:
        case LogicRules.AXIOM:
            return prop in context  # Check if the proposition is in the provided context

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
        contexto_inicial = contexto_inicial
        resolvente_final = resolvente_final

        # listaDePasos store tuples: (Paso object, step_index, rule_applied)
        initial_goal_paso = Paso(contexto_inicial, resolvente_final)
        self.lista_de_pasos: List[Tuple[Paso, int, LogicRules]] = [
            (initial_goal_paso, 0, None) 
        ]
        self.pasos_a_resolver: Set[int] = {0}  

    def isProofComplete(self) -> bool:
        """
        Checks if the proof is complete.
        A proof is complete if there are no more steps left to resolve.
        """
        return len(self.pasos_a_resolver) == 0

    def aplicarRegla(self, num_pos: int, regla: LogicRules) -> bool:
        """
        Attempts to apply a given rule to the step at `num_pos`.
        If successful, it updates `pasos_a_resolver` and `lista_de_pasos`.

        Args:
            num_pos (int): The 0-based index of the step to which the rule is being applied.
            regla (LogicRules): The rule to attempt to apply.

        Returns:
            bool: True if the rule was successfully applied, False otherwise.
        """
        if num_pos not in self.pasos_a_resolver:
            print(f"Error: Paso {num_pos} ya está resuelto o no existe como paso a resolver.")
            return False

        if num_pos >= len(self.lista_de_pasos) or num_pos < 0:
            print(f"Error: El número de posición {num_pos} está fuera de los límites de la lista de pasos.")
            return False

        current_paso, _, _ = self.lista_de_pasos[num_pos]

        if not esReglaAplicable(current_paso, regla):
            print(f"Error: La regla '{regla.value}' no es estructuralmente aplicable a la proposición {pretty_print(current_paso.resolvente)}.")
            return False

        print(f"Aplicando regla '{regla.value}' al paso {num_pos} (Prop: {pretty_print(current_paso.resolvente)})...")

        match regla:
            case LogicRules.AXIOM:
                if current_paso.resolvente in self.contexto_inicial:
                    self.pasos_a_resolver.remove(num_pos)
                    self.lista_de_pasos[num_pos] = (
                        Paso(current_paso.contexto, current_paso.resolvente), num_pos, regla)
                    return True
                else:
                    return False

            case LogicRules.AND_INTRODUCTION:
                izquierda = current_paso.resolvente.left
                derecha = current_paso.resolvente.right
                paso_izq = Paso(contexto=current_paso.contexto, resolvente=izquierda)
                paso_der = Paso(contexto=current_paso.contexto, resolvente=derecha)
                nuevo_idx_izq = len(self.lista_de_pasos)
                nuevo_idx_der = len(self.lista_de_pasos) + 1
                self.lista_de_pasos.append((paso_izq, num_pos, None))
                self.lista_de_pasos.append((paso_der, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.update([nuevo_idx_izq, nuevo_idx_der])
                return True

            case LogicRules.AND_ELIMINATION_1:
                izquierda = current_paso.resolvente.left
                paso_izq = Paso(contexto=current_paso.contexto, resolvente=izquierda)
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_izq, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.AND_ELIMINATION_2:
                derecha = current_paso.resolvente.right
                paso_der = Paso(contexto=current_paso.contexto, resolvente=derecha)
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_der, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.IMPLICATION_INTRODUCTION:
                tau = current_paso.resolvente.premise
                sigma = current_paso.resolvente.conclusion
                paso_nuevo = Paso(contexto=current_paso.contexto + [tau], resolvente=sigma)
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_nuevo, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.IMPLICATION_ELIMINATION:
                tau = getFormula()
                sigma = current_paso.resolvente
                paso_tau = Paso(contexto=current_paso.contexto, resolvente=tau)
                paso_impl = Paso(contexto=current_paso.contexto, resolvente=tau.impl(sigma))
                idx_tau = len(self.lista_de_pasos)
                idx_impl = len(self.lista_de_pasos) + 1
                self.lista_de_pasos.append((paso_tau, num_pos, None))
                self.lista_de_pasos.append((paso_impl, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.update([idx_tau, idx_impl])
                return True

            case LogicRules.OR_INTRODUCTION_1:
                a = current_paso.resolvente.left
                paso_a = Paso(contexto=current_paso.contexto, resolvente=a)
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_a, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.OR_INTRODUCTION_2:
                b = current_paso.resolvente.right
                paso_b = Paso(contexto=current_paso.contexto, resolvente=b)
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_b, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.OR_ELIMINATION:
                a = getFormula()
                b = getFormula()
                sigma = current_paso.resolvente
                paso_or = Paso(contexto=current_paso.contexto, resolvente=a.or_(b))
                paso_a = Paso(contexto=current_paso.contexto + [a], resolvente=sigma)
                paso_b = Paso(contexto=current_paso.contexto + [b], resolvente=sigma)
                idx_or = len(self.lista_de_pasos)
                idx_a = len(self.lista_de_pasos) + 1
                idx_b = len(self.lista_de_pasos) + 2
                self.lista_de_pasos.append((paso_or, num_pos, None))
                self.lista_de_pasos.append((paso_a, num_pos, None))
                self.lista_de_pasos.append((paso_b, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.update([idx_or, idx_a, idx_b])
                return True

            case LogicRules.NEGATION_INTRODUCTION:
                sigma = current_paso.resolvente.prop
                paso_bottom = Paso(contexto=current_paso.contexto + [sigma], resolvente=BOTTOM())
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_bottom, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.NEGATION_ELIMINATION:
                a = getFormula()
                paso_a = Paso(contexto=current_paso.contexto, resolvente=a)
                paso_neg_a = Paso(contexto=current_paso.contexto, resolvente=NEG(a))
                idx_a = len(self.lista_de_pasos)
                idx_neg_a = len(self.lista_de_pasos) + 1
                self.lista_de_pasos.append((paso_a, num_pos, None))
                self.lista_de_pasos.append((paso_neg_a, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.update([idx_a, idx_neg_a])
                return True

            case LogicRules.BOTTOM_ELIMINATION:
                tau = getFormula()
                paso_bottom = Paso(contexto=current_paso.contexto, resolvente=BOTTOM())
                paso_tau = Paso(contexto=current_paso.contexto, resolvente=tau)
                idx_bottom = len(self.lista_de_pasos)
                idx_tau = len(self.lista_de_pasos) + 1
                self.lista_de_pasos.append((paso_bottom, num_pos, None))
                self.lista_de_pasos.append((paso_tau, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.update([idx_bottom, idx_tau])
                return True

            case LogicRules.MODUS_TOLLENS:
                sigma = current_paso.resolvente.prop
                paso_impl = Paso(contexto=current_paso.contexto, resolvente=sigma.impl(BOTTOM()))
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_impl, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.NEGATION_NEGATION_INTRODUCTION:
                neg_sigma = current_paso.resolvente.prop
                paso_neg_neg = Paso(contexto=current_paso.contexto, resolvente=neg_sigma.neg())
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_neg_neg, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.NEGATION_NEGATION_ELIMINATION:
                neg_neg_sigma = current_paso.resolvente.prop
                paso_sigma = Paso(contexto=current_paso.contexto, resolvente=neg_neg_sigma.prop)
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_sigma, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.EXCLUDED_MIDDLE:
                a = current_paso.resolvente.left
                paso_or = Paso(contexto=current_paso.contexto, resolvente=a.or_(a.neg()))
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_or, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case LogicRules.PBC:
                sigma = current_paso.resolvente
                paso_bottom = Paso(contexto=current_paso.contexto + [sigma.neg()], resolvente=BOTTOM())
                nuevo_idx = len(self.lista_de_pasos)
                self.lista_de_pasos.append((paso_bottom, num_pos, None))
                self.pasos_a_resolver.remove(num_pos)
                self.pasos_a_resolver.add(nuevo_idx)
                return True

            case _:
                return False

    def mostrar_prueba(self):
        """
        Displays the current state of the proof, showing steps from last to first.
        """
        print("\n--- Current Proof State (Last to First) ---")
        if not self.lista_de_pasos:
            print("No steps in the proof yet.")
            return

        # Mostrar pasos en orden inverso
        reversed_steps = list(reversed(self.lista_de_pasos))
        for i, (paso, idx_original, regla_aplicada) in enumerate(reversed_steps):
            real_index = len(self.lista_de_pasos) - 1 - i
            status = " (UNRESOLVED)" if idx_original in self.pasos_a_resolver else ""
            references_str = ""
            regla_str = regla_aplicada.value if regla_aplicada else "No rule"
            print(f"[{idx_original}]{status}: {paso.toString()} by {regla_str}{references_str}")

        print("------------------------------------------")

        # Mostrar las fórmulas sin resolver con su representación
        if self.pasos_a_resolver:
            print("Steps to resolve:")
            for idx in sorted(self.pasos_a_resolver):
                try:
                    paso, _, _ = self.lista_de_pasos[idx]
                    formula_str = pretty_print(paso.resolvente)
                    print(f"  [{idx}]: {formula_str}")
                except IndexError:
                    print(f"  [{idx}]: <Invalid index>")
        else:
            print("All steps resolved!")

def main():
    """
    Main function to manage the natural deduction proof process.
    """
    print("Welcome to the Natural Deduction Resolver!")
    
    # Get context and resolvent from the user
    contexto = getContext()
    resolvente = getResolvent()
    resolver = Resolver(contexto, resolvente)

    while not resolver.isProofComplete():
        resolver.mostrar_prueba()
        print("\nSteps to resolve:", sorted(resolver.pasos_a_resolver))
        
        try:
            # Prompt user to select a step and a rule
            num_pos = int(input("Enter the step number to apply a rule: "))
            print("Available rules:")
            for rule in LogicRules:
                print(f"- {rule.value}")
            regla_input = input("Enter the rule to apply: ").strip()
            regla = LogicRules(regla_input)

            # Apply the rule
            if resolver.aplicarRegla(num_pos, regla):
                print(f"Rule '{regla.value}' applied successfully to step {num_pos}.")
            else:
                print(f"Failed to apply rule '{regla.value}' to step {num_pos}.")
        except (ValueError, KeyError):
            print("Invalid input. Please try again.")

    print("\nProof complete!")
    resolver.mostrar_prueba()

main()