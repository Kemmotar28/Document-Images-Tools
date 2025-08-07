import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import random
from gpt4all import GPT4All
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

def crear_imagen_texto(config):
    """
    Genera una imagen PNG con texto formateado, tamaño A4, márgenes y soporte para títulos.
    
    Parámetros:
        config (dict): Diccionario con las claves:
            - texto (str): Texto principal (puede tener \n\n para separar párrafos)
            - titulo (str): Título opcional (aparece al inicio)
            - nombre_archivo (str): Nombre del archivo (sin extensión)
            - fuente_path (str): Ruta al archivo de fuente (.ttf, .otf). Si no existe, usa predeterminada.
            - tamaño_fuente (int): Tamaño base del texto (por defecto 20)
    """
    # Parámetros con valores por defecto
    texto = config.get("texto", "")
    titulo = config.get("titulo", "")
    nombre_archivo = config.get("nombre_archivo", "documento")
    fuente_path = config.get("fuente_path", None)
    tamaño_fuente = config.get("tamaño_fuente", 20)

    # Nombre de la carpeta: 3 primeras + 4 últimas letras del nombre_archivo
    nombre_carpeta = nombre_archivo[:3] + nombre_archivo[-4:]
    os.makedirs(nombre_carpeta, exist_ok=True)

    # Dimensiones A4 a 150 DPI
    ancho_imagen = 1240
    alto_imagen = 1754
    color_fondo = (255, 255, 255)
    color_texto = (0, 0, 0)
    margen = 50

    # Crear imagen
    imagen = Image.new('RGB', (ancho_imagen, alto_imagen), color_fondo)
    dibujo = ImageDraw.Draw(imagen)

    # Fuente principal
    try:
        fuente = ImageFont.truetype(fuente_path, tamaño_fuente) if fuente_path else ImageFont.load_default()
    except (OSError, IOError):
        print(f"⚠️ Fuente '{fuente_path}' no encontrada. Usando fuente predeterminada.")
        fuente = ImageFont.load_default()

    # Fuente del título (25% más grande)
    tamaño_titulo = int(tamaño_fuente * 1.25)
    try:
        fuente_titulo = ImageFont.truetype(fuente_path, tamaño_titulo) if fuente_path else ImageFont.truetype("arial.ttf", tamaño_titulo)
    except:
        try:
            fuente_titulo = ImageFont.truetype("arial.ttf", tamaño_titulo)
        except:
            # Si no hay arial, usamos la predeterminada escalada
            fuente_titulo = ImageFont.load_default()

    # Alturas y espaciados
    bbox = fuente.getbbox("Ay")
    linea_altura = bbox[3]
    espacio_entre_lineas = int(linea_altura * 0.6)
    espacio_entre_parrafos = linea_altura * 2

    # Posición inicial
    pos_y = margen

    # Dibujar título si existe
    if titulo:
        lineas_titulo = textwrap.wrap(titulo, width=50)  # Ajuste simple para título
        for linea in lineas_titulo:
            dibujo.text((margen, pos_y), linea, font=fuente_titulo, fill=color_texto)
            pos_y += tamaño_titulo + espacio_entre_lineas
        pos_y += espacio_entre_parrafos  # Espacio extra después del título

    # Procesar párrafos del texto principal
    parrafos = texto.split('\n\n')
    area_ancho = ancho_imagen - 2 * margen

    for parrafo in parrafos:
        lineas = textwrap.wrap(parrafo.strip(), width=int(area_ancho / fuente.getlength("a")))
        for linea in lineas:
            dibujo.text((margen, pos_y), linea, font=fuente, fill=color_texto)
            pos_y += linea_altura + espacio_entre_lineas
        pos_y += espacio_entre_parrafos  # Espacio entre párrafos

    # Guardar imagen
    ruta_archivo = os.path.join(nombre_carpeta, f"{nombre_archivo}.png")
    imagen.save(ruta_archivo)

    print(f"✅ Imagen guardada en: {ruta_archivo}")
    return ruta_archivo

