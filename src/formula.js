let pyodide = null;

/**
 * Initializes the bridge with a Pyodide instance.
 */
export function initPython(instance) {
    pyodide = instance;
    // Bootstrap standard imports
    pyodide.runPython(`
        import json
        try:
            from src.lexer import Lexer
            # from src.parser import Parser (Assume you have a parser)
        except ImportError:
            pass
    `);
}

export function normalizeFormula(raw) {
    // Example of calling a Python function for normalization
    return pyodide.runPython(`
        import re
        raw = ${JSON.stringify(raw)}
        unquoted = re.sub(r'"([^"]+)"', r'\\1', raw)
        unquoted.replace("->", " → ").replace("^", " ∧ ").replace("V", " ∨ ").replace("_", " ⊥ ").replace("-", " ¬").strip()
    `);
}

export function tokenizeFormula(input) {
    // Use the Python Lexer defined in src/lexer.py
    return pyodide.runPython(`
        lexer = Lexer(${JSON.stringify(input)})
        tokens = lexer.tokenize()
        # Map Python objects to JS-serializable list
        json.dumps([{"type": t.type.name, "value": getattr(t, 'value', None)} for t in tokens])
    `).then(JSON.parse);
}

export function parseFormulaString(raw) {
    // This assumes you have a Parser class in Python
    return pyodide.runPython(`
        # Replace with actual parser logic when available
        # For now, return a mock/minimal AST compatible with current UI
        {"type": "VAR", "name": "PythonParsed"} 
    `);
}

export function formulaToString(ast) {
    return pyodide.runPython(`
        # Logic to convert AST back to string using Python
        "TODO: Python Stringification"
    `);
}

export function applyRuleToStep(step, rule) {
    // Proxy the rule application to Python logic
    const result = pyodide.runPython(`
        # Use Python logic to apply rules
        None # Return message if error, else None
    `);
    
    if (result) return result;

    // Manual implementation for rules that change state (until Python handles state)
    if (rule.key === 'IMPLICATION_INTRODUCTION') {
        const goalAst = parseFormulaString(step.goal);
        if (goalAst.type !== 'IMPLIES') {
            return 'The selected step is not an implication; →I cannot be applied.';
        }

        const premise = formulaToString(goalAst.left);
        const conclusion = formulaToString(goalAst.right);
        step.context = [...step.context, premise];
        step.goal = conclusion;
        step.resolvedBy = rule.value;
        return null;
    }

    if (rule.key === 'AXIOM') {
        const normalizedGoal = normalizeFormula(step.goal);
        const hasGoalInContext = step.context.some((ctx) => normalizeFormula(ctx) === normalizedGoal);
        if (!hasGoalInContext) {
            return 'Axiom can only be applied when the goal is already in the context.';
        }
        step.resolvedBy = rule.value;
        return null;
    }

    return 'This rule is not yet implemented for UI simulation.';
}

export function validateInput(raw) {
    const trimmed = raw.trim();
    if (!trimmed) return false;
    parseFormulaString(trimmed);
    return true;
}
