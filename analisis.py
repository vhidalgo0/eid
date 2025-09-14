import sympy as sp
import re
import math
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

x = sp.symbols('x')
# --------------------------------------------------------------
# ------------- Conversión de expresiones ----------------------
# --------------------------------------------------------------
transformaciones_parser = standard_transformations + (implicit_multiplication_application,)
#-------------------------------------------------------------------
_local_dict = {
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
    'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
    'Abs': sp.Abs, 'pi': sp.pi, 'E': sp.E
}

def convertir_expresion(texto_funcion):
    texto = texto_funcion.strip()
    texto = texto.replace('^', '**').replace(',', '.')
    texto = re.sub(r'\|([^|]+)\|', r'Abs(\1)', texto)
    try:
        expr = parse_expr(texto, transformations = transformaciones_parser, local_dict = _local_dict)          
    except Exception as e:
        raise ValueError(f"No se pudo convertir la expresión: {e}")
    if expr.free_symbols and expr.free_symbols != {x}:
        raise ValueError("La funcion solo puede contener la variable 'x'. ")
    return expr

# --------------------------------------------------------------
# ------------- Calcular recorrido -----------------------------
# --------------------------------------------------------------
def calcularRecorrido(expresion_simbolica, dominio=None):
    # Intentar primero function_range simbólico
    try:
        r = sp.calculus.util.function_range(expresion_simbolica, x, dominio if dominio else sp.S.Reals)
        return f"Recorrido exacto: {sp.pretty(r)}"
    except Exception:
        pass
    # Aproximación numérica
    try:
        fn = sp.lambdify(x, expresion_simbolica, 'math')
    except Exception:
        return "No se pudo determinar"
    valores_y = []
    for i in range(-200, 201):  # Extender a [-20, 20] para mejor aproximación
        xv = i/10
        try:
            y_val = fn(xv)
            if isinstance(y_val, (int, float)) and math.isfinite(y_val) and abs(y_val) < 1e6:
                valores_y.append(float(y_val))
        except Exception:
            continue
    if valores_y:
        return f"Aproximado en [-20,20]: [{min(valores_y):.2f}, {max(valores_y):.2f}]"
    return "No se pudo determinar"

# --------------------------------------------------------------
# ------------- Buscar intersecciones numéricamente -----------
# --------------------------------------------------------------
def _biseccion(fn, a, b, tol=1e-6, maxiter=50):
    fa, fb = fn(a), fn(b)
    if not (math.isfinite(fa) and math.isfinite(fb)) or fa * fb > 0:
        raise ValueError("Bisección no aplicable")
    for _ in range(maxiter):
        m = (a + b) / 2.0
        fm = fn(m)
        if not math.isfinite(fm):
            break
        if abs(fm) < tol or (b - a) / 2 < tol:
            return m
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return (a + b) / 2.0
    
def buscar_intersecciones_numericas(expresion_simbolica, rango=(-10, 10), step=0.1):
    try:
        fn = sp.lambdify(x, expresion_simbolica, 'math')
    except Exception:
        return []
    posibles = []
    a0, b0 = rango
    i = a0
    while i < b0:
        a, b = i, i + step
        try:
            fa, fb = fn(a), fn(b)
            if not (math.isfinite(fa) and math.isfinite(fb)):
                i += step
                continue
            if fa * fb < 0:
                try:
                    raiz = _biseccion(fn, a, b)
                    posibles.append(raiz)
                except Exception:
                    posibles.append((a + b) / 2.0)
        except Exception:
            pass
        i += step
    # eliminar duplicados cercanos
    finales = []
    for r in posibles:
        if not any(abs(r - s) < 1e-3 for s in finales):
            finales.append(r)
    return finales[:10]

