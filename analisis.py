import sympy as sp
import re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

x = sp.symbols('x')
# --------------------------------------------------------------
# ------------- Conversión de expresiones ----------------------
# --------------------------------------------------------------
transformaciones_parser = standard_transformations + (implicit_multiplication_application,)

def convertir_expresion(texto_funcion):
    try:
        if '^' in texto_funcion:
            texto_funcion = texto_funcion.replace('^', '**')  # Reemplazar ^ por ** para potencias
            
        if "," in texto_funcion:
            texto_funcion = texto_funcion.replace(',', '.')  # Reemplazar , por . para decimales
        
        # Manejar valor absoluto |x| -> Abs(x)
        if "|" in texto_funcion:
            texto_funcion = re.sub(r'\|([^|]+)\|', r'Abs(\1)', texto_funcion)
        
        # Convertir la funcion en una expresion de SymPy usando parse_expr
        expresion_convertida = parse_expr(texto_funcion, transformations=transformaciones_parser)
        return expresion_convertida
    except Exception as e:
        raise ValueError(f"No se pudo convertir la expresión: {e}")

# --------------------------------------------------------------
# ------------- Calcular recorrido aproximado ------------------
# --------------------------------------------------------------
def calcularRecorrido(expresion_simbolica):
    try:
        # Evaluar en varios puntos para estimar el recorrido
        valores_y = []
        for i in range(-100, 101):
            try:
                y_val = float(expresion_simbolica.subs(x, i/10))
                if abs(y_val) < 1e6 and str(y_val) != 'nan':  # Verificar valores finitos
                    valores_y.append(y_val)
            except:
                continue
        
        if valores_y:
            y_min = min(valores_y)
            y_max = max(valores_y)
            return f"Aproximadamente [{y_min:.2f}, {y_max:.2f}]"
        else:
            return "No se pudo determinar"
    except:
        return "No se pudo determinar"

# --------------------------------------------------------------
# ------------- Buscar intersecciones numéricamente -----------
# --------------------------------------------------------------
def buscar_intersecciones_numericas(expresion_simbolica):
    intersecciones_numericas = []
    try:
        # Evaluar en muchos puntos para buscar cambios de signo
        for i in range(-100, 101):
            x_val = i / 10.0  # De -10 a 10 con paso 0.1
            try:
                y1 = float(expresion_simbolica.subs(x, x_val))
                y2 = float(expresion_simbolica.subs(x, x_val + 0.1))
                
                # Si hay cambio de signo, hay una raíz entre estos puntos
                if y1 * y2 < 0 and abs(y1) < 1e6 and abs(y2) < 1e6:
                    # Aproximar la raíz por bisección simple
                    raiz_aprox = x_val + 0.05  # Punto medio
                    intersecciones_numericas.append(raiz_aprox)
            except:
                continue
                
        # Eliminar duplicados cercanos
        intersecciones_finales = []
        for raiz in intersecciones_numericas:
            es_nueva = True
            for existente in intersecciones_finales:
                if abs(raiz - existente) < 0.2:  # Si están muy cerca, es la misma
                    es_nueva = False
                    break
            if es_nueva:
                intersecciones_finales.append(raiz)
                
        return intersecciones_finales[:5]  # Máximo 5
    except:
        return []

# --------------------------------------------------------------
# ------------- Calcular las intersecciones -------------------
# --------------------------------------------------------------
def calcularIntersecciones(expresion_simbolica):
    try:
        y0 = expresion_simbolica.subs(x, 0) # Interseccion con y
        y0 = float(y0) if y0.is_real else float('NaN')
    except (ZeroDivisionError, ValueError, OverflowError):
        y0 = float('NaN')
    
    try:
        xi = []
        x0 = sp.solve(sp.Eq(expresion_simbolica, 0), x) # Interseccion con x (método simbólico)
        for s in x0:
            if s.is_real: 
                xi.append(float(s))
        
        # Si no encontró soluciones simbólicas, buscar numéricamente
        if not xi:
            xi_numericas = buscar_intersecciones_numericas(expresion_simbolica)
            xi.extend(xi_numericas)
            
    except (ZeroDivisionError, ValueError, OverflowError):
        # Si falla completamente, buscar numéricamente
        xi = buscar_intersecciones_numericas(expresion_simbolica)
        
    return xi, y0

# --------------------------------------------------------------
# ------------- Calcula los valores de la funcion --------------
# --------------------------------------------------------------
def calcularFuncion(funcion_numerica):
    valores_y = [] # Lista de valores de y
    for i in range(-10, 11): # Evaluar en el rango -10 a 10
        try:
            valores_y.append(funcion_numerica(i))
        except (ZeroDivisionError, ValueError, OverflowError): # Manejo de errores
            valores_y.append(float('NaN'))
    return valores_y

# --------------------------------------------------------------
# ------------- Determinar dominio -----------------------------
# --------------------------------------------------------------
def determinarDominio(expresion_simbolica):
    pasos = []

    # Revisar si hay denominador (división por 0)
    den = sp.denom(expresion_simbolica)
    if den != 1:
        try:
            ceros = sp.solve(sp.Eq(den, 0), x)
            if ceros:
                pasos.append(f"Se quita {ceros} porque hacen cero el denominador.")
        except:
            pasos.append(f"Se requiere que {den} ≠ 0.")

    # Revisar si hay raíz cuadrada (sqrt)
    for pot in expresion_simbolica.atoms(sp.Pow):
        base, exp = pot.as_base_exp()
        if exp == sp.Rational(1,2):  # raíz cuadrada
            pasos.append(f"Se pide {base} ≥ 0 por la raíz cuadrada.")

    # Revisar si hay funciones sqrt directamente
    for expr in expresion_simbolica.atoms(sp.sqrt):
        arg = expr.args[0]
        pasos.append(f"Se pide {arg} ≥ 0 por sqrt({arg}).")

    # Revisar si hay logaritmos 
    for log in expresion_simbolica.atoms(sp.log):
        arg = log.args[0]
        pasos.append(f"Se pide {arg} > 0 por log({arg}).")

    # Revisar si hay funciones trigonométricas inversas
    for asin_expr in expresion_simbolica.atoms(sp.asin):
        arg = asin_expr.args[0]
        pasos.append(f"Se pide -1 ≤ {arg} ≤ 1 por asin({arg}).")

    for acos_expr in expresion_simbolica.atoms(sp.acos):
        arg = acos_expr.args[0]
        pasos.append(f"Se pide -1 ≤ {arg} ≤ 1 por acos({arg}).")

    if not pasos:
        pasos.append("La función se puede usar en todos los reales.")

    return sp.S.Reals, "\n".join(pasos)