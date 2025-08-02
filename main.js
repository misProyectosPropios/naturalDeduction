const IntuicionisticRules = Object.freeze({
    AXIOM: "Axiom", 
    AND_INTRODUCTION: "∧I", 
    AND_ELIMINATION: "∧E",  
    IMPLICATION_INTRODUCTION: "→I",
    IMPLICATION_ELIMINATION: "→E", 
    OR_INTRODUCTION: "∨I", 
    OR_ELIMINATION: "∨E",  
    NEGATION_INTRODUCTION: "¬I", 
    NEGATION_ELIMINATION: "¬E",  
    BOTTOM_INTRODUCTION: "⊥I", 

    // Reglas Derivadas Comunes
    MODUS_TOLLENS: "MT", 
    NEGATION_NEGATION_INTRODUCTION: "¬¬I"
});

const ClassicalRules = Object.freeze({
    // Spread all rules from IntuitionisticRules
    ...IntuicionisticRules,

    // Classical-specific axiom/rule
    NEGATION_NEGATION_ELIMINATION: "¬¬E",

    // Reglas Derivadas Comunes
    EXCLUDED_MIDDLE: "LEM",
    PBC: "PBC"
});

class Resolvedor {
    //Hacer que tenga un DAG de pasos resolvidos
}

// --- Definición de la Clase Paso ---
class Paso {
    /**
     * Crea una nueva instancia de Paso.
     * @param {Prop[]} contexto - Una lista de proposiciones que forman el contexto.
     * @param {Prop} resolvente - La proposición resolvente.
     */
    constructor(contexto, resolvente) {
        // Aseguramos que el contexto sea un array y sus elementos sean instancias de Prop
        if (!Array.isArray(contexto) || !contexto.every(item => item instanceof Prop)) {
            throw new Error("El contexto debe ser un array de instancias de Prop.");
        }
        // Aseguramos que la resolvente sea una instancia de Prop
        if (!(resolvente instanceof Prop)) {
            throw new Error("La resolvente debe ser una instancia de Prop.");
        }

        this.contexto = contexto;
        this.resolvente = resolvente;
    }

    /**
     * Devuelve una representación en cadena del paso lógico.
     * El formato es "contexto[0], contexto[1], ..., contexto[n - 1] |- resolvente".
     * Utilizamos \vdash para el símbolo de "deriva" o "se sigue".
     * @returns {string} La representación en cadena del paso.
     */
    toString() {
        const contextoStr = this.contexto.map(prop => prop.toString()).join(', ');
        // El símbolo unicode para 'turnstile' (⊢) es U+22A2.
        // También podríamos usar '\vdash' si el contexto es para LaTeX.
        return `${contextoStr} ⊢ ${this.resolvente.toString()}`;
    }

    isAbleToAPllyRule(ruleName) {
        switch (ruleName) {
            case IntuicionisticRules.AXIOM:
                return this.contexto.some(prop => Prop.equals(prop, this.resolvente));

            case IntuicionisticRules.AND_INTRODUCTION:
                return this.contexto.some(prop => 
                    prop.type === 'And' &&
                    this.contexto.some(ctxProp => Prop.equals(ctxProp, prop.left)) &&
                    this.contexto.some(ctxProp => Prop.equals(ctxProp, prop.right))
                );

            case IntuicionisticRules.AND_ELIMINATION:
                return this.contexto.some(prop => 
                    prop.type === 'And' &&
                    (Prop.equals(this.resolvente, prop.left) || Prop.equals(this.resolvente, prop.right))
                );

            case IntuicionisticRules.IMPLICATION_INTRODUCTION:
                return true;
            case IntuicionisticRules.IMPLICATION_ELIMINATION:
                return this.contexto.some(prop => 
                    prop.type === 'Impl' &&
                    Prop.equals(prop.left, this.resolvente)
                );

            case IntuicionisticRules.OR_INTRODUCTION:
                return this.resolvente.type === 'Or' &&
                    (this.contexto.some(ctxProp => Prop.equals(ctxProp, this.resolvente.left)) ||
                     this.contexto.some(ctxProp => Prop.equals(ctxProp, this.resolvente.right)));

            case IntuicionisticRules.OR_ELIMINATION:
                return true;

            case IntuicionisticRules.NEGATION_INTRODUCTION:
                return true;

            case IntuicionisticRules.NEGATION_ELIMINATION:
                return this.contexto.some(prop => 
                    prop.type === 'Neg' &&
                    this.contexto.some(ctxProp => Prop.equals(ctxProp, prop.prop))
                );

            case IntuicionisticRules.BOTTOM_INTRODUCTION:
                return true;

            case IntuicionisticRules.MODUS_TOLLENS:
                return this.contexto.some(prop => 
                    prop.type === 'Impl' &&
                    this.contexto.some(ctxProp => 
                        Prop.equals(ctxProp, prop.right.neg())
                    )
                );

            case IntuicionisticRules.NEGATION_NEGATION_INTRODUCTION:
                return this.contexto.some(prop => 
                    prop.type === 'Neg' &&
                    prop.prop.type === 'Neg' &&
                    Prop.equals(prop.prop.prop, this.resolvente)
                );

            default:
                throw new Error(`Regla no reconocida: ${ruleName}`);
        }
    }
}

