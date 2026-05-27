import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import locale
import re

# --- VARIABLE DE CONTROL ---
esperando_nuevo_numero = False

try:
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

def resolver_ruta(ruta_relativa):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)

# ---------------- LÓGICA DE FORMATEO Y TAMAÑO ----------------

def ajustar_fuente():
    texto = pantalla.get()
    largo = len(texto)
    if largo <= 12: nueva_fuente = ("Segoe UI", 35)
    elif largo <= 18: nueva_fuente = ("Segoe UI", 25)
    else: nueva_fuente = ("Segoe UI", 18)
    pantalla.configure(font=nueva_fuente)

def formatear_segmento(segmento):
    if not segmento: return ""
    tiene_pct = "%" in segmento
    temp = segmento.replace("%", "").replace(".", "")
    try:
        if ',' in temp:
            partes = temp.split(',')
            entera = partes[0] if partes[0] != "" else "0"
            entera_fmt = locale.format_string("%d", int(entera), grouping=True)
            res = entera_fmt + "," + partes[1]
        else:
            res = locale.format_string("%d", int(temp), grouping=True)
        return res + "%" if tiene_pct else res
    except:
        return segmento

def actualizar_formato_visual():
    pantalla.config(state="normal")
    texto_actual = pantalla.get()
    if not texto_actual or texto_actual == "Error": 
        pantalla.config(state="readonly")
        return
    
    tokens = re.split(r'([+\-*/×÷−])', texto_actual)
    texto_fmt = ""
    for t in tokens:
        if t in "+-*/×÷−": texto_fmt += t
        else: texto_fmt += formatear_segmento(t)
    
    if texto_actual != texto_fmt:
        pantalla.delete(0, tk.END)
        pantalla.insert(0, texto_fmt)
    
    ajustar_fuente()
    pantalla.config(state="readonly")

# ---------------- FUNCIONES BOTONES ----------------

def agregar(valor):
    global esperando_nuevo_numero
    pantalla.config(state="normal")
    if esperando_nuevo_numero:
        if valor.isdigit() or valor == ",":
            pantalla.delete(0, tk.END)
        esperando_nuevo_numero = False
    pantalla.insert(tk.END, valor)
    actualizar_formato_visual()

def limpiar():
    global esperando_nuevo_numero
    pantalla.config(state="normal")
    pantalla.delete(0, tk.END)
    esperando_nuevo_numero = False
    ajustar_fuente()
    pantalla.config(state="readonly")

def borrar():
    global esperando_nuevo_numero
    pantalla.config(state="normal")
    if esperando_nuevo_numero:
        limpiar()
    else:
        texto = pantalla.get()
        pantalla.delete(0, tk.END)
        pantalla.insert(0, texto[:-1])
        actualizar_formato_visual()
    pantalla.config(state="readonly")

def calcular():
    global esperando_nuevo_numero
    pantalla.config(state="normal")
    try:
        texto = pantalla.get().strip().replace('.', '').replace(',', '.')
        if not texto: return
        if texto[-1] in "+-*/×÷−": texto = texto[:-1]

        patron = r'(\d+\.?\d*)([+\-−×*÷/])(\d+\.?\d*)%'
        match = re.search(patron, texto)
        
        if match:
            base, operador, porcentaje = match.groups()
            if operador in "+-−":
                op_mat = '-' if operador == "−" else operador
                nueva_expresion = f"{base}{op_mat}({base}*{porcentaje}/100)"
            else:
                op_mat = '*' if operador in "×*" else '/'
                nueva_expresion = f"{base}{op_mat}({porcentaje}/100)"
            texto = texto.replace(match.group(0), nueva_expresion)
        else:
            texto = re.sub(r'(\d+\.?\d*)%', r'(\1/100)', texto)
        
        expresion = texto.replace('×', '*').replace('−', '-').replace('÷', '/')
        resultado = eval(expresion)
        
        res_fmt = locale.format_string("%.2f", resultado, grouping=True)
        if ',' in res_fmt: res_fmt = res_fmt.rstrip('0').rstrip(',')
            
        pantalla.delete(0, tk.END)
        pantalla.insert(0, res_fmt)
        ajustar_fuente()
        esperando_nuevo_numero = True
    except:
        pantalla.delete(0, tk.END)
        pantalla.insert(0, "Error")
        esperando_nuevo_numero = True
    pantalla.config(state="readonly")

