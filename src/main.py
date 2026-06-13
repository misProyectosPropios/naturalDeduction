from __future__ import annotations

from abc import abstractmethod
import sys
from dataclasses import dataclass, field
from typing import List, Optional

from .lexer import Lexer
from .logic import AND, IMPLIES, OR, Prop, VAR, NEG, IMPLIES, BOTTOM

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_current_proof = None

def parse_formula_with_lexer(expr: str) -> Optional[Prop]:
    """Parse a formula using the lexer and parser."""
    try:
        # print("Parsing") # Commented out print statements for cleaner output
        from .parser import Parser # Changed to relative import
        # print("LEXING") # Commented out print statements for cleaner output
        from .lexer import Token, TokenType # Changed to relative import
        
        lexer = Lexer(expr)
        tokens = lexer.tokenize()
        tokens.append(Token(TokenType.EOF))

        parser = Parser(tokens)
        return parser.parse()
    except Exception as exc:
        raise ValueError(f"Parse error: {exc}") from exc


def getFormula() -> Prop:
    """Read a single formula from the user."""
    print('Enter a formula (e.g., "P" -> "Q" ^ "R"):\n')
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                print("Formula cannot be empty.")
                continue
            return parse_formula_with_lexer(user_input)
        except ValueError as exc:
            print(f"Invalid input: {exc}. Please try again.")


def getContext() -> List[Prop]:
    """Read the initial context from the user."""
    print("\n=== Enter Context Propositions ===")
    print('Format: "P" -> "Q" ^ "R" V -"S" _ (for variables, implication, and, or, not, bottom)')
    print("Empty line to finish.\n")

    context: List[Prop] = []
    proposition_count = 0

    while True:
        try:
            user_input = input(f"Proposition {proposition_count + 1} > ").strip()
            if not user_input:
                print(f"\nContext complete with {proposition_count} proposition(s).")
                break

            proposition = parse_formula_with_lexer(user_input)
            context.append(proposition)
            proposition_count += 1
            print(f"✓ Parsed successfully: {proposition.prettify()}")
        except ValueError as exc:
            print(f"✗ {exc} Please try again.")

    return context


def getResolvent() -> Prop:
    """Read the goal proposition from the user."""
    print("\n=== Enter Goal Proposition (Resolvent) ===")
    print('Format: "P" -> "Q" ^ "R" V -"S" _ (for variables, implication, and, or, not, bottom)\n')

    while True:
        try:
            user_input = input("Goal > ").strip()
            if not user_input:
                print("Goal cannot be empty. Please try again.")
                continue

            proposition = parse_formula_with_lexer(user_input)
            print(f"✓ Parsed successfully: {proposition.prettify()}\n")
            return proposition
        except ValueError as exc:
            print(f"✗ {exc} Please try again.")


def apply_rule(step_idx: int, rule_name: str):
    global _current_proof

    if _current_proof is None:
        return {
            "success": False,
            "error": "No proof initialized."
        }

    if step_idx < 0 or step_idx >= len(_current_proof.steps):
        return {
            "success": False,
            "error": f"Invalid step index: {step_idx}"
        }

    rule = next(
        (
            r for r in available_rules()
            if r.__class__.__name__ == rule_name
        ),
        None
    )

    if rule is None:
        return {
            "success": False,
            "error": f"Unknown rule: {rule_name}"
        }

    try:
        applied, subgoals = _current_proof.aplicarRegla(
            rule,
            step_idx
        )

        if not applied:
            return {
                "success": False,
                "error": "Rule is not applicable to the selected step."
            }

        return {
            "success": True,
            "subgoals": len(subgoals)
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc)
        }


def get_applicable_rules(step_idx):
    global _current_proof

    goal = _current_proof.steps[step_idx]

    print(
        "Selected goal:",
        goal.formula,
        type(goal.formula)
    )

    result = []

    for rule in available_rules():
        app = rule.applicable(goal)

        print(
            rule.__class__.__name__,
            app
        )

        if app:
            result.append({
                "id": rule.__class__.__name__,
                "name": rule.display_name()
            })

    return result
def get_current_proof():
    global _current_proof
    return _current_proof

def init_proof(formulas, goal):
    global _current_proof

    # Convert JS proxies to Python objects
    if hasattr(formulas, "to_py"):
        formulas = formulas.to_py()

    if hasattr(goal, "to_py"):
        goal = goal.to_py()

    context = set()

    for item in formulas:
        if hasattr(item, "to_py"):
            item = item.to_py()

        formula_str = str(item["str"])

        context.add(
            parse_formula_with_lexer(formula_str)
        )

    if goal is None:
        raise ValueError("Goal is required")

    goal_formula = parse_formula_with_lexer(
        str(goal["str"])
    )

    _current_proof = Proof(
        Goal(
            context=context,
            formula=goal_formula
        )
    )

    return _current_proof.describe()

