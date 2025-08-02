¡Excelente idea! Una buena documentación es crucial para cualquier proyecto de código. Aquí te presento una plantilla de documentación de código en Markdown, pensada para ser clara, concisa y útil, especialmente para tus clases Prop, Paso, y Resolvedor, junto con tus constantes de reglas.

Puedes usar esta plantilla en un archivo README.md o en archivos de documentación específicos para cada componente.

Documentación del Proyecto de Lógica Natural

Este documento describe la estructura y el uso de las clases y funciones principales para la manipulación de proposiciones y la verificación de pasos en la Deducción Natural.

1. Visión General del Proyecto

Este proyecto implementa una base para un sistema de deducción natural, permitiendo la representación de proposiciones lógicas, la definición de pasos de inferencia y la verificación de la aplicación de las reglas de inferencia tanto para la lógica intuicionista como para la clásica.

Componentes Principales

    Prop: Clase para construir y representar proposiciones lógicas.

    Paso: Clase para representar un paso individual en una demostración, con su contexto y resolvente. Incluye métodos para verificar la aplicación de reglas de inferencia.

    Resolvedor: (Aún por implementar completamente) Clase que gestionará la secuencia de pasos para construir y verificar una demostración completa, posiblemente utilizando un DAG.

    Constantes de Reglas: Objetos congelados (Object.freeze) que definen los nombres canónicos de las reglas de inferencia para lógica intuicionista y clásica.

2. Clases y Funciones

2.1. Clase Prop

Representa una proposición lógica. Puede ser una variable, una negación, una implicación, una conjunción o una disyunción, o el símbolo de falsedad (bottom).

Constructor:
new Prop(type: string, ...args: Prop[] | string[])

    type: El tipo de la proposición ('Var', 'Neg', 'Impl', 'And', 'Or', 'Bottom').

    ...args:

        Si type es 'Var', el primer argumento es el nombre de la variable (string).

        Si type es 'Neg', el primer argumento es la proposición negada (Prop).

        Si type es 'Bottom', no se requieren argumentos.

        Si type es 'Impl', 'And', o 'Or', el primer y segundo argumento son las proposiciones izquierda y derecha, respectivamente (Prop).

Métodos de Instancia:

    impl(otherProp: Prop): Prop

        Crea una nueva proposición que es la implicación de this (antecedente) y otherProp (consecuente).

        Retorna: Prop

    and(otherProp: Prop): Prop

        Crea una nueva proposición que es la conjunción de this y otherProp.

        Retorna: Prop

    or(otherProp: Prop): Prop

        Crea una nueva proposición que es la disyunción de this y otherProp.

        Retorna: Prop

    neg(): Prop

        Crea una nueva proposición que es la negación de this.

        Retorna: Prop

    toString(): string

        Devuelve una representación en cadena de la proposición, utilizando símbolos lógicos Unicode (¬, →, ∧, ∨, ⊥).

        Retorna: string

Métodos Estáticos:

    Prop.equals(p1: Prop, p2: Prop): boolean

        Compara estructuralmente dos instancias de Prop para determinar si son lógicamente equivalentes en su forma (misma estructura y variables).

        Parámetros:

            p1: La primera proposición a comparar.

            p2: La segunda proposición a comparar.

        Retorna: boolean

Funciones de Ayuda (Globales):

    Var(name: string): Prop

        Función de conveniencia para crear una nueva variable proposicional.

    Bottom(): Prop

        Función de conveniencia para crear el símbolo de falsedad (Bottom).

Ejemplo de Uso:
JavaScript

const p = Var("p");
const q = Var("q");
const r = Var("r");

const pImplQ = p.impl(q); // (p → q)
const complexProp = p.and(q).impl(r); // ((p ∧ q) → r)
const notP = p.neg(); // (¬p)
const bottomProp = Bottom(); // ⊥

console.log(pImplQ.toString());
console.log(Prop.equals(p.and(q), Var("p").and(Var("q")))); // true

