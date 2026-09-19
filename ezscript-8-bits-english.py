# -*- coding: utf-8 -*-
"""
EZSCRIPT 8-BITS EDITION v2.0.0 — ENGLISH
=========================================
Retro NES/Arcade-style IDE + Interpreter for the EZScript language.

RETRO FEATURES:
 ★ Authentic NES color palette
 ★ Pixelated font (Press Start 2P / Fixedsys / Courier New)
 ★ Chiptune sound engine (square waves)
 ★ Arcade boot screen "INSERT COIN / PRESS START"
 ★ Hard pixelated borders instead of modern UI
 ★ Block-based ASCII progress bar █░
 ★ New commands: pixel, sprite, chiptune, sound
 ★ Optional CRT effect (scanlines)
 ★ Full v2.0 engine with the previous 70 improvements

70 INHERITED IMPROVEMENTS (M01–M70) + NEW 8-BIT (R01–R10):
 R01 Authentic NES palette
 R02 Pixelated font
 R03 Chiptune sound engine (square waves)
 R04 Arcade boot screen
 R05 Hard pixelated borders
 R06 Block-based ASCII progress bar
 R07 CRT effect (optional scanlines)
 R08 New commands: pixel, sprite, chiptune, sound
 R09 ASCII pixel-art logo
 R10 Action sounds (click, error, success, boot)
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
import uuid as uuidlib
from datetime import datetime

# ============================================================
# AUTHENTIC NES PALETTE (R01)
# ============================================================
NES = {
    # Basics
    "black":       "#000000",
    "white":       "#FCFCFC",
    "gray":        "#BCBCBC",
    "dark_gray":   "#7C7C7C",
    "light_gray":  "#D8D8D8",
    # Reds
    "red":         "#F83800",
    "dark_red":    "#A81000",
    "light_red":   "#F87858",
    # Oranges / Browns
    "orange":      "#E45C10",
    "brown":       "#503000",
    "light_brown": "#AC7C00",
    # Yellows
    "yellow":      "#FCE0A8",
    "bright_yellow": "#F8B800",
    "gold":        "#AC7C00",
    # Greens
    "green":       "#00A800",
    "light_green": "#58D854",
    "lime":        "#B8F818",
    "dark_green":  "#005800",
    # Blues
    "blue":        "#0000FC",
    "light_blue":  "#3CBCFC",
    "dark_blue":   "#0000A8",
    "sky_blue":    "#A4E4FC",
    # Purples / Pinks
    "purple":      "#6844FC",
    "dark_purple": "#3800A8",
    "pink":        "#F878F8",
    "light_pink":  "#F8B8F8",
    # 8-bit UI
    "ui_bg":       "#0B0B1A",
    "ui_panel":    "#1A1A3E",
    "ui_border":   "#F8B800",
    "ui_border2":  "#F83800",
    "ui_text":     "#FCFCFC",
    "ui_text2":    "#F8B800",
}

# English color map for the interpreter
COLOR_MAP_EN = {
    "red": "#F83800", "blue": "#0000FC", "green": "#00A800",
    "yellow": "#F8B800", "orange": "#E45C10", "purple": "#6844FC",
    "pink": "#F878F8", "black": "#000000", "white": "#FCFCFC",
    "gray": "#BCBCBC", "grey": "#BCBCBC", "cyan": "#3CBCFC",
    "violet": "#6844FC", "brown": "#503000",
    "gold": "#F8B800", "silver": "#D8D8D8",
    "lime": "#B8F818",
    "dark_red": "#A81000", "light_red": "#F87858",
    "dark_blue": "#0000A8", "light_blue": "#3CBCFC", "sky_blue": "#A4E4FC",
    "dark_green": "#005800", "light_green": "#58D854",
    "dark_purple": "#3800A8", "light_pink": "#F8B8F8",
    "dark_gray": "#7C7C7C", "light_gray": "#D8D8D8",
    "bright_yellow": "#F8B800", "light_brown": "#AC7C00",
}

APP_NAME = "EZSCRIPT 8-BITS"
VERSION = "2.0.0"
AUTOSAVE_INTERVAL_MS = 60000
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ezscript_8bit_en_config.json")


# ============================================================
# CHIPTUNE SOUND ENGINE (R03, R10)
# ============================================================
class ChiptuneSoundBank:
    """Generates 8-bit style square waves and plays them."""

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

    # -------- Public API --------
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
        """notes = [(freq, duration_ms), ...] — plays sequentially."""
        if not self.enabled:
            return
        def worker():
            for f, d in notes:
                self.play(f, d)
                time.sleep(d / 1000.0 * 0.7)
        threading.Thread(target=worker, daemon=True).start()

    def note(self, name):
        """Plays a musical note: do, re, mi, fa, sol, la, si (with octaves)."""
        notas = {
            "c3": 262, "d3": 294, "e3": 330, "f3": 349, "g3": 392, "a3": 440, "b3": 494,
            "c4": 523, "d4": 587, "e4": 659, "f4": 698, "g4": 784, "a4": 880, "b4": 988,
            "c5": 1047, "d5": 1175, "e5": 1319,
        }
        f = notas.get(str(name).strip().lower())
        if f:
            self.play(f, 150)


# ============================================================
# EASYSCRIPT INTERPRETER (8-bit version)
# ============================================================
class EZScriptEnglishInterpreter:
    COMMANDS = [
        "AI:", "OperatingSystem:", "JS:", "HTML:", "CSS:", "JSON:", "ICON:",
        "line:", "connect:", "color:", "clear_screen", "show", "print",
        "button:", "var:", "DEFINE_VARIABLE:", "increment:", "decrement:",
        "input:", "uppercase:", "lowercase:", "length:", "replace:",
        "data_type:", "concat:", "random:", "sqrt:", "power:", "round:",
        "abs:", "sin:", "cos:", "max:", "min:", "pi:", "rectangle:",
        "circle:", "oval:", "triangle:", "canvas_text:", "canvas_color:",
        "line_width:", "clear_canvas", "polygon:", "arc:", "grid:",
        "date", "time", "wait:", "alert:", "confirm:", "open_url:",
        "copy:", "notification:", "beep", "run_cmd:", "ai_summarize:",
        "ai_translate:", "ai_explain:", "create_file:", "read_file:",
        "json_get:", "html_title:", "css_theme:", "js_eval:", "stop",
        "clear_console", "current_time", "date_time",
        "to_number:", "to_text:", "join:", "split_text:", "index:",
        "reverse:", "sort:", "count:",
        "add:", "subtract:", "multiply:", "divide:", "modulo:",
        "equal_to:", "greater_than:", "less_than:", "and:", "or:", "not:",
        "rgb:", "file_exists:", "delete_file:", "list_files:",
        "uuid:", "log_info:", "log_warn:", "log_error:", "beep:",
        "wait_key", "loop:", "while:", "if:", "else:", "end_if", "end_loop",
        # New 8-bit (R08)
        "pixel:", "sprite:", "chiptune:", "sound:", "note:",
        "sfx_8bit:", "coin:", "powerup:", "success:", "error_8bit:",
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
        self.current_draw_color = NES["blue"]
        self.COLOR_MAP = COLOR_MAP_EN
        self.show_timestamps = False
        self.execution_start = None
        self.execution_time = 0.0
        self.executed_lines = 0
        self.last_error_line = None
        self.sound = getattr(app, "sound", None)
        self._setup_console_tags()

    def _setup_console_tags(self):
        try:
            self.output.tag_config("info",    foreground=NES["white"])
            self.output.tag_config("error",   foreground=NES["red"])
            self.output.tag_config("warn",    foreground=NES["bright_yellow"])
            self.output.tag_config("success", foreground=NES["light_green"])
            self.output.tag_config("dim",     foreground=NES["dark_gray"])
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

    def log_info(self, t):    self.log(f"> {t}", "info")
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
                problems.append((idx, "Unbalanced parentheses"))
            if line.count("[") != line.count("]"):
                problems.append((idx, "Unbalanced brackets"))
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*:', line)
            if m:
                cmd = m.group(1) + ":"
                if not any(c.startswith(cmd) for c in self.COMMANDS):
                    problems.append((idx, f"Unknown command: {cmd}"))
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
                self.log_error(f"Error on line {line_num}: {e}")
                if self.sound: self.sound.error()
                if self.app:
                    self.app.highlight_error_line(line_num)
            i += 1

    def _execute_line(self, line, line_num):
        # ============ BASE COMMANDS ============
        if line.startswith("AI:"):
            m = re.match(r'AI:\s*\((.*?)\)', line)
            if m: self.log_info(f"AI <- '{self.eval_expr(m.group(1))}'")

        elif line.startswith("OperatingSystem:"):
            m = re.match(r'OperatingSystem:\s*\((.*?)\)', line)
            if m:
                tgt = str(self.eval_expr(m.group(1))).strip()
                if tgt in ["Windows", "macOS", "Linux"]:
                    self.emulated_os = tgt
                    self.log_info(f"Emulated OS: {self.emulated_os}")

        elif line.startswith("JS:"):    self.log(f"[JS] {line[3:].strip()}")
        elif line.startswith("HTML:"):  self.log(f"[HTML] {line[5:].strip()}")
        elif line.startswith("CSS:"):   self.log(f"[CSS] {line[4:].strip()}")
        elif line.startswith("JSON:"):
            try: self.log(f"[JSON] {json.loads(line[5:].strip())}")
            except Exception as e: self.log_warn(f"Invalid JSON L{line_num}: {e}")
        elif line.startswith("ICON:"): self.log(f"[Icon] {line[5:].strip()}")

        elif line.startswith("line:"):
            m = re.match(r'line:\s*\((.*?)\)', line)
            if m:
                args = [a.strip() for a in m.group(1).split(',')]
                if len(args) >= 4:
                    x1 = self._safe_int(self.eval_expr(args[0]))
                    y1 = self._safe_int(self.eval_expr(args[1]))
                    x2 = self._safe_int(self.eval_expr(args[2]))
                    y2 = self._safe_int(self.eval_expr(args[3]))
                    col = self.get_color(self.eval_expr(args[4])) if len(args) > 4 else self.current_draw_color
                    self.canvas.create_line(x1, y1, x2, y2, fill=col, width=self.current_line_width)

        elif line.startswith("connect:"):
            m = re.match(r'connect:\s*\((.*?)\)', line)
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

        elif line == "clear_screen":
            self.output.delete("1.0", tk.END)
            self.canvas.delete("all")
            self.text_positions.clear()

        elif line == "clear_console":
            self.output.delete("1.0", tk.END)

        elif line.startswith("show ") or line.startswith("print "):
            self.log(self.eval_expr(line.split(" ", 1)[1]))

        elif line.startswith("button:"):
            content = line[len("button:"):].strip()
            if content.startswith("(") and content.endswith(")"): content = content[1:-1]
            parts = content.split(",", 1)
            txt = str(self.eval_expr(parts[0]))
            action = parts[1].strip() if len(parts) > 1 else ""
            btn = tk.Button(
                self.output, text=txt, bg=NES["red"], fg=NES["white"],
                activebackground=NES["bright_yellow"], activeforeground=NES["black"],
                font=(getattr(self.app, "pixel_font_family", "Courier New"), 9, "bold"),
                relief=tk.RAISED, bd=3, padx=6, pady=2,
                command=lambda c=action: self.execute_inline(c)
            )
            self.output.window_create(tk.END, window=btn)
            self.output.insert(tk.END, "\n")

        # ============ VARIABLES AND STRINGS ============
        elif line.startswith("var:") or line.startswith("DEFINE_VARIABLE:"):
            m = re.match(r'(?:var|DEFINE_VARIABLE):\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = self.eval_expr(m.group(2))

        elif line.startswith("increment:"):
            m = re.match(r'increment:\s*\((.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = self.variables.get(k, 0) + self._safe_int(self.eval_expr(m.group(2)), 1)

        elif line.startswith("decrement:"):
            m = re.match(r'decrement:\s*\((.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = self.variables.get(k, 0) - self._safe_int(self.eval_expr(m.group(2)), 1)

        elif line.startswith("input:"):
            m = re.match(r'input:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    self.app.ask_input(str(self.eval_expr(m.group(2)))) or ""

        elif line.startswith("uppercase:"):
            m = re.match(r'uppercase:\s*\((.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k, "")).upper()

        elif line.startswith("lowercase:"):
            m = re.match(r'lowercase:\s*\((.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k, "")).lower()

        elif line.startswith("length:"):
            m = re.match(r'length:\s*\((.*?)\)', line)
            if m: self.log(f"Length: {len(str(self.eval_expr(m.group(1))))}")

        elif line.startswith("replace:"):
            m = re.match(r'replace:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k, "")).replace(
                    str(self.eval_expr(m.group(2))), str(self.eval_expr(m.group(3))))

        elif line.startswith("data_type:"):
            m = re.match(r'data_type:\s*\((.*?)\)', line)
            if m: self.log(f"Type: {type(self.eval_expr(m.group(1))).__name__}")

        elif line.startswith("concat:"):
            m = re.match(r'concat:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

        elif line.startswith("to_number:"):
            m = re.match(r'to_number:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2)))
                except Exception: self.variables[m.group(1).strip()] = 0

        elif line.startswith("to_text:"):
            m = re.match(r'to_text:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2)))

        elif line.startswith("join:"):
            m = re.match(r'join:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

        elif line.startswith("split_text:"):
            m = re.match(r'split_text:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2))).split(str(self.eval_expr(m.group(3))))

        elif line.startswith("index:"):
            m = re.match(r'index:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                lst = self.eval_expr(m.group(2)); idx = self._safe_int(self.eval_expr(m.group(3)))
                try: self.variables[m.group(1).strip()] = lst[idx]
                except Exception: self.variables[m.group(1).strip()] = ""

        elif line.startswith("reverse:"):
            m = re.match(r'reverse:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2)))[::-1]

        elif line.startswith("sort:"):
            m = re.match(r'sort:\s*\((.*?),(.*?)\)', line)
            if m:
                v = self.eval_expr(m.group(2))
                try: self.variables[m.group(1).strip()] = sorted(v)
                except Exception: self.variables[m.group(1).strip()] = v

        elif line.startswith("count:"):
            m = re.match(r'count:\s*\((.*?)\)', line)
            if m: self.log(f"Count: {len(str(self.eval_expr(m.group(1))))}")

        # ============ MATHEMATICS ============
        elif line.startswith("random:"):
            m = re.match(r'random:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = random.randint(
                    self._safe_int(self.eval_expr(m.group(2))), self._safe_int(self.eval_expr(m.group(3))))

        elif line.startswith("sqrt:"):
            m = re.match(r'sqrt:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = math.sqrt(float(self.eval_expr(m.group(2))))
                except Exception: self.variables[m.group(1).strip()] = 0

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

        elif line.startswith("add:"):
            m = re.match(r'add:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) + float(self.eval_expr(m.group(3)))
        elif line.startswith("subtract:"):
            m = re.match(r'subtract:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) - float(self.eval_expr(m.group(3)))
        elif line.startswith("multiply:"):
            m = re.match(r'multiply:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) * float(self.eval_expr(m.group(3)))
        elif line.startswith("divide:"):
            m = re.match(r'divide:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) / float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = 0
        elif line.startswith("modulo:"):
            m = re.match(r'modulo:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) % float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = 0

        elif line.startswith("equal_to:"):
            m = re.match(r'equal_to:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = (str(self.eval_expr(m.group(2))) == str(self.eval_expr(m.group(3))))
        elif line.startswith("greater_than:"):
            m = re.match(r'greater_than:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) > float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = False
        elif line.startswith("less_than:"):
            m = re.match(r'less_than:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) < float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = False
        elif line.startswith("and:"):
            m = re.match(r'and:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) and bool(self.eval_expr(m.group(3)))
        elif line.startswith("or:"):
            m = re.match(r'or:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) or bool(self.eval_expr(m.group(3)))
        elif line.startswith("not:"):
            m = re.match(r'not:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = not bool(self.eval_expr(m.group(2)))

        # ============ DRAWING ============
        elif line.startswith("rectangle:"):
            m = re.match(r'rectangle:\s*\((.*?)\)', line)
            if m:
                args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                x, y = self._safe_int(args[0]), self._safe_int(args[1])
                w, h = self._safe_int(args[2]), self._safe_int(args[3])
                c = self.get_color(args[4]) if len(args) > 4 else self.current_draw_color
                self.canvas.create_rectangle(x, y, x + w, y + h, fill=c, outline="")

        elif line.startswith("circle:"):
            m = re.match(r'circle:\s*\((.*?)\)', line)
            if m:
                args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                x, y = self._safe_int(args[0]), self._safe_int(args[1])
                r = self._safe_int(args[2])
                c = self.get_color(args[3]) if len(args) > 3 else self.current_draw_color
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=c, outline="")

        elif line.startswith("oval:"):
            m = re.match(r'oval:\s*\((.*?)\)', line)
            if m:
                args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                x, y = self._safe_int(args[0]), self._safe_int(args[1])
                w, h = self._safe_int(args[2]), self._safe_int(args[3])
                c = self.get_color(args[4]) if len(args) > 4 else self.current_draw_color
                self.canvas.create_oval(x, y, x + w, y + h, fill=c, outline="")

        elif line.startswith("triangle:"):
            m = re.match(r'triangle:\s*\((.*?)\)', line)
            if m:
                args = [self.eval_expr(a.strip()) for a in m.group(1).split(',')]
                pts = [self._safe_int(args[i]) for i in range(6)]
                c = self.get_color(args[6]) if len(args) > 6 else self.current_draw_color
                self.canvas.create_polygon(pts, fill=c, outline="")

        elif line.startswith("canvas_text:"):
            m = re.match(r'canvas_text:\s*\((.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                x = self._safe_int(self.eval_expr(m.group(1)))
                y = self._safe_int(self.eval_expr(m.group(2)))
                txt = self.eval_expr(m.group(3))
                c = self.get_color(self.eval_expr(m.group(4))) if m.group(4) else self.current_draw_color
                self.canvas.create_text(x, y, text=str(txt), fill=c,
                                        font=(getattr(self.app, "pixel_font_family", "Courier New"), 10, "bold"))

        elif line.startswith("canvas_color:"):
            m = re.match(r'canvas_color:\s*\((.*?)\)', line)
            if m: self.canvas.config(bg=self.get_color(self.eval_expr(m.group(1))))

        elif line.startswith("line_width:"):
            m = re.match(r'line_width:\s*\((.*?)\)', line)
            if m: self.current_line_width = self._safe_int(self.eval_expr(m.group(1)), 1)

        elif line == "clear_canvas": self.canvas.delete("all")

        elif line.startswith("polygon:"):
            m = re.match(r'polygon:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                vals = [self._safe_int(self.eval_expr(x)) for x in m.groups()[:6]]
                c = self.get_color(self.eval_expr(m.group(7))) if m.group(7) else self.current_draw_color
                self.canvas.create_polygon(vals, fill=c, outline="")

        elif line.startswith("arc:"):
            m = re.match(r'arc:\s*\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                vals = [self._safe_int(self.eval_expr(x)) for x in m.groups()[:6]]
                c = self.get_color(self.eval_expr(m.group(7))) if m.group(7) else self.current_draw_color
                self.canvas.create_arc(vals[0], vals[1], vals[2], vals[3], start=vals[4], extent=vals[5], fill=c)

        elif line.startswith("grid:"):
            m = re.match(r'grid:\s*\((.*?)\)', line)
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

        # ============ 8-BIT EXCLUSIVES (R08) ============
        elif line.startswith("pixel:"):
            m = re.match(r'pixel:\s*\((.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                x = self._safe_int(self.eval_expr(m.group(1)))
                y = self._safe_int(self.eval_expr(m.group(2)))
                size = self._safe_int(self.eval_expr(m.group(3)), 4) if m.group(3) else 4
                c = self.current_draw_color
                self.canvas.create_rectangle(x, y, x + size, y + size, fill=c, outline="")

        elif line.startswith("sprite:"):
            # sprite:(x, y, "rows;cols;c0=red,c1=blue;00110011...", pixel_size)
            m = re.match(r'sprite:\s*\((.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                x0 = self._safe_int(self.eval_expr(m.group(1)))
                y0 = self._safe_int(self.eval_expr(m.group(2)))
                data = str(self.eval_expr(m.group(3)))
                scale = max(1, self._safe_int(self.eval_expr(m.group(4)), 4))
                # Format: "rows;cols;c0=color1,c1=color2;00110011..."
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
                    self.log_warn(f"Invalid sprite: {e}")

        elif line.startswith("chiptune:"):
            m = re.match(r'chiptune:\s*\((.*?)\)', line)
            if m and self.sound:
                note = str(self.eval_expr(m.group(1))).strip()
                self.sound.note(note)

        elif line.startswith("sound:"):
            m = re.match(r'sound:\s*\((.*?)(?:,(.*?))?\)', line)
            if m and self.sound:
                freq = self._safe_int(self.eval_expr(m.group(1)), 880)
                dur = self._safe_int(self.eval_expr(m.group(2)), 50) if m.group(2) else 50
                self.sound.play(freq, dur)

        elif line.startswith("sfx_8bit:"):
            m = re.match(r'sfx_8bit:\s*\((.*?)\)', line)
            if m and self.sound:
                name = str(self.eval_expr(m.group(1))).strip().lower()
                fn = getattr(self.sound, name, None)
                if callable(fn): fn()

        elif line.startswith("coin:"):
            if self.sound: self.sound.coin()
        elif line.startswith("powerup:"):
            if self.sound: self.sound.powerup()
        elif line.startswith("success:"):
            if self.sound: self.sound.success()
        elif line.startswith("error_8bit:"):
            if self.sound: self.sound.error()

        # ============ SYSTEM ============
        elif line == "date": self.log(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        elif line == "time": self.log(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        elif line == "current_time": self.log(f"{datetime.now().strftime('%H:%M:%S')}")
        elif line == "date_time": self.log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        elif line.startswith("wait:"):
            m = re.match(r'wait:\s*\((.*?)\)', line)
            if m:
                try: t = float(self.eval_expr(m.group(1)))
                except Exception: t = 0
                end = time.time() + t
                while time.time() < end and not self.should_stop:
                    time.sleep(0.02)
                    try: self.output.update()
                    except Exception: pass

        elif line.startswith("alert:"):
            m = re.match(r'alert:\s*\((.*?)\)', line)
            if m: messagebox.showinfo("ALERT", str(self.eval_expr(m.group(1))))

        elif line.startswith("confirm:"):
            m = re.match(r'confirm:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = messagebox.askyesno("CONFIRM", str(self.eval_expr(m.group(2))))

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
            if m: self.log(f"[{self.eval_expr(m.group(1))}] {self.eval_expr(m.group(2))}")

        elif line == "beep":
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

        elif line.startswith("run_cmd:"):
            m = re.match(r'run_cmd:\s*\((.*?)\)', line)
            if m: self.log(f"CMD (simulated): '{self.eval_expr(m.group(1))}'")

        elif line.startswith("log_info:"):
            m = re.match(r'log_info:\s*\((.*?)\)', line)
            if m: self.log_info(self.eval_expr(m.group(1)))
        elif line.startswith("log_warn:"):
            m = re.match(r'log_warn:\s*\((.*?)\)', line)
            if m: self.log_warn(self.eval_expr(m.group(1)))
        elif line.startswith("log_error:"):
            m = re.match(r'log_error:\s*\((.*?)\)', line)
            if m: self.log_error(self.eval_expr(m.group(1)))

        elif line == "wait_key":
            messagebox.showinfo("EZSCRIPT", "Press OK to continue")

        elif line.startswith("uuid:"):
            m = re.match(r'uuid:\s*\((.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(uuidlib.uuid4())

        # ============ AI, WEB & FILES ============
        elif line.startswith("ai_summarize:"):
            m = re.match(r'ai_summarize:\s*\((.*?)\)', line)
            if m: self.log(f"[AI Summary] {str(self.eval_expr(m.group(1)))[:60]}...")

        elif line.startswith("ai_translate:"):
            m = re.match(r'ai_translate:\s*\((.*?),(.*?)\)', line)
            if m: self.log(f"[AI Translated to {self.eval_expr(m.group(2))}] {self.eval_expr(m.group(1))}")

        elif line.startswith("ai_explain:"):
            m = re.match(r'ai_explain:\s*\((.*?)\)', line)
            if m: self.log("[AI Explanation] Analysis completed.")

        elif line.startswith("create_file:"):
            m = re.match(r'create_file:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    with open(self.eval_expr(m.group(1)), "w", encoding="utf-8") as f:
                        f.write(str(self.eval_expr(m.group(2))))
                    self.log_success(f"File created: {self.eval_expr(m.group(1))}")
                except Exception as e:
                    self.log_error(str(e))

        elif line.startswith("read_file:"):
            m = re.match(r'read_file:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    with open(self.eval_expr(m.group(2)), "r", encoding="utf-8") as f:
                        self.variables[m.group(1).strip()] = f.read()
                except Exception as e:
                    self.log_error(f"Read error: {e}")

        elif line.startswith("json_get:"):
            m = re.match(r'json_get:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    j = self.eval_expr(m.group(2))
                    data = json.loads(j) if isinstance(j, str) else j
                    self.variables[m.group(1).strip()] = data.get(self.eval_expr(m.group(3)), "")
                except Exception as e:
                    self.log_warn(str(e))

        elif line.startswith("file_exists:"):
            m = re.match(r'file_exists:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = os.path.exists(str(self.eval_expr(m.group(2))))
        elif line.startswith("delete_file:"):
            m = re.match(r'delete_file:\s*\((.*?)\)', line)
            if m:
                try: os.remove(str(self.eval_expr(m.group(1))))
                except Exception as e: self.log_error(str(e))
        elif line.startswith("list_files:"):
            m = re.match(r'list_files:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = os.listdir(str(self.eval_expr(m.group(2))))
                except Exception as e: self.log_error(str(e))

        elif line.startswith("html_title:"):
            m = re.match(r'html_title:\s*\((.*?)\)', line)
            if m: self.log(f"<title>{self.eval_expr(m.group(1))}</title>")

        elif line.startswith("css_theme:"):
            m = re.match(r'css_theme:\s*\((.*?)\)', line)
            if m:
                v = str(self.eval_expr(m.group(1))).lower()
                bg = NES["ui_bg"] if v == "dark" else NES["white"]
                fg = NES["white"] if v == "dark" else NES["black"]
                self.output.config(bg=bg, fg=fg)
                self.canvas.config(bg=bg)

        elif line.startswith("js_eval:"):
            m = re.match(r'js_eval:\s*\((.*?)\)', line)
            if m: self.log(f"[JS] {self.eval_expr(m.group(1))}")

        elif line == "stop":
            self.should_stop = True
            self.log_warn("Execution stopped.")

        else:
            if ":" in line and not line.startswith("//"):
                self.log_warn(f"Unknown command L{line_num}: {line}")

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
        self.output.config(bg=NES["ui_bg"], fg=NES["white"])
        self.canvas.config(bg=NES["ui_bg"])
        self.current_draw_color = NES["blue"]

        if self.sound: self.sound.start()
        self.execution_start = time.time()
        raw_lines = code.split('\n')
        structured = [{'num': i + 1, 'text': l} for i, l in enumerate(raw_lines)]
        self.run_block(structured)
        self.execution_time = time.time() - self.execution_start

        self.log("", "info")
        self.log_success(
            f"END IN {self.execution_time:.3f}s · {self.executed_lines} lines · {len(self.variables)} variables"
        )
        if self.sound: self.sound.success()
        if self.app:
            self.app.on_execution_finished(self.execution_time, self.executed_lines)


EZScriptInterpreter = EZScriptEnglishInterpreter


# ============================================================
# ARCADE BOOT SCREEN (R04)
# ============================================================
class BootScreen:
    def __init__(self, root, sound, on_done):
        self.root = root
        self.sound = sound
        self.on_done = on_done

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.configure(bg=NES["black"])
        w, h = 640, 480
        sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
        x = (sw - w) // 2; y = (sh - h) // 2
        self.win.geometry(f"{w}x{h}+{x}+{y}")

        self.canvas = tk.Canvas(self.win, width=w, height=h, bg=NES["black"], highlightthickness=0)
        self.canvas.pack()

        # Pixelated outer border
        for i in range(0, w, 8):
            self.canvas.create_rectangle(i, 0, i+4, 4, fill=NES["red"], outline="")
            self.canvas.create_rectangle(i, h-4, i+4, h, fill=NES["red"], outline="")
        for j in range(0, h, 8):
            self.canvas.create_rectangle(0, j, 4, j+4, fill=NES["red"], outline="")
            self.canvas.create_rectangle(w-4, j, w, j+4, fill=NES["red"], outline="")

        # ASCII pixel-art logo (R09)
        logo = [
            "  ███████ ███████ ███████  ██████ ██████ ██ ██████  ███████ ",
            "  ██         ██      ██   ██      ██  ██ ██ ██  ██     ██  ",
            "  █████      ██      ██   ██████  ██████ ██ ██████     ██  ",
            "  ██         ██      ██        ██ ██     ██ ██         ██  ",
            "  ███████    ██      ██   ██████  ██     ██ ██         ██  ",
        ]
        for i, line in enumerate(logo):
            self.canvas.create_text(w//2, 100 + i*26, text=line,
                                    fill=NES["bright_yellow"],
                                    font=(getattr(root, "pixel_font_family", "Courier New"), 14, "bold"),
                                    anchor="center")

        self.canvas.create_text(w//2, 280, text="8-BITS EDITION",
                                fill=NES["light_green"],
                                font=(getattr(root, "pixel_font_family", "Courier New"), 18, "bold"))

        self.canvas.create_text(w//2, 320, text=f"v{VERSION}",
                                fill=NES["light_gray"],
                                font=(getattr(root, "pixel_font_family", "Courier New"), 10, "bold"))

        # Blinking "PRESS START"
        self.press = self.canvas.create_text(w//2, 390, text="PRESS START",
                                            fill=NES["red"],
                                            font=(getattr(root, "pixel_font_family", "Courier New"), 16, "bold"))
        self.canvas.create_text(w//2, 430, text="(click or press any key)",
                                fill=NES["dark_gray"],
                                font=(getattr(root, "pixel_font_family", "Courier New"), 8))

        # Block loading bar
        self.bar_y = 355
        self.bar_blocks = self.canvas.create_text(w//2, self.bar_y, text="",
                                                  fill=NES["bright_yellow"],
                                                  font=(getattr(root, "pixel_font_family", "Courier New"), 12, "bold"))
        self._blink_state = True
        self._bar_fill = 0
        self._blink()

        # Boot sound
        self.sound.boot()

        # Events
        self.win.bind("<Key>", lambda e: self._finish())
        self.win.bind("<Button-1>", lambda e: self._finish())
        self.canvas.bind("<Button-1>", lambda e: self._finish())

    def _blink(self):
        if not self.win.winfo_exists(): return
        self._blink_state = not self._blink_state
        try:
            self.canvas.itemconfig(self.press,
                                   fill=NES["red"] if self._blink_state else NES["ui_bg"])
        except Exception:
            return
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
# 8-BIT IDE
# ============================================================
class EZScriptEnglishIDE8Bit:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1120x840")
        self.root.configure(bg=NES["black"])

        # Pixel font detection (R02)
        self.pixel_font_family = self._pick_pixel_font()
        root.pixel_font_family = self.pixel_font_family

        # State
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

        # Sound engine (R03)
        self.sound = ChiptuneSoundBank(root)

        # Load config
        self._load_config()

        # Fonts
        self.editor_font   = tkfont.Font(family=self.font_family, size=self.font_size, weight="bold")
        self.console_font  = tkfont.Font(family=self.font_family, size=max(9, self.font_size - 1))
        self.linenum_font  = tkfont.Font(family=self.font_family, size=max(9, self.font_size - 1))

        # Build (hidden until boot screen finishes)
        self.root.withdraw()

        self._build_menu()
        self._build_toolbar()
        self._build_editor_area()
        self._build_output_area()
        self._build_statusbar()

        # Interpreter
        self.interpreter = EZScriptEnglishInterpreter(self.console, self.canvas, self)

        self._bind_shortcuts()
        self._build_context_menu()
        self._load_demo()
        self._schedule_autosave()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Arcade boot screen
        BootScreen(self.root, self.sound, self._after_boot)

    def _pick_pixel_font(self):
        """Picks the best pixelated font available (R02)."""
        available = set(tkfont.families())
        candidates = [
            "Press Start 2P", "PressStart2P", "Pixel Emulator", "Silkscreen",
            "Fixedsys", "Terminal", "MS Sans Serif", "Small Fonts",
            "Courier New", "Consolas", "Monaco",
        ]
        for c in candidates:
            if c in available:
                return c
        return "Courier New"

    def _after_boot(self):
        self.root.deiconify()
        self.status.set("READY! PRESS F5 TO RUN")
        self.sound.click()

    # ============================================================
    # UI CONSTRUCTION (R05 — hard pixelated borders)
    # ============================================================
    def _pixel_frame(self, parent, bg=None):
        outer = tk.Frame(parent, bg=NES["ui_border"], bd=0)
        inner = tk.Frame(outer, bg=bg or NES["ui_panel"], bd=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        return outer, inner

    def _build_menu(self):
        menubar = tk.Menu(self.root,
                          bg=NES["ui_panel"], fg=NES["ui_text"],
                          activebackground=NES["red"], activeforeground=NES["white"],
                          bd=0, relief=tk.FLAT,
                          font=(self.font_family, 9, "bold"))

        m_file = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_text"],
                         activebackground=NES["red"], activeforeground=NES["white"],
                         font=(self.font_family, 9, "bold"))
        m_file.add_command(label="NEW",              accelerator="Ctrl+N", command=self.new_project)
        m_file.add_command(label="OPEN...",          accelerator="Ctrl+O", command=self.load_project)
        m_file.add_command(label="SAVE",             accelerator="Ctrl+S", command=self.save_project)
        m_file.add_command(label="SAVE AS...",       accelerator="Ctrl+Shift+S", command=self.save_project_as)
        m_file.add_separator()
        m_file.add_command(label="SAVE CONSOLE...",  command=self.save_console)
        m_file.add_command(label="SAVE CANVAS (PS)...", command=self.save_canvas_ps)
        m_file.add_separator()
        self.recent_menu = tk.Menu(m_file, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_text"],
                                   font=(self.font_family, 9, "bold"))
        m_file.add_cascade(label="RECENT", menu=self.recent_menu)
        self._rebuild_recent_menu()
        m_file.add_separator()
        m_file.add_command(label="EXIT", command=self._on_close)
        menubar.add_cascade(label="FILE", menu=m_file)

        m_edit = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_text"],
                         font=(self.font_family, 9, "bold"))
        m_edit.add_command(label="UNDO",  accelerator="Ctrl+Z", command=lambda: self.code_editor.event_generate("<<Undo>>"))
        m_edit.add_command(label="REDO",  accelerator="Ctrl+Y", command=lambda: self.code_editor.event_generate("<<Redo>>"))
        m_edit.add_separator()
        m_edit.add_command(label="FIND / REPLACE", accelerator="Ctrl+F", command=self.open_find_dialog)
        m_edit.add_command(label="GO TO LINE...",  accelerator="Ctrl+G", command=self.goto_line)
        m_edit.add_separator()
        m_edit.add_command(label="DUPLICATE LINE", accelerator="Ctrl+D", command=self.duplicate_line)
        m_edit.add_command(label="COMMENT",        accelerator="Ctrl+/", command=self.toggle_comment)
        m_edit.add_command(label="INDENT",         accelerator="Tab", command=lambda: self.indent_selection(True))
        m_edit.add_command(label="DEDENT",         accelerator="Shift+Tab", command=lambda: self.indent_selection(False))
        m_edit.add_separator()
        m_edit.add_command(label="COMMAND PALETTE", accelerator="Ctrl+Shift+P", command=self.open_command_palette)
        m_edit.add_command(label="AUTOCOMPLETE",    accelerator="Ctrl+Space", command=self.autocomplete)
        m_edit.add_separator()
        m_edit.add_command(label="INSPECT VARIABLES", command=self.inspect_variables)
        m_edit.add_command(label="EXPORT VARIABLES (JSON)", command=self.export_variables)
        m_edit.add_command(label="IMPORT VARIABLES (JSON)", command=self.import_variables)
        menubar.add_cascade(label="EDIT", menu=m_edit)

        m_view = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_text"],
                         font=(self.font_family, 9, "bold"))
        m_view.add_command(label="FONT +", command=lambda: self.change_font_size(+1))
        m_view.add_command(label="FONT -", command=lambda: self.change_font_size(-1))
        m_view.add_command(label="FONT RESET", command=self.reset_font_size)
        m_view.add_separator()
        self.var_wrap = tk.BooleanVar(value=self.word_wrap)
        m_view.add_checkbutton(label="WORD WRAP", variable=self.var_wrap, command=self.toggle_wrap)
        self.var_ts = tk.BooleanVar(value=False)
        m_view.add_checkbutton(label="CONSOLE TIMESTAMPS", variable=self.var_ts, command=self.toggle_timestamps)
        self.var_snd = tk.BooleanVar(value=True)
        m_view.add_checkbutton(label="CHIPTUNE SOUND", variable=self.var_snd, command=self.toggle_sound)
        m_view.add_separator()
        m_view.add_command(label="FULLSCREEN", accelerator="F11", command=self.toggle_fullscreen)
        menubar.add_cascade(label="VIEW", menu=m_view)

        m_run = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_text"],
                        font=(self.font_family, 9, "bold"))
        m_run.add_command(label="RUN ALL", accelerator="F5", command=self.run_code)
        m_run.add_command(label="RUN SELECTION", accelerator="F6", command=self.run_selection)
        m_run.add_command(label="RUN FROM CURSOR", accelerator="Ctrl+F5", command=self.run_from_cursor)
        m_run.add_command(label="VALIDATE SYNTAX", accelerator="Ctrl+Shift+V", command=self.validate_syntax)
        m_run.add_separator()
        m_run.add_command(label="STOP", accelerator="Esc", command=self.stop_execution)
        m_run.add_separator()
        m_run.add_command(label="CLEAR CONSOLE", command=lambda: self.console.delete("1.0", tk.END))
        m_run.add_command(label="CLEAR CANVAS",  command=lambda: self.canvas.delete("all"))
        m_run.add_command(label="COPY CONSOLE",  command=self.copy_console)
        menubar.add_cascade(label="RUN", menu=m_run)

        m_help = tk.Menu(menubar, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_text"],
                         font=(self.font_family, 9, "bold"))
        m_help.add_command(label="COMMAND REFERENCE", command=self.show_command_reference)
        m_help.add_command(label="EXAMPLES LIBRARY",  command=self.show_examples)
        m_help.add_command(label="QUICK TEMPLATES",   command=self.show_templates)
        m_help.add_separator()
        m_help.add_command(label="STATISTICS", command=self.show_stats)
        m_help.add_command(label="ABOUT...", command=self.show_about)
        menubar.add_cascade(label="HELP", menu=m_help)

        self.root.config(menu=menubar)

    def _build_toolbar(self):
        outer, inner = self._pixel_frame(self.root, bg=NES["ui_panel"])
        outer.pack(side=tk.TOP, fill=tk.X, padx=6, pady=(6, 3))

        def add_btn(txt, color, cmd):
            b = tk.Button(inner, text=txt, bg=color, fg=NES["white"],
                          activebackground=NES["bright_yellow"], activeforeground=NES["black"],
                          font=(self.font_family, 9, "bold"),
                          command=lambda: (self.sound.click(), cmd()),
                          relief=tk.RAISED, bd=3, padx=8, pady=3)
            b.pack(side=tk.LEFT, padx=2, pady=4)
            return b

        add_btn("NEW",     NES["blue"],       self.new_project)
        add_btn("OPEN",    NES["orange"],     self.load_project)
        add_btn("SAVE",    NES["green"],      self.save_project)
        add_btn("RUN",     NES["red"],        self.run_code)
        add_btn("STOP",    NES["purple"],     self.stop_execution)
        add_btn("CLEAR",   NES["light_brown"], lambda: self.console.delete("1.0", tk.END))
        add_btn("HELP",    NES["dark_gray"],  self.show_command_reference)

        # Block-based progress bar (R06)
        self.progress_lbl = tk.Label(inner, text="", bg=NES["ui_panel"], fg=NES["bright_yellow"],
                                     font=(self.font_family, 10, "bold"))
        self.progress_lbl.pack(side=tk.RIGHT, padx=8)
        self._progress_anim = False

    def _build_editor_area(self):
        outer, inner = self._pixel_frame(self.root, bg=NES["ui_panel"])
        outer.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)

        # Line numbers
        self.linenumbers = tk.Text(inner, width=4, padx=4, takefocus=0, border=0,
                                   background=NES["ui_bg"], foreground=NES["dark_gray"],
                                   font=self.linenum_font, state="disabled")
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        self.code_editor = tk.Text(inner, font=self.editor_font, undo=True,
                                   wrap=tk.NONE, tabs=f"{{{self.tab_size}c}}",
                                   bg=NES["ui_bg"], fg=NES["white"],
                                   insertbackground=NES["bright_yellow"],
                                   insertwidth=8,
                                   selectbackground=NES["blue"],
                                   selectforeground=NES["white"],
                                   bd=0, highlightthickness=0)
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code_editor.bind("<<Modified>>", self._on_modified)
        self.code_editor.bind("<KeyRelease>", self._on_key_release)
        self.code_editor.bind("<Button-1>", self._on_click)
        self.code_editor.bind("<MouseWheel>", self._on_mousewheel)

        sb = tk.Scrollbar(inner, command=self._on_scroll, orient="vertical",
                          bg=NES["ui_panel"], troughcolor=NES["ui_bg"],
                          activebackground=NES["bright_yellow"], bd=0, width=14)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_editor.config(yscrollcommand=lambda a, b: self._yscroll(a, b, sb))
        self._editor_scrollbar = sb

        self._setup_syntax_tags()

    def _build_output_area(self):
        outer, inner = self._pixel_frame(self.root, bg=NES["ui_panel"])
        outer.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        # Console
        self.console = tk.Text(inner, font=self.console_font, height=11,
                               bg=NES["ui_bg"], fg=NES["white"], width=50,
                               wrap=tk.WORD, bd=0, highlightthickness=0,
                               insertbackground=NES["bright_yellow"])
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.interpreter_console = self.console

        # Canvas (with hard border)
        canvas_frame = tk.Frame(inner, bg=NES["ui_border"], bd=0)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))
        self.canvas = tk.Canvas(canvas_frame, bg=NES["ui_bg"], highlightthickness=0,
                                width=360)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=NES["ui_panel"])
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status = tk.StringVar()
        self.status.set("SYSTEM READY. INSERT COIN.")
        self.lbl_status = tk.Label(bar, textvariable=self.status,
                                   bg=NES["ui_panel"], fg=NES["bright_yellow"],
                                   font=(self.font_family, 9, "bold"), anchor="w")
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=3)

        self.lbl_pos = tk.Label(bar, text="Ln 1, Col 1",
                                bg=NES["ui_panel"], fg=NES["white"],
                                font=(self.font_family, 9, "bold"))
        self.lbl_pos.pack(side=tk.RIGHT, padx=6)

        self.lbl_count = tk.Label(bar, text="0 L · 0 CH",
                                  bg=NES["ui_panel"], fg=NES["light_green"],
                                  font=(self.font_family, 9, "bold"))
        self.lbl_count.pack(side=tk.RIGHT, padx=6)

    # ============================================================
    # SYNTAX HIGHLIGHTING (NES colors)
    # ============================================================
    def _setup_syntax_tags(self):
        e = self.code_editor
        e.tag_configure("kw",       foreground=NES["bright_yellow"])
        e.tag_configure("string",   foreground=NES["lime"])
        e.tag_configure("comment",  foreground=NES["dark_gray"], font=(self.font_family, self.font_size, "italic"))
        e.tag_configure("number",   foreground=NES["orange"])
        e.tag_configure("color",    foreground=NES["pink"])
        e.tag_configure("errorline", background=NES["dark_red"])
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
        for c in ("red","blue","green","yellow","orange","purple","pink",
                  "black","white","gray","grey","cyan","violet","brown",
                  "gold","silver","lime",
                  "dark_red","light_red","dark_blue","light_blue","sky_blue",
                  "dark_green","light_green","dark_purple","light_pink",
                  "dark_gray","light_gray","bright_yellow","light_brown"):
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
    # SCROLL AND EVENTS
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
    # SHORTCUTS
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
    # EDITOR FUNCTIONS
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
        ln = simpledialog.askinteger("GO TO LINE", "Line number:", parent=self.root)
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
        pop.configure(bg=NES["ui_border"])
        lb = tk.Listbox(pop, height=min(10, len(items)),
                        bg=NES["ui_bg"], fg=NES["white"],
                        selectbackground=NES["red"], selectforeground=NES["white"],
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
    # FIND / REPLACE
    # ============================================================
    def open_find_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("FIND AND REPLACE")
        win.geometry("440x200")
        win.configure(bg=NES["ui_bg"])

        tk.Label(win, text="FIND:", bg=NES["ui_bg"], fg=NES["bright_yellow"],
                 font=(self.font_family, 10, "bold")).grid(row=0, column=0, sticky="e", padx=6, pady=6)
        e_find = tk.Entry(win, width=30, bg=NES["ui_bg"], fg=NES["white"],
                          insertbackground=NES["bright_yellow"],
                          font=(self.font_family, 10, "bold"))
        e_find.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(win, text="REPLACE:", bg=NES["ui_bg"], fg=NES["bright_yellow"],
                 font=(self.font_family, 10, "bold")).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        e_repl = tk.Entry(win, width=30, bg=NES["ui_bg"], fg=NES["white"],
                          insertbackground=NES["bright_yellow"],
                          font=(self.font_family, 10, "bold"))
        e_repl.grid(row=1, column=1, padx=6, pady=6)

        def mk_btn(txt, cmd):
            return tk.Button(win, text=txt, command=cmd, bg=NES["blue"], fg=NES["white"],
                             activebackground=NES["bright_yellow"], activeforeground=NES["black"],
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

        mk_btn("FIND",          find_next).grid(row=2, column=0, padx=6, pady=6)
        mk_btn("REPLACE",       replace_one).grid(row=2, column=1, padx=6, pady=6)
        mk_btn("REPLACE ALL",   replace_all).grid(row=3, column=1, padx=6, pady=6)
        e_find.focus_set()

    # ============================================================
    # FONT / VIEW
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
    # EXECUTION
    # ============================================================
    def run_code(self):
        code = self.code_editor.get("1.0", tk.END)
        self._start_execution(code)

    def run_selection(self):
        try:
            code = self.code_editor.get("sel.first", "sel.last")
            self._start_execution(code)
        except Exception:
            messagebox.showinfo("SELECTION", "Please select code first.")

    def run_from_cursor(self):
        idx = self.code_editor.index(tk.INSERT)
        code = self.code_editor.get(idx, tk.END)
        self._start_execution(code)

    def validate_syntax(self):
        code = self.code_editor.get("1.0", tk.END)
        problems = self.interpreter.validate(code)
        if not problems:
            self.sound.success()
            messagebox.showinfo("VALIDATION", "OK SYNTAX IS CORRECT.")
        else:
            self.sound.error()
            msg = "\n".join(f"L{l}: {m}" for l, m in problems)
            messagebox.showwarning("PROBLEMS DETECTED", msg)

    def _start_execution(self, code):
        if self.execution_thread and self.execution_thread.is_alive():
            messagebox.showinfo("EXECUTION", "An execution is already running.")
            return
        self.code_editor.tag_remove("errorline", "1.0", tk.END)
        self.status.set("RUNNING...")
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
        self.progress_lbl.config(text="LOADING " + frames[idx % 4] * 6)
        self._prog_idx = idx + 1
        self.root.after(120, self._animate_progress)

    def _on_execution_done(self):
        self._progress_anim = False
        self.progress_lbl.config(text="")
        self.status.set("READY.")

    def on_execution_finished(self, secs, lines):
        self.status.set(f"OK {lines} LINES · {secs:.3f}s")

    def stop_execution(self):
        self.interpreter.should_stop = True
        self.status.set("STOPPING...")
        self.sound.hit()

    # ============================================================
    # CONSOLE / FILES
    # ============================================================
    def copy_console(self):
        try:
            txt = self.console.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self.status.set("CONSOLE COPIED.")
        except Exception: pass

    def save_console(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text", "*.txt"), ("All Files", "*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.console.get("1.0", "end-1c"))
            self.status.set(f"CONSOLE SAVED: {os.path.basename(path)}")

    def save_canvas_ps(self):
        path = filedialog.asksaveasfilename(defaultextension=".ps",
                                            filetypes=[("PostScript", "*.ps"), ("All Files", "*.*")])
        if path:
            try:
                self.canvas.postscript(file=path)
                self.status.set(f"CANVAS SAVED: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("ERROR", str(e))

    # ============================================================
    # CONTEXT MENU
    # ============================================================
    def _build_context_menu(self):
        m = tk.Menu(self.root, tearoff=0, bg=NES["ui_panel"], fg=NES["ui_text"],
                    font=(self.font_family, 9, "bold"))
        m.add_command(label="CUT",   command=lambda: self.code_editor.event_generate("<<Cut>>"))
        m.add_command(label="COPY",  command=lambda: self.code_editor.event_generate("<<Copy>>"))
        m.add_command(label="PASTE", command=lambda: self.code_editor.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label="DUPLICATE LINE", command=self.duplicate_line)
        m.add_command(label="COMMENT",        command=self.toggle_comment)
        m.add_command(label="GO TO LINE...",  command=self.goto_line)
        m.add_separator()
        m.add_command(label="RUN SELECTION",  command=self.run_selection)
        def popup(e):
            try: m.tk_popup(e.x_root, e.y_root)
            finally: m.grab_release()
        self.code_editor.bind("<Button-3>", popup)
        self.code_editor.bind("<Button-2>", popup)

    # ============================================================
    # DIALOGS
    # ============================================================
    def show_about(self):
        self.sound.coin()
        messagebox.showinfo("ABOUT",
                            f"{APP_NAME}\nVersion {VERSION}\n\n"
                            "► Retro 8-bit IDE\n"
                            "► Font: {}\n"
                            "► Sound engine: Chiptune\n"
                            "► 70 improvements + 10 new retro".format(self.pixel_font_family))

    def show_command_reference(self):
        win = tk.Toplevel(self.root)
        win.title("COMMAND REFERENCE")
        win.geometry("700x560")
        win.configure(bg=NES["ui_bg"])
        txt = tk.Text(win, wrap=tk.WORD, font=(self.font_family, 10),
                      bg=NES["ui_bg"], fg=NES["white"], bd=0, highlightthickness=0)
        txt.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        txt.insert("1.0", self._command_reference_text())
        txt.config(state="disabled")

    def _command_reference_text(self):
        return """EZSCRIPT 8-BITS — COMMAND REFERENCE
