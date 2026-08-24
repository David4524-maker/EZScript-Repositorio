import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import re
import platform
import json
import random
import math
import time
import webbrowser
from datetime import datetime

# ==========================================
# 1. MOTOR Y EVALUADOR DE EASYSCRIPT (EZSCRIPT)
# ==========================================
class EasyScriptInterpreter:
    def __init__(self, output_widget, canvas_widget, app):
        self.variables = {}
        self.output = output_widget
        self.canvas = canvas_widget
        self.app = app
        self.should_stop = False
        self.text_positions = {}
        self.emulated_os = platform.system()
        self.current_line_width = 3

    def log(self, text):
        pos_index = self.output.index(tk.END)
        self.output.insert(tk.END, str(text) + "\n")
        self.output.see(tk.END)
        self.output.update()
        line_num = int(pos_index.split('.')[0])
        self.text_positions[str(text).strip()] = (100, line_num * 20)

    def eval_expr(self, expr):
        expr = str(expr).strip()
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        tokens = re.split(r'(\s+|[+\-*/()==><!]+)', expr)
        new_tokens = []
        for token in tokens:
            t = token.strip()
            if t in self.variables:
                val = self.variables[t]
                new_tokens.append(f'"{val}"' if isinstance(val, str) else str(val))
            else:
                new_tokens.append(token)
        
        parsed_expr = "".join(new_tokens)
        try:
            return eval(parsed_expr, {"__builtins__": None}, {})
        except Exception:
            return expr

    def run_block(self, lines):
        i = 0
        n = len(lines)
        
        while i < n and not self.should_stop:
            line_data = lines[i]
            line_num = line_data['num']
            line = line_data['text'].strip()

            if not line or line.startswith("//"):
                i += 1
                continue

            # ------------------------------------------
            # 13 COMANDOS BASE
            # ------------------------------------------
            if line.startswith("IA:"):
                match = re.match(r'IA:\s*\((.*?)\)', line)
                if match:
                    prompt = self.eval_expr(match.group(1))
                    self.log(f"🤖 [IA Response to '{prompt}']: Funcionalidad de IA integrada.")

            elif line.startswith("SistemaOperativo:"):
                match = re.match(r'SistemaOperativo:\s*\((.*?)\)', line)
                if match:
                    target_os = str(self.eval_expr(match.group(1))).strip()
                    if target_os in ["Windows", "macOS", "Linux"]:
                        self.emulated_os = target_os
                        self.log(f"🖥️ Sistema operativo configurado a: {self.emulated_os}")

            elif line.startswith("JS:"):
                self.log(f"📜 [JS Executed]: {line[3:].strip()}")

            elif line.startswith("HTML:"):
                self.log(f"🌐 [HTML Rendered]: {line[5:].strip()}")

            elif line.startswith("CSS:"):
                self.log(f"🎨 [CSS Applied]: {line[4:].strip()}")

            elif line.startswith("JSON:"):
                try:
                    parsed_json = json.loads(line[5:].strip())
                    self.log(f"📦 [JSON Parsed]: {parsed_json}")
                except Exception as e:
                    self.log(f"⚠️ Error JSON (Línea {line_num}): {e}")

            elif line.startswith("ICON:"):
                self.log(f"🖼️ [Icono cargado]: {line[5:].strip()}")

            elif line.startswith("linea:"):
                match = re.match(r'linea:\s*\((.*?)\)', line)
                if match:
                    raw_args = [a.strip() for a in match.group(1).split(',')]
                    if len(raw_args) >= 4:
                        x1, y1 = int(self.eval_expr(raw_args[0])), int(self.eval_expr(raw_args[1]))
                        x2, y2 = int(self.eval_expr(raw_args[2])), int(self.eval_expr(raw_args[3]))
                        color = str(self.eval_expr(raw_args[4])) if len(raw_args) > 4 else "#00d2d3"
                        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=self.current_line_width)

            elif line.startswith("conectar:"):
                match = re.match(r'conectar:\s*\((.*?)\)', line)
                if match:
                    raw_args = [a.strip() for a in match.group(1).split(',')]
                    if len(raw_args) >= 2:
                        t1, t2 = str(self.eval_expr(raw_args[0])), str(self.eval_expr(raw_args[1]))
                        color = str(self.eval_expr(raw_args[2])) if len(raw_args) > 2 else "#ff7675"
                        p1, p2 = self.text_positions.get(t1), self.text_positions.get(t2)
                        if p1 and p2:
                            self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=color, width=self.current_line_width, dash=(4, 2))

            elif line.startswith("color:"):
                match = re.match(r'color:\s*\((.*?)\)', line)
                if match:
                    c = str(self.eval_expr(match.group(1).strip()))
                    self.output.config(bg=c)
                    self.canvas.config(bg=c)

            elif line == "limpiar_pantalla":
                self.output.delete("1.0", tk.END)
                self.canvas.delete("all")
                self.text_positions.clear()

            elif line.startswith("mostrar ") or line.startswith("print "):
                self.log(self.eval_expr(line.split(" ", 1)[1]))

            elif line.startswith("boton:") or line.startswith("button:"):
                prefix = "boton:" if line.startswith("boton:") else "button:"
                content = line[len(prefix):].strip()
                if content.startswith("(") and content.endswith(")"):
                    content = content[1:-1]
                parts = content.split(",", 1)
                txt_label = str(self.eval_expr(parts[0]))
                action_code = parts[1].strip() if len(parts) > 1 else ""
                btn = tk.Button(
                    self.output, text=txt_label, bg="#0984e3", fg="white", font=("Arial", 9, "bold"),
                    command=lambda code=action_code: self.execute_inline(code)
                )
                self.output.window_create(tk.END, window=btn)
                self.output.insert(tk.END, "\n")

            # ------------------------------------------
            # SUITE DE 50 COMANDOS COMPLEMENTARIOS
            # ------------------------------------------
            # 1. Variables y Cadenas
            elif line.startswith("var:") or line.startswith("VARIABLE_DEFINIR:"):
                m = re.match(r'(?:var|VARIABLE_DEFINIR):\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = self.eval_expr(m.group(2))

            elif line.startswith("incrementar:"):
                m = re.match(r'incrementar:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = self.variables.get(m.group(1).strip(), 0) + int(self.eval_expr(m.group(2)))

            elif line.startswith("decrementar:"):
                m = re.match(r'decrementar:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = self.variables.get(m.group(1).strip(), 0) - int(self.eval_expr(m.group(2)))

            elif line.startswith("entrada:"):
                m = re.match(r'entrada:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = self.app.ask_input(str(self.eval_expr(m.group(2)))) or ""

            elif line.startswith("mayusculas:"):
                m = re.match(r'mayusculas:\s*\((.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = str(self.variables.get(m.group(1).strip(), "")).upper()

            elif line.startswith("minusculas:"):
                m = re.match(r'minusculas:\s*\((.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = str(self.variables.get(m.group(1).strip(), "")).lower()

            elif line.startswith("longitud:"):
                m = re.match(r'longitud:\s*\((.*?)\)', line)
                if m: self.log(f"📏 Longitud: {len(str(self.eval_expr(m.group(1))))}")

            elif line.startswith("reemplazar:"):
                m = re.match(r'reemplazar:\s*\((.*?),(.*?),(.*?)\)', line)
                if m:
                    v = m.group(1).strip()
                    self.variables[v] = str(self.variables.get(v, "")).replace(str(self.eval_expr(m.group(2))), str(self.eval_expr(m.group(3))))

            elif line.startswith("tipo_dato:"):
                m = re.match(r'tipo_dato:\s*\((.*?)\)', line)
                if m: self.log(f"ℹ️ Tipo: {type(self.eval_expr(m.group(1))).__name__}")

            elif line.startswith("concatenar:"):
                m = re.match(r'concatenar:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

            # 2. Matemáticas
            elif line.startswith("random:"):
                m = re.match(r'random:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = random.randint(int(self.eval_expr(m.group(2))), int(self.eval_expr(m.group(3))))

            elif line.startswith("raiz:"):
                m = re.match(r'raiz:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.sqrt(float(self.eval_expr(m.group(2))))

            elif line.startswith("potencia:"):
                m = re.match(r'potencia:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.pow(float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

            elif line.startswith("redondear:"):
                m = re.match(r'redondear:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = round(float(self.eval_expr(m.group(2))))

            elif line.startswith("absoluto:"):
                m = re.match(r'absoluto:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = abs(float(self.eval_expr(m.group(2))))

            elif line.startswith("seno:"):
                m = re.match(r'seno:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.sin(math.radians(float(self.eval_expr(m.group(2)))))

            elif line.startswith("coseno:"):
                m = re.match(r'coseno:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.cos(math.radians(float(self.eval_expr(m.group(2)))))

            elif line.startswith("maximo:"):
                m = re.match(r'maximo:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = max(float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

            elif line.startswith("minimo:"):
                m = re.match(r'minimo:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = min(float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

            elif line.startswith("pi:"):
                m = re.match(r'pi:\s*\((.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.pi

            # 3. Dibujo y Canvas
            elif line.startswith("rectangulo:"):
                m = re.match(r'rectangulo:\s*\((.*?),(.*?),(.*?),(.*?),(.*?)\)', line)
                if m:
                    x1, y1, x2, y2, c = [self.eval_expr(x) for x in m.groups()]
                    self.canvas.create_rectangle(int(x1), int(y1), int(x2), int(y2), fill=c)

            elif line.startswith("circulo:"):
                m = re.match(r'circulo:\s*\((.*?),(.*?),(.*?),(.*?)\)', line)
                if m:
                    x, y, r, c = [self.eval_expr(x) for x in m.groups()]
                    x, y, r = int(x), int(y), int(r)
                    self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=c)

            elif line.startswith("ovalo:"):
                m = re.match(r'ovalo:\s*\((.*?),(.*?),(.*?),(.*?),(.*?)\)', line)
                if m:
                    x1, y1, x2, y2, c = [self.eval_expr(x) for x in m.groups()]
                    self.canvas.create_oval(int(x1), int(y1), int(x2), int(y2), fill=c)

            elif line.startswith("texto_canvas:"):
                m = re.match(r'texto_canvas:\s*\((.*?),(.*?),(.*?),(.*?)\)', line)
                if m:
                    x, y, txt, c = [self.eval_expr(x) for x in m.groups()]
                    self.canvas.create_text(int(x), int(y), text=str(txt), fill=c, font=("Arial", 10, "bold"))

            elif line.startswith("color_canvas:"):
                m = re.match(r'color_canvas:\s*\((.*?)\)', line)
                if m: self.canvas.config(bg=self.eval_expr(m.group(1)))

            elif line.startswith("grosor_linea:"):
                m = re.match(r'grosor_linea:\s*\((.*?)\)', line)
                if m: self.current_line_width = int(self.eval_expr(m.group(1)))

            elif line == "borrar_canvas":
                self.canvas.delete("all")

            elif line.startswith("poligono:"):
                m = re.match(r'poligono:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\)', line)
                if m:
                    x1, y1, x2, y2, x3, y3, c = [self.eval_expr(x) for x in m.groups()]
                    self.canvas.create_polygon(int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), fill=c)

            elif line.startswith("arco:"):
                m = re.match(r'arco:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\)', line)
                if m:
                    x1, y1, x2, y2, st, ex, c = [self.eval_expr(x) for x in m.groups()]
                    self.canvas.create_arc(int(x1), int(y1), int(x2), int(y2), start=int(st), extent=int(ex), fill=c)

            elif line.startswith("cuadricula:"):
                m = re.match(r'cuadricula:\s*\((.*?)\)', line)
                if m:
                    step = int(self.eval_expr(m.group(1)))
                    for x in range(0, 400, step): self.canvas.create_line(x, 0, x, 400, fill="#34495e", dash=(1, 3))
                    for y in range(0, 400, step): self.canvas.create_line(0, y, 400, y, fill="#34495e", dash=(1, 3))

            # 4. Sistema y Utilidades
            elif line == "fecha":
                self.log(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d')}")

            elif line == "hora":
                self.log(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")

            elif line.startswith("esperar:"):
                m = re.match(r'esperar:\s*\((.*?)\)', line)
                if m:
                    self.output.update()
                    time.sleep(float(self.eval_expr(m.group(1))))

            elif line.startswith("alerta:"):
                m = re.match(r'alerta:\s*\((.*?)\)', line)
                if m: messagebox.showinfo("Alerta EasyScript", str(self.eval_expr(m.group(1))))

            elif line.startswith("confirmar:"):
                m = re.match(r'confirmar:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = messagebox.askyesno("Confirmación", str(self.eval_expr(m.group(2))))

            elif line.startswith("abrir_url:"):
                m = re.match(r'abrir_url:\s*\((.*?)\)', line)
                if m: webbrowser.open(str(self.eval_expr(m.group(1))))

            elif line.startswith("copiar:"):
                m = re.match(r'copiar:\s*\((.*?)\)', line)
                if m:
                    self.app.root.clipboard_clear()
                    self.app.root.clipboard_append(str(self.eval_expr(m.group(1))))

            elif line.startswith("notificacion:"):
                m = re.match(r'notificacion:\s*\((.*?),(.*?)\)', line)
                if m: self.log(f"🔔 [{self.eval_expr(m.group(1))}]: {self.eval_expr(m.group(2))}")

            elif line == "pitido":
                self.app.root.bell()

            elif line.startswith("ejecutar_cmd:"):
                m = re.match(r'ejecutar_cmd:\s*\((.*?)\)', line)
                if m: self.log(f"💻 CMD ejecutado: '{self.eval_expr(m.group(1))}'")

            # 5. IA, Web y Archivos
            elif line.startswith("ia_resumir:"):
                m = re.match(r'ia_resumir:\s*\((.*?)\)', line)
                if m: self.log(f"🤖 [IA Resumen]: {str(self.eval_expr(m.group(1)))[:40]}...")

            elif line.startswith("ia_traducir:"):
                m = re.match(r'ia_traducir:\s*\((.*?),(.*?)\)', line)
                if m: self.log(f"🤖 [IA Traducido a {self.eval_expr(m.group(2))}]: {self.eval_expr(m.group(1))}")

            elif line.startswith("ia_explicar:"):
                m = re.match(r'ia_explicar:\s*\((.*?)\)', line)
                if m: self.log(f"🤖 [IA Explicación]: Análisis de código realizado.")

            elif line.startswith("crear_archivo:"):
                m = re.match(r'crear_archivo:\s*\((.*?),(.*?)\)', line)
                if m:
                    with open(self.eval_expr(m.group(1)), "w", encoding="utf-8") as f:
                        f.write(str(self.eval_expr(m.group(2))))

            elif line.startswith("leer_archivo:"):
                m = re.match(r'leer_archivo:\s*\((.*?),(.*?)\)', line)
                if m:
                    try:
                        with open(self.eval_expr(m.group(2)), "r", encoding="utf-8") as f:
                            self.variables[m.group(1).strip()] = f.read()
                    except Exception as e:
                        self.log(f"⚠️ Error al leer: {e}")

            elif line.startswith("json_obtener:"):
                m = re.match(r'json_obtener:\s*\((.*?),(.*?),(.*?)\)', line)
                if m:
                    j_raw = self.eval_expr(m.group(2))
                    data = json.loads(j_raw) if isinstance(j_raw, str) else j_raw
                    self.variables[m.group(1).strip()] = data.get(self.eval_expr(m.group(3)), "")

            elif line.startswith("html_titulo:"):
                m = re.match(r'html_titulo:\s*\((.*?)\)', line)
                if m: self.log(f"🌐 HTML Title: <title>{self.eval_expr(m.group(1))}</title>")

            elif line.startswith("css_tema:"):
                m = re.match(r'css_tema:\s*\((.*?)\)', line)
                if m:
                    bg = "#1e272e" if str(self.eval_expr(m.group(1))).lower() == "oscuro" else "#ffffff"
                    self.output.config(bg=bg)
                    self.canvas.config(bg=bg)

            elif line.startswith("js_eval:"):
                m = re.match(r'js_eval:\s*\((.*?)\)', line)
                if m: self.log(f"📜 [JS Result]: {self.eval_expr(m.group(1))}")

            elif line == "detener":
                self.should_stop = True
                self.log("🛑 Ejecución detenida.")

            i += 1

    def execute_inline(self, single_line):
        if single_line:
            self.run_block([{'num': 0, 'text': single_line}])

    def execute(self, code):
        self.variables = {}
        self.should_stop = False
        self.output.delete("1.0", tk.END)
        self.canvas.delete("all")
        self.text_positions.clear()
        self.output.config(bg="#1e272e", fg="#ffffff")
        self.canvas.config(bg="#1e272e")
        
        raw_lines = code.split('\n')
        structured_lines = [{'num': idx + 1, 'text': l} for idx, l in enumerate(raw_lines)]
        self.run_block(structured_lines)


# Aliases para compatibilidad total
EZScriptInterpreter = EasyScriptInterpreter


# ==========================================
# 2. ENTORNO GRÁFICO (EASYSCRIPT STUDIO)
# ==========================================
class EasyScriptIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyScript (EZScript) Studio")
        self.root.geometry("980x750")

        # Barra Superior
        toolbar = tk.Frame(root, bg="#2c3e50")
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_new = tk.Button(toolbar, text="📄 Nuevo", bg="#3498db", fg="white", font=("Arial", 10, "bold"), command=self.new_project)
        btn_new.pack(side=tk.LEFT, padx=5)

        btn_open = tk.Button(toolbar, text="📂 Cargar Proy.", bg="#f39c12", fg="white", font=("Arial", 10, "bold"), command=self.load_project)
        btn_open.pack(side=tk.LEFT, padx=5)

        btn_save = tk.Button(toolbar, text="💾 Guardar Proy.", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=self.save_project)
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_run = tk.Button(toolbar, text="▶️ Ejecutar Todo", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), command=self.run_code)
        btn_run.pack(side=tk.LEFT, padx=15)

        # Editor de Código
        self.code_editor = tk.Text(root, font=("Consolas", 11), height=14)
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Paneles de Salida
        output_frame = tk.Frame(root, bg="#1e272e")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.console = tk.Text(output_frame, font=("Consolas", 10), height=10, bg="#1e272e", fg="#ffffff", width=50)
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(output_frame, bg="#1e272e", highlightthickness=0, width=320)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.interpreter = EasyScriptInterpreter(self.console, self.canvas, self)

        # Script de prueba completo listo para correr
        demo_script = (
            "// --- DEMOSTRACIÓN COMPLETA DE EASYSCRIPT ---\n"
            "SistemaOperativo: (Windows)\n"
            "var:(num, 10)\n"
            "incrementar:(num, 5)\n"
            "decrementar:(num, 2)\n"
            "var:(txt, \"hola ezscript\")\n"
            "mayusculas:(txt)\n"
            "longitud:(txt)\n"
            "reemplazar:(txt, \"HOLA\", \"SALUDOS\")\n"
            "tipo_dato:(num)\n"
            "concatenar:(saludo, txt, \" MUNDO\")\n"
            "mostrar saludo\n"
            "\n"
            "// --- MATEMÁTICAS ---\n"
            "random:(dado, 1, 6)\n"
            "raiz:(r, 16)\n"
            "potencia:(p, 2, 3)\n"
            "redondear:(rd, 4.7)\n"
            "absoluto:(ab, -9)\n"
            "seno:(sn, 90)\n"
            "coseno:(cs, 0)\n"
            "maximo:(mx, 10, 20)\n"
            "minimo:(mn, 10, 20)\n"
            "pi:(constante_pi)\n"
            "mostrar dado\n"
            "\n"
            "// --- DIBUJO Y CANVAS ---\n"
            "cuadricula:(50)\n"
            "grosor_linea:(2)\n"
            "rectangulo:(10, 10, 100, 60, \"#0984e3\")\n"
            "circulo:(200, 50, 30, \"#e84393\")\n"
            "ovalo:(50, 100, 150, 150, \"#fdcb6e\")\n"
            "poligono:(200, 100, 250, 180, 180, 180, \"#00b894\")\n"
            "arco:(10, 160, 100, 250, 0, 120, \"#e17055\")\n"
            "texto_canvas:(150, 20, \"EasyScript Canvas\", \"#ffffff\")\n"
            "\n"
            "// --- SISTEMA E IA ---\n"
            "fecha\n"
            "hora\n"
            "notificacion:(\"Sistema\", \"Proceso ejecutado con exito\")\n"
            "ia_resumir:(\"EasyScript es un lenguaje de desarrollo experimental interactivo\")\n"
            "ia_traducir:(\"Hola mundo\", \"Ingles\")\n"
            "ia_explicar:(\"var:(x, 100)\")\n"
            "html_titulo:(\"EasyScript App\")\n"
            "js_eval:(\"2 + 2\")\n"
            "boton:(\"Click me\", print \"¡Boton Presionado!\")"
        )
        self.code_editor.insert(tk.END, demo_script)

    def ask_input(self, prompt_text):
        return simpledialog.askstring("Entrada EasyScript", prompt_text, parent=self.root)

    def run_code(self):
        code = self.code_editor.get("1.0", tk.END)
        self.interpreter.execute(code)

    def new_project(self):
        if messagebox.askyesno("Nuevo Proyecto", "¿Deseas crear un nuevo proyecto?"):
            self.code_editor.delete("1.0", tk.END)
            self.console.delete("1.0", tk.END)
            self.canvas.delete("all")

    def save_project(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ez",
            filetypes=[("Proyectos EasyScript", "*.ez"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.code_editor.get("1.0", tk.END))
            messagebox.showinfo("Éxito", "¡Proyecto guardado con éxito!")

    def load_project(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Proyectos EasyScript", "*.ez"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert(tk.END, content)
            messagebox.showinfo("Éxito", "¡Proyecto cargado con éxito!")


EZScriptIDE = EasyScriptIDE

if __name__ == "__main__":
    root = tk.Tk()
    app = EasyScriptIDE(root)
    root.mainloop()
