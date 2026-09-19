# -*- coding: utf-8 -*-
"""
EZSCRIPT 8-BITS EDITION v2.0.0
================================
IDE + Intérprete retro estilo NES/Arcade para EasyScript.

CARACTERÍSTICAS RETRO:
 ★ Paleta de colores NES auténtica
 ★ Fuente pixelada (Press Start 2P / Fixedsys / Courier New)
 ★ Efectos de sonido chiptune (onda cuadrada)
 ★ Pantalla de arranque "INSERT COIN / PRESS START"
 ★ Bordes duros pixelados en lugar de UI moderna
 ★ Barra de progreso con bloques █░
 ★ Comandos nuevos: pixel, sprite, chiptune, sonido
 ★ Modo CRT (scanlines)
 ★ Todo el motor v2.0 con las 70 mejoras anteriores

70 MEJORAS HEREDADAS (M01–M70) + NUEVAS 8-BIT (R01–R10):
 R01 Paleta NES auténtica
 R02 Fuente pixelada
 R03 Motor de sonido chiptune (onda cuadrada)
 R04 Pantalla de arranque arcade
 R05 Bordes pixelados duros
 R06 Barra de progreso con bloques ASCII
 R07 Efecto CRT (scanlines opcional)
 R08 Comandos nuevos: pixel, sprite, chiptune, sonido
 R09 Logo ASCII pixel-art
 R10 Sonidos para acciones (click, error, éxito, arranque)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk, font as tkfont
import re
import platform
import json
import random
import math
import time
import webbrowser
import os
import sys
import threading
import queue
import traceback
import struct
import tempfile
import uuid as uuidlib
from datetime import datetime

# ============================================================
# PALETA NES AUTÉNTICA (R01)
# ============================================================
NES = {
    # Básicos
    "negro":       "#000000",
    "blanco":      "#FCFCFC",
    "gris":        "#BCBCBC",
    "gris_osc":    "#7C7C7C",
    "gris_cl":     "#D8D8D8",
    # Rojos
    "rojo":        "#F83800",
    "rojo_osc":    "#A81000",
    "rojo_cl":     "#F87858",
    # Naranjas / Marrones
    "naranja":     "#E45C10",
    "marron":      "#503000",
    "marron_cl":   "#AC7C00",
    # Amarillos
    "amarillo":    "#FCE0A8",
    "amarillo_v":  "#F8B800",
    "dorado":      "#AC7C00",
    # Verdes
    "verde":       "#00A800",
    "verde_cl":    "#58D854",
    "verde_lima":  "#B8F818",
    "verde_osc":   "#005800",
    # Azules
    "azul":        "#0000FC",
    "azul_cl":     "#3CBCFC",
    "azul_osc":    "#0000A8",
    "azul_cielo":  "#A4E4FC",
    # Morados / Rosas
    "morado":      "#6844FC",
    "morado_osc":  "#3800A8",
    "rosa":        "#F878F8",
    "rosa_cl":     "#F8B8F8",
    # Especiales UI 8-bit
    "ui_fondo":    "#0B0B1A",
    "ui_panel":    "#1A1A3E",
    "ui_borde":    "#F8B800",
    "ui_borde2":   "#F83800",
    "ui_texto":    "#FCFCFC",
    "ui_texto2":   "#F8B800",
}

# Mapa de colores en español para el intérprete
COLOR_MAP_ES = {
    "rojo": "#F83800", "azul": "#0000FC", "verde": "#00A800",
    "amarillo": "#F8B800", "naranja": "#E45C10", "morado": "#6844FC",
    "rosa": "#F878F8", "negro": "#000000", "blanco": "#FCFCFC",
    "gris": "#BCBCBC", "cian": "#3CBCFC", "violeta": "#6844FC",
    "marron": "#503000", "marrón": "#503000",
    "dorado": "#F8B800", "plateado": "#D8D8D8",
    "lima": "#B8F818",
}

APP_NAME = "EZSCRIPT 8-BITS"
VERSION = "2.0.0"
AUTOSAVE_INTERVAL_MS = 60000
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ezscript_8bit_config.json")


# ============================================================
# MOTOR DE SONIDO CHIPTUNE (R03, R10)
# ============================================================
class ChiptuneSoundBank:
    """Genera ondas cuadradas de estilo 8-bit y las reproduce."""

    def __init__(self, root):
        self.root = root
        self.enabled = True
        self._is_windows = platform.system() == "Windows"
        self._winsound = None
        if self._is_windows:
            try:
                import winsound
                self._winsound = winsound
            except Exception:
                self._winsound = None

    # -------- API pública --------
    def click(self):     self.play(880, 30)
    def start(self):     self._melody([(523, 60), (659, 60), (784, 120)])
    def success(self):   self._melody([(659, 80), (880, 120)])
    def error(self):     self._melody([(196, 100), (165, 180)])
    def coin(self):      self._melody([(988, 60), (1319, 180)])
    def boot(self):      self._melody([(392, 100), (523, 100), (659, 100), (784, 200)])
    def powerup(self):   self._melody([(523, 40), (659, 40), (784, 40), (1047, 120)])
    def hit(self):       self._melody([(220, 40), (180, 60)])

    def play(self, freq=880, duration_ms=50):
        if not self.enabled:
            return
        try:
            if self._winsound:
                self._winsound.Beep(int(freq), int(duration_ms))
            else:
                self.root.bell()
        except Exception:
            try:
                self.root.bell()
            except Exception:
                pass

    def _melody(self, notes):
        """notes = [(freq, duration_ms), ...] – reproduce secuencialmente."""
        if not self.enabled:
            return
        def worker():
            for f, d in notes:
                self.play(f, d)
                time.sleep(d / 1000.0 * 0.7)
        threading.Thread(target=worker, daemon=True).start()

    def note(self, name):
        """Reproduce una nota musical: do, re, mi, fa, sol, la, si (con octavas)."""
        notas = {
            "do3": 262, "re3": 294, "mi3": 330, "fa3": 349, "sol3": 392, "la3": 440, "si3": 494,
            "do4": 523, "re4": 587, "mi4": 659, "fa4": 698, "sol4": 784, "la4": 880, "si4": 988,
            "do5": 1047, "re5": 1175, "mi5": 1319,
        }
        f = notas.get(str(name).strip().lower())
        if f:
            self.play(f, 150)


# ============================================================
# INTÉRPRETE EASYSCRIPT (versión 8-bits)
# ============================================================
class EasyScriptInterpreter:
    COMMANDS = [
        "IA:", "SistemaOperativo:", "JS:", "HTML:", "CSS:", "JSON:", "ICON:",
        "linea:", "conectar:", "color:", "limpiar_pantalla", "mostrar", "print",
        "boton:", "button:", "var:", "VARIABLE_DEFINIR:", "incrementar:",
        "decrementar:", "entrada:", "mayusculas:", "minusculas:", "longitud:",
        "reemplazar:", "tipo_dato:", "concatenar:", "random:", "raiz:",
        "potencia:", "redondear:", "absoluto:", "seno:", "coseno:", "maximo:",
        "minimo:", "pi:", "rectangulo:", "circulo:", "ovalo:", "triangulo:",
        "texto_canvas:", "color_canvas:", "grosor_linea:", "borrar_canvas",
        "poligono:", "arco:", "cuadricula:", "fecha", "hora", "esperar:",
        "alerta:", "confirmar:", "abrir_url:", "copiar:", "notificacion:",
        "pitido", "ejecutar_cmd:", "ia_resumir:", "ia_traducir:", "ia_explicar:",
        "crear_archivo:", "leer_archivo:", "json_obtener:", "html_titulo:",
        "css_tema:", "js_eval:", "detener",
        "limpiar_consola", "hora_actual", "fecha_hora",
        "a_numero:", "a_texto:", "unir:", "dividir_texto:", "indice:",
        "invertir:", "ordenar:", "contar:",
        "sumar:", "restar:", "multiplicar:", "dividir:", "modulo:",
        "igual_a:", "mayor_que:", "menor_que:", "y:", "o:", "no:",
        "rgb:", "existe_archivo:", "eliminar_archivo:", "listar_archivos:",
        "uuid:", "log_info:", "log_warn:", "log_error:", "beep:",
        "esperar_tecla", "bucle:", "mientras:", "si:", "sino:", "fin_si", "fin_bucle",
        # Nuevos 8-bit (R08)
        "pixel:", "sprite:", "chiptune:", "sonido:", "nota:",
        "efecto_8bit:", "moneda:", "powerup:", "exito:", "error_8bit:",
    ]

    def __init__(self, output_widget, canvas_widget, app):
        self.variables = {}
        self.output = output_widget
        self.canvas = canvas_widget
        self.app = app
        self.should_stop = False
        self.text_positions = {}
        self.emulated_os = platform.system()
        self.current_line_width = 3
        self.current_draw_color = NES["azul"]
        self.COLOR_MAP = COLOR_MAP_ES
        self.show_timestamps = False
        self.execution_start = None
        self.execution_time = 0.0
        self.executed_lines = 0
        self.last_error_line = None
        self.sound = getattr(app, "sound", None)
        self._setup_console_tags()

    def _setup_console_tags(self):
        try:
            self.output.tag_config("info",    foreground=NES["blanco"])
            self.output.tag_config("error",   foreground=NES["rojo"])
            self.output.tag_config("warn",    foreground=NES["amarillo_v"])
            self.output.tag_config("success", foreground=NES["verde_cl"])
            self.output.tag_config("dim",     foreground=NES["gris_osc"])
        except Exception:
            pass

    def get_color(self, val):
        clean_val = str(val).strip().lower().replace('"', '').replace("'", "")
        if clean_val.startswith("#") or clean_val.startswith("rgb"):
            return clean_val
        return self.COLOR_MAP.get(clean_val, clean_val)

    def log(self, text, level="info"):
        prefix = ""
        if self.show_timestamps:
            prefix = f"[{datetime.now().strftime('%H:%M:%S')}] "
        full = prefix + str(text)
        self.output.insert(tk.END, full + "\n", level)
        self.output.see(tk.END)
        try: self.output.update()
        except Exception: pass
        try:
            line_num = int(self.output.index(tk.END).split('.')[0])
            self.text_positions[str(text).strip()] = (100, line_num * 20)
        except Exception: pass

    def log_info(self, t):    self.log(f"► {t}", "info")
    def log_warn(self, t):    self.log(f"! {t}", "warn")
    def log_error(self, t):   self.log(f"X {t}", "error")
    def log_success(self, t): self.log(f"OK {t}", "success")

    def eval_expr(self, expr):
        expr = str(expr).strip()
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
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
        parsed = "".join(new_tokens)
        try:
            return eval(parsed, {"__builtins__": None}, {})
        except Exception:
            return expr

    def validate(self, code):
        problems = []
        for idx, raw in enumerate(code.split("\n"), start=1):
            line = raw.strip()
            if not line or line.startswith("//"):
                continue
            if line.count("(") != line.count(")"):
                problems.append((idx, "Paréntesis desbalanceados"))
            if line.count("[") != line.count("]"):
                problems.append((idx, "Corchetes desbalanceados"))
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*:', line)
            if m:
                cmd = m.group(1) + ":"
                if not any(c.startswith(cmd) for c in self.COMMANDS):
                    problems.append((idx, f"Comando desconocido: {cmd}"))
        return problems

    def _safe_int(self, v, default=0):
        try:    return int(float(v))
        except Exception: return default

    def run_block(self, lines):
        i = 0
        n = len(lines)
        while i < n and not self.should_stop:
            line_data = lines[i]
            line_num = line_data['num']
            line = line_data['text'].strip()
            self.executed_lines += 1
            if not line or line.startswith("//"):
                i += 1
                continue
            try:
                self._execute_line(line, line_num)
            except Exception as e:
                self.last_error_line = line_num
                self.log_error(f"Error en línea {line_num}: {e}")
                if self.sound: self.sound.error()
                if self.app:
                    self.app.highlight_error_line(line_num)
            i += 1

    def _execute_line(self, line, line_num):
        # ============ COMANDOS BASE ============
        if line.startswith("IA:"):
            m = re.match(r'IA:\s*\((.*?)\)', line)
            if m: self.log_info(f"IA <- '{self.eval_expr(m.group(1))}'")

        elif line.startswith("SistemaOperativo:"):
            m = re.match(r'SistemaOperativo:\s*\((.*?)\)', line)
            if m:
                tgt = str(self.eval_expr(m.group(1))).strip()
                if tgt in ["Windows", "macOS", "Linux"]:
                    self.emulated_os = tgt
                    self.log_info(f"SO emulado: {self.emulated_os}")

        elif line.startswith("JS:"):    self.log(f"[JS] {line[3:].strip()}")
        elif line.startswith("HTML:"):  self.log(f"[HTML] {line[5:].strip()}")
        elif line.startswith("CSS:"):   self.log(f"[CSS] {line[4:].strip()}")
        elif line.startswith("JSON:"):
            try: self.log(f"[JSON] {json.loads(line[5:].strip())}")
            except Exception as e: self.log_warn(f"JSON inválido L{line_num}: {e}")
        elif line.startswith("ICON:"): self.log(f"[Icono] {line[5:].strip()}")

        elif line.startswith("linea:"):
            m = re.match(r'linea:\s*\((.*?)\)', line)
            if m:
                args = [a.strip() for a in m.group(1).split(',')]
                if len(args) >= 4:
                    x1 = self._safe_int(self.eval_expr(args[0]))
                    y1 = self._safe_int(self.eval_expr(args[1]))
                    x2 = self._safe_int(self.eval_expr(args[2]))
                    y2 = self._safe_int(self.eval_expr(args[3]))
                    col = self.get_color(self.eval_expr(args[4])) if len(args) > 4 else self.current_draw_color
                    self.canvas.create_line(x1, y1, x2, y2, fill=col, width=self.current_line_width)

        elif line.startswith("conectar:"):
            m = re.match(r'conectar:\s*\((.*?)\)', line)
            if m:
                args = [a.strip() for a in m.group(1).split(',')]
                if len(args) >= 2:
                    t1 = str(self.eval_expr(args[0]))
                    t2 = str(self.eval_expr(args[1]))
                    col = self.get_color(self.eval_expr(args[2])) if len(args) > 2 else self.current_draw_color
                    p1 = self.text_positions.get(t1); p2 = self.text_positions.get(t2)
                    if p1 and p2:
                        self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                                fill=col, width=self.current_line_width, dash=(4, 2))

        elif line.startswith("color:"):
            m = re.match(r'color:\s*\((.*?)\)', line)
            if m: self.current_draw_color = self.get_color(self.eval_expr(m.group(1).strip()))

        elif line == "limpiar_pantalla":
            self.output.delete("1.0", tk.END)
            self.canvas.delete("all")
            self.text_positions.clear()

        elif line == "limpiar_consola":
            self.output.delete("1.0", tk.END)

        elif line.startswith("mostrar ") or line.startswith("print "):
            self.log(self.eval_expr(line.split(" ", 1)[1]))

        elif line.startswith("boton:") or line.startswith("button:"):
            prefix = "boton:" if line.startswith("boton:") else "button:"
            content = line[len(prefix):].strip()
            if content.startswith("(") and content.endswith(")"): content = content[1:-1]
            parts = content.split(",", 1)
            txt = str(self.eval_expr(parts[0]))
            action = parts[1].strip() if len(parts) > 1 else ""
            btn = tk.Button(
                self.output, text=txt, bg=NES["rojo"], fg=NES["blanco"],
                activebackground=NES["amarillo_v"], activeforeground=NES["negro"],
                font=(getattr(self.app, "pixel_font_family", "Courier New"), 9, "bold"),
                relief=tk.RAISED, bd=3, padx=6, pady=2,
                command=lambda c=action: self.execute_inline(c)
            )
            self.output.window_create(tk.END, window=btn)
            self.output.insert(tk.END, "\n")

        # ============ VARIABLES Y CADENAS ============
        elif line.startswith("var:") or line.startswith("VARIABLE_DEFINIR:"):
            m = re.match(r'(?:var|VARIABLE_DEFINIR):\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = self.eval_expr(m.group(2))

        elif line.startswith("incrementar:"):
            m = re.match(r'incrementar:\s*\((.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = self.variables.get(k, 0) + self._safe_int(self.eval_expr(m.group(2)), 1)

        elif line.startswith("decrementar:"):
            m = re.match(r'decrementar:\s*\((.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = self.variables.get(k, 0) - self._safe_int(self.eval_expr(m.group(2)), 1)

        elif line.startswith("entrada:"):
            m = re.match(r'entrada:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    self.app.ask_input(str(self.eval_expr(m.group(2)))) or ""

        elif line.startswith("mayusculas:"):
            m = re.match(r'mayusculas:\s*\((.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k, "")).upper()

        elif line.startswith("minusculas:"):
            m = re.match(r'minusculas:\s*\((.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k, "")).lower()

        elif line.startswith("longitud:"):
            m = re.match(r'longitud:\s*\((.*?)\)', line)
            if m: self.log(f"Longitud: {len(str(self.eval_expr(m.group(1))))}")

        elif line.startswith("reemplazar:"):
            m = re.match(r'reemplazar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k, "")).replace(
                    str(self.eval_expr(m.group(2))), str(self.eval_expr(m.group(3))))

        elif line.startswith("tipo_dato:"):
            m = re.match(r'tipo_dato:\s*\((.*?)\)', line)
            if m: self.log(f"Tipo: {type(self.eval_expr(m.group(1))).__name__}")

        elif line.startswith("concatenar:"):
            m = re.match(r'concatenar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

        elif line.startswith("a_numero:"):
            m = re.match(r'a_numero:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2)))
                except Exception: self.variables[m.group(1).strip()] = 0

        elif line.startswith("a_texto:"):
            m = re.match(r'a_texto:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2)))

        elif line.startswith("unir:"):
            m = re.match(r'unir:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

        elif line.startswith("dividir_texto:"):
            m = re.match(r'dividir_texto:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2))).split(str(self.eval_expr(m.group(3))))

        elif line.startswith("indice:"):
            m = re.match(r'indice:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                lst = self.eval_expr(m.group(2)); idx = self._safe_int(self.eval_expr(m.group(3)))
                try: self.variables[m.group(1).strip()] = lst[idx]
                except Exception: self.variables[m.group(1).strip()] = ""

        elif line.startswith("invertir:"):
            m = re.match(r'invertir:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2)))[::-1]

        elif line.startswith("ordenar:"):
            m = re.match(r'ordenar:\s*\((.*?),(.*?)\)', line)
            if m:
                v = self.eval_expr(m.group(2))
                try: self.variables[m.group(1).strip()] = sorted(v)
                except Exception: self.variables[m.group(1).strip()] = v

        elif line.startswith("contar:"):
            m = re.match(r'contar:\s*\((.*?)\)', line)
            if m: self.log(f"Contar: {len(str(self.eval_expr(m.group(1))))}")

        # ============ MATEMÁTICAS ============
        elif line.startswith("random:"):
            m = re.match(r'random:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = random.randint(
                    self._safe_int(self.eval_expr(m.group(2))), self._safe_int(self.eval_expr(m.group(3))))

        elif line.startswith("raiz:"):
            m = re.match(r'raiz:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = math.sqrt(float(self.eval_expr(m.group(2))))
                except Exception: self.variables[m.group(1).strip()] = 0

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

        elif line.startswith("sumar:"):
            m = re.match(r'sumar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) + float(self.eval_expr(m.group(3)))
        elif line.startswith("restar:"):
            m = re.match(r'restar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) - float(self.eval_expr(m.group(3)))
        elif line.startswith("multiplicar:"):
            m = re.match(r'multiplicar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) * float(self.eval_expr(m.group(3)))
        elif line.startswith("dividir:"):
            m = re.match(r'dividir:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) / float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = 0
        elif line.startswith("modulo:"):
            m = re.match(r'modulo:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) % float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = 0

        elif line.startswith("igual_a:"):
            m = re.match(r'igual_a:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = (str(self.eval_expr(m.group(2))) == str(self.eval_expr(m.group(3))))
        elif line.startswith("mayor_que:"):
            m = re.match(r'mayor_que:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) > float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = False
        elif line.startswith("menor_que:"):
            m = re.match(r'menor_que:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) < float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = False
        elif line.startswith("y:"):
            m = re.match(r'y:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) and bool(self.eval_expr(m.group(3)))
        elif line.startswith("o:"):
            m = re.match(r'o:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) or bool(self.eval_expr(m.group(3)))
        elif line.startswith("no:"):
            m = re.match(r'no:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = not bool(self.eval_expr(m.group(2)))

        # ============ DIBUJO ============
        elif line.startswith("rectangulo:"):
            m = re.match(r'rectangulo:\s*\((.*?)\)', line)
            if m:
                args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                x, y = self._safe_int(args[0]), self._safe_int(args[1])
                w, h = self._safe_int(args[2]), self._safe_int(args[3])
                c = self.get_color(args[4]) if len(args) > 4 else self.current_draw_color
                self.canvas.create_rectangle(x, y, x + w, y + h, fill=c, outline="")

        elif line.startswith("circulo:"):
            m = re.match(r'circulo:\s*\((.*?)\)', line)
            if m:
                args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                x, y = self._safe_int(args[0]), self._safe_int(args[1])
                r = self._safe_int(args[2])
                c = self.get_color(args[3]) if len(args) > 3 else self.current_draw_color
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=c, outline="")

        elif line.startswith("ovalo:"):
            m = re.match(r'ovalo:\s*\((.*?)\)', line)
            if m:
                args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                x, y = self._safe_int(args[0]), self._safe_int(args[1])
                w, h = self._safe_int(args[2]), self._safe_int(args[3])
                c = self.get_color(args[4]) if len(args) > 4 else self.current_draw_color
                self.canvas.create_oval(x, y, x + w, y + h, fill=c, outline="")

        elif line.startswith("triangulo:"):
            m = re.match(r'triangulo:\s*\((.*?)\)', line)
            if m:
                args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                pts = [self._safe_int(args[i]) for i in range(6)]
                c = self.get_color(args[6]) if len(args) > 6 else self.current_draw_color
                self.canvas.create_polygon(pts, fill=c, outline="")

        elif line.startswith("texto_canvas:"):
            m = re.match(r'texto_canvas:\s*\((.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                x = self._safe_int(self.eval_expr(m.group(1)))
                y = self._safe_int(self.eval_expr(m.group(2)))
                txt = self.eval_expr(m.group(3))
                c = self.get_color(self.eval_expr(m.group(4))) if m.group(4) else self.current_draw_color
                self.canvas.create_text(x, y, text=str(txt), fill=c,
                                        font=(getattr(self.app, "pixel_font_family", "Courier New"), 10, "bold"))

        elif line.startswith("color_canvas:"):
            m = re.match(r'color_canvas:\s*\((.*?)\)', line)
            if m: self.canvas.config(bg=self.get_color(self.eval_expr(m.group(1))))

        elif line.startswith("grosor_linea:"):
            m = re.match(r'grosor_linea:\s*\((.*?)\)', line)
            if m: self.current_line_width = self._safe_int(self.eval_expr(m.group(1)), 1)

        elif line == "borrar_canvas": self.canvas.delete("all")

        elif line.startswith("poligono:"):
            m = re.match(r'poligono:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                vals = [self._safe_int(self.eval_expr(x)) for x in m.groups()[:6]]
                c = self.get_color(self.eval_expr(m.group(7))) if m.group(7) else self.current_draw_color
                self.canvas.create_polygon(vals, fill=c, outline="")

        elif line.startswith("arco:"):
            m = re.match(r'arco:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                vals = [self._safe_int(self.eval_expr(x)) for x in m.groups()[:6]]
                c = self.get_color(self.eval_expr(m.group(7))) if m.group(7) else self.current_draw_color
                self.canvas.create_arc(vals[0], vals[1], vals[2], vals[3], start=vals[4], extent=vals[5], fill=c)

        elif line.startswith("cuadricula:"):
            m = re.match(r'cuadricula:\s*\((.*?)\)', line)
            if m:
                step = self._safe_int(self.eval_expr(m.group(1)), 40)
                if step > 0:
                    for x in range(0, 400, step): self.canvas.create_line(x, 0, x, 400, fill=NES["ui_panel"], dash=(1, 3))
                    for y in range(0, 400, step): self.canvas.create_line(0, y, 400, y, fill=NES["ui_panel"], dash=(1, 3))

        elif line.startswith("rgb:"):
            m = re.match(r'rgb:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                r = self._safe_int(self.eval_expr(m.group(1))) % 256
                g = self._safe_int(self.eval_expr(m.group(2))) % 256
                b = self._safe_int(self.eval_expr(m.group(3))) % 256
                self.current_draw_color = f"#{r:02x}{g:02x}{b:02x}"

        # ============ 8-BIT EXCLUSIVOS (R08) ============
        elif line.startswith("pixel:"):
            m = re.match(r'pixel:\s*\((.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                x = self._safe_int(self.eval_expr(m.group(1)))
                y = self._safe_int(self.eval_expr(m.group(2)))
                size = self._safe_int(self.eval_expr(m.group(3)), 4) if m.group(3) else 4
                c = self.current_draw_color
                self.canvas.create_rectangle(x, y, x + size, y + size, fill=c, outline="")

        elif line.startswith("sprite:"):
            # sprite:(x, y, "RRRBBBGGG...", tamaño_pixel, color_mapa_json)
            m = re.match(r'sprite:\s*\((.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                x0 = self._safe_int(self.eval_expr(m.group(1)))
                y0 = self._safe_int(self.eval_expr(m.group(2)))
                data = str(self.eval_expr(m.group(3)))
                scale = max(1, self._safe_int(self.eval_expr(m.group(4)), 4))
                # Formato: "filas;columnas;c0=col1,c1=col2;00110011..."
                try:
                    parts = data.split(";")
                    rows, cols = int(parts[0]), int(parts[1])
                    pal = {}
                    for pair in parts[2].split(","):
                        k, v = pair.split("=")
                        pal[k.strip()] = self.get_color(v.strip())
                    bitmap = parts[3] if len(parts) > 3 else ""
                    for r in range(rows):
                        for c_idx in range(cols):
                            bit = bitmap[r * cols + c_idx] if r * cols + c_idx < len(bitmap) else "0"
                            if bit in pal:
                                px = x0 + c_idx * scale
                                py = y0 + r * scale
                                self.canvas.create_rectangle(px, py, px + scale, py + scale, fill=pal[bit], outline="")
                except Exception as e:
                    self.log_warn(f"Sprite inválido: {e}")

        elif line.startswith("chiptune:"):
            m = re.match(r'chiptune:\s*\((.*?)\)', line)
            if m and self.sound:
                note = str(self.eval_expr(m.group(1))).strip()
                self.sound.note(note)

        elif line.startswith("sonido:"):
            m = re.match(r'sonido:\s*\((.*?)(?:,(.*?))?\)', line)
            if m and self.sound:
                freq = self._safe_int(self.eval_expr(m.group(1)), 880)
                dur = self._safe_int(self.eval_expr(m.group(2)), 50) if m.group(2) else 50
                self.sound.play(freq, dur)

        elif line.startswith("efecto_8bit:"):
            m = re.match(r'efecto_8bit:\s*\((.*?)\)', line)
            if m and self.sound:
                name = str(self.eval_expr(m.group(1))).strip().lower()
                fn = getattr(self.sound, name, None)
                if callable(fn): fn()

        elif line.startswith("moneda:"):
            if self.sound: self.sound.coin()
        elif line.startswith("powerup:"):
            if self.sound: self.sound.powerup()
        elif line.startswith("exito:"):
            if self.sound: self.sound.success()
        elif line.startswith("error_8bit:"):
            if self.sound: self.sound.error()

        # ============ SISTEMA ============
        elif line == "fecha": self.log(f"Fecha: {datetime.now().strftime('%Y-%m-%d')}")
        elif line == "hora": self.log(f"Hora: {datetime.now().strftime('%H:%M:%S')}")
        elif line == "hora_actual": self.log(f"{datetime.now().strftime('%H:%M:%S')}")
        elif line == "fecha_hora": self.log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        elif line.startswith("esperar:"):
            m = re.match(r'esperar:\s*\((.*?)\)', line)
            if m:
                try: t = float(self.eval_expr(m.group(1)))
                except Exception: t = 0
                end = time.time() + t
                while time.time() < end and not self.should_stop:
                    time.sleep(0.02)
                    try: self.output.update()
                    except Exception: pass

        elif line.startswith("alerta:"):
            m = re.match(r'alerta:\s*\((.*?)\)', line)
            if m: messagebox.showinfo("ALERTA", str(self.eval_expr(m.group(1))))

        elif line.startswith("confirmar:"):
            m = re.match(r'confirmar:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = messagebox.askyesno("CONFIRMAR", str(self.eval_expr(m.group(2))))

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
            if m: self.log(f"[{self.eval_expr(m.group(1))}] {self.eval_expr(m.group(2))}")

        elif line == "pitido":
            if self.sound: self.sound.play(880, 80)
            else:
                try: self.app.root.bell()
                except Exception: pass

        elif line.startswith("beep:"):
            m = re.match(r'beep:\s*\((.*?)(?:,(.*?))?\)', line)
            if m and self.sound:
                freq = self._safe_int(self.eval_expr(m.group(1)), 880)
                dur = self._safe_int(self.eval_expr(m.group(2)), 100) if m.group(2) else 100
                self.sound.play(freq, dur)

        elif line.startswith("ejecutar_cmd:"):
            m = re.match(r'ejecutar_cmd:\s*\((.*?)\)', line)
            if m: self.log(f"CMD simulado: '{self.eval_expr(m.group(1))}'")

        elif line.startswith("log_info:"):
            m = re.match(r'log_info:\s*\((.*?)\)', line)
            if m: self.log_info(self.eval_expr(m.group(1)))
        elif line.startswith("log_warn:"):
            m = re.match(r'log_warn:\s*\((.*?)\)', line)
            if m: self.log_warn(self.eval_expr(m.group(1)))
        elif line.startswith("log_error:"):
            m = re.match(r'log_error:\s*\((.*?)\)', line)
            if m: self.log_error(self.eval_expr(m.group(1)))

        elif line == "esperar_tecla":
            messagebox.showinfo("EZSCRIPT", "Pulsa OK para continuar")

        elif line.startswith("uuid:"):
            m = re.match(r'uuid:\s*\((.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(uuidlib.uuid4())

        # ============ IA, WEB Y ARCHIVOS ============
        elif line.startswith("ia_resumir:"):
            m = re.match(r'ia_resumir:\s*\((.*?)\)', line)
            if m: self.log(f"[IA Resumen] {str(self.eval_expr(m.group(1)))[:60]}...")

        elif line.startswith("ia_traducir:"):
            m = re.match(r'ia_traducir:\s*\((.*?),(.*?)\)', line)
            if m: self.log(f"[IA Traducido a {self.eval_expr(m.group(2))}] {self.eval_expr(m.group(1))}")

        elif line.startswith("ia_explicar:"):
            m = re.match(r'ia_explicar:\s*\((.*?)\)', line)
            if m: self.log("[IA Explicación] Análisis completado.")

        elif line.startswith("crear_archivo:"):
            m = re.match(r'crear_archivo:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    with open(self.eval_expr(m.group(1)), "w", encoding="utf-8") as f:
                        f.write(str(self.eval_expr(m.group(2))))
                    self.log_success(f"Archivo creado: {self.eval_expr(m.group(1))}")
                except Exception as e:
                    self.log_error(str(e))

        elif line.startswith("leer_archivo:"):
            m = re.match(r'leer_archivo:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    with open(self.eval_expr(m.group(2)), "r", encoding="utf-8") as f:
                        self.variables[m.group(1).strip()] = f.read()
                except Exception as e:
                    self.log_error(f"Error al leer: {e}")

        elif line.startswith("json_obtener:"):
            m = re.match(r'json_obtener:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    j = self.eval_expr(m.group(2))
                    data = json.loads(j) if isinstance(j, str) else j
                    self.variables[m.group(1).strip()] = data.get(self.eval_expr(m.group(3)), "")
                except Exception as e:
                    self.log_warn(str(e))

        elif line.startswith("existe_archivo:"):
            m = re.match(r'existe_archivo:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = os.path.exists(str(self.eval_expr(m.group(2))))
        elif line.startswith("eliminar_archivo:"):
            m = re.match(r'eliminar_archivo:\s*\((.*?)\)', line)
            if m:
                try: os.remove(str(self.eval_expr(m.group(1))))
                except Exception as e: self.log_error(str(e))
        elif line.startswith("listar_archivos:"):
            m = re.match(r'listar_archivos:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = os.listdir(str(self.eval_expr(m.group(2))))
                except Exception as e: self.log_error(str(e))

        elif line.startswith("html_titulo:"):
            m = re.match(r'html_titulo:\s*\((.*?)\)', line)
            if m: self.log(f"<title>{self.eval_expr(m.group(1))}</title>")

        elif line.startswith("css_tema:"):
            m = re.match(r'css_tema:\s*\((.*?)\)', line)
            if m:
                v = str(self.eval_expr(m.group(1))).lower()
                bg = NES["ui_fondo"] if v == "oscuro" else NES["blanco"]
                fg = NES["blanco"] if v == "oscuro" else NES["negro"]
                self.output.config(bg=bg, fg=fg)
                self.canvas.config(bg=bg)

        elif line.startswith("js_eval:"):
            m = re.match(r'js_eval:\s*\((.*?)\)', line)
            if m: self.log(f"[JS] {self.eval_expr(m.group(1))}")

        elif line == "detener":
            self.should_stop = True
            self.log_warn("Ejecución detenida.")

        else:
            if ":" in line and not line.startswith("//"):
                self.log_warn(f"Comando no reconocido L{line_num}: {line}")

    def execute_inline(self, single_line):
        if single_line:
            self.run_block([{'num': 0, 'text': single_line}])

    def execute(self, code):
        self.variables = {}
        self.should_stop = False
        self.executed_lines = 0
        self.last_error_line = None
        self.output.delete("1.0", tk.END)
        self.canvas.delete("all")
        self.text_positions.clear()
        self.output.config(bg=NES["ui_fondo"], fg=NES["blanco"])
        self.canvas.config(bg=NES["ui_fondo"])
        self.current_draw_color = NES["azul"]

        if self.sound: self.sound.start()
        self.execution_start = time.time()
        raw_lines = code.split('\n')
        structured = [{'num': i + 1, 'text': l} for i, l in enumerate(raw_lines)]
        self.run_block(structured)
        self.execution_time = time.time() - self.execution_start

        self.log("", "info")
        self.log_success(
            f"FIN EN {self.execution_time:.3f}s · {self.executed_lines} líneas · {len(self.variables)} variables"
        )
        if self.sound: self.sound.success()
        if self.app:
            self.app.on_execution_finished(self.execution_time, self.executed_lines)


EZScriptInterpreter = EasyScriptInterpreter


# ============================================================
# PANTALLA DE ARRANQUE ARCADE (R04)
# ============================================================
class BootScreen:
    def __init__(self, root, sound, on_done):
        self.root = root
        self.sound = sound
        self.on_done = on_done

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.configure(bg=NES["negro"])
        w, h = 640, 480
        sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
        x = (sw - w) // 2; y = (sh - h) // 2
        self.win.geometry(f"{w}x{h}+{x}+{y}")

        self.canvas = tk.Canvas(self.win, width=w, height=h, bg=NES["negro"], highlightthickness=0)
        self.canvas.pack()

        # Borde exterior pixelado
        for i in range(0, w, 8):
            self.canvas.create_rectangle(i, 0, i+4, 4, fill=NES["rojo"], outline="")
            self.canvas.create_rectangle(i, h-4, i+4, h, fill=NES["rojo"], outline="")
        for j in range(0, h, 8):
            self.canvas.create_rectangle(0, j, 4, j+4, fill=NES["rojo"], outline="")
            self.canvas.create_rectangle(w-4, j, w, j+4, fill=NES["rojo"], outline="")

        # Logo ASCII pixel-art (R09)
        logo = [
            "  ███████ ███████ ███████  ██████ ██████ ██ ██████  ███████ ",
            "  ██         ██      ██   ██      ██  ██ ██ ██  ██     ██  ",
            "  █████      ██      ██   ██████  ██████ ██ ██████     ██  ",
            "  ██         ██      ██        ██ ██     ██ ██         ██  ",
            "  ███████    ██      ██   ██████  ██     ██ ██         ██  ",
        ]
        for i, line in enumerate(logo):
            self.canvas.create_text(w//2, 100 + i*26, text=line,
                                    fill=NES["amarillo_v"],
                                    font=(getattr(root, "pixel_font_family", "Courier New"), 14, "bold"),
                                    anchor="center")

        self.canvas.create_text(w//2, 280, text="8-BITS EDITION",
                                fill=NES["verde_cl"],
                                font=(getattr(root, "pixel_font_family", "Courier New"), 18, "bold"))

        self.canvas.create_text(w//2, 320, text=f"v{VERSION}",
                                fill=NES["gris_cl"],
                                font=(getattr(root, "pixel_font_family", "Courier New"), 10, "bold"))

        # Animación "PRESS START"
        self.press = self.canvas.create_text(w//2, 390, text="PULSA START",
                                            fill=NES["rojo"],
                                            font=(getattr(root, "pixel_font_family", "Courier New"), 16, "bold"))
        self.canvas.create_text(w//2, 430, text="(haz clic o pulsa una tecla)",
                                fill=NES["gris_osc"],
                                font=(getattr(root, "pixel_font_family", "Courier New"), 8))

        # Línea de bloques (barra de carga animada)
        self.bar_y = 355
        self.bar_blocks = self.canvas.create_text(w//2, self.bar_y, text="",
                                                  fill=NES["amarillo_v"],
                                                  font=(getattr(root, "pixel_font_family", "Courier New"), 12, "bold"))
        self._blink_state = True
        self._bar_fill = 0
        self._blink()

        # Sonido de arranque
        self.sound.boot()

        # Eventos
        self.win.bind("<Key>", lambda e: self._finish())
        self.win.bind("<Button-1>", lambda e: self._finish())
        self.canvas.bind("<Button-1>", lambda e: self._finish())

    def _blink(self):
        if not self.win.winfo_exists(): return
        self._blink_state = not self._blink_state
        try:
            self.canvas.itemconfig(self.press,
                                   fill=NES["rojo"] if self._blink_state else NES["ui_fondo"])
        except Exception:
            return
        # Barra de progreso animada
        self._bar_fill = (self._bar_fill + 1) % 21
        filled = "█" * self._bar_fill
        empty  = "░" * (20 - self._bar_fill)
        try:
            self.canvas.itemconfig(self.bar_blocks, text=filled + empty)
        except Exception:
            return
        self.win.after(80, self._blink)

    def _finish(self):
        try:
            self.sound.powerup()
            self.win.destroy()
        except Exception:
            pass
        self.on_done()


# ============================================================
# IDE 8-BIT
# ============================================================
class EasyScriptIDE8Bit:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1120x840")
        self.root.configure(bg=NES["negro"])

        # Detección de fuente pixelada (R02)
        self.pixel_font_family = self._pick_pixel_font()
        root.pixel_font_family = self.pixel_font_family

        # Estado
        self.font_family = self.pixel_font_family
        self.font_size = 10
        self.tab_size = 4
        self.word_wrap = False
        self.show_whitespace = False
        self.current_theme = "8bit"
        self.recent_files = []
        self.current_file = None
        self.execution_thread = None
        self.console_queue = queue.Queue()
        self.autosave_id = None

        # Motor de sonido (R03)
        self.sound = ChiptuneSoundBank(root)

        # Cargar config
        self._load_config()

        # Fuentes
        self.editor_font   = tkfont.Font(family=self.font_family, size=self.font_size, weight="bold")
        self.console_font  = tkfont.Font(family=self.font_family, size=max(9, self.font_size - 1))
        self.linenum_font  = tkfont.Font(family=self.font_family, size=max(9, self.font_size - 1))

        # Construcción (oculta hasta que termine la pantalla de arranque)
        self.root.withdraw()

        self._build_menu()
        self._build_toolbar()
        self._build_editor_area()
        self._build_output_area()
        self._build_statusbar()

        # Intérprete
        self.interpreter = EasyScriptInterpreter(self.console, self.canvas, self)

        self._bind_shortcuts()
        self._build_context_menu()
        self._load_demo()
        self._schedule_autosave()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Pantalla de arranque arcade
        BootScreen(self.root, self.sound, self._after_boot)

    def _pick_pixel_font(self):
        """Elige la mejor fuente pixelada disponible (R02)."""
        available = set(tkfont.families())
        candidatos = [
            "Press Start 2P", "PressStart2P", "Pixel Emulator", "Silkscreen",
            "Fixedsys", "Terminal", "MS Sans Serif", "Small Fonts",
            "Courier New", "Consolas", "Monaco",
        ]
        for c in candidatos:
            if c in available:
                return c
        return "Courier New"

    def _after_boot(self):
        self.root.deiconify()
        self.status.set("¡LISTO! PULSA F5 PARA EJECUTAR")
        self.sound.click()

    # ============================================================
    # UI CONSTRUCTION (R05 - bordes pixelados)
    # ============================================================
    def _pixel_frame(self, parent, bg=None):
        """Crea un marco con borde pixelado duro."""
        outer = tk.Frame(parent, bg=NES["ui_borde"], bd=0)
        inner = tk.Frame(outer, bg=bg or NES["ui_panel"], bd=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        return outer, inner

    def _build_menu(self):
        menubar = tk.Menu(self.root,
                          bg=NES["ui_panel"], fg=NES["ui_texto"],
                          activebackground=NES["rojo"], activeforeground=NES["blanco"],
                          bd=0, relief=tk.FLAT,
                          font=(self.font_family, 9, "bold"))

        m_file = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_texto"],
                         activebackground=NES["rojo"], activeforeground=NES["blanco"],
                         font=(self.font_family, 9, "bold"))
        m_file.add_command(label="NUEVO",            accelerator="Ctrl+N", command=self.new_project)
        m_file.add_command(label="ABRIR...",         accelerator="Ctrl+O", command=self.load_project)
        m_file.add_command(label="GUARDAR",          accelerator="Ctrl+S", command=self.save_project)
        m_file.add_command(label="GUARDAR COMO...",  accelerator="Ctrl+Shift+S", command=self.save_project_as)
        m_file.add_separator()
        m_file.add_command(label="GUARDAR CONSOLA...", command=self.save_console)
        m_file.add_command(label="GUARDAR CANVAS (PS)...", command=self.save_canvas_ps)
        m_file.add_separator()
        self.recent_menu = tk.Menu(m_file, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_texto"],
                                   font=(self.font_family, 9, "bold"))
        m_file.add_cascade(label="RECIENTES", menu=self.recent_menu)
        self._rebuild_recent_menu()
        m_file.add_separator()
        m_file.add_command(label="SALIR", command=self._on_close)
        menubar.add_cascade(label="ARCHIVO", menu=m_file)

        m_edit = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_texto"],
                         font=(self.font_family, 9, "bold"))
        m_edit.add_command(label="DESHACER",  accelerator="Ctrl+Z", command=lambda: self.code_editor.event_generate("<<Undo>>"))
        m_edit.add_command(label="REHACER",   accelerator="Ctrl+Y", command=lambda: self.code_editor.event_generate("<<Redo>>"))
        m_edit.add_separator()
        m_edit.add_command(label="BUSCAR / REEMPLAZAR", accelerator="Ctrl+F", command=self.open_find_dialog)
        m_edit.add_command(label="IR A LÍNEA...",       accelerator="Ctrl+G", command=self.goto_line)
        m_edit.add_separator()
        m_edit.add_command(label="DUPLICAR LÍNEA",   accelerator="Ctrl+D", command=self.duplicate_line)
        m_edit.add_command(label="COMENTAR",         accelerator="Ctrl+/", command=self.toggle_comment)
        m_edit.add_command(label="INDENTAR",         accelerator="Tab", command=lambda: self.indent_selection(True))
        m_edit.add_command(label="DESINDENTAR",      accelerator="Shift+Tab", command=lambda: self.indent_selection(False))
        m_edit.add_separator()
        m_edit.add_command(label="PALETA DE COMANDOS", accelerator="Ctrl+Shift+P", command=self.open_command_palette)
        m_edit.add_command(label="AUTOCOMPLETAR",      accelerator="Ctrl+Space", command=self.autocomplete)
        m_edit.add_separator()
        m_edit.add_command(label="INSPECCIONAR VARIABLES", command=self.inspect_variables)
        m_edit.add_command(label="EXPORTAR VARIABLES (JSON)", command=self.export_variables)
        m_edit.add_command(label="IMPORTAR VARIABLES (JSON)", command=self.import_variables)
        menubar.add_cascade(label="EDITAR", menu=m_edit)

        m_view = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_texto"],
                         font=(self.font_family, 9, "bold"))
        m_view.add_command(label="FUENTE +", command=lambda: self.change_font_size(+1))
        m_view.add_command(label="FUENTE -", command=lambda: self.change_font_size(-1))
        m_view.add_command(label="FUENTE RESET", command=self.reset_font_size)
        m_view.add_separator()
        self.var_wrap = tk.BooleanVar(value=self.word_wrap)
        m_view.add_checkbutton(label="AJUSTAR TEXTO", variable=self.var_wrap, command=self.toggle_wrap)
        self.var_ts = tk.BooleanVar(value=False)
        m_view.add_checkbutton(label="TIMESTAMPS EN CONSOLA", variable=self.var_ts, command=self.toggle_timestamps)
        self.var_snd = tk.BooleanVar(value=True)
        m_view.add_checkbutton(label="SONIDO CHIPTUNE", variable=self.var_snd, command=self.toggle_sound)
        m_view.add_separator()
        m_view.add_command(label="PANTALLA COMPLETA", accelerator="F11", command=self.toggle_fullscreen)
        menubar.add_cascade(label="VER", menu=m_view)

        m_run = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_texto"],
                        font=(self.font_family, 9, "bold"))
        m_run.add_command(label="EJECUTAR TODO",    accelerator="F5", command=self.run_code)
        m_run.add_command(label="EJECUTAR SELECCIÓN", accelerator="F6", command=self.run_selection)
        m_run.add_command(label="EJECUTAR DESDE CURSOR", accelerator="Ctrl+F5", command=self.run_from_cursor)
        m_run.add_command(label="VALIDAR SINTAXIS", accelerator="Ctrl+Shift+V", command=self.validate_syntax)
        m_run.add_separator()
        m_run.add_command(label="DETENER", accelerator="Esc", command=self.stop_execution)
        m_run.add_separator()
        m_run.add_command(label="LIMPIAR CONSOLA", command=lambda: self.console.delete("1.0", tk.END))
        m_run.add_command(label="LIMPIAR CANVAS",  command=lambda: self.canvas.delete("all"))
        m_run.add_command(label="COPIAR CONSOLA",  command=self.copy_console)
        menubar.add_cascade(label="EJECUTAR", menu=m_run)

        m_help = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_texto"],
                         font=(self.font_family, 9, "bold"))
        m_help.add_command(label="REFERENCIA DE COMANDOS", command=self.show_command_reference)
        m_help.add_command(label="BIBLIOTECA DE EJEMPLOS", command=self.show_examples)
        m_help.add_command(label="PLANTILLAS RÁPIDAS",     command=self.show_templates)
        m_help.add_separator()
        m_help.add_command(label="ESTADÍSTICAS", command=self.show_stats)
        m_help.add_command(label="ACERCA DE...", command=self.show_about)
        menubar.add_cascade(label="AYUDA", menu=m_help)

        self.root.config(menu=menubar)

    def _build_toolbar(self):
        outer, inner = self._pixel_frame(self.root, bg=NES["ui_panel"])
        outer.pack(side=tk.TOP, fill=tk.X, padx=6, pady=(6, 3))

        def add_btn(txt, color, cmd):
            b = tk.Button(inner, text=txt, bg=color, fg=NES["blanco"],
                          activebackground=NES["amarillo_v"], activeforeground=NES["negro"],
                          font=(self.font_family, 9, "bold"),
                          command=lambda: (self.sound.click(), cmd()),
                          relief=tk.RAISED, bd=3, padx=8, pady=3)
            b.pack(side=tk.LEFT, padx=2, pady=4)
            return b

        add_btn("NUEVO",     NES["azul"],      self.new_project)
        add_btn("ABRIR",     NES["naranja"],   self.load_project)
        add_btn("GUARDAR",   NES["verde"],     self.save_project)
        add_btn("EJECUTAR",  NES["rojo"],      self.run_code)
        add_btn("DETENER",   NES["morado"],    self.stop_execution)
        add_btn("LIMPIAR",   NES["marron_cl"], lambda: self.console.delete("1.0", tk.END))
        add_btn("AYUDA",     NES["gris_osc"],  self.show_command_reference)

        # Barra de progreso con bloques (R06)
        self.progress_lbl = tk.Label(inner, text="", bg=NES["ui_panel"], fg=NES["amarillo_v"],
                                     font=(self.font_family, 10, "bold"))
        self.progress_lbl.pack(side=tk.RIGHT, padx=8)
        self._progress_anim = False

    def _build_editor_area(self):
        outer, inner = self._pixel_frame(self.root, bg=NES["ui_panel"])
        outer.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)

        # Números de línea
        self.linenumbers = tk.Text(inner, width=4, padx=4, takefocus=0, border=0,
                                   background=NES["ui_fondo"], foreground=NES["gris_osc"],
                                   font=self.linenum_font, state="disabled")
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        self.code_editor = tk.Text(inner, font=self.editor_font, undo=True,
                                   wrap=tk.NONE, tabs=f"{{{self.tab_size}c}}",
                                   bg=NES["ui_fondo"], fg=NES["blanco"],
                                   insertbackground=NES["amarillo_v"],
                                   insertwidth=8,  # cursor grueso tipo consola
                                   selectbackground=NES["azul"],
                                   selectforeground=NES["blanco"],
                                   bd=0, highlightthickness=0)
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code_editor.bind("<<Modified>>", self._on_modified)
        self.code_editor.bind("<KeyRelease>", self._on_key_release)
        self.code_editor.bind("<Button-1>", self._on_click)
        self.code_editor.bind("<MouseWheel>", self._on_mousewheel)

        sb = tk.Scrollbar(inner, command=self._on_scroll, orient="vertical",
                          bg=NES["ui_panel"], troughcolor=NES["ui_fondo"],
                          activebackground=NES["amarillo_v"], bd=0, width=14)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_editor.config(yscrollcommand=lambda a, b: self._yscroll(a, b, sb))
        self._editor_scrollbar = sb

        self._setup_syntax_tags()

    def _build_output_area(self):
        outer, inner = self._pixel_frame(self.root, bg=NES["ui_panel"])
        outer.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        # Consola
        self.console = tk.Text(inner, font=self.console_font, height=11,
                               bg=NES["ui_fondo"], fg=NES["blanco"], width=50,
                               wrap=tk.WORD, bd=0, highlightthickness=0,
                               insertbackground=NES["amarillo_v"])
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.interpreter_console = self.console

        # Canvas (con borde duro)
        canvas_frame = tk.Frame(inner, bg=NES["ui_borde"], bd=0)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))
        self.canvas = tk.Canvas(canvas_frame, bg=NES["ui_fondo"], highlightthickness=0,
                                width=360)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=NES["ui_panel"])
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status = tk.StringVar()
        self.status.set("SISTEMA LISTO. INSERTA MONEDA.")
        self.lbl_status = tk.Label(bar, textvariable=self.status,
                                   bg=NES["ui_panel"], fg=NES["amarillo_v"],
                                   font=(self.font_family, 9, "bold"), anchor="w")
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=3)

        self.lbl_pos = tk.Label(bar, text="Ln 1, Col 1",
                                bg=NES["ui_panel"], fg=NES["blanco"],
                                font=(self.font_family, 9, "bold"))
        self.lbl_pos.pack(side=tk.RIGHT, padx=6)

        self.lbl_count = tk.Label(bar, text="0 L · 0 CH",
                                  bg=NES["ui_panel"], fg=NES["verde_cl"],
                                  font=(self.font_family, 9, "bold"))
        self.lbl_count.pack(side=tk.RIGHT, padx=6)

    # ============================================================
    # SINTAXIS (colores NES)
    # ============================================================
    def _setup_syntax_tags(self):
        e = self.code_editor
        e.tag_configure("kw",       foreground=NES["amarillo_v"])
        e.tag_configure("string",   foreground=NES["verde_lima"])
        e.tag_configure("comment",  foreground=NES["gris_osc"], font=(self.font_family, self.font_size, "italic"))
        e.tag_configure("number",   foreground=NES["naranja"])
        e.tag_configure("color",    foreground=NES["rosa"])
        e.tag_configure("errorline", background=NES["rojo_osc"])
        e.tag_configure("current",  background=NES["ui_panel"])

    def _highlight_syntax(self):
        e = self.code_editor
        for tag in ("kw", "string", "comment", "number", "color"):
            e.tag_remove(tag, "1.0", tk.END)
        text = e.get("1.0", tk.END)
        for m in re.finditer(r'//[^\n]*', text):
            self._tag_range("comment", m.start(), m.end())
        for m in re.finditer(r'"[^"\n]*"|\'[^\'\n]*\'', text):
            self._tag_range("string", m.start(), m.end())
        for m in re.finditer(r'\b\d+(\.\d+)?\b', text):
            self._tag_range("number", m.start(), m.end())
        for c in ("rojo","azul","verde","amarillo","naranja","morado","rosa",
                  "negro","blanco","gris","cian","violeta","marron","marrón",
                  "dorado","plateado","lima"):
            for m in re.finditer(r'\b' + c + r'\b', text):
                self._tag_range("color", m.start(), m.end())
        for m in re.finditer(r'(?m)^\s*([A-Za-z_][A-Za-z0-9_]*\s*:)', text):
            self._tag_range("kw", m.start(1), m.end(1))

    def _tag_range(self, tag, start, end):
        try:
            s = self.code_editor.index(f"1.0+{start}c")
            e = self.code_editor.index(f"1.0+{end}c")
            self.code_editor.tag_add(tag, s, e)
        except Exception:
            pass

    def _highlight_current_line(self):
        self.code_editor.tag_remove("current", "1.0", tk.END)
        idx = self.code_editor.index(tk.INSERT)
        self.code_editor.tag_add("current", f"{idx} linestart", f"{idx} lineend+1c")

    def highlight_error_line(self, line_num):
        try:
            self.code_editor.tag_add("errorline", f"{line_num}.0", f"{line_num}.end+1c")
        except Exception:
            pass

    # ============================================================
    # SCROLL Y EVENTOS
    # ============================================================
    def _on_scroll(self, *args):
        self.code_editor.yview(*args)
        self.linenumbers.yview(*args)

    def _yscroll(self, a, b, sb):
        sb.set(a, b)
        self.linenumbers.yview_moveto(a)

    def _update_linenumbers(self):
        lines = int(self.code_editor.index("end-1c").split(".")[0])
        txt = "\n".join(str(i) for i in range(1, lines + 1))
        self.linenumbers.config(state="normal")
        self.linenumbers.delete("1.0", tk.END)
        self.linenumbers.insert("1.0", txt)
        self.linenumbers.config(state="disabled")
        self._update_status_counts()

    def _update_status_counts(self):
        txt = self.code_editor.get("1.0", "end-1c")
        lines = txt.count("\n") + 1
        self.lbl_count.config(text=f"{lines} L · {len(txt)} CH")

    def _on_modified(self, event):
        self.code_editor.edit_modified(False)
        self._update_linenumbers()

    def _on_key_release(self, event):
        self._highlight_syntax()
        self._highlight_current_line()
        self._update_cursor_pos()
        if event.char in ("(", "[", "{", '"', "'"):
            self._autoclose(event.char)

    def _on_click(self, event):
        self.root.after(10, self._highlight_current_line)
        self.root.after(10, self._update_cursor_pos)

    def _on_mousewheel(self, event):
        self.code_editor.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.linenumbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _update_cursor_pos(self):
        idx = self.code_editor.index(tk.INSERT)
        ln, col = idx.split(".")
        self.lbl_pos.config(text=f"Ln {ln}, Col {int(col)+1}")

    def _autoclose(self, ch):
        pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        close = pairs.get(ch)
        if close and ch in ('"', "'"):
            prev = self.code_editor.get("insert-2c", "insert-1c")
            if prev == ch: return
        if close:
            self.code_editor.insert(tk.INSERT, close)
            self.code_editor.mark_set(tk.INSERT, "insert-1c")

    # ============================================================
    # ATAJOS
    # ============================================================
    def _bind_shortcuts(self):
        b = self.root.bind
        b("<Control-n>", lambda e: self.new_project())
        b("<Control-o>", lambda e: self.load_project())
        b("<Control-s>", lambda e: self.save_project())
        b("<Control-Shift-S>", lambda e: self.save_project_as())
        b("<Control-f>", lambda e: self.open_find_dialog())
        b("<Control-g>", lambda e: self.goto_line())
        b("<Control-d>", lambda e: self.duplicate_line())
        b("<Control-slash>", lambda e: self.toggle_comment())
        b("<Control-plus>",  lambda e: self.change_font_size(+1))
        b("<Control-equal>", lambda e: self.change_font_size(+1))
        b("<Control-minus>", lambda e: self.change_font_size(-1))
        b("<Control-0>", lambda e: self.reset_font_size())
        b("<F5>", lambda e: self.run_code())
        b("<F6>", lambda e: self.run_selection())
        b("<Control-F5>", lambda e: self.run_from_cursor())
        b("<Control-Shift-V>", lambda e: self.validate_syntax())
        b("<Control-Shift-P>", lambda e: self.open_command_palette())
        b("<F11>", lambda e: self.toggle_fullscreen())
        b("<Escape>", lambda e: self.stop_execution())
        self.code_editor.bind("<Tab>", self._on_tab)
        self.code_editor.bind("<Shift-Tab>", self._on_shift_tab)
        self.code_editor.bind("<Control-space>", lambda e: self.autocomplete())

    def _on_tab(self, event):
        if self.code_editor.tag_ranges("sel"):
            self.indent_selection(True)
        else:
            self.code_editor.insert(tk.INSERT, " " * self.tab_size)
        return "break"

    def _on_shift_tab(self, event):
        self.indent_selection(False)
        return "break"

    # ============================================================
    # FUNCIONES DEL EDITOR
    # ============================================================
    def duplicate_line(self):
        try:
            idx = self.code_editor.index(tk.INSERT)
            line = int(idx.split(".")[0])
            content = self.code_editor.get(f"{line}.0", f"{line}.end")
            self.code_editor.insert(f"{line}.end", "\n" + content)
        except Exception: pass

    def toggle_comment(self):
        try:
            if self.code_editor.tag_ranges("sel"):
                start = int(self.code_editor.index("sel.first").split(".")[0])
                end = int(self.code_editor.index("sel.last").split(".")[0])
            else:
                start = end = int(self.code_editor.index(tk.INSERT).split(".")[0])
            for ln in range(start, end + 1):
                line = self.code_editor.get(f"{ln}.0", f"{ln}.end")
                if line.strip().startswith("//"):
                    new = re.sub(r'^(\s*)//\s?', r'\1', line)
                else:
                    new = re.sub(r'^(\s*)', r'\1// ', line)
                self.code_editor.delete(f"{ln}.0", f"{ln}.end")
                self.code_editor.insert(f"{ln}.0", new)
        except Exception: pass

    def indent_selection(self, positive=True):
        try:
            if self.code_editor.tag_ranges("sel"):
                start = int(self.code_editor.index("sel.first").split(".")[0])
                end = int(self.code_editor.index("sel.last").split(".")[0])
            else:
                start = end = int(self.code_editor.index(tk.INSERT).split(".")[0])
            for ln in range(start, end + 1):
                line = self.code_editor.get(f"{ln}.0", f"{ln}.end")
                if positive:
                    self.code_editor.delete(f"{ln}.0", f"{ln}.end")
                    self.code_editor.insert(f"{ln}.0", " " * self.tab_size + line)
                else:
                    stripped = re.sub(r'^ {1,' + str(self.tab_size) + r'}', '', line)
                    self.code_editor.delete(f"{ln}.0", f"{ln}.end")
                    self.code_editor.insert(f"{ln}.0", stripped)
        except Exception: pass

    def goto_line(self):
        ln = simpledialog.askinteger("IR A LÍNEA", "Número de línea:", parent=self.root)
        if ln:
            try:
                self.code_editor.mark_set(tk.INSERT, f"{ln}.0")
                self.code_editor.see(f"{ln}.0")
            except Exception: pass

    def autocomplete(self):
        idx = self.code_editor.index(tk.INSERT)
        line_start = self.code_editor.index(f"{idx} linestart")
        prefix = self.code_editor.get(line_start, idx)
        matches = [c for c in self.interpreter.COMMANDS if c.startswith(prefix.strip())] if prefix.strip() else []
        if len(matches) == 1:
            self.code_editor.insert(tk.INSERT, matches[0][len(prefix.strip()):])
        elif len(matches) > 1:
            self._show_popup_list(matches, self.code_editor, idx)

    def _show_popup_list(self, items, widget, at):
        pop = tk.Toplevel(self.root)
        pop.overrideredirect(True)
        pop.configure(bg=NES["ui_borde"])
        lb = tk.Listbox(pop, height=min(10, len(items)),
                        bg=NES["ui_fondo"], fg=NES["blanco"],
                        selectbackground=NES["rojo"], selectforeground=NES["blanco"],
                        font=(self.font_family, 9, "bold"), bd=0, highlightthickness=0)
        for it in items: lb.insert(tk.END, it)
        lb.pack(padx=2, pady=2)
        try:
            x = self.root.winfo_pointerx(); y = self.root.winfo_pointery()
            pop.geometry(f"+{x}+{y}")
        except Exception: pass
        def on_select(event):
            sel = lb.curselection()
            if sel: widget.insert(at, items[sel[0]])
            pop.destroy()
        lb.bind("<Double-Button-1>", on_select)
        lb.bind("<Return>", on_select)
        pop.bind("<FocusOut>", lambda e: pop.destroy())

    # ============================================================
    # BUSCAR / REEMPLAZAR
    # ============================================================
    def open_find_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("BUSCAR Y REEMPLAZAR")
        win.geometry("440x200")
        win.configure(bg=NES["ui_fondo"])

        tk.Label(win, text="BUSCAR:", bg=NES["ui_fondo"], fg=NES["amarillo_v"],
                 font=(self.font_family, 10, "bold")).grid(row=0, column=0, sticky="e", padx=6, pady=6)
        e_find = tk.Entry(win, width=30, bg=NES["ui_fondo"], fg=NES["blanco"],
                          insertbackground=NES["amarillo_v"],
                          font=(self.font_family, 10, "bold"))
        e_find.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(win, text="REEMPLAZAR:", bg=NES["ui_fondo"], fg=NES["amarillo_v"],
                 font=(self.font_family, 10, "bold")).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        e_repl = tk.Entry(win, width=30, bg=NES["ui_fondo"], fg=NES["blanco"],
                          insertbackground=NES["amarillo_v"],
                          font=(self.font_family, 10, "bold"))
        e_repl.grid(row=1, column=1, padx=6, pady=6)

        def mk_btn(txt, cmd):
            return tk.Button(win, text=txt, command=cmd, bg=NES["azul"], fg=NES["blanco"],
                             activebackground=NES["amarillo_v"], activeforeground=NES["negro"],
                             font=(self.font_family, 9, "bold"), bd=3, relief=tk.RAISED, padx=8, pady=2)

        def find_next():
            needle = e_find.get()
            if not needle: return
            idx = self.code_editor.search(needle, tk.INSERT, stopindex=tk.END)
            if not idx:
                idx = self.code_editor.search(needle, "1.0", stopindex=tk.END)
            if idx:
                end = f"{idx}+{len(needle)}c"
                self.code_editor.tag_add("sel", idx, end)
                self.code_editor.mark_set(tk.INSERT, end)
                self.code_editor.see(idx)

        def replace_one():
            if self.code_editor.tag_ranges("sel"):
                self.code_editor.delete("sel.first", "sel.last")
                self.code_editor.insert(tk.INSERT, e_repl.get())
            find_next()

        def replace_all():
            needle = e_find.get()
            if not needle: return
            content = self.code_editor.get("1.0", "end-1c")
            new = content.replace(needle, e_repl.get())
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", new)

        mk_btn("BUSCAR",        find_next).grid(row=2, column=0, padx=6, pady=6)
        mk_btn("REEMPLAZAR",    replace_one).grid(row=2, column=1, padx=6, pady=6)
        mk_btn("REEMPLAZAR TODO", replace_all).grid(row=3, column=1, padx=6, pady=6)
        e_find.focus_set()

    # ============================================================
    # FUENTE / VISTA
    # ============================================================
    def change_font_size(self, delta):
        self.font_size = max(7, min(24, self.font_size + delta))
        self._apply_fonts()

    def reset_font_size(self):
        self.font_size = 10
        self._apply_fonts()

    def _apply_fonts(self):
        self.editor_font.configure(size=self.font_size)
        self.console_font.configure(size=max(9, self.font_size - 1))
        self.linenum_font.configure(size=max(9, self.font_size - 1))
        self.code_editor.configure(font=self.editor_font, tabs=f"{{{self.tab_size}c}}")

    def toggle_wrap(self):
        self.word_wrap = self.var_wrap.get()
        self.code_editor.configure(wrap=tk.WORD if self.word_wrap else tk.NONE)

    def toggle_timestamps(self):
        self.interpreter.show_timestamps = self.var_ts.get()

    def toggle_sound(self):
        self.sound.enabled = self.var_snd.get()
        if self.sound.enabled:
            self.sound.click()

    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    # ============================================================
    # EJECUCIÓN
    # ============================================================
    def run_code(self):
        code = self.code_editor.get("1.0", tk.END)
        self._start_execution(code)

    def run_selection(self):
        try:
            code = self.code_editor.get("sel.first", "sel.last")
            self._start_execution(code)
        except Exception:
            messagebox.showinfo("SELECCIÓN", "Selecciona código primero.")

    def run_from_cursor(self):
        idx = self.code_editor.index(tk.INSERT)
        code = self.code_editor.get(idx, tk.END)
        self._start_execution(code)

    def validate_syntax(self):
        code = self.code_editor.get("1.0", tk.END)
        problems = self.interpreter.validate(code)
        if not problems:
            self.sound.success()
            messagebox.showinfo("VALIDACIÓN", "OK SINTAXIS CORRECTA.")
        else:
            self.sound.error()
            msg = "\n".join(f"L{l}: {m}" for l, m in problems)
            messagebox.showwarning("ERRORES DETECTADOS", msg)

    def _start_execution(self, code):
        if self.execution_thread and self.execution_thread.is_alive():
            messagebox.showinfo("EJECUCIÓN", "Ya hay una ejecución en curso.")
            return
        self.code_editor.tag_remove("errorline", "1.0", tk.END)
        self.status.set("EJECUTANDO...")
        self._progress_anim = True
        self._animate_progress()

        def worker():
            try:
                self.interpreter.execute(code)
            except Exception:
                self.console_queue.put(("error", traceback.format_exc()))
            finally:
                self.root.after(0, self._on_execution_done)

        self.execution_thread = threading.Thread(target=worker, daemon=True)
        self.execution_thread.start()

    def _animate_progress(self):
        if not self._progress_anim: return
        frames = ["░", "▒", "▓", "█"]
        idx = getattr(self, "_prog_idx", 0)
        self.progress_lbl.config(text="CARGANDO " + frames[idx % 4] * 6)
        self._prog_idx = idx + 1
        self.root.after(120, self._animate_progress)

    def _on_execution_done(self):
        self._progress_anim = False
        self.progress_lbl.config(text="")
        self.status.set("LISTO.")

    def on_execution_finished(self, secs, lines):
        self.status.set(f"OK {lines} LÍNEAS · {secs:.3f}s")

    def stop_execution(self):
        self.interpreter.should_stop = True
        self.status.set("DETENIENDO...")
        self.sound.hit()

    # ============================================================
    # CONSOLA / ARCHIVOS
    # ============================================================
    def copy_console(self):
        try:
            txt = self.console.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self.status.set("CONSOLA COPIADA.")
        except Exception: pass

    def save_console(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.console.get("1.0", "end-1c"))
            self.status.set(f"CONSOLA GUARDADA: {os.path.basename(path)}")

    def save_canvas_ps(self):
        path = filedialog.asksaveasfilename(defaultextension=".ps",
                                            filetypes=[("PostScript", "*.ps"), ("Todos", "*.*")])
        if path:
            try:
                self.canvas.postscript(file=path)
                self.status.set(f"CANVAS GUARDADO: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("ERROR", str(e))

    # ============================================================
    # MENÚ CONTEXTUAL
    # ============================================================
    def _build_context_menu(self):
        m = tk.Menu(self.root, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_texto"],
                    font=(self.font_family, 9, "bold"))
        m.add_command(label="CORTAR",     command=lambda: self.code_editor.event_generate("<<Cut>>"))
        m.add_command(label="COPIAR",     command=lambda: self.code_editor.event_generate("<<Copy>>"))
        m.add_command(label="PEGAR",      command=lambda: self.code_editor.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label="DUPLICAR LÍNEA", command=self.duplicate_line)
        m.add_command(label="COMENTAR",       command=self.toggle_comment)
        m.add_command(label="IR A LÍNEA...",  command=self.goto_line)
        m.add_separator()
        m.add_command(label="EJECUTAR SELECCIÓN", command=self.run_selection)
        def popup(e):
            try: m.tk_popup(e.x_root, e.y_root)
            finally: m.grab_release()
        self.code_editor.bind("<Button-3>", popup)
        self.code_editor.bind("<Button-2>", popup)

    # ============================================================
    # DIÁLOGOS
    # ============================================================
    def show_about(self):
        self.sound.coin()
        messagebox.showinfo("ACERCA DE",
                            f"{APP_NAME}\nVersión {VERSION}\n\n"
                            "► Retro 8-bit IDE\n"
                            "► Fuente: {}\n"
                            "► Sound engine: Chiptune\n"
                            "► 70 mejoras + 10 nuevas retro".format(self.pixel_font_family))

    def show_command_reference(self):
        win = tk.Toplevel(self.root)
        win.title("REFERENCIA DE COMANDOS")
        win.geometry("680x540")
        win.configure(bg=NES["ui_fondo"])
        txt = tk.Text(win, wrap=tk.WORD, font=(self.font_family, 10),
                      bg=NES["ui_fondo"], fg=NES["blanco"], bd=0, highlightthickness=0)
        txt.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        txt.insert("1.0", self._command_reference_text())
        txt.config(state="disabled")

    def _command_reference_text(self):
        return """EZSCRIPT 8-BITS - REFERENCIA DE COMANDOS