2.2. Clase Paso

Representa un paso individual dentro de una demostración de deducción natural. Contiene el contexto (proposiciones asumidas o ya probadas) y la proposición resolvente (la proposición derivada en este paso).

Constructor:
new Paso(contexto: Prop[], resolvente: Prop)

    contexto: Un array de instancias de Prop que representa las premisas o proposiciones ya establecidas en este punto de la demostración.

    resolvente: Una instancia de Prop que es la proposición derivada en este paso.

Métodos de Instancia:

    toString(): string

        Devuelve una representación en cadena del paso lógico en el formato "Contexto ⊢ Resolvente", utilizando el símbolo unicode ⊢.

        Retorna: string

    isAbleToApplyRule(ruleName: string, ...premises: Prop[]): boolean

        Verifica si este Paso actual es una aplicación válida de la ruleName especificada, dadas las premises adicionales que la regla pueda requerir.

        Parámetros:

            ruleName: El nombre de la regla de inferencia a verificar (debe ser una de las constantes definidas en IntuicionisticRules o ClassicalRules).

            ...premises: Un número variable de argumentos de tipo Prop que representan las proposiciones necesarias para la aplicación de la regla (e.g., los lados de una conjunción para AND_INTRODUCTION, o las implicaciones y antecedentes para IMPLICATION_ELIMINATION).

        Retorna: boolean

        Detalles de Implementación para isAbleToApplyRule:

            Internamente, usa Prop.equals para comparar proposiciones.

            Verifica que las proposiciones requeridas por la regla (premises) estén presentes en el this.contexto del Paso (excepto para reglas que descargan asunciones, donde la verificación es sobre la forma).

            Comprueba que la this.resolvente tenga la estructura correcta para la conclusión de la regla y que sus subcomponentes coincidan con las premisas.

            Nota sobre reglas de descarga (→I, ∨E, ¬I, PBC): La verificación de estas reglas es una simplificación en este modelo. En un sistema de prueba completo, estas requerirían un mecanismo de sub-pruebas para verificar que las proposiciones intermedias (derivedProp, derivedContradiction, conclusionFromLeft/Right) fueron realmente derivadas bajo las asunciones temporales y luego descargadas. Aquí, la función solo verifica la forma del paso dada la resolvente y las premises proporcionadas.

Reglas Soportadas por isAbleToApplyRule:

    Básicas (Intuicionistas):

        IntuicionisticRules.AXIOM (Asunción)

        IntuicionisticRules.AND_INTRODUCTION (∧I)

        IntuicionisticRules.AND_ELIMINATION (∧E)

        IntuicionisticRules.IMPLICATION_INTRODUCTION (→I)

        IntuicionisticRules.IMPLICATION_ELIMINATION (→E - Modus Ponens)

        IntuicionisticRules.OR_INTRODUCTION (∨I)

        IntuicionisticRules.OR_ELIMINATION (∨E)

        IntuicionisticRules.NEGATION_INTRODUCTION (¬I)

        IntuicionisticRules.NEGATION_ELIMINATION (¬E)

        IntuicionisticRules.BOTTOM_INTRODUCTION (⊥I - Ex Falso Quodlibet)

    Derivadas Comunes (Intuicionistas/Clásicas):

        IntuicionisticRules.MODUS_TOLLENS (MT)

        IntuicionisticRules.NEGATION_NEGATION_INTRODUCTION (¬¬I)

    Específicas de Lógica Clásica:

        ClassicalRules.NEGATION_NEGATION_ELIMINATION (¬¬E)

        ClassicalRules.EXCLUDED_MIDDLE (LEM - Principio del Tercero Excluido)

        ClassicalRules.PBC (Proof by Contradiction)

Ejemplo de Uso:
JavaScript

const p = Var("p");
const q = Var("q");
const pAndQ = p.and(q);