# ---------------- VENTANA ----------------

ventana = tk.Tk()
ventana.title("Calculadora")
ventana.geometry("360x600")
ventana.resizable(False, False)

try:
    icono_path = resolver_ruta("icono.ico")
    ventana.iconbitmap(icono_path)
except: pass

try:
    img_p = resolver_ruta("fondo.png") 
    img = Image.open(img_p).resize((360, 600), Image.Resampling.LANCZOS)
    foto = ImageTk.PhotoImage(img)
    lbl_f = tk.Label(ventana, image=foto)
    lbl_f.place(x=0, y=0, relwidth=1, relheight=1)
    lbl_f.image = foto 
except: pass

# PANTALLA CON COLORES FIJOS EN ESTADO BLOQUEADO
pantalla = tk.Entry(ventana, font=("Segoe UI", 35), bg="#1F1F1F", fg="white", 
                    readonlybackground="#1F1F1F", disabledforeground="white",
                    bd=0, justify="right", insertbackground="white", state="readonly")
pantalla.pack(fill="both", padx=20, pady=(30, 10), ipady=20)

frame = tk.Frame(ventana, bg="#1F1F1F")
frame.pack(expand=True, fill="both", padx=15, pady=10)

for i in range(6): frame.rowconfigure(i, weight=1)
for j in range(4): frame.columnconfigure(j, weight=1)

def crear_boton(texto, fila, columna, color, comando):
    btn = tk.Button(frame, text=texto, font=("Segoe UI", 16), bg=color, fg="white", 
                    bd=0, activebackground="#505050", command=comando)
    btn.grid(row=fila, column=columna, sticky="nsew", padx=4, pady=4)

botones = [
    ("%", lambda: agregar("%"), "#323232"), ("CE", limpiar, "#323232"),
    ("C", limpiar, "#323232"), ("⌫", borrar, "#323232"),
    ("1/x", lambda: agregar("1/"), "#3A3A3D"), ("x²", lambda: agregar("**2"), "#3A3A3D"),
    ("√x", lambda: agregar("**0.5"), "#3A3A3D"), ("÷", lambda: agregar("/"), "#3A3A3D"),
    ("7", lambda: agregar("7"), "#2D2D30"), ("8", lambda: agregar("8"), "#2D2D30"),
    ("9", lambda: agregar("9"), "#2D2D30"), ("×", lambda: agregar("*"), "#3A3A3D"),
    ("4", lambda: agregar("4"), "#2D2D30"), ("5", lambda: agregar("5"), "#2D2D30"),
    ("6", lambda: agregar("6"), "#2D2D30"), ("−", lambda: agregar("-"), "#3A3A3D"),
    ("1", lambda: agregar("1"), "#2D2D30"), ("2", lambda: agregar("2"), "#2D2D30"),
    ("3", lambda: agregar("3"), "#2D2D30"), ("+", lambda: agregar("+"), "#3A3A3D"),
    ("+/-", lambda: agregar("-"), "#2D2D30"), ("0", lambda: agregar("0"), "#2D2D30"),
    (".", lambda: agregar(","), "#2D2D30"), 
]

fila, columna = 0, 0
for texto, comando, color in botones:
    crear_boton(texto, fila, columna, color, comando)
    columna += 1
    if columna == 4: columna = 0; fila += 1

tk.Button(frame, text="=", font=("Segoe UI", 18), bg="#671669", fg="white", bd=0, command=calcular).grid(row=5, column=3, sticky="nsew", padx=4, pady=4)

def tecla_presionada(event):
    tecla, char = event.keysym, event.char
    if tecla in ("Return", "KP_Enter"): calcular()
    elif tecla == "BackSpace": borrar()
    elif tecla == "Escape": limpiar()
    elif char in "0123456789": agregar(char)
    elif char in "+-*/%": agregar(char)
    elif char in ".,": agregar(",")
    return "break"

ventana.bind("<Key>", tecla_presionada)
ventana.mainloop()