=====================================

VARIABLES
  var:(name, value)            Define variable
  increment:(var, n)           Add n
  decrement:(var, n)           Subtract n
  input:(var, "prompt")        Ask the user

STRINGS
  uppercase / lowercase
  length / replace / concat
  to_text / to_number
  split_text / index / reverse / sort / count

MATH
  add / subtract / multiply / divide / modulo
  sqrt / power / round / abs
  sin / cos / max / min / pi

LOGIC
  equal_to / greater_than / less_than / and / or / not

DRAWING
  color:("red")                Current color
  line / rectangle / circle / oval / triangle
  polygon / arc / canvas_text / canvas_color
  line_width / grid / clear_canvas / clear_screen
  rgb:(r,g,b)                  Component colors

AVAILABLE COLORS (NES palette)
  red, blue, green, yellow, orange, purple, pink,
  black, white, gray/grey, cyan, violet, brown,
  gold, silver, lime,
  dark_red, light_red, dark_blue, light_blue, sky_blue,
  dark_green, light_green, dark_purple, light_pink,
  dark_gray, light_gray, bright_yellow, light_brown

★ EXCLUSIVE 8-BIT COMMANDS ★
  pixel:(x, y, [size])             Draw a pixel
  sprite:(x, y, "rows;cols;c0=red,c1=blue;00110011", scale)
                                    Draw bitmap sprite
  chiptune:("c4")                  Play musical note
                                    Notes: c3..b3, c4..b4, c5..
  sound:(freq, dur_ms)             Custom square wave
  sfx_8bit:("coin")                Preset effects:
                                    coin, powerup, success, error,
                                    start, boot, hit, click
  coin:                            Quick "coin" SFX
  powerup:                         Power-up SFX
  success: / error_8bit:           State SFX

