from dataclasses import dataclass
from typing import Callable, Union, List, Set, Tuple, Optional
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


@dataclass
class Rule:
    key: str
    value: str
    applicable: Callable[[Paso], bool]
    handler: Callable[['Resolver', int, Paso], bool]
    description: str = ""
    precondition: str = ""
    postcondition: str = ""


def make_rule(
    key: str,
    value: str,
    applicable: Callable[[Paso], bool],
    make_substeps: Optional[Callable[[Paso], List[Paso]]] = None,
    handler: Optional[Callable[['Resolver', int, Paso], bool]] = None,
    description: str = "",
    precondition: str = "",
    postcondition: str = ""
) -> Rule:
    if handler is None:
        if make_substeps is None:
            raise ValueError("Either handler or make_substeps must be provided.")

        def handler(self, num_pos: int, current_paso: Paso) -> bool:
            return self._try_rule(num_pos, current_paso, make_substeps)

    return Rule(
        key=key,
        value=value,
        applicable=applicable,
        handler=handler,
        description=description,
        precondition=precondition,
        postcondition=postcondition,
    )


class Resolver:
    """
    Manages the state of a natural deduction proof.
    """
    def __init__(self, contexto_inicial: List[Prop], resolvente_final: Prop, rules: Optional[List[Rule]] = None):
        """
        Initializes the Resolver with the initial context (axioms/assumptions)
        and the final proposition to be proven (resolvent).
        """
        self.contexto_inicial = contexto_inicial
        self.resolvente_final = resolvente_final
        self.rules: List[Rule] = rules or create_default_rules()
        self._build_rule_lookups()

        # listaDePasos store tuples: (Paso object, step_index, rule_applied)
        initial_goal_paso = Paso(contexto_inicial, resolvente_final)
        self.lista_de_pasos: List[Tuple[Paso, int, Optional[Rule]]] = [
            (initial_goal_paso, 0, None) 
        ]
        self.pasos_a_resolver: Set[int] = {0}  

    def _build_rule_lookups(self):
        self.rules_by_key = {rule.key: rule for rule in self.rules}
        self.rules_by_value = {rule.value: rule for rule in self.rules}

    def _resolve_rule(self, regla: Union[LogicRules, Rule, str, int]) -> Rule:
        if isinstance(regla, Rule):
            return regla
        if isinstance(regla, LogicRules):
            rule = self.rules_by_key.get(regla.name)
            if rule is None:
                raise ValueError(f"Rule not found for logic enum: {regla}")
            return rule
        if isinstance(regla, int):
            if 0 <= regla < len(self.rules):
                return self.rules[regla]
            raise IndexError(f"Rule index out of range: {regla}")
        if isinstance(regla, str):
            cleaned = regla.strip()
            if cleaned in self.rules_by_key:
                return self.rules_by_key[cleaned]
            if cleaned in self.rules_by_value:
                return self.rules_by_value[cleaned]
            for rule in self.rules:
                if cleaned.upper() == rule.key.upper():
                    return rule
            raise ValueError(f"Unknown rule identifier: {regla}")
        raise TypeError("Rule must be a Rule, LogicRules, string, or integer.")

    def register_rule(self, rule: Rule):
        if rule.key in self.rules_by_key or rule.value in self.rules_by_value:
            raise ValueError(f"Rule with key '{rule.key}' or value '{rule.value}' already exists.")
        self.rules.append(rule)
        self.rules_by_key[rule.key] = rule
        self.rules_by_value[rule.value] = rule

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
    
    def _mark_resolved(self, num_pos: int, regla: Rule):
        """Mark a step as resolved with the given rule."""
        paso, _, _ = self.lista_de_pasos[num_pos]
        self.lista_de_pasos[num_pos] = (paso, num_pos, regla)
        self.pasos_a_resolver.discard(num_pos)
    
    def _try_axiom(self, num_pos: int, current_paso: Paso) -> bool:
        """Try to apply AXIOM rule."""
        if current_paso.resolvente in current_paso.contexto:
            self._mark_resolved(num_pos, self._resolve_rule(LogicRules.AXIOM))
            return True
        return False

    def _try_rule(self, num_pos: int, current_paso: Paso, make_substeps: Callable[[Paso], List[Paso]]) -> bool:
        """Generic rule application for rules that generate substeps."""
        substeps = make_substeps(current_paso)
        self._add_substeps(num_pos, substeps)
        self.pasos_a_resolver.discard(num_pos)
        return True

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
    
    def aplicarRegla(self, num_pos: int, regla: Union[LogicRules, Rule, str, int]) -> bool:
        """
        Attempts to apply a given rule to the step at `num_pos`.
        If successful, it updates `pasos_a_resolver` and `lista_de_pasos`.
        """
        if not self._validate_step(num_pos):
            return False

        current_paso = self._get_paso(num_pos)
        rule = self._resolve_rule(regla)

        if not rule.applicable(current_paso):
            print(f"Error: La regla '{rule.value}' no es estructuralmente aplicable a la proposición {current_paso.resolvente.prettify()}.")
            return False

        print(f"Aplicando regla '{rule.value}' al paso {num_pos} (Prop: {current_paso.resolvente.prettify()})...")
        return rule.handler(self, num_pos, current_paso)


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