class Prop {
    constructor(type, ...args) {
        this.type = type;
        if (type === 'Var') {
            this.name = args[0];
        } else if (type === 'Neg') {
            this.prop = args[0];
        } else if (type === 'Bottom') {
            // No necesita argumentos adicionales para Bottom
        } else { // Impl, And, Or
            this.left = args[0];
            this.right = args[1];
        }
    }

    // Métodos para operadores infijos
    impl(otherProp) {
        return new Prop('Impl', this, otherProp);
    }

    and(otherProp) {
        return new Prop('And', this, otherProp);
    }

    or(otherProp) {
        return new Prop('Or', this, otherProp);
    }

    neg() {
        return new Prop('Neg', this);
    }

    toString() {
        switch (this.type) {
            case 'Var':
                return this.name;
            case 'Neg':
                return `(¬${this.prop.toString()})`; // Aquí no verás 'Prop'
            case 'Impl':
                return `(${this.left.toString()} → ${this.right.toString()})`;
            case 'And':
                return `(${this.left.toString()} ∧ ${this.right.toString()})`;
            case 'Or':
                return `(${this.left.toString()} ∨ ${this.right.toString()})`;
            case 'Bottom':
                return '⊥';
            default:
                return 'Error';
        }
    }

    /**
     * Static helper method to compare if two propositions are structurally equal.
     * @param {Prop} p1 - First proposition.
     * @param {Prop} p2 - Second proposition.
     * @returns {boolean} True if they are structurally equal.
     */
    static equals(p1, p2) {
        if (p1 === p2) return true;
        if (!p1 || !p2 || p1.type !== p2.type) return false;

        switch (p1.type) {
            case 'Var':
                return p1.name === p2.name;
            case 'Neg':
                return Prop.equals(p1.prop, p2.prop);
            case 'Impl':
            case 'And':
            case 'Or':
                return Prop.equals(p1.left, p2.left) && Prop.equals(p1.right, p2.right);
            case 'Bottom':
                return true;
            default:
                return false;
        }
    }
}


// Para crear variables:
const Var = (name) => new Prop('Var', name);
const Bottom = () => new Prop('Bottom');






































































// Ejemplos de uso:
const p = Var("p");
const q = Var("q");
const r = Var("r");

// Representando "p -> q"
const pImplQ = p.impl(q);
console.log("p -> q:", pImplQ.toString()); // Salida: (p → q)

// Representando "(p /\ q) -> r"
const complexProp = p.and(q).impl(r);
console.log("(p /\\ q) -> r:", complexProp.toString()); // Salida: ((p ∧ q) → r)

// Representando "not p"
const notP = p.neg();
console.log("not p:", notP.toString()); // Salida: (¬p)

// Si usas console.log(objeto) directamente, algunas consolas (como la de Node.js)
// pueden usar el método `inspect` o `[Symbol.for('nodejs.util.inspect.custom')]`
// Si quieres que `console.log(pImplQ)` también use `toString()`, puedes descomentar el método opcional de arriba.
// Sin ese método, console.log(pImplQ) seguirá mostrando la estructura interna del objeto.
console.log("\nEjemplo de console.log(objeto) sin toString() personalizado en el objeto:");
console.log(pImplQ); // Esto mostrará la estructura completa del objeto, no solo la cadena formateada.

// Si descomentas el método [Symbol.for('nodejs.util.inspect.custom')]
// console.log("\nEjemplo de console.log(objeto) con toString() personalizado en el objeto (descomentar el método [Symbol.for('nodejs.util.inspect.custom')]):");
// console.log(pImplQ);

/*
 <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
 */