class Rule:
    @abstractmethod
    def applicable(self, goal: Goal) -> bool:
        raise NotImplementedError

    @abstractmethod
    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        raise NotImplementedError

    @property
    def label(self) -> str:
        return self.__class__.__name__
    
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def display_name(self) -> str:
        raise NotImplementedError


class Axiom(Rule):
    def applicable(self, goal: Goal) -> bool:
        return goal.formula in goal.context

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return []

    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "Axiom"


class AndIntro(Rule):
    def applicable(self, goal: Goal) -> bool:
        return isinstance(goal.formula, AND)

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context, goal.formula.left), Goal(goal.context, goal.formula.right)]

    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "AndIntro"

class AndElim1(Rule):
    def applicable(self, goal: Goal) -> bool:
        return True

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context, AND(goal.formula, VAR("_")))]

    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "AndElim1"

class AndElim2(Rule):
    def applicable(self, goal: Goal) -> bool:
        return True

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context, AND(VAR("_"), goal.formula))]

    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "AndElim2"

class OrIntro1(Rule):
    def applicable(self, goal: Goal) -> bool:
        return isinstance(goal.formula, OR)

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context, goal.formula.left)]

    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "OrIntro1"

class OrIntro2(Rule):
    def applicable(self, goal: Goal) -> bool:
        return isinstance(goal.formula, OR)

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context, goal.formula.right)]
    
    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "OrIntro2"


class OrElim(Rule):
    def applicable(self, goal: Goal) -> bool:
        return True

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        if len(premises) < 2:
            raise ValueError("OrElim requires two formulas.")

        left, right = premises[0], premises[1]
        return [
            Goal(goal.context, OR(left, right)),
            Goal(goal.context | {left}, goal.formula),
            Goal(goal.context | {right}, goal.formula),
        ]

    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "OrElim"

class ImpIntro(Rule):
    def applicable(self, goal: Goal) -> bool:
        return isinstance(goal.formula, IMPLIES)

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context | {goal.formula.premise}, goal.formula.conclusion)]

    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "ImpIntro"

class ImpElimination(Rule):
    def applicable(self, goal: Goal) -> bool:
        return True

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        formula = premises[0]
        return [Goal(goal.context, IMPLIES(formula, goal.formula))]
    
    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "ImpElimination"
    
class NotIntro(Rule):
    def applicable(self, goal: Goal) -> bool:
        return isinstance(goal.formula, NEG)

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
            return [Goal(goal.context | {goal.formula}, BOTTOM())]
    
    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "NotIntro"

    
class NotElimination(Rule):
    def applicable(self, goal: Goal) -> bool:
            return isinstance(goal.formula, BOTTOM)

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        premisesValue = premises[0]
        raise [Goal(goal.context, premisesValue), Goal(goal.context, NEG(premisesValue))] 
    
    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "NotElimination"
    
class BottomElimination(Rule):
    def applicable(self, goal: Goal) -> bool:
        return True

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context, BOTTOM())]
    
    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "BottomElimination"

class PBC(Rule):
    def applicable(self, goal: Goal) -> bool:
        return True

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context | {NEG(goal.formula)}, BOTTOM())]
    
    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "PBC"

class LEM(Rule):
    def applicable(self, goal: Goal) -> bool:
        return isinstance(goal.formula, OR) and (goal.formula.left == NEG(goal.formula.right) or goal.formula.right == NEG(goal.formula.left))

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return []
    
    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "LEM"

class NotNotElimination(Rule):
    def applicable(self, goal: Goal) -> bool:
        return True

    def subgoals(self, goal: Goal, *premises: Prop) -> list[Goal]:
        return [Goal(goal.context, NEG(NEG(goal.formula)))]
    
    def description(self) -> str:
        return "Hola mundo"
    
    def display_name(self) -> str:
        return "--Elimination"


@dataclass
class Goal:
    context: set[Prop]
    formula: Prop
    rule: Optional[Rule] = None

    def __post_init__(self) -> None:
        if not isinstance(self.context, set):
            self.context = set(self.context)

    def fueCompletada(self) -> bool:
        return self.rule is not None

    def aplicarRegla(self, regla: Rule, *premises: Prop) -> tuple[bool, list[Goal]]:
        if self.fueCompletada() or not regla.applicable(self):
            return False, []
        return True, regla.subgoals(self, *premises)

    def describe(self) -> str:
        contexto = ", ".join(prop.prettify() for prop in sorted(self.context, key=lambda item: item.prettify()))
        return f"{contexto} |- {self.formula.prettify()}"