def create_default_rules() -> List[Rule]:
    return [
        make_rule(
            key="AXIOM",
            value="Axiom",
            applicable=lambda paso: paso.resolvente in paso.contexto,
            handler=Resolver._try_axiom,
            description="Resolve a goal directly if it is in the current context.",
            precondition="The goal must already appear in the current context.",
            postcondition="The goal is discharged immediately."
        ),
        make_rule(
            key="AND_INTRODUCTION",
            value="∧I",
            applicable=lambda paso: isinstance(paso.resolvente, AND),
            make_substeps=lambda paso: [
                Paso(contexto=paso.contexto, resolvente=paso.resolvente.left),
                Paso(contexto=paso.contexto, resolvente=paso.resolvente.right)
            ],
            description="Introduce a conjunction by proving both conjuncts.",
            precondition="The goal must be a conjunction.",
            postcondition="Both conjuncts become new subgoals."
        ),
        make_rule(
            key="AND_ELIMINATION_1",
            value="∧E1",
            applicable=lambda paso: isinstance(paso.resolvente, AND),
            make_substeps=lambda paso: [
                Paso(contexto=paso.contexto, resolvente=paso.resolvente.left)
            ],
            description="Extract the left conjunct from a conjunction.",
            precondition="The goal must be a conjunction.",
            postcondition="Left conjunct becomes the new subgoal."
        ),
        make_rule(
            key="AND_ELIMINATION_2",
            value="∧E2",
            applicable=lambda paso: isinstance(paso.resolvente, AND),
            make_substeps=lambda paso: [
                Paso(contexto=paso.contexto, resolvente=paso.resolvente.right)
            ],
            description="Extract the right conjunct from a conjunction.",
            precondition="The goal must be a conjunction.",
            postcondition="Right conjunct becomes the new subgoal."
        ),
        make_rule(
            key="IMPLICATION_INTRODUCTION",
            value="→I",
            applicable=lambda paso: isinstance(paso.resolvente, IMPLIES),
            make_substeps=lambda paso: [
                Paso(contexto=paso.contexto + [paso.resolvente.premise], resolvente=paso.resolvente.conclusion)
            ],
            description="Introduce an implication by assuming its premise.",
            precondition="The goal must be an implication.",
            postcondition="The implication is proven by proving the conclusion under the premise assumption."
        ),
        make_rule(
            key="IMPLICATION_ELIMINATION",
            value="→E",
            applicable=lambda paso: True,
            handler=Resolver._try_implication_elimination,
            description="Use implication elimination to derive a conclusion.",
            precondition="Requires a chosen antecedent formula.",
            postcondition="Creates subgoals to prove the antecedent and the implication conclusion."
        ),
        make_rule(
            key="OR_INTRODUCTION_1",
            value="∨I1",
            applicable=lambda paso: isinstance(paso.resolvente, OR),
            make_substeps=lambda paso: [
                Paso(contexto=paso.contexto, resolvente=paso.resolvente.left)
            ],
            description="Introduce a disjunction by proving the left disjunct.",
            precondition="The goal must be a disjunction.",
            postcondition="The left disjunct becomes a new subgoal."
        ),
        make_rule(
            key="OR_INTRODUCTION_2",
            value="∨I2",
            applicable=lambda paso: isinstance(paso.resolvente, OR),
            make_substeps=lambda paso: [
                Paso(contexto=paso.contexto, resolvente=paso.resolvente.right)
            ],
            description="Introduce a disjunction by proving the right disjunct.",
            precondition="The goal must be a disjunction.",
            postcondition="The right disjunct becomes a new subgoal."
        ),
        make_rule(
            key="OR_ELIMINATION",
            value="∨E",
            applicable=lambda paso: True,
            handler=Resolver._try_or_elimination,
            description="Eliminate a disjunction by proving the goal from both disjuncts.",
            precondition="Requires two alternative assumptions.",
            postcondition="Creates subgoals for both disjunct cases."
        ),
        make_rule(
            key="NEGATION_INTRODUCTION",
            value="¬I",
            applicable=lambda paso: isinstance(paso.resolvente, NEG),
            handler=Resolver._try_negation_introduction,
            description="Introduce a negation by proving a contradiction from the negated formula.",
            precondition="The goal must be a negation.",
            postcondition="Assumes the positive formula and creates a contradiction subgoal."
        ),
        make_rule(
            key="NEGATION_ELIMINATION",
            value="¬E",
            applicable=lambda paso: True,
            handler=Resolver._try_negation_elimination,
            description="Eliminate a negation to derive a contradiction.",
            precondition="Requires a chosen formula to test against its negation.",
            postcondition="Creates a formula and its negation as subgoals."
        ),
        make_rule(
            key="BOTTOM_ELIMINATION",
            value="⊥E",
            applicable=lambda paso: True,
            handler=Resolver._try_bottom_elimination,
            description="Derive any formula from a contradiction.",
            precondition="Requires a contradiction to be handled.",
            postcondition="Creates a contradiction subgoal and the desired conclusion."
        ),
        make_rule(
            key="MODUS_TOLLENS",
            value="MT",
            applicable=lambda paso: isinstance(paso.resolvente, NEG),
            handler=Resolver._try_modus_tollens,
            description="Infer a negated antecedent from an implication and a negated consequent.",
            precondition="The goal must be a negation.",
            postcondition="Creates the implication to contradiction subgoal."
        ),
        make_rule(
            key="NEGATION_NEGATION_INTRODUCTION",
            value="¬¬I",
            applicable=lambda paso: isinstance(paso.resolvente, NEG) and isinstance(paso.resolvente.prop, NEG),
            handler=Resolver._try_negation_negation_introduction,
            description="Introduce double negation.",
            precondition="The goal must be a double negation.",
            postcondition="Creates the inner negation as a new subgoal."
        ),
        make_rule(
            key="NEGATION_NEGATION_ELIMINATION",
            value="¬¬E",
            applicable=lambda paso: isinstance(paso.resolvente, NEG) and isinstance(paso.resolvente.prop, NEG),
            handler=Resolver._try_negation_negation_elimination,
            description="Eliminate double negation.",
            precondition="The goal must be a double negation.",
            postcondition="Creates the inner formula as a new subgoal."
        ),
        make_rule(
            key="EXCLUDED_MIDDLE",
            value="LEM",
            applicable=lambda paso: isinstance(paso.resolvente, OR) and isinstance(paso.resolvente.right, NEG) and paso.resolvente.left == paso.resolvente.right.prop,
            handler=Resolver._try_excluded_middle,
            description="Introduce the law of excluded middle for a formula.",
            precondition="The goal must be a tautological disjunction A ∨ ¬A.",
            postcondition="Creates a tautology subgoal for the formula."
        ),
        make_rule(
            key="PBC",
            value="PBC",
            applicable=lambda paso: True,
            handler=Resolver._try_pbc,
            description="Use proof by contradiction to infer a formula.",
            precondition="The goal can be assumed false to derive a contradiction.",
            postcondition="Creates a contradiction subgoal under the negated goal."
        ),
    ]


def choose_rule(rules: List[Rule]) -> Rule:
    """Allow the user to choose a rule by number or by its value/name."""
    print("\nAvailable rules:")
    for idx, rule in enumerate(rules, start=1):
        print(f"  {idx}. {rule.value} - {rule.description}")
        if rule.precondition or rule.postcondition:
            print(f"       pre: {rule.precondition} | post: {rule.postcondition}")

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
            if rule_input == rule.value or rule_input.upper() == rule.key.upper():
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
            
            regla = choose_rule(resolver.rules)

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