class GPT4AllApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPT4All Prompt Runner")
        self.root.geometry("800x600")

        # Variables
        self.model_var = tk.StringVar(value="Nous-Hermes-2-Mistral-7B-DPO.Q4_0")
        self.temperature_var = tk.DoubleVar(value=0.7)
        self.top_p_var = tk.DoubleVar(value=0.9)
        self.top_k_var = tk.IntVar(value=40)

        self.prompt_text = ""
        self.generated_text = ""

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Modelo selector
        tk.Label(self.root, text="Seleccionar modelo:").pack(pady=5)
        model_options = ["Nous-Hermes-2-Mistral-7B-DPO.Q4_0", "Meta-Llama-3-8B-Instruct.Q4_0"]
        tk.OptionMenu(self.root, self.model_var, *model_options).pack()

        # Botón seleccionar archivo
        tk.Button(self.root, text="Seleccionar archivo de texto", command=self.load_prompt_file).pack(pady=10)

        # Parámetros
        param_frame = tk.Frame(self.root)
        param_frame.pack(pady=10)

        tk.Label(param_frame, text="Temperatura:").grid(row=0, column=0)
        tk.Scale(param_frame, from_=0.0, to_=2.0, resolution=0.1, orient="horizontal",
                 variable=self.temperature_var).grid(row=0, column=1)

        tk.Label(param_frame, text="Top-P:").grid(row=1, column=0)
        tk.Scale(param_frame, from_=0.0, to_=1.0, resolution=0.01, orient="horizontal",
                 variable=self.top_p_var).grid(row=1, column=1)

        tk.Label(param_frame, text="Top-K:").grid(row=2, column=0)
        tk.Scale(param_frame, from_=1, to_=100, resolution=1, orient="horizontal",
                 variable=self.top_k_var).grid(row=2, column=1)

        # Área de salida
        self.output_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.output_box.pack(pady=10)

        # Botones
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Generar respuesta", command=self.generate_response).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Limpiar", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Guardar resultado", command=self.save_result).pack(side=tk.LEFT, padx=5)

    def load_prompt_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if not paragraphs:
            messagebox.showerror("Error", "El archivo no contiene párrafos válidos.")
            return
        self.prompt_text = random.choice(paragraphs)
        self.update_output(f"Prompt seleccionado:\n{self.prompt_text}\n\n")

    def update_output(self, message):
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, message)

    def generate_response(self):
        if not self.prompt_text:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo de texto.")
            return

        model_name = self.model_var.get()
        try:
            model = GPT4All(model_name=model_name)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el modelo: {e}")
            return

        config = {
            "temp": self.temperature_var.get(),
            "top_p": self.top_p_var.get(),
            "top_k": self.top_k_var.get()
        }

        self.update_output("Generando respuesta...\n")
        try:
            response = model.generate(self.prompt_text, **config)
            self.generated_text = response
            self.update_output(f"Prompt:\n{self.prompt_text}\n\nRespuesta:\n{response}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar la respuesta: {e}")

    def clear_output(self):
        self.prompt_text = ""
        self.generated_text = ""
        self.output_box.delete(1.0, tk.END)

    def save_result(self):
        if not self.generated_text:
            messagebox.showwarning("Advertencia", "No hay texto generado para guardar.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Prompt:\n{self.prompt_text}\n\nRespuesta:\n{self.generated_text}")
            messagebox.showinfo("Éxito", "Texto guardado correctamente.")
            letra=str((int)(random.random()*10))+str((int)(random.random()*10)) # Dos digitos aleatorios
            nombreArchivo="Gn"+letra+file_path[-2:-4]+".png"
            confImagen={
                "título": "Texto Generado",
                "texto":self.generated_text,
                "nombre_archivo":nombreArchivo,
                "fuente_path":"/home/seretur/Imágenes/Fuentes/Montse/Montserrat-Variable.ttf",
                "tamaño_fuente":18
            }
            print("Creando imagen")
            crear_imagen_texto(confImagen)

if __name__ == "__main__":
    root = tk.Tk()
    app = GPT4AllApp(root)
    root.mainloop()