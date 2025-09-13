import customtkinter as ctk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from sympy import lambdify, symbols, zoo
from analisis import convertir_expresion, determinarDominio, calcularRecorrido, calcularIntersecciones
from grafica import graficarFuncion

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analizador y Graficador de Funciones")
        self.geometry("1200x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Configuracion del grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)  
        self.grid_columnconfigure(0, weight=1, uniform="cols") 
        self.grid_columnconfigure(1, weight=1, uniform="cols")
        
        # Elementos de la interfaz
        self.frame = ctk.CTkFrame(self)
        self.frame.grid(row = 0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10) 
        
        # Elementos del frame superior
        
        # Elementos para la funcion
        self.frame_funcion = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.frame_funcion.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.label_funcion = ctk.CTkLabel(self.frame_funcion, text="Funcion f(x):", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_funcion.pack(side="left", padx=(0, 5))
        self.input = ctk.CTkEntry(self.frame_funcion, width=700)
        self.input.pack (expand=True, pady=10)

        # Elementos para evaluar
        self.frame_evaluar = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.frame_evaluar.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        self.label_evaluar = ctk.CTkLabel(self.frame_evaluar, text="Evaluar en x =", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_evaluar.pack(side="left", padx=(0, 5))
        self.input_evaluar = ctk.CTkEntry(self.frame_evaluar, width=700)
        self.input_evaluar.pack(expand=True, pady=10)

        # Botones
        self.frame_boton = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.frame_boton.grid(row=0, column=1, rowspan=2, sticky="", padx=5, pady=5)
        self.button_funcion = ctk.CTkButton(self.frame_boton, text="Calcular", width=200, height=40, command=lambda: self.comprobarErrores(self.input.get()))
        self.button_funcion.pack(expand=True, pady=10)
        self.button_evaluar = ctk.CTkButton(self.frame_boton, text="Evaluar", width=200, height=40)
        self.button_evaluar.pack(expand=True, pady=10)

        # Elementos para el analisis
        self.frame_analisis = ctk.CTkFrame(self)
        self.frame_analisis.grid(row=1, column=0, sticky="nsew", padx=(10,5), pady=(0,10))
        
        # Label para mostrar resultados del analisis
        self.label_titulo = ctk.CTkLabel(self.frame_analisis, text="Análisis de la Función", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_titulo.pack(pady=10)
        
        # Texto para mostrar dominio
        self.textbox_analisis = ctk.CTkTextbox(self.frame_analisis, height=200, width=300)
        self.textbox_analisis.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Elementos para la grafica
        self.fig, self.ax = plt.subplots(figsize=(5,4))
        self.ax.grid(True)
        
        self.frame_grafica = ctk.CTkFrame(self)
        self.frame_grafica.grid(row=1, column=1, sticky="nsew", padx=(5,10), pady=(0,10))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafica)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # --------------------------------------------------------------
    # ------------- Comprueba errores en la funcion ----------------
    # --------------------------------------------------------------
    def comprobarErrores(self, texto_funcion):
        if texto_funcion.strip() == "": # Verificar si la funcion esta vacia
            messagebox.showerror("Error en la función:", "La función no puede estar vacía.") 
            return None
        
        if "=" in texto_funcion: # Verificar si la funcion tiene igualdades
            messagebox.showerror("Error en la función:", "La función no puede contener igualdades.")
            return None
        
        try:
            expresion = convertir_expresion(texto_funcion) # Convertir la funcion a una expresion de SymPy
        except Exception as e:
            messagebox.showerror("Error en la función:", f"Expresión inválida: {e}")
            return None


        if expresion.is_constant(): # Verificar si la funcion es constante
            if expresion.simplify() == 0: # Verificar si la funcion es cero
                messagebox.showerror("Error en la función:", "La función no puede ser cero.") 
                return None
        
            
        # Verificar si la funcion tiene variables distintas a x
        variable_x = symbols('x')
        variables_en_funcion = expresion.free_symbols
        if variables_en_funcion and variables_en_funcion != {variable_x}:
            messagebox.showerror("Error en la función:", "La función solo puede contener la variable 'x'.")
            return None


        if expresion == zoo or expresion.has(zoo): # Verificar si la funcion tiene infinitos
            messagebox.showerror("Error en la función:", "La función no puede tener infinitos o divisiones por 0.")
            return None
        
        
        # Crear la funcion numerica
        try:
            funcion_numerica = lambdify(variable_x, expresion, 'math')
            dominio_resultado, pasos_dominio = determinarDominio(expresion) # Determinar el dominio de la funcion
            recorrido_resultado = calcularRecorrido(expresion) # Calcular recorrido aproximado
            xi, y0 = calcularIntersecciones(expresion) # Calcular intersecciones
            self.mostrarAnalisis(expresion, dominio_resultado, pasos_dominio, recorrido_resultado, xi, y0) # Mostrar el analisis en la interfaz
            graficarFuncion(self, funcion_numerica, expresion) # Pasar tambien la expresion simbolica
        except Exception as e:
            messagebox.showerror("Error en la función:", f"No se pudo crear la función: {e}")
            return None
    
    
    # --------------------------------------------------------------
    # ------------- Comprueba errores en evaluar -------------------
    # --------------------------------------------------------------
    def erroresEvaluar(self, texto_evaluar):
        if texto_evaluar.strip() == "": # Verificar si el campo de evaluar esta vacio
            messagebox.showerror("Error al evaluar:", "El campo de evaluar no puede estar vacío.") 
            return None
        
        try:
            valor_evaluar = float(texto_evaluar) # Convertir el texto a un numero
            return valor_evaluar
        except ValueError:
            messagebox.showerror("Error al evaluar:", "El valor a evaluar debe ser un número real.")
            return None
        
    
    # --------------------------------------------------------------
    # ------------- Mostrar analisis en la interfaz ---------------
    # --------------------------------------------------------------
    def mostrarAnalisis(self, expresion, dominio, pasos_dominio, recorrido, xi, y0):
        # Limpiar el textbox
        self.textbox_analisis.delete("0.0", "end")
        
        # Mostrar la funcion
        self.textbox_analisis.insert("0.0", f"Función: f(x) = {expresion}\n\n")
        
        # Mostrar dominio
        self.textbox_analisis.insert("end", f"Dominio: {dominio}\n\n")
        
        # Mostrar pasos del dominio
        self.textbox_analisis.insert("end", f"Justificación del dominio:\n{pasos_dominio}\n\n")
        
        # Mostrar recorrido
        self.textbox_analisis.insert("end", f"Recorrido: {recorrido}\n")
        self.textbox_analisis.insert("end", "Cómo se obtuvo: Se evaluó la función en puntos desde -10 a 10\n")
        self.textbox_analisis.insert("end", "con pasos de 0.1 y se tomaron los valores mínimo y máximo.\n")
        self.textbox_analisis.insert("end", "Es una aproximación estimada en [-10,10].\n\n")
        
        # Mostrar intersecciones
        self.textbox_analisis.insert("end", "Intersecciones:\n")
        if not (str(y0) == 'nan' or y0 == float('inf') or y0 == float('-inf')):
            self.textbox_analisis.insert("end", f"• Eje Y: (0, {y0:.3f})\n")
            self.textbox_analisis.insert("end", "  Ecuación resuelta: f(0) = y\n")
        else:
            self.textbox_analisis.insert("end", "• Eje Y: No existe\n")
            self.textbox_analisis.insert("end", "  Por qué: x=0 no está en el dominio o f(0) no es real\n")
            
        if xi:
            for i, x_val in enumerate(xi[:5]): 
                self.textbox_analisis.insert("end", f"• Eje X: ({x_val:.3f}, 0)\n")
            self.textbox_analisis.insert("end", "  Ecuación resuelta: f(x) = 0 (método simbólico o numérico)\n")
        else:
            self.textbox_analisis.insert("end", "• Eje X: No hay intersecciones\n")
            self.textbox_analisis.insert("end", "  Por qué: La ecuación f(x) = 0 no tiene soluciones en [-10,10]\n")
