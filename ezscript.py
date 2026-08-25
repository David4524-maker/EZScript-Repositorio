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
        
        # Estado global de color y mapa en español
        self.current_draw_color = "#0984e3"
        self.COLOR_MAP = {
            "rojo": "#e74c3c", "azul": "#3498db", "verde": "#2ecc71",
            "amarillo": "#f1c40f", "naranja": "#e67e22", "morado": "#9b59b6",
            "rosa": "#fd79a8", "negro": "#2c3e50", "blanco": "#ffffff", "gris": "#95a5a6"
        }

    def get_color(self, val):
        """Convierte nombres de colores en español o mantiene el valor dado."""
        clean_val = str(val).strip().lower().replace('"', '').replace("'", "")
        return self.COLOR_MAP.get(clean_val, clean_val)

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
            # 13 COMANDOS BASE Y SISTEMA DE COLOR
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
                        color = self.get_color(self.eval_expr(raw_args[4])) if len(raw_args) > 4 else self.current_draw_color
                        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=self.current_line_width)

            elif line.startswith("conectar:"):
                match = re.match(r'conectar:\s*\((.*?)\)', line)
                if match:
                    raw_args = [a.strip() for a in match.group(1).split(',')]
                    if len(raw_args) >= 2:
                        t1, t2 = str(self.eval_expr(raw_args[0])), str(self.eval_expr(raw_args[1]))
                        color = self.get_color(self.eval_expr(raw_args[2])) if len(raw_args) > 2 else self.current_draw_color
                        p1, p2 = self.text_positions.get(t1), self.text_positions.get(t2)
                        if p1 and p2:
                            self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=color, width=self.current_line_width, dash=(4, 2))

            elif line.startswith("color:"):
                match = re.match(r'color:\s*\((.*?)\)', line)
                if match:
                    self.current_draw_color = self.get_color(self.eval_expr(match.group(1).strip()))

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
            # SUITE DE COMANDOS COMPLEMENTARIOS
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

            # 3. Dibujo y Canvas (Simplificados)
            elif line.startswith("rectangulo:"):
                m = re.match(r'rectangulo:\s*\((.*?)\)', line)
                if m:
                    args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                    x, y, w, h = int(args[0]), int(args[1]), int(args[2]), int(args[3])
                    c = self.get_color(args[4]) if len(args) > 4 else self.current_draw_color
                    self.canvas.create_rectangle(x, y, x + w, y + h, fill=c, outline="")

            elif line.startswith("circulo:"):
                m = re.match(r'circulo:\s*\((.*?)\)', line)
                if m:
                    args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                    x, y, r = int(args[0]), int(args[1]), int(args[2])
                    c = self.get_color(args[3]) if len(args) > 3 else self.current_draw_color
                    self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=c, outline="")

            elif line.startswith("ovalo:"):
                m = re.match(r'ovalo:\s*\((.*?)\)', line)
                if m:
                    args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                    x, y, w, h = int(args[0]), int(args[1]), int(args[2]), int(args[3])
                    c = self.get_color(args[4]) if len(args) > 4 else self.current_draw_color
                    self.canvas.create_oval(x, y, x + w, y + h, fill=c, outline="")

            elif line.startswith("triangulo:"):
                m = re.match(r'triangulo:\s*\((.*?)\)', line)
                if m:
                    args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                    pts = [int(args[i]) for i in range(6)]
                    c = self.get_color(args[6]) if len(args) > 6 else self.current_draw_color
                    self.canvas.create_polygon(pts, fill=c, outline="")

            elif line.startswith("texto_canvas:"):
                m = re.match(r'texto_canvas:\s*\((.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
                if m:
                    x, y, txt = self.eval_expr(m.group(1)), self.eval_expr(m.group(2)), self.eval_expr(m.group(3))
                    c = self.get_color(self.eval_expr(m.group(4))) if m.group(4) else self.current_draw_color
                    self.canvas.create_text(int(x), int(y), text=str(txt), fill=c, font=("Arial", 10, "bold"))

            elif line.startswith("color_canvas:"):
                m = re.match(r'color_canvas:\s*\((.*?)\)', line)
                if m: self.canvas.config(bg=self.get_color(self.eval_expr(m.group(1))))

            elif line.startswith("grosor_linea:"):
                m = re.match(r'grosor_linea:\s*\((.*?)\)', line)
                if m: self.current_line_width = int(self.eval_expr(m.group(1)))

            elif line == "borrar_canvas":
                self.canvas.delete("all")

            elif line.startswith("poligono:"):
                m = re.match(r'poligono:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\)', line)
                if m:
                    x1, y1, x2, y2, x3, y3 = [self.eval_expr(x) for x in m.groups()[:6]]
                    c = self.get_color(self.eval_expr(m.groups()[6]))
                    self.canvas.create_polygon(int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), fill=c)

            elif line.startswith("arco:"):
                m = re.match(r'arco:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
                if m:
                    raw = [self.eval_expr(x) for x in m.groups() if x is not None]
                    x1, y1, x2, y2, st, ex = [int(v) for v in raw[:6]]
                    c = self.get_color(raw[6]) if len(raw) > 6 else self.current_draw_color
                    self.canvas.create_arc(x1, y1, x2, y2, start=st, extent=ex, fill=c)

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
        self.current_draw_color = "#0984e3"
        
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

        # Script de prueba actualizado con la nueva sintaxis simplificada
        demo_script = (
            "// --- DEMOSTRACIÓN COMPLETA DE EASYSCRIPT (NUEVA SINTAXIS) ---\n"
            "SistemaOperativo: (Windows)\n"
            "var:(num, 10)\n"
            "incrementar:(num, 5)\n"
            "mostrar num\n"
            "\n"
            "// --- DIBUJO Y MANEJO DE COLOR EN ESPAÑOL ---\n"
            "cuadricula:(40)\n"
            "color:(\"azul\")\n"
            "circulo:(60, 60, 35)\n"
            "rectangulo:(120, 25, 90, 60)\n"
            "\n"
            "color:(\"rojo\")\n"
            "triangulo:(230, 85, 270, 25, 310, 85)\n"
            "ovalo:(30, 110, 100, 50)\n"
            "\n"
            "// Dibujar indicando el color directamente al final\n"
            "circulo:(170, 135, 25, \"amarillo\")\n"
            "texto_canvas:(160, 200, \"¡EZScript Simplificado!\", \"verde\")\n"
            "\n"
            "// --- SISTEMA E INTERACCIÓN ---\n"
            "fecha\n"
            "hora\n"
            "boton:(\"¡Haz clic aquí!\", print \"¡Botón Funcionando!\")\n"
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
