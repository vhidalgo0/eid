from tkinter import messagebox
import sympy as sp

# Función para comprobar errores en la función ingresada
def comprobarErrores(texto_funcion, convertir_expresion, determinarDominio,
                     calcularRecorrido, calcularIntersecciones, graficarFuncion,
                     self):
    # Validar que no esté vacío
    if texto_funcion.strip() == "":
        messagebox.showerror("Error en la función:", "La función no puede estar vacía.")
        return None
    
    # No debe contener el signo "="
    if "=" in texto_funcion:
        messagebox.showerror("Error en la función:", "La función no puede contener igualdades.")
        return None
    
    # Intentar convertir a expresión matemática
    try:
        expresion = convertir_expresion(texto_funcion)
    except Exception as e:
        messagebox.showerror("Error en la función:", f"Expresión inválida: {e}")
        return None
    
    # Evitar que sea la función cero
    if expresion.is_constant() and expresion.simplify() == 0:
        messagebox.showerror("Error en la función:", "La función no puede ser cero.")
        return None
    
    # Solo debe usarse la variable x
    variable_x = sp.symbols('x')
    if expresion.free_symbols and expresion.free_symbols != {variable_x}:
        messagebox.showerror("Error en la función:", "La función solo puede contener la variable 'x'.")
        return None
    
    # Evitar infinitos o divisiones por cero
    if expresion == sp.zoo or expresion.has(sp.zoo):
        messagebox.showerror("Error en la función:", "La función no puede tener infinitos o divisiones por 0.")
        return None
    
    # Si pasa todas las validaciones, se procede al análisis
    try:
        funcion_numerica = sp.lambdify(variable_x, expresion, 'math')
        dominio_resultado, pasos_dominio = determinarDominio(expresion)
        recorrido_resultado = calcularRecorrido(expresion)
        xi, y0 = calcularIntersecciones(expresion)
        
        # Mostrar resultados en pantalla
        self.mostrarAnalisis(expresion, dominio_resultado, pasos_dominio, recorrido_resultado, xi, y0)
        graficarFuncion(self, funcion_numerica, expresion)
    except Exception as e:
        messagebox.showerror("Error en la función:", f"No se pudo crear la función: {e}")
        return None

# Función para comprobar errores al evaluar un valor
def erroresEvaluar(texto_evaluar):
    # Validar que no esté vacío
    if texto_evaluar.strip() == "":
        messagebox.showerror("Error al evaluar:", "El campo de evaluar no puede estar vacío.")
        return None
    
    # Intentar convertir a número real
    try:
        return float(texto_evaluar)
    except ValueError:
        messagebox.showerror("Error al evaluar:", "El valor a evaluar debe ser un número real.")
        return None