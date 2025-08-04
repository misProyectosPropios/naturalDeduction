const IntuicionisticRules = Object.freeze({
    AXIOM: "Axiom", 
    AND_INTRODUCTION: "∧I", 
    AND_ELIMINATION_1: "∧E1",  
    AND_ELIMINATION_2: "∧E2",  
    IMPLICATION_INTRODUCTION: "→I",
    IMPLICATION_ELIMINATION: "→E", 
    OR_INTRODUCTION_1: "∨I1", 
    OR_INTRODUCTION_2: "∨I2", 
    OR_ELIMINATION: "∨E",  
    NEGATION_INTRODUCTION: "¬I", 
    NEGATION_ELIMINATION: "¬E",  
    BOTTOM_ELIMINATION: "⊥E", 

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
    constructor(contexto, resolvente) {
        this.contexto = contexto;
        this.resolvente = resolvente;
        primerPaso = new Paso(contexto, resolvente);
        this.listaDePasos = [primerPaso, 0, null];
        this.pasosAResolver = new Set([0]);
    }

    esCompletaPrueba() {
        return this.pasosAResolver.size === 0;
    }

    esAxioma(paso) {
        // Verifica si un paso es un axioma
        return paso.isInTheContext(paso.resolvente);
    }

    implementRule(numeroPaso, regla) {
        //Agrega los nuevos pasos a resolver a partir de la regla
        //Por cada paso agregar la cantidad de pasos que se digan y como deberían estar puestas
        if (!this.listaDePasos.isAbleToAPllyRule(regla)) {
            throw new Error(`No es posible usar la regla ${regla} en este paso`);
        }
        if (!this.pasosAResolver.has(numeroPaso)) {
            throw new Error(`No se puede aplicar otra regla a un paso al que ya se le aplicó`);
        }
        switch (regla) {
            case IntuicionisticRules.AND_ELIMINATION_1:
                break;
            case IntuicionisticRules.AND_ELIMINATION_2:
                break;
            case IntuicionisticRules.AND_INTRODUCTION:
                const pasoActual = this.listaDePasos[numeroPaso];
                const ladoIzquierdo = pasoActual.resolvente.left;
                const ladoDerecho = pasoActual.resolvente.right;

                const nuevoPasoIzquierdo = new Paso(pasoActual.contexto, ladoIzquierdo);
                const nuevoPasoDerecho = new Paso(pasoActual.contexto, ladoDerecho);

                this.listaDePasos.push(nuevoPasoIzquierdo);
                this.listaDePasos.push(nuevoPasoDerecho);

                this.pasosAResolver.delete(numeroPaso);
                this.pasosAResolver.add(this.listaDePasos.length - 2); // Índice del nuevo paso izquierdo
                this.pasosAResolver.add(this.listaDePasos.length - 1); // Índice del nuevo paso derecho
                break;
            case IntuicionisticRules.IMPLICATION_INTRODUCTION:
                break;
            case IntuicionisticRules.IMPLICATION_ELIMINATION:
                break;
            case IntuicionisticRules.OR_INTRODUCTION_1:
                break;
            case IntuicionisticRules.OR_INTRODUCTION_2:
                break;
            case IntuicionisticRules.OR_ELIMINATION:
                break;
            case IntuicionisticRules.NEGATION_INTRODUCTION:
                break;
            case IntuicionisticRules.NEGATION_ELIMINATION:
                break;
            case IntuicionisticRules.BOTTOM_ELIMINATION:
                break;
            case IntuicionisticRules.MODUS_TOLLENS:
                break;
            case IntuicionisticRules.NEGATION_NEGATION_INTRODUCTION:
                break;
        }
    }

    mostrarPrueba() {
        //Muestra la prueba
        const reversedSteps = [...this.listaDePasos].reverse();
        reversedSteps.forEach(function(element, index) {
            console.log(`${reversedSteps.length - 1 - index}: ${element.toString()}`);
        });
    }
}

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
                return this.isInTheContext(this.resolvente);
            case IntuicionisticRules.AND_INTRODUCTION:
                return this.resolvente.type === 'And';
            case IntuicionisticRules.AND_ELIMINATION_1:
            case IntuicionisticRules.AND_ELIMINATION_2:
                return true;
            case IntuicionisticRules.IMPLICATION_INTRODUCTION:
                return this.resolvente.type === 'Impl';
            case IntuicionisticRules.IMPLICATION_ELIMINATION:
                return true;
            case IntuicionisticRules.OR_INTRODUCTION_1:
            case IntuicionisticRules.OR_INTRODUCTION_2:
                return this.resolvente.type === 'Or';
            case IntuicionisticRules.OR_ELIMINATION:
                return true;
            case IntuicionisticRules.NEGATION_INTRODUCTION:
                return this.resolvente.type === 'Neg';
            case IntuicionisticRules.NEGATION_ELIMINATION:
                return true;
            case IntuicionisticRules.BOTTOM_ELIMINATION:
                return true;
            case IntuicionisticRules.MODUS_TOLLENS:
                return this.resolvente.type === 'Neg';
            case IntuicionisticRules.NEGATION_NEGATION_INTRODUCTION:
                return this.resolvente.type === 'Neg' && this.resolvente.prop.type === 'Neg';
            default:
                throw new Error(`Regla no reconocida: ${ruleName}`);
        }
    }

    isInTheContext(proposition) {
        // Devuelve true si la proposición está en el contexto
        return this.contexto.some(ctxProp => Prop.equals(ctxProp, proposition));
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

function Main() {
/**
 * Metodos a implementar:
 * + Obtener el contexto y la resolvente (y guardarlo que se entienda en main.js (un parser)).
 * + Ir resolviendo la deducción evaluando si cada paso nuevo es resoluble o no
 * + Resolver hasta llegar a la prueba final
 */
    contexto = obtenerContexto();
    resolvente = obtenerResolvente();
    resolv = new Resolvedor(contexto, resolvente);

}

function obtenerContexto() {
    let input = "";
}

function obtenerResolvente() {

}

//Feature más adelante
class TablaDeVerdad{
    // Hace la tabla de verdad de una proposición dada
    // Muestra si es tautologia, contingencia o contradicción
    // Muestra la tabla de verdad
}