=========================================

VARIABLES
  var:(nombre, valor)          Define variable
  incrementar:(var, n)         Suma n
  decrementar:(var, n)         Resta n
  entrada:(var, "prompt")      Pide al usuario

CADENAS
  mayusculas / minusculas
  longitud / reemplazar / concatenar
  a_texto / a_numero
  dividir_texto / indice / invertir / ordenar / contar

MATEMÁTICAS
  sumar / restar / multiplicar / dividir / modulo
  raiz / potencia / redondear / absoluto
  seno / coseno / maximo / minimo / pi

LÓGICA
  igual_a / mayor_que / menor_que / y / o / no

DIBUJO
  color:("rojo")                Color actual
  linea / rectangulo / circulo / ovalo / triangulo
  poligono / arco / texto_canvas / color_canvas
  grosor_linea / cuadricula / borrar_canvas / limpiar_pantalla
  rgb:(r,g,b)                   Color por componentes

COLORES DISPONIBLES (paleta NES)
  rojo, azul, verde, amarillo, naranja, morado, rosa,
  negro, blanco, gris, cian, violeta, marron, dorado,
  plateado, lima

★ COMANDOS 8-BIT EXCLUSIVOS ★
  pixel:(x, y, [tam])              Dibuja un pixel
  sprite:(x, y, "filas;cols;c0=rojo,c1=azul;00110011", escala)
                                    Dibuja un sprite bitmap
  chiptune:("do4")                 Reproduce nota musical
                                    Notas: do3..si3, do4..si4, do5..
  sonido:(freq, dur_ms)            Onda cuadrada personalizada
  efecto_8bit:("coin")             Efectos predefinidos:
                                    coin, powerup, success, error,
                                    start, boot, hit, click
  moneda:                          Efecto "coin" rápido
  powerup:                         Efecto power-up
  exito: / error_8bit:             Efectos de estado

