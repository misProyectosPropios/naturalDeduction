from dataclasses import dataclass
from typing import Union, List, Set, Tuple, Optional
from lexer import Lexer
from logic import Prop, NEG, AND, OR, IMPLIES, BOTTOM, VAR, LogicRules



# --- Helper Functions for User Input Parsing (from previous interactions) ---
def parse_formula(expr: str) -> Prop:
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

def parse_formula_with_lexer(expr: str) -> Optional[Prop]:
    """
    Parse a formula using the lexer and parser.
    Returns the parsed Prop or None if parsing fails.
    """
    try:
        from parser import Parser
        from lexer import Token, TokenType
        lexer = Lexer(expr)
        tokens = lexer.tokenize()
        tokens.append(Token(TokenType.EOF))  # Add EOF token
        
        parser = Parser(tokens)
        return parser.parse()
    except Exception as e:
        raise ValueError(f"Parse error: {e}")

def getContext() -> List[Prop]:
    """
    Get context propositions from user input.
    Uses the parser to parse each proposition.
    """
    print("\n=== Enter Context Propositions ===")
    print('Format: "P" -> "Q" ^ "R" V -"S" _ (for variables, implication, and, or, not, bottom)')
    print("Empty line to finish.\n")
    context = []
    prop_count = 0
    
    while True:
        try:
            user_input = input(f"Proposition {prop_count + 1} > ").strip()
            if not user_input:
                print(f"\nContext complete with {prop_count} proposition(s).")
                break
            
            # Try to parse with lexer/parser
            prop = parse_formula_with_lexer(user_input)
            context.append(prop)
            prop_count += 1
            print(f"✓ Parsed successfully: {prop.prettify()}")
            
        except ValueError as e:
            print(f"✗ {e} Please try again.")
    
    return context

def getResolvent() -> Prop:
    """
    Get the resolvent (goal) proposition from user input.
    Uses the parser to parse the proposition.
    """
    print("\n=== Enter Goal Proposition (Resolvent) ===")
    print('Format: "P" -> "Q" ^ "R" V -"S" _ (for variables, implication, and, or, not, bottom)\n')
    
    while True:
        try:
            user_input = input("Goal > ").strip()
            if not user_input:
                print("Goal cannot be empty. Please try again.")
                continue
            
            # Try to parse with lexer/parser
            prop = parse_formula_with_lexer(user_input)
            print(f"✓ Parsed successfully: {prop.prettify()}\n")
            return prop
            
        except ValueError as e:
            print(f"✗ {e} Please try again.")

def getFormula() -> Prop:
    """
    Prompts the user to input a formula and parses it into a Prop object.
    """
    print('Enter a formula (e.g., "P" -> "Q" ^ "R"):\n')
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                print("Formula cannot be empty.")
                continue
            return parse_formula_with_lexer(user_input)
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")

