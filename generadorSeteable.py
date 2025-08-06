import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import random
from gpt4all import GPT4All

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

if __name__ == "__main__":
    root = tk.Tk()
    app = GPT4AllApp(root)
    root.mainloop()