# --------------------------------------------------------------
# ------------- Calcular las intersecciones -------------------
# --------------------------------------------------------------
def calcularIntersecciones(expresion_simbolica):
    # intersección con eje Y
    try:
        y0_sym = expresion_simbolica.subs(x, 0)
        y0 = float(sp.N(y0_sym))
    except Exception:
        y0 = float('nan')

    # intersección con eje X: preferir solveset en los reales
    xi = []
    try:
        solset = sp.solveset(sp.Eq(expresion_simbolica, 0), x, domain=sp.S.Reals)
        # Si es un conjunto finito, convertir a float
        if getattr(solset, 'is_FiniteSet', False):
            for s in solset:
                try:
                    xi.append(float(sp.N(s)))
                except Exception:
                    continue
        else:
            # fallback numérico
            xi = buscar_intersecciones_numericas(expresion_simbolica)
    except Exception:
        xi = buscar_intersecciones_numericas(expresion_simbolica)

    return [round(r, 5) for r in xi], y0

# --------------------------------------------------------------
# ------------- Determinar dominio -----------------------------
# --------------------------------------------------------------
def determinarDominio(expresion_simbolica):
    pasos = []
    dominio = sp.S.Reals

    # 1) discontinuidades / singularidades
    try:
        sing = sp.calculus.util.singularities(expresion_simbolica, x)
        if sing:
            pasos.append(f"Excluir {sing} por ser puntos de discontinuidad.")
            dominio = sp.Complement(dominio, sing)
    except Exception:
        pasos.append("No se pudo determinar singularidades exactamente.")

    # 2) denominador != 0
    den = sp.denom(expresion_simbolica)
    if den != 1:
        try:
            ceros = sp.solveset(sp.Eq(den, 0), x, domain=sp.S.Reals)
            pasos.append(f"Excluir {ceros} porque anulan el denominador {den}.")
            dominio = sp.Complement(dominio, ceros)
        except Exception:
            pasos.append(f"No se pudo resolver denominador {den} exactamente.")

    # 3) restricciones de potencias pares, sqrt, log
    for pot in expresion_simbolica.atoms(sp.Pow):
        base, exp = pot.as_base_exp()
        if exp.is_Rational and exp.q % 2 == 0:
            pasos.append(f"Se exige {base} ≥ 0 por exponente {exp}.")
            try:
                sol = sp.solve_univariate_inequality(base >= 0, x)
                dominio = sp.Intersection(dominio, sol)
            except Exception:
                pass

    for s in expresion_simbolica.atoms(sp.Function):
        if isinstance(s, sp.log):
            arg = s.args[0]
            pasos.append(f"Se pide {arg} > 0 por log({arg}).")
            try:
                sol = sp.solve_univariate_inequality(arg > 0, x)
                dominio = sp.Intersection(dominio, sol)
            except Exception:
                pass
        if s.func == sp.sqrt:
            arg = s.args[0]
            pasos.append(f"Se pide {arg} ≥ 0 por sqrt({arg}).")
            try:
                sol = sp.solve_univariate_inequality(arg >= 0, x)
                dominio = sp.Intersection(dominio, sol)
            except Exception:
                pass

    if not pasos:
        pasos.append("La función se puede usar en todos los reales.")
    return dominio, "\n".join(f"{i+1}) {p}" for i, p in enumerate(pasos))

# --------------------------------------------------------------
# ------------- Evaluación paso a paso -------------------------
# --------------------------------------------------------------
def evaluar_en_punto(expresion_simbolica, valor):
    pasos = []
    pasos.append(f"1) Función: f(x) = {sp.pretty(expresion_simbolica)}")
    pasos.append(f"2) Sustituimos x = {valor}: {sp.pretty(expresion_simbolica.subs(x, valor))}")
    try:
        resultado_simpl = sp.simplify(expresion_simbolica.subs(x, valor))
        resultado_num = float(sp.N(resultado_simpl))
        pasos.append(f"3) Simplificando: {sp.pretty(resultado_simpl)}")
        pasos.append(f"4) Evaluación numérica: f({valor}) ≈ {resultado_num}")
    except Exception as e:
        pasos.append(f"No se pudo evaluar numéricamente: {e}")
        resultado_num = float('nan')
    return resultado_num, "\n".join(pasos)