# --- Paso Class (as per your previous context) ---
@dataclass
class Paso:
    contexto: List[Prop]
    resolvente: Prop

    def __post_init__(self):
        # Normalize missing context to an empty list
        if self.contexto is None:
            self.contexto = []

        # Ensure context elements are Props
        if not all(isinstance(item, Prop) for item in self.contexto):
            raise TypeError("All elements in 'contexto' must be instances of Prop.")
        # Ensure resolvente is a Prop
        if not isinstance(self.resolvente, Prop):
            raise TypeError("'resolvente' must be an instance of Prop.")

    def toString(self) -> str:
        contexto_str = ', '.join(prop.prettify() for prop in self.contexto)
        return f"{contexto_str} ⊢ {self.resolvente.prettify()}"

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
        self.contexto_inicial = contexto_inicial
        self.resolvente_final = resolvente_final

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

    def _validate_step(self, num_pos: int) -> bool:
        """Validate that the step can be resolved."""
        if num_pos not in self.pasos_a_resolver:
            print(f"Error: Paso {num_pos} ya está resuelto o no existe como paso a resolver.")
            return False
        if num_pos >= len(self.lista_de_pasos) or num_pos < 0:
            print(f"Error: El número de posición {num_pos} está fuera de los límites de la lista de pasos.")
            return False
        return True
    
    def _get_paso(self, num_pos: int) -> Paso:
        """Get the Paso object at the given position."""
        return self.lista_de_pasos[num_pos][0]
    
    def _add_substeps(self, parent_idx: int, substeps: List[Paso]) -> List[int]:
        """Add substeps to the proof tree. Returns list of new indices."""
        new_indices = []
        for substep in substeps:
            new_idx = len(self.lista_de_pasos)
            self.lista_de_pasos.append((substep, parent_idx, None))
            new_indices.append(new_idx)
            self.pasos_a_resolver.add(new_idx)
        return new_indices
    
    def _mark_resolved(self, num_pos: int, regla: LogicRules):
        """Mark a step as resolved with the given rule."""
        paso, _, _ = self.lista_de_pasos[num_pos]
        self.lista_de_pasos[num_pos] = (paso, num_pos, regla)
        self.pasos_a_resolver.discard(num_pos)
    
    def _try_axiom(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply AXIOM rule."""
        if current_paso.resolvente in current_paso.contexto:
            self._mark_resolved(num_pos, LogicRules.AXIOM)
            return True
        return False
    
    def _try_and_introduction(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply AND_INTRODUCTION rule."""
        substeps = [
            Paso(contexto=current_paso.contexto, resolvente=current_paso.resolvente.left),
            Paso(contexto=current_paso.contexto, resolvente=current_paso.resolvente.right)
        ]
        self._add_substeps(num_pos, substeps)
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_and_elimination_1(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply AND_ELIMINATION_1 rule."""
        substep = Paso(contexto=current_paso.contexto, resolvente=current_paso.resolvente.left)
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_and_elimination_2(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply AND_ELIMINATION_2 rule."""
        substep = Paso(contexto=current_paso.contexto, resolvente=current_paso.resolvente.right)
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_implication_introduction(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply IMPLICATION_INTRODUCTION rule."""
        tau = current_paso.resolvente.premise
        sigma = current_paso.resolvente.conclusion
        substep = Paso(contexto=current_paso.contexto + [tau], resolvente=sigma)
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_implication_elimination(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply IMPLICATION_ELIMINATION rule."""
        tau = getFormula()
        sigma = current_paso.resolvente
        substeps = [
            Paso(contexto=current_paso.contexto, resolvente=tau),
            Paso(contexto=current_paso.contexto, resolvente=tau.implies(sigma))
        ]
        self._add_substeps(num_pos, substeps)
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_or_introduction_1(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply OR_INTRODUCTION_1 rule."""
        substep = Paso(contexto=current_paso.contexto, resolvente=current_paso.resolvente.left)
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_or_introduction_2(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply OR_INTRODUCTION_2 rule."""
        substep = Paso(contexto=current_paso.contexto, resolvente=current_paso.resolvente.right)
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_or_elimination(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply OR_ELIMINATION rule."""
        a = getFormula()
        b = getFormula()
        sigma = current_paso.resolvente
        substeps = [
            Paso(contexto=current_paso.contexto, resolvente=a.or_with(b)),
            Paso(contexto=current_paso.contexto + [a], resolvente=sigma),
            Paso(contexto=current_paso.contexto + [b], resolvente=sigma)
        ]
        self._add_substeps(num_pos, substeps)
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_negation_introduction(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply NEGATION_INTRODUCTION rule."""
        sigma = current_paso.resolvente.prop
        substep = Paso(contexto=current_paso.contexto + [sigma], resolvente=BOTTOM())
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_negation_elimination(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply NEGATION_ELIMINATION rule."""
        a = getFormula()
        substeps = [
            Paso(contexto=current_paso.contexto, resolvente=a),
            Paso(contexto=current_paso.contexto, resolvente=a.negate())
        ]
        self._add_substeps(num_pos, substeps)
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_bottom_elimination(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply BOTTOM_ELIMINATION rule."""
        tau = getFormula()
        substeps = [
            Paso(contexto=current_paso.contexto, resolvente=BOTTOM()),
            Paso(contexto=current_paso.contexto, resolvente=tau)
        ]
        self._add_substeps(num_pos, substeps)
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_modus_tollens(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply MODUS_TOLLENS rule."""
        sigma = current_paso.resolvente.prop
        substep = Paso(contexto=current_paso.contexto, resolvente=sigma.implies(BOTTOM()))
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_negation_negation_introduction(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply NEGATION_NEGATION_INTRODUCTION rule."""
        neg_sigma = current_paso.resolvente.prop
        substep = Paso(contexto=current_paso.contexto, resolvente=neg_sigma.negate())
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_negation_negation_elimination(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply NEGATION_NEGATION_ELIMINATION rule."""
        neg_neg_sigma = current_paso.resolvente.prop
        substep = Paso(contexto=current_paso.contexto, resolvente=neg_neg_sigma.prop)
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_excluded_middle(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply EXCLUDED_MIDDLE rule."""
        a = current_paso.resolvente.left
        substep = Paso(contexto=current_paso.contexto, resolvente=a.or_with(a.negate()))
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
    def _try_pbc(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply PBC (Proof by Contradiction) rule."""
        sigma = current_paso.resolvente
        substep = Paso(contexto=current_paso.contexto + [sigma.negate()], resolvente=BOTTOM())
        self._add_substeps(num_pos, [substep])
        self.pasos_a_resolver.discard(num_pos)
        return True
    
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
        if not self._validate_step(num_pos):
            return False
        
        current_paso = self._get_paso(num_pos)
        
        if not esReglaAplicable(current_paso, regla):
            print(f"Error: La regla '{regla.value}' no es estructuralmente aplicable a la proposición {current_paso.resolvente.prettify()}.")
            return False
        
        print(f"Aplicando regla '{regla.value}' al paso {num_pos} (Prop: {current_paso.resolvente.prettify()})...")
        
        # Try to apply the rule using the appropriate handler
        handlers = {
            LogicRules.AXIOM: self._try_axiom,
            LogicRules.AND_INTRODUCTION: self._try_and_introduction,
            LogicRules.AND_ELIMINATION_1: self._try_and_elimination_1,
            LogicRules.AND_ELIMINATION_2: self._try_and_elimination_2,
            LogicRules.IMPLICATION_INTRODUCTION: self._try_implication_introduction,
            LogicRules.IMPLICATION_ELIMINATION: self._try_implication_elimination,
            LogicRules.OR_INTRODUCTION_1: self._try_or_introduction_1,
            LogicRules.OR_INTRODUCTION_2: self._try_or_introduction_2,
            LogicRules.OR_ELIMINATION: self._try_or_elimination,
            LogicRules.NEGATION_INTRODUCTION: self._try_negation_introduction,
            LogicRules.NEGATION_ELIMINATION: self._try_negation_elimination,
            LogicRules.BOTTOM_ELIMINATION: self._try_bottom_elimination,
            LogicRules.MODUS_TOLLENS: self._try_modus_tollens,
            LogicRules.NEGATION_NEGATION_INTRODUCTION: self._try_negation_negation_introduction,
            LogicRules.NEGATION_NEGATION_ELIMINATION: self._try_negation_negation_elimination,
            LogicRules.EXCLUDED_MIDDLE: self._try_excluded_middle,
            LogicRules.PBC: self._try_pbc,
        }
        
        handler = handlers.get(regla)
        if handler:
            return handler(num_pos, current_paso)
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
                    formula_str = paso.resolvente.prettify()
                    print(f"  [{idx}]: {formula_str}")
                except IndexError:
                    print(f"  [{idx}]: <Invalid index>")
        else:
            print("All steps resolved!")


def choose_rule() -> LogicRules:
    """Allow the user to choose a rule by number or by its value/name."""
    print("\nAvailable rules:")
    rules = list(LogicRules)
    for idx, rule in enumerate(rules, start=1):
        print(f"  {idx}. {rule.value}")

    while True:
        rule_input = input("\nEnter the rule number or rule value: ").strip()
        if not rule_input:
            print("Rule selection cannot be empty. Please enter a number or rule name.")
            continue

        if rule_input.isdigit():
            index = int(rule_input)
            if 1 <= index <= len(rules):
                return rules[index - 1]
            print(f"✗ Invalid rule number: {index}. Please choose a number between 1 and {len(rules)}.")
            continue

        for rule in rules:
            if rule_input == rule.value or rule_input.upper() == rule.name:
                return rule

        print(f"✗ Unknown rule: '{rule_input}'. Please enter a valid rule number or rule name.")


def main():
    """
    Main function to manage the natural deduction proof process.
    """
    print("=" * 60)
    print("Welcome to the Natural Deduction Resolver!")
    print("=" * 60)
    
    # Get context and resolvent from the user
    try:
        contexto = getContext()
        resolvente = getResolvent()
    except KeyboardInterrupt:
        print("\n\nProof cancelled.")
        return
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return
    
    # Validate that we have at least a goal
    if resolvente is None:
        print("Error: Could not parse goal proposition.")
        return
    
    # Show the parsed formulas to the user
    print("\n" + "=" * 60)
    print("PARSED FORMULAS")
    print("=" * 60)
    
    if contexto:
        print("\nContext (Assumptions):")
        for i, prop in enumerate(contexto, 1):
            print(f"  {i}. {prop.prettify()}")
    else:
        print("\nContext: (empty)")
    
    print(f"\nGoal: {resolvente.prettify()}")
    print("\n" + "=" * 60)
    
    # Create the resolver
    resolver = Resolver(contexto, resolvente)
    
    print("\nStarting proof...\n")

    while not resolver.isProofComplete():
        resolver.mostrar_prueba()
        print("\nSteps to resolve:", sorted(resolver.pasos_a_resolver))
        
        try:
            # Prompt user to select a step and a rule
            num_pos = int(input("\nEnter the step number to apply a rule (or -1 to quit): "))
            
            if num_pos == -1:
                print("Proof cancelled.")
                break
            
            regla = choose_rule()

            # Apply the rule
            if resolver.aplicarRegla(num_pos, regla):
                print(f"✓ Rule '{regla.value}' applied successfully to step {num_pos}.")
            else:
                print(f"✗ Failed to apply rule '{regla.value}' to step {num_pos}.")
                
        except ValueError:
            print("✗ Invalid input. Please enter a valid step number.")
        except KeyboardInterrupt:
            print("\n\nProof cancelled.")
            break

    if resolver.isProofComplete():
        print("\n" + "=" * 60)
        print("SUCCESS! PROOF COMPLETE!")
        print("=" * 60)
        resolver.mostrar_prueba()
    else:
        print("\nProof incomplete.")


if __name__ == "__main__":
    main()