SYSTEM
  date / time / current_time / date_time
  wait:(sec) / wait_key
  alert / confirm / notification
  copy / open_url / run_cmd
  beep / beep:(freq,dur)

FILES
  create_file / read_file / file_exists
  delete_file / list_files
  json_get

AI / WEB
  AI: / ai_summarize / ai_translate / ai_explain
  JS: / HTML: / CSS: / JS_EVAL:
  html_title / css_theme

LOGS
  log_info / log_warn / log_error
  uuid:(var)

CONSOLE
  clear_console / clear_screen / stop

SPRITE EXAMPLE
  color:("red")
  sprite:(50, 50, "8;8;1=red,0=black;111001111111111111111111011111100111110000111000000100000000", 6)
"""

    def show_examples(self):
        win = tk.Toplevel(self.root)
        win.title("EXAMPLES LIBRARY")
        win.geometry("600x460")
        win.configure(bg=NES["ui_bg"])
        examples = {
            "HELLO WORLD":  'show "HELLO, 8-BITS!"\ncoin:',
            "COUNTER":      'var:(n, 0)\nincrement:(n, 1)\nincrement:(n, 1)\nprint n\ncoin:',
            "RED CIRCLE":   'color:("red")\ncircle:(100, 100, 40)\nsound:(440, 80)',
            "GRID + RECTANGLE":
                'grid:(40)\ncolor:("blue")\nrectangle:(40, 40, 120, 80)',
            "PIXEL TEXT":   'canvas_text:(150, 60, "HELLO!", "green")',
            "RGB":          'rgb:(255, 100, 50)\ncircle:(80, 80, 40)',
            "RANDOM + MATH":
                'random:(n, 1, 100)\nprint n\nadd:(r, n, 5)\nprint r',
            "CHIPTUNE MELODY":
                'chiptune:("c4")\nchiptune:("e4")\nchiptune:("g4")\nchiptune:("c5")',
            "8-BIT SFX":
                'sfx_8bit:("coin")\nsfx_8bit:("powerup")\nsfx_8bit:("success")',
            "BUTTON":       'button:("CLICK", coin:)',
            "SPRITE HEART":
                'color:("red")\nsprite:(50, 50, "8;8;1=red,0=black;111001111111111111111111011111100111110000111000000100000000", 6)',
            "DATE AND TIME": 'date\ntime',
        }
        lb = tk.Listbox(win, font=(self.font_family, 10, "bold"),
                        bg=NES["ui_bg"], fg=NES["white"],
                        selectbackground=NES["red"], selectforeground=NES["white"],
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
            "DRAWING BASE":  'clear_screen\ngrid:(40)\ncolor:("blue")\n',
            "INTERACTION":   'input:(name, "What is your name?")\nprint name\ncoin:',
            "FULL DEMO":     self.code_editor.get("1.0", "end-1c"),
        }
        win = tk.Toplevel(self.root)
        win.title("QUICK TEMPLATES")
        win.geometry("380x260")
        win.configure(bg=NES["ui_bg"])
        lb = tk.Listbox(win, font=(self.font_family, 10, "bold"),
                        bg=NES["ui_bg"], fg=NES["white"],
                        selectbackground=NES["red"], selectforeground=NES["white"],
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
        win.configure(bg=NES["ui_bg"])
        lb = tk.Listbox(win, font=(self.font_family, 10),
                        bg=NES["ui_bg"], fg=NES["white"],
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
            self.status.set(f"VARIABLES EXPORTED: {os.path.basename(path)}")

    def import_variables(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.interpreter.variables.update(data)
            self.status.set(f"VARIABLES IMPORTED: {os.path.basename(path)}")

    def show_stats(self):
        info = (
            f"STATISTICS\n"
            f"─────────────\n"
            f"Lines executed: {self.interpreter.executed_lines}\n"
            f"Time: {self.interpreter.execution_time:.3f} s\n"
            f"Variables: {len(self.interpreter.variables)}\n"
            f"Last error line: {self.interpreter.last_error_line}\n"
        )
        self.sound.coin()
        messagebox.showinfo("STATISTICS", info)

    def open_command_palette(self):
        win = tk.Toplevel(self.root)
        win.title("COMMAND PALETTE")
        win.geometry("440x320")
        win.configure(bg=NES["ui_bg"])
        entry = tk.Entry(win, font=(self.font_family, 11, "bold"),
                         bg=NES["ui_bg"], fg=NES["white"],
                         insertbackground=NES["bright_yellow"], bd=3, relief=tk.RAISED)
        entry.pack(fill=tk.X, padx=6, pady=6)
        lb = tk.Listbox(win, font=(self.font_family, 10),
                        bg=NES["ui_bg"], fg=NES["white"],
                        selectbackground=NES["red"], selectforeground=NES["white"],
                        bd=0, highlightthickness=0)
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        actions = {
            "NEW PROJECT": self.new_project,
            "OPEN PROJECT": self.load_project,
            "SAVE PROJECT": self.save_project,
            "RUN ALL": self.run_code,
            "RUN SELECTION": self.run_selection,
            "STOP": self.stop_execution,
            "FIND / REPLACE": self.open_find_dialog,
            "GO TO LINE": self.goto_line,
            "INSPECT VARIABLES": self.inspect_variables,
            "EXPORT VARIABLES": self.export_variables,
            "IMPORT VARIABLES": self.import_variables,
            "EXAMPLES": self.show_examples,
            "COMMAND REFERENCE": self.show_command_reference,
            "STATISTICS": self.show_stats,
            "FULLSCREEN": self.toggle_fullscreen,
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
    # FILES / AUTOSAVE / CONFIG
    # ============================================================
    def new_project(self):
        if messagebox.askyesno("NEW PROJECT", "Create a new project?"):
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
            filetypes=[("EZScript Projects", "*.ez"), ("All Files", "*.*")])
        if path:
            self._write_file(path)
            self._add_recent(path)

    def _write_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.code_editor.get("1.0", tk.END))
        self.current_file = path
        self.status.set(f"SAVED: {os.path.basename(path)}")

    def load_project(self):
        path = filedialog.askopenfilename(
            filetypes=[("EZScript Projects", "*.ez"), ("All Files", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert(tk.END, content)
                self.current_file = path
                self._add_recent(path)
                self.status.set(f"LOADED: {os.path.basename(path)}")
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
            self.recent_menu.add_command(label="(empty)", state="disabled")
        for p in self.recent_files:
            self.recent_menu.add_command(label=p, command=lambda path=p: self._open_recent(path))

    def _open_recent(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert(tk.END, content)
            self.current_file = path
            self.status.set(f"LOADED: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def _schedule_autosave(self):
        def tick():
            try:
                if self.current_file and self.code_editor.edit_modified():
                    self._write_file(self.current_file)
                    self.status.set("AUTOSAVED.")
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
    # UTILITIES
    # ============================================================
    def ask_input(self, prompt_text):
        return simpledialog.askstring("EZSCRIPT INPUT", prompt_text, parent=self.root)

    def _load_demo(self):
        demo = (
            "// ============================================\n"
            "// EZSCRIPT 8-BITS — RETRO DEMO\n"
            "// ============================================\n"
            "sfx_8bit:(\"start\")\n"
            "log_info:(\"BOOTING 8-BIT SYSTEM...\")\n"
            "\n"
            "// --- VARIABLES ---\n"
            "var:(lives, 3)\n"
            "var:(score, 0)\n"
            "increment:(score, 100)\n"
            "print score\n"
            "\n"
            "// --- PIXEL DRAWING ---\n"
            "canvas_color:(\"dark_blue\")\n"
            "grid:(40)\n"
            "\n"
            "color:(\"red\")\n"
            "circle:(60, 60, 35)\n"
            "rectangle:(120, 25, 90, 60)\n"
            "\n"
            "color:(\"lime\")\n"
            "triangle:(230, 85, 270, 25, 310, 85)\n"
            "\n"
            "color:(\"yellow\")\n"
            "oval:(30, 130, 100, 50)\n"
            "circle:(170, 150, 25, \"pink\")\n"
            "\n"
            "canvas_text:(160, 210, \"EZSCRIPT 8-BITS!\", \"white\")\n"
            "\n"
            "// --- CHIPTUNE SOUND ---\n"
            "chiptune:(\"c4\")\n"
            "chiptune:(\"e4\")\n"
            "chiptune:(\"g4\")\n"
            "chiptune:(\"c5\")\n"
            "\n"
            "// --- SYSTEM ---\n"
            "date\n"
            "time\n"
            "log_info:(\"SYSTEM READY\")\n"
            "sfx_8bit:(\"coin\")\n"
            "\n"
            "// --- RETRO BUTTONS ---\n"
            "button:(\"PRESS HERE\", coin:)\n"
            "button:(\"POWER-UP\", powerup:)\n"
        )
        self.code_editor.insert(tk.END, demo)
        self._update_linenumbers()
        self._highlight_syntax()
        self._highlight_current_line()


EZScriptIDE = EZScriptEnglishIDE8Bit


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = EZScriptEnglishIDE8Bit(root)
    root.mainloop()