SISTEMA
  fecha / hora / hora_actual / fecha_hora
  esperar:(seg) / esperar_tecla
  alerta / confirmar / notificacion
  copiar / abrir_url / ejecutar_cmd
  pitido / beep:(freq,dur)

ARCHIVOS
  crear_archivo / leer_archivo / existe_archivo
  eliminar_archivo / listar_archivos
  json_obtener

IA / WEB
  IA: / ia_resumir / ia_traducir / ia_explicar
  JS: / HTML: / CSS: / JS_EVAL:
  html_titulo / css_tema

LOGS
  log_info / log_warn / log_error
  uuid:(var)

CONSOLA
  limpiar_consola / limpiar_pantalla / detener

EJEMPLO SPRITE
  color:("rojo")
  sprite:(50, 50, "8;8;#=rojo,.=negro;#.#.#.#..##..##..#.#.#.#...#..#..#.#.#.#..##..##..#.#.#.#", 6)
"""

    def show_examples(self):
        win = tk.Toplevel(self.root)
        win.title("BIBLIOTECA DE EJEMPLOS")
        win.geometry("580x440")
        win.configure(bg=NES["ui_fondo"])
        examples = {
            "HOLA MUNDO":     'mostrar "¡HOLA, 8-BITS!"\nmoneda:',
            "CONTADOR":       'var:(n, 0)\nincrementar:(n, 1)\nincrementar:(n, 1)\nmostrar n\nmoneda:',
            "CÍRCULO ROJO":   'color:("rojo")\ncirculo:(100, 100, 40)\nsonido:(440, 80)',
            "CUADRÍCULA + RECTÁNGULO":
                'cuadricula:(40)\ncolor:("azul")\nrectangulo:(40, 40, 120, 80)',
            "TEXTO PIXEL":    'texto_canvas:(150, 60, "¡HOLA!", "verde")',
            "RGB":            'rgb:(255, 100, 50)\ncirculo:(80, 80, 40)',
            "ALEATORIO + MATH":
                'random:(n, 1, 100)\nmostrar n\nsumar:(r, n, 5)\nmostrar r',
            "MELODÍA CHIPTUNE":
                'chiptune:("do4")\nchiptune:("mi4")\nchiptune:("sol4")\nchiptune:("do5")',
            "EFECTOS 8-BIT":
                'efecto_8bit:("coin")\nefecto_8bit:("powerup")\nefecto_8bit:("success")',
            "BOTÓN":          'boton:("CLIC", moneda:)',
            "SPRITE CORAZÓN":
                'color:("rojo")\nsprite:(50, 50, "8;8;#=rojo,.=fondo;#..##..##..##..##..##..##..##..#", 6)',
            "FECHA Y HORA":   'fecha\nhora',
        }
        lb = tk.Listbox(win, font=(self.font_family, 10, "bold"),
                        bg=NES["ui_fondo"], fg=NES["blanco"],
                        selectbackground=NES["rojo"], selectforeground=NES["blanco"],
                        bd=0, highlightthickness=0)
        for k in examples: lb.insert(tk.END, k)
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        def insert_example(_e=None):
            sel = lb.curselection()
            if not sel: return
            name = lb.get(sel[0])
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", examples[name])
            self.sound.click()
            win.destroy()
        lb.bind("<Double-Button-1>", insert_example)

    def show_templates(self):
        templates = {
            "BASE DIBUJO":   'limpiar_pantalla\ncuadricula:(40)\ncolor:("azul")\n',
            "INTERACCIÓN":   'entrada:(nombre, "¿Cómo te llamas?")\nmostrar nombre\nmoneda:',
            "DEMO COMPLETA": self.code_editor.get("1.0", "end-1c"),
        }
        win = tk.Toplevel(self.root)
        win.title("PLANTILLAS RÁPIDAS")
        win.geometry("380x260")
        win.configure(bg=NES["ui_fondo"])
        lb = tk.Listbox(win, font=(self.font_family, 10, "bold"),
                        bg=NES["ui_fondo"], fg=NES["blanco"],
                        selectbackground=NES["rojo"], selectforeground=NES["blanco"],
                        bd=0, highlightthickness=0)
        for k in templates: lb.insert(tk.END, k)
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        def pick(_e=None):
            sel = lb.curselection()
            if not sel: return
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", templates[lb.get(sel[0])])
            self.sound.click()
            win.destroy()
        lb.bind("<Double-Button-1>", pick)

    def inspect_variables(self):
        win = tk.Toplevel(self.root)
        win.title("VARIABLES")
        win.geometry("440x400")
        win.configure(bg=NES["ui_fondo"])
        lb = tk.Listbox(win, font=(self.font_family, 10),
                        bg=NES["ui_fondo"], fg=NES["blanco"],
                        bd=0, highlightthickness=0)
        for k, v in self.interpreter.variables.items():
            lb.insert(tk.END, f"{k} = {v!r}")
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def export_variables(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.interpreter.variables, f, indent=2, ensure_ascii=False)
            self.status.set(f"VARIABLES EXPORTADAS: {os.path.basename(path)}")

    def import_variables(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.interpreter.variables.update(data)
            self.status.set(f"VARIABLES IMPORTADAS: {os.path.basename(path)}")

    def show_stats(self):
        info = (
            f"ESTADÍSTICAS\n"
            f"─────────────\n"
            f"Líneas ejecutadas: {self.interpreter.executed_lines}\n"
            f"Tiempo: {self.interpreter.execution_time:.3f} s\n"
            f"Variables: {len(self.interpreter.variables)}\n"
            f"Última línea con error: {self.interpreter.last_error_line}\n"
        )
        self.sound.coin()
        messagebox.showinfo("ESTADÍSTICAS", info)

    def open_command_palette(self):
        win = tk.Toplevel(self.root)
        win.title("PALETA DE COMANDOS")
        win.geometry("440x320")
        win.configure(bg=NES["ui_fondo"])
        entry = tk.Entry(win, font=(self.font_family, 11, "bold"),
                         bg=NES["ui_fondo"], fg=NES["blanco"],
                         insertbackground=NES["amarillo_v"], bd=3, relief=tk.RAISED)
        entry.pack(fill=tk.X, padx=6, pady=6)
        lb = tk.Listbox(win, font=(self.font_family, 10),
                        bg=NES["ui_fondo"], fg=NES["blanco"],
                        selectbackground=NES["rojo"], selectforeground=NES["blanco"],
                        bd=0, highlightthickness=0)
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        actions = {
            "NUEVO PROYECTO": self.new_project,
            "ABRIR PROYECTO": self.load_project,
            "GUARDAR PROYECTO": self.save_project,
            "EJECUTAR TODO": self.run_code,
            "EJECUTAR SELECCIÓN": self.run_selection,
            "DETENER": self.stop_execution,
            "BUSCAR / REEMPLAZAR": self.open_find_dialog,
            "IR A LÍNEA": self.goto_line,
            "INSPECCIONAR VARIABLES": self.inspect_variables,
            "EXPORTAR VARIABLES": self.export_variables,
            "IMPORTAR VARIABLES": self.import_variables,
            "EJEMPLOS": self.show_examples,
            "REFERENCIA DE COMANDOS": self.show_command_reference,
            "ESTADÍSTICAS": self.show_stats,
            "PANTALLA COMPLETA": self.toggle_fullscreen,
        }
        def refresh(*_):
            q = entry.get().lower()
            lb.delete(0, tk.END)
            for name in actions:
                if q in name.lower(): lb.insert(tk.END, name)
        def run(_e=None):
            sel = lb.curselection()
            if not sel: return
            name = lb.get(sel[0])
            win.destroy()
            actions[name]()
        entry.bind("<KeyRelease>", refresh)
        entry.bind("<Return>", run)
        lb.bind("<Double-Button-1>", run)
        refresh()
        entry.focus_set()

    # ============================================================
    # ARCHIVOS / AUTOGUARDADO / CONFIG
    # ============================================================
    def new_project(self):
        if messagebox.askyesno("NUEVO PROYECTO", "¿Crear un proyecto nuevo?"):
            self.code_editor.delete("1.0", tk.END)
            self.console.delete("1.0", tk.END)
            self.canvas.delete("all")
            self.current_file = None

    def save_project(self):
        if self.current_file: self._write_file(self.current_file)
        else: self.save_project_as()

    def save_project_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".ez",
            filetypes=[("Proyectos EasyScript", "*.ez"), ("Todos", "*.*")])
        if path:
            self._write_file(path)
            self._add_recent(path)

    def _write_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.code_editor.get("1.0", tk.END))
        self.current_file = path
        self.status.set(f"GUARDADO: {os.path.basename(path)}")

    def load_project(self):
        path = filedialog.askopenfilename(
            filetypes=[("Proyectos EasyScript", "*.ez"), ("Todos", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert(tk.END, content)
                self.current_file = path
                self._add_recent(path)
                self.status.set(f"CARGADO: {os.path.basename(path)}")
                self._highlight_syntax()
                self.sound.coin()
            except Exception as e:
                messagebox.showerror("ERROR", str(e))

    def _add_recent(self, path):
        if path in self.recent_files: self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:8]
        self._rebuild_recent_menu()
        self._save_config()

    def _rebuild_recent_menu(self):
        self.recent_menu.delete(0, tk.END)
        if not self.recent_files:
            self.recent_menu.add_command(label="(vacío)", state="disabled")
        for p in self.recent_files:
            self.recent_menu.add_command(label=p, command=lambda path=p: self._open_recent(path))

    def _open_recent(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert(tk.END, content)
            self.current_file = path
            self.status.set(f"CARGADO: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def _schedule_autosave(self):
        def tick():
            try:
                if self.current_file and self.code_editor.edit_modified():
                    self._write_file(self.current_file)
                    self.status.set("AUTOGUARDADO.")
            except Exception: pass
            self.autosave_id = self.root.after(AUTOSAVE_INTERVAL_MS, tick)
        self.autosave_id = self.root.after(AUTOSAVE_INTERVAL_MS, tick)

    def _load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.font_size = cfg.get("font_size", 10)
                self.tab_size = cfg.get("tab_size", 4)
                self.recent_files = cfg.get("recent_files", [])
                geo = cfg.get("geometry")
                if geo: self.root.geometry(geo)
        except Exception: pass

    def _save_config(self):
        try:
            cfg = {
                "font_size": self.font_size,
                "tab_size":  self.tab_size,
                "recent_files": self.recent_files,
                "geometry":  self.root.geometry(),
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception: pass

    def _on_close(self):
        self._save_config()
        self.interpreter.should_stop = True
        self.sound.hit()
        self.root.destroy()

    # ============================================================
    # UTILIDADES
    # ============================================================
    def ask_input(self, prompt_text):
        return simpledialog.askstring("ENTRADA EASYSCRIPT", prompt_text, parent=self.root)

    def _load_demo(self):
        demo = (
            "// ============================================\n"
            "// EZSCRIPT 8-BITS - DEMO RETRO\n"
            "// ============================================\n"
            "efecto_8bit:(\"start\")\n"
            "log_info:(\"INICIANDO SISTEMA 8-BIT...\")\n"
            "\n"
            "// --- VARIABLES ---\n"
            "var:(vidas, 3)\n"
            "var:(puntos, 0)\n"
            "incrementar:(puntos, 100)\n"
            "mostrar puntos\n"
            "\n"
            "// --- DIBUJO PIXEL ---\n"
            "color_canvas:(\"azul_osc\")\n"
            "cuadricula:(40)\n"
            "\n"
            "color:(\"rojo\")\n"
            "circulo:(60, 60, 35)\n"
            "rectangulo:(120, 25, 90, 60)\n"
            "\n"
            "color:(\"verde_lima\")\n"
            "triangulo:(230, 85, 270, 25, 310, 85)\n"
            "\n"
            "color:(\"amarillo\")\n"
            "ovalo:(30, 130, 100, 50)\n"
            "circulo:(170, 150, 25, \"rosa\")\n"
            "\n"
            "texto_canvas:(160, 210, \"EZSCRIPT 8-BITS!\", \"blanco\")\n"
            "\n"
            "// --- SONIDO CHIPTUNE ---\n"
            "chiptune:(\"do4\")\n"
            "chiptune:(\"mi4\")\n"
            "chiptune:(\"sol4\")\n"
            "chiptune:(\"do5\")\n"
            "\n"
            "// --- SISTEMA ---\n"
            "fecha\n"
            "hora\n"
            "log_info:(\"SISTEMA LISTO\")\n"
            "efecto_8bit:(\"coin\")\n"
            "\n"
            "// --- BOTÓN RETRO ---\n"
            "boton:(\"PULSA AQUI\", moneda:)\n"
            "boton:(\"POWER-UP\", powerup:)\n"
        )
        self.code_editor.insert(tk.END, demo)
        self._update_linenumbers()
        self._highlight_syntax()
        self._highlight_current_line()


EZScriptIDE = EasyScriptIDE8Bit


# ============================================================
# ENTRADA
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = EasyScriptIDE8Bit(root)
    root.mainloop()