@dataclass
class Proof:
    goal: Goal
    steps: list[Goal] = field(default_factory=list)
    _step_parents: dict[int, int] = field(default_factory=dict)  # Maps step index to parent step index (-1 for root)

    def __post_init__(self) -> None:
        if not self.steps:
            self.steps.append(self.goal)
            self._step_parents[0] = -1  # Root goal has no parent

    def isCompleted(self) -> bool:
        return all(step.fueCompletada() for step in self.steps)

    def aplicarRegla(self, regla: Rule, posicion: int, *premises: Prop) -> tuple[bool, list[Goal]]:
        if posicion < 0 or posicion >= len(self.steps):
            return False, []
        step = self.steps[posicion]
        applied, subgoals = step.aplicarRegla(regla, *premises)
        if not applied:
            return False, []

        self.steps[posicion].rule = regla
        # Track parent-child relationships in the proof tree
        start_index = len(self.steps)
        for i, subgoal in enumerate(subgoals):
            self._step_parents[start_index + i] = posicion
        self.steps.extend(subgoals)
        return True, subgoals

    def describe(self) -> list[str]:
        lines = ["\n--- Current Proof State ---"]
        if not self.steps:
            lines.append("No steps in the proof yet.")
            return lines
        for index, step in enumerate(self.steps):
            status = "resolved" if step.fueCompletada() else "pending"
            parent = self._step_parents.get(index, -2)
            origin_info = f"(from: {parent})" if parent >= 0 else "(root)" if parent == -1 else ""
            lines.append(f"[{index}] {origin_info} ({status}) {step.describe()}")        
        pending = [index for index, step in enumerate(self.steps) if not step.fueCompletada()]
        if pending:
            lines.append(f"Steps to resolve: {pending}")
        else:
            lines.append("All steps resolved!")

        return lines


def available_rules() -> list[Rule]:
    rules = []

    def collect(cls):
        for subcls in cls.__subclasses__():
            rules.append(subcls())
            collect(subcls)

    collect(Rule)

    return rules

def proof_description():
    global _current_proof
    
    if _current_proof is None:
        return []

    return _current_proof.describe()

def proof_complete():
    global _current_proof

    if _current_proof is None:
        return False

    return _current_proof.fueCompletada()

def available_rule_info():
    return [
        {
            "id": rule.__class__.__name__,
            "name": rule.display_name(),
            "description": rule.description(),
        }
        for rule in available_rules()
    ]

class ProofConsole:
    def __init__(self) -> None:
        self.rules = available_rules()

    def prompt_context(self) -> list[Prop]:
        return getContext()

    def prompt_goal(self) -> Prop:
        return getResolvent()

    def choose_rule(self) -> Rule:
        print("\nAvailable rules:")
        for index, rule in enumerate(self.rules, start=1):
            print(f"  {index}. {rule.label}")

        while True:
            choice = input("Enter the rule number or press Enter to cancel: ").strip()
            if not choice:
                raise KeyboardInterrupt

            if choice.isdigit():
                number = int(choice)
                if 1 <= number <= len(self.rules):
                    return self.rules[number - 1]
                print(f"✗ Invalid rule number: {number}. Please choose between 1 and {len(self.rules)}.")
                continue

            for rule in self.rules:
                if choice.upper() == rule.label.upper():
                    return rule

            print(f"✗ Unknown rule: '{choice}'. Please enter a valid rule number or rule name.")

    def prompt_premises(self, rule: Rule) -> list[Prop]:
        if isinstance(rule, OrElim):
            print("Enter the two formulas required by OrElim.")
            return [getFormula(), getFormula()]
        return []

    def run(self) -> None:
        print("=" * 60)
        print("Welcome to the Natural Deduction Resolver!")
        print("=" * 60)

        try:
            context = self.prompt_context()
            goal = self.prompt_goal()
        except KeyboardInterrupt:
            print("\n\nProof cancelled.")
            return

        proof = Proof(Goal(set(context), goal))

        while not proof.isCompleted():
            for line in proof.describe():
                print(line)

            try:
                position_text = input("\nEnter the step number to apply a rule (or -1 to quit): ").strip()
                if position_text == "-1":
                    print("Proof cancelled.")
                    return

                position = int(position_text)
                rule = self.choose_rule()
                premises = self.prompt_premises(rule)

                applied, _ = proof.aplicarRegla(rule, position, *premises)
                if applied:
                    print(f"✓ Rule '{rule.label}' applied successfully to step {position}.")
                else:
                    print(f"✗ Failed to apply rule '{rule.label}' to step {position}.")
            except ValueError:
                print("✗ Invalid input. Please enter a valid step number.")
            except KeyboardInterrupt:
                print("\n\nProof cancelled.")
                return

        print("\n" + "=" * 60)
        print("SUCCESS! PROOF COMPLETE!")
        print("=" * 60)
        for line in proof.describe():
            print(line)


def main() -> None:
    ProofConsole().run()


if __name__ == "__main__":
    main()