const pasoAndI = new Paso([p, q], pAndQ);
console.log(pasoAndI.isAbleToApplyRule(IntuicionisticRules.AND_INTRODUCTION, p, q)); // true

const pImplQ = p.impl(q);
const pasoImplE = new Paso([pImplQ, p], q);
console.log(pasoImplE.isAbleToApplyRule(IntuicionisticRules.IMPLICATION_ELIMINATION, pImplQ, p)); // true

const pOrNegP = p.or(p.neg());
const pasoLEM = new Paso([], pOrNegP);
console.log(pasoLEM.isAbleToApplyRule(ClassicalRules.EXCLUDED_MIDDLE, p)); // true

2.3. Clase Resolvedor

(Aún por implementar completamente)

Esta clase está diseñada para gestionar la secuencia de Pasos que forman una demostración. Su objetivo es construir un Grafo Acíclico Dirigido (DAG) de pasos resueltos, donde cada nodo es un Paso y las aristas representan las dependencias de las premisas.

Funcionalidades Previstas:

    Almacenar la secuencia de Pasos de la demostración.

    Mantener el estado del "contexto" de proposiciones disponibles en cada línea.

    Validar la corrección de cada Paso agregado utilizando los métodos isAbleToApplyRule de la clase Paso.

    Gestionar asunciones y la descarga de las mismas en el contexto de sub-pruebas para reglas como →I, ∨E, ¬I, y PBC.

    (Opcional) Implementar búsqueda de demostraciones o asistencia.

3. Constantes de Reglas

Estos objetos congelados proporcionan nombres canónicos para las reglas de deducción natural, facilitando la legibilidad y el mantenimiento del código al evitar cadenas mágicas.

3.1. IntuicionisticRules

Contiene las reglas fundamentales y algunas derivadas comunes en lógica intuicionista.
JavaScript

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
    MODUS_TOLLENS: "MT",
    NEGATION_NEGATION_INTRODUCTION: "¬¬I"
});

3.2. ClassicalRules

Extiende IntuicionisticRules para incluir axiomas y reglas específicas de la lógica clásica. Utiliza la sintaxis de propagación (...) para heredar las reglas intuicionistas y añade las propias.
JavaScript

const ClassicalRules = Object.freeze({
    ...IntuicionisticRules,
    NEGATION_NEGATION_ELIMINATION: "¬¬E", // Doble Negación (versión fuerte de ¬E)
    EXCLUDED_MIDDLE: "LEM",               // Principio del Tercero Excluido
    PBC: "PBC"                            // Prueba por Contradicción
});

Ejemplo de Uso:
JavaScript

console.log(IntuicionisticRules.IMPLICATION_INTRODUCTION); // →I
console.log(ClassicalRules.EXCLUDED_MIDDLE);             // LEM

4. Estructura de Archivos Recomendada

Para un proyecto más grande, podrías organizar tu código de la siguiente manera:

.
├── src/
│   ├── models/
│   │   ├── Prop.js        // Clase Prop y funciones Var, Bottom
│   │   ├── Paso.js        // Clase Paso
│   │   └── Resolvedor.js  // Clase Resolvedor
│   ├── rules/
│   │   └── RuleNames.js   // Constantes IntuicionisticRules, ClassicalRules
│   └── index.js           // Punto de entrada o archivo principal que importa y usa todo
└── README.md              // Este archivo de documentación

5. Cómo Contribuir / Próximos Pasos

    Implementación del Resolvedor: Desarrollar la lógica para construir y verificar demostraciones completas, incluyendo la gestión de contextos y el seguimiento de asunciones/descargas.

    Manejo de Variables Libres/Atadas: Si se extienden a lógica de predicados, será necesario manejar variables.

    Parser de Fórmulas: Implementar un parser para leer cadenas de texto de fórmulas y convertirlas en objetos Prop.

    Generador de Demostraciones: (Avanzado) Un módulo que intente construir demostraciones automáticamente.