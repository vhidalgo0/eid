from analisis import calcularFuncion, calcularIntersecciones
import sympy as sp

# --------------------------------------------------------------
# ------------- Grafica la funcion en pantalla -----------------
# --------------------------------------------------------------
def graficarFuncion(self, funcion_numerica, expresion_simbolica):
    # Calcular valores
    valores_y = calcularFuncion(funcion_numerica)
    valores_x = list(range(-10, 11))
    
    # Limpiar y graficar
    self.ax.clear()
    self.ax.set_title("Gráfica de f(x)")
    self.ax.set_xlabel("x")
    self.ax.set_ylabel("y")
    self.ax.grid(True)

    # Usar la expresion simbolica directamente para intersecciones
    try:
        xi, y0 = calcularIntersecciones(expresion_simbolica)
    except:
        xi, y0 = [], float('NaN')
    
    # Graficar la función
    self.ax.plot(valores_x, valores_y, label="f(x)", linewidth=2)
    
    # Marcar intersecciones si existen
    if not (str(y0) == 'nan' or y0 == float('inf') or y0 == float('-inf')):
        self.ax.scatter(0, y0, color="red", s=80, label=f"Intersección eje Y (0, {y0:.2f})", zorder=5)
    
    for i, xi_val in enumerate(xi):
        if i < 5:  # Limitar a 5 intersecciones para no saturar
            self.ax.scatter(float(xi_val), 0, color="green", s=80, label=f"Intersección eje X ({float(xi_val):.2f}, 0)", zorder=5)
    
    self.ax.axhline(0, color='black', linewidth=0.8)
    self.ax.axvline(0, color='black', linewidth=0.8)
    self.ax.legend()
    # Actualizar canvas
    self.canvas.draw()