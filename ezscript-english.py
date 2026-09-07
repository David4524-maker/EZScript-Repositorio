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
# 1. EZSCRIPT ENGLISH ENGINE & INTERPRETER
# ==========================================
class EZScriptEnglishInterpreter:
    def __init__(self, output_widget, canvas_widget, app):
        self.variables = {}
        self.output = output_widget
        self.canvas = canvas_widget
        self.app = app
        self.should_stop = False
        self.text_positions = {}
        self.emulated_os = platform.system()
        self.current_line_width = 3
        
        # Global color state and English color map
        self.current_draw_color = "#0984e3"
        self.COLOR_MAP = {
            "red": "#e74c3c", "blue": "#3498db", "green": "#2ecc71",
            "yellow": "#f1c40f", "orange": "#e67e22", "purple": "#9b59b6",
            "pink": "#fd79a8", "black": "#2c3e50", "white": "#ffffff", "gray": "#95a5a6"
        }

    def get_color(self, val):
        """Converts English color names or returns the raw hex/color string."""
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
            # BASE COMMANDS & COLOR SYSTEM
            # ------------------------------------------
            if line.startswith("AI:"):
                match = re.match(r'AI:\s*\((.*?)\)', line)
                if match:
                    prompt = self.eval_expr(match.group(1))
                    self.log(f"🤖 [AI Response to '{prompt}']: Integrated AI feature.")

            elif line.startswith("OperatingSystem:"):
                match = re.match(r'OperatingSystem:\s*\((.*?)\)', line)
                if match:
                    target_os = str(self.eval_expr(match.group(1))).strip()
                    if target_os in ["Windows", "macOS", "Linux"]:
                        self.emulated_os = target_os
                        self.log(f"🖥️ Operating System set to: {self.emulated_os}")

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
                    self.log(f"⚠️ JSON Error (Line {line_num}): {e}")

            elif line.startswith("ICON:"):
                self.log(f"🖼️ [Icon loaded]: {line[5:].strip()}")

            elif line.startswith("line:"):
                match = re.match(r'line:\s*\((.*?)\)', line)
                if match:
                    raw_args = [a.strip() for a in match.group(1).split(',')]
                    if len(raw_args) >= 4:
                        x1, y1 = int(self.eval_expr(raw_args[0])), int(self.eval_expr(raw_args[1]))
                        x2, y2 = int(self.eval_expr(raw_args[2])), int(self.eval_expr(raw_args[3]))
                        color = self.get_color(self.eval_expr(raw_args[4])) if len(raw_args) > 4 else self.current_draw_color
                        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=self.current_line_width)

            elif line.startswith("connect:"):
                match = re.match(r'connect:\s*\((.*?)\)', line)
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

            elif line == "clear_screen":
                self.output.delete("1.0", tk.END)
                self.canvas.delete("all")
                self.text_positions.clear()

            elif line.startswith("show ") or line.startswith("print "):
                self.log(self.eval_expr(line.split(" ", 1)[1]))

            elif line.startswith("button:"):
                content = line[len("button:"):].strip()
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
            # EXTENDED COMMAND SUITE
            # ------------------------------------------
            # 1. Variables and Strings
            elif line.startswith("var:") or line.startswith("DEFINE_VARIABLE:"):
                m = re.match(r'(?:var|DEFINE_VARIABLE):\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = self.eval_expr(m.group(2))

            elif line.startswith("increment:"):
                m = re.match(r'increment:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = self.variables.get(m.group(1).strip(), 0) + int(self.eval_expr(m.group(2)))

            elif line.startswith("decrement:"):
                m = re.match(r'decrement:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = self.variables.get(m.group(1).strip(), 0) - int(self.eval_expr(m.group(2)))

            elif line.startswith("input:"):
                m = re.match(r'input:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = self.app.ask_input(str(self.eval_expr(m.group(2)))) or ""

            elif line.startswith("uppercase:"):
                m = re.match(r'uppercase:\s*\((.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = str(self.variables.get(m.group(1).strip(), "")).upper()

            elif line.startswith("lowercase:"):
                m = re.match(r'lowercase:\s*\((.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = str(self.variables.get(m.group(1).strip(), "")).lower()

            elif line.startswith("length:"):
                m = re.match(r'length:\s*\((.*?)\)', line)
                if m: self.log(f"📏 Length: {len(str(self.eval_expr(m.group(1))))}")

            elif line.startswith("replace:"):
                m = re.match(r'replace:\s*\((.*?),(.*?),(.*?)\)', line)
                if m:
                    v = m.group(1).strip()
                    self.variables[v] = str(self.variables.get(v, "")).replace(str(self.eval_expr(m.group(2))), str(self.eval_expr(m.group(3))))

            elif line.startswith("data_type:"):
                m = re.match(r'data_type:\s*\((.*?)\)', line)
                if m: self.log(f"ℹ️ Type: {type(self.eval_expr(m.group(1))).__name__}")

            elif line.startswith("concat:"):
                m = re.match(r'concat:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

            # 2. Mathematics
            elif line.startswith("random:"):
                m = re.match(r'random:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = random.randint(int(self.eval_expr(m.group(2))), int(self.eval_expr(m.group(3))))

            elif line.startswith("sqrt:"):
                m = re.match(r'sqrt:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.sqrt(float(self.eval_expr(m.group(2))))

            elif line.startswith("power:"):
                m = re.match(r'power:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.pow(float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

            elif line.startswith("round:"):
                m = re.match(r'round:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = round(float(self.eval_expr(m.group(2))))

            elif line.startswith("abs:"):
                m = re.match(r'abs:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = abs(float(self.eval_expr(m.group(2))))

            elif line.startswith("sin:"):
                m = re.match(r'sin:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.sin(math.radians(float(self.eval_expr(m.group(2)))))

            elif line.startswith("cos:"):
                m = re.match(r'cos:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.cos(math.radians(float(self.eval_expr(m.group(2)))))

            elif line.startswith("max:"):
                m = re.match(r'max:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = max(float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

            elif line.startswith("min:"):
                m = re.match(r'min:\s*\((.*?),(.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = min(float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

            elif line.startswith("pi:"):
                m = re.match(r'pi:\s*\((.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = math.pi

            # 3. Canvas Drawing
            elif line.startswith("rectangle:"):
                m = re.match(r'rectangle:\s*\((.*?)\)', line)
                if m:
                    args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                    x, y, w, h = int(args[0]), int(args[1]), int(args[2]), int(args[3])
                    c = self.get_color(args[4]) if len(args) > 4 else self.current_draw_color
                    self.canvas.create_rectangle(x, y, x + w, y + h, fill=c, outline="")

            elif line.startswith("circle:"):
                m = re.match(r'circle:\s*\((.*?)\)', line)
                if m:
                    args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                    x, y, r = int(args[0]), int(args[1]), int(args[2])
                    c = self.get_color(args[3]) if len(args) > 3 else self.current_draw_color
                    self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=c, outline="")

            elif line.startswith("oval:"):
                m = re.match(r'oval:\s*\((.*?)\)', line)
                if m:
                    args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                    x, y, w, h = int(args[0]), int(args[1]), int(args[2]), int(args[3])
                    c = self.get_color(args[4]) if len(args) > 4 else self.current_draw_color
                    self.canvas.create_oval(x, y, x + w, y + h, fill=c, outline="")

            elif line.startswith("triangle:"):
                m = re.match(r'triangle:\s*\((.*?)\)', line)
                if m:
                    args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                    pts = [int(args[i]) for i in range(6)]
                    c = self.get_color(args[6]) if len(args) > 6 else self.current_draw_color
                    self.canvas.create_polygon(pts, fill=c, outline="")

            elif line.startswith("canvas_text:"):
                m = re.match(r'canvas_text:\s*\((.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
                if m:
                    x, y, txt = self.eval_expr(m.group(1)), self.eval_expr(m.group(2)), self.eval_expr(m.group(3))
                    c = self.get_color(self.eval_expr(m.group(4))) if m.group(4) else self.current_draw_color
                    self.canvas.create_text(int(x), int(y), text=str(txt), fill=c, font=("Arial", 10, "bold"))

            elif line.startswith("canvas_color:"):
                m = re.match(r'canvas_color:\s*\((.*?)\)', line)
                if m: self.canvas.config(bg=self.get_color(self.eval_expr(m.group(1))))

            elif line.startswith("line_width:"):
                m = re.match(r'line_width:\s*\((.*?)\)', line)
                if m: self.current_line_width = int(self.eval_expr(m.group(1)))

            elif line == "clear_canvas":
                self.canvas.delete("all")

            elif line.startswith("polygon:"):
                m = re.match(r'polygon:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\)', line)
                if m:
                    x1, y1, x2, y2, x3, y3 = [self.eval_expr(x) for x in m.groups()[:6]]
                    c = self.get_color(self.eval_expr(m.groups()[6]))
                    self.canvas.create_polygon(int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), fill=c)

            elif line.startswith("arc:"):
                m = re.match(r'arc:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
                if m:
                    raw = [self.eval_expr(x) for x in m.groups() if x is not None]
                    x1, y1, x2, y2, st, ex = [int(v) for v in raw[:6]]
                    c = self.get_color(raw[6]) if len(raw) > 6 else self.current_draw_color
                    self.canvas.create_arc(x1, y1, x2, y2, start=st, extent=ex, fill=c)

            elif line.startswith("grid:"):
                m = re.match(r'grid:\s*\((.*?)\)', line)
                if m:
                    step = int(self.eval_expr(m.group(1)))
                    for x in range(0, 400, step): self.canvas.create_line(x, 0, x, 400, fill="#34495e", dash=(1, 3))
                    for y in range(0, 400, step): self.canvas.create_line(0, y, 400, y, fill="#34495e", dash=(1, 3))

            # 4. System & Utilities
            elif line == "date":
                self.log(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")

            elif line == "time":
                self.log(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")

            elif line.startswith("wait:"):
                m = re.match(r'wait:\s*\((.*?)\)', line)
                if m:
                    self.output.update()
                    time.sleep(float(self.eval_expr(m.group(1))))

            elif line.startswith("alert:"):
                m = re.match(r'alert:\s*\((.*?)\)', line)
                if m: messagebox.showinfo("EZScript Alert", str(self.eval_expr(m.group(1))))

            elif line.startswith("confirm:"):
                m = re.match(r'confirm:\s*\((.*?),(.*?)\)', line)
                if m: self.variables[m.group(1).strip()] = messagebox.askyesno("Confirmation", str(self.eval_expr(m.group(2))))

            elif line.startswith("open_url:"):
                m = re.match(r'open_url:\s*\((.*?)\)', line)
                if m: webbrowser.open(str(self.eval_expr(m.group(1))))

            elif line.startswith("copy:"):
                m = re.match(r'copy:\s*\((.*?)\)', line)
                if m:
                    self.app.root.clipboard_clear()
                    self.app.root.clipboard_append(str(self.eval_expr(m.group(1))))

            elif line.startswith("notification:"):
                m = re.match(r'notification:\s*\((.*?),(.*?)\)', line)
                if m: self.log(f"🔔 [{self.eval_expr(m.group(1))}]: {self.eval_expr(m.group(2))}")

            elif line == "beep":
                self.app.root.bell()

            elif line.startswith("run_cmd:"):
                m = re.match(r'run_cmd:\s*\((.*?)\)', line)
                if m: self.log(f"💻 CMD executed: '{self.eval_expr(m.group(1))}'")

            # 5. AI, Web & Files
            elif line.startswith("ai_summarize:"):
                m = re.match(r'ai_summarize:\s*\((.*?)\)', line)
                if m: self.log(f"🤖 [AI Summary]: {str(self.eval_expr(m.group(1)))[:40]}...")

            elif line.startswith("ai_translate:"):
                m = re.match(r'ai_translate:\s*\((.*?),(.*?)\)', line)
                if m: self.log(f"🤖 [AI Translated to {self.eval_expr(m.group(2))}]: {self.eval_expr(m.group(1))}")

            elif line.startswith("ai_explain:"):
                m = re.match(r'ai_explain:\s*\((.*?)\)', line)
                if m: self.log("🤖 [AI Explanation]: Code analysis completed.")

            elif line.startswith("create_file:"):
                m = re.match(r'create_file:\s*\((.*?),(.*?)\)', line)
                if m:
                    with open(self.eval_expr(m.group(1)), "w", encoding="utf-8") as f:
                        f.write(str(self.eval_expr(m.group(2))))

            elif line.startswith("read_file:"):
                m = re.match(r'read_file:\s*\((.*?),(.*?)\)', line)
                if m:
                    try:
                        with open(self.eval_expr(m.group(2)), "r", encoding="utf-8") as f:
                            self.variables[m.group(1).strip()] = f.read()
                    except Exception as e:
                        self.log(f"⚠️ Read error: {e}")

            elif line.startswith("json_get:"):
                m = re.match(r'json_get:\s*\((.*?),(.*?),(.*?)\)', line)
                if m:
                    j_raw = self.eval_expr(m.group(2))
                    data = json.loads(j_raw) if isinstance(j_raw, str) else j_raw
                    self.variables[m.group(1).strip()] = data.get(self.eval_expr(m.group(3)), "")

            elif line.startswith("html_title:"):
                m = re.match(r'html_title:\s*\((.*?)\)', line)
                if m: self.log(f"🌐 HTML Title: <title>{self.eval_expr(m.group(1))}</title>")

            elif line.startswith("css_theme:"):
                m = re.match(r'css_theme:\s*\((.*?)\)', line)
                if m:
                    bg = "#1e272e" if str(self.eval_expr(m.group(1))).lower() == "dark" else "#ffffff"
                    self.output.config(bg=bg)
                    self.canvas.config(bg=bg)

            elif line.startswith("js_eval:"):
                m = re.match(r'js_eval:\s*\((.*?)\)', line)
                if m: self.log(f"📜 [JS Result]: {self.eval_expr(m.group(1))}")

            elif line == "stop":
                self.should_stop = True
                self.log("🛑 Execution stopped.")

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


EZScriptInterpreter = EZScriptEnglishInterpreter


# ==========================================
# 2. GUI IDE (EZSCRIPT ENGLISH STUDIO)
# ==========================================
class EZScriptEnglishIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("EZScript English Studio")
        self.root.geometry("980x750")

        # Top Toolbar
        toolbar = tk.Frame(root, bg="#2c3e50")
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_new = tk.Button(toolbar, text="📄 New", bg="#3498db", fg="white", font=("Arial", 10, "bold"), command=self.new_project)
        btn_new.pack(side=tk.LEFT, padx=5)

        btn_open = tk.Button(toolbar, text="📂 Open Project", bg="#f39c12", fg="white", font=("Arial", 10, "bold"), command=self.load_project)
        btn_open.pack(side=tk.LEFT, padx=5)

        btn_save = tk.Button(toolbar, text="💾 Save Project", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=self.save_project)
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_run = tk.Button(toolbar, text="▶️ Run All", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), command=self.run_code)
        btn_run.pack(side=tk.LEFT, padx=15)

        # Code Editor
        self.code_editor = tk.Text(root, font=("Consolas", 11), height=14)
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Output Panels
        output_frame = tk.Frame(root, bg="#1e272e")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.console = tk.Text(output_frame, font=("Consolas", 10), height=10, bg="#1e272e", fg="#ffffff", width=50)
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(output_frame, bg="#1e272e", highlightthickness=0, width=320)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.interpreter = EZScriptEnglishInterpreter(self.console, self.canvas, self)

        # Demo script in EZScript English syntax
        demo_script = (
            "// --- COMPLETE EZSCRIPT ENGLISH DEMO ---\n"
            "OperatingSystem: (Windows)\n"
            "var:(num, 10)\n"
            "increment:(num, 5)\n"
            "print num\n"
            "\n"
            "// --- DRAWING & ENGLISH COLOR HANDLING ---\n"
            "grid:(40)\n"
            "color:(\"blue\")\n"
            "circle:(60, 60, 35)\n"
            "rectangle:(120, 25, 90, 60)\n"
            "\n"
            "color:(\"red\")\n"
            "triangle:(230, 85, 270, 25, 310, 85)\n"
            "oval:(30, 110, 100, 50)\n"
            "\n"
            "// Direct inline color at end\n"
            "circle:(170, 135, 25, \"yellow\")\n"
            "canvas_text:(160, 200, \"EZScript English!\", \"green\")\n"
            "\n"
            "// --- SYSTEM & INTERACTION ---\n"
            "date\n"
            "time\n"
            "button:(\"Click here!\", print \"Button Working!\")\n"
        )
        self.code_editor.insert(tk.END, demo_script)

    def ask_input(self, prompt_text):
        return simpledialog.askstring("EZScript Input", prompt_text, parent=self.root)

    def run_code(self):
        code = self.code_editor.get("1.0", tk.END)
        self.interpreter.execute(code)

    def new_project(self):
        if messagebox.askyesno("New Project", "Do you want to create a new project?"):
            self.code_editor.delete("1.0", tk.END)
            self.console.delete("1.0", tk.END)
            self.canvas.delete("all")

    def save_project(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ez",
            filetypes=[("EZScript Projects", "*.ez"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.code_editor.get("1.0", tk.END))
            messagebox.showinfo("Success", "Project saved successfully!")

    def load_project(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("EZScript Projects", "*.ez"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert(tk.END, content)
            messagebox.showinfo("Success", "Project loaded successfully!")


EZScriptIDE = EZScriptEnglishIDE

if __name__ == "__main__":
    root = tk.Tk()
    app = EZScriptEnglishIDE(root)
    root.mainloop()
