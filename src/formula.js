let pyodide = null;

/**
 * Initializes the bridge with a Pyodide instance.
 */
export function initPython(instance) {
    pyodide = instance;
    // Bootstrap standard imports
    pyodide.runPython(`
        import json
        import re
        from src.lexer import Lexer
        from src.parser import Parser
        from src.logic import apply_logic_rule
    `);
}

export function normalizeFormula(raw) {
    pyodide.globals.set("raw_input", raw);
    return pyodide.runPython(`re.sub(r'"([^"]+)"', r'\\1', raw_input).replace("->", " → ").replace("^", " ∧ ").replace("V", " ∨ ").replace("_", " ⊥ ").replace("-", " ¬").strip()`);
}

export function tokenizeFormula(input) {
    pyodide.globals.set("tok_input", input);
    const json = pyodide.runPython(`
        tokens = Lexer(tok_input).tokenize()
        json.dumps([{"type": t.type.name, "value": getattr(t, 'value', None)} for t in tokens])
    `);
    return JSON.parse(json);
}

export function parseFormulaString(raw) {
    pyodide.globals.set("parse_input", raw);
    // This returns the Python AST object; we can call methods on it or convert to JS
    return pyodide.runPython(`Parser(Lexer(parse_input).tokenize()).parse()`);
}

export function formulaToString(ast) {
    // If ast is a PyProxy (Python object), we call its prettify method
    return ast.prettify();
}

export function applyRuleToStep(step, rule) {
    pyodide.globals.set("ctx_input", step.context);
    pyodide.globals.set("goal_input", step.goal);
    pyodide.globals.set("rule_key", rule.key);

    const result = pyodide.runPython(`apply_logic_rule(ctx_input.to_py(), goal_input, rule_key)`).toJs({dict_converter: Object.fromEntries});

    if (result.error) return result.error;

    if (result.new_goal) {
        step.context = result.new_context;
        step.goal = result.new_goal;
    }
    step.resolvedBy = result.resolved_by;
    return null;
}

export function validateInput(raw) {
    try {
        const trimmed = raw.trim();
        if (!trimmed) return false;
        parseFormulaString(trimmed);
        return true;
    } catch (e) {
        return false;
    }
}
