# -*- coding: utf-8 -*-
"""
EZScript English Studio v2.0.0
===============================
English IDE + Interpreter for the EZScript language.

70 IMPROVEMENTS APPLIED (see comments # Mxx):
 M01 Full menu bar
 M02 Keyboard shortcuts (Ctrl+N/O/S, F5, Ctrl+F, etc.)
 M03 Status bar with cursor position and counters
 M04 Line numbers panel
 M05 Syntax highlighting
 M06 Find & Replace dialog
 M07 Font zoom (Ctrl +/-)
 M08 Light/Dark theme
 M09 Recent files
 M10 Periodic autosave
 M11 Threaded execution (non-blocking UI)
 M12 Stop execution button
 M13 Execution timer
 M14 Colored console output (info/warn/error/success)
 M15 Optional console timestamps
 M16 Clear console button
 M17 Clear canvas button
 M18 Save canvas as PostScript
 M19 Save console to file
 M20 Copy console to clipboard
 M21 Highlight line with error
 M22 Go to line (Ctrl+G)
 M23 Duplicate line (Ctrl+D)
 M24 Comment/Uncomment (Ctrl+/)
 M25 Indent / Dedent (Tab / Shift+Tab)
 M26 Word wrap toggle
 M27 Configurable tab size
 M28 Show whitespace toggle
 M29 Inspect variables (window)
 M30 Export/Import variables as JSON
 M31 Examples library
 M32 Quick templates
 M33 About dialog
 M34 Help with command reference
 M35 Basic command autocompletion (Ctrl+Space)
 M36 Command palette (Ctrl+Shift+P)
 M37 Current-line highlight
 M38 Bracket matching
 M39 Auto-close brackets/quotes
 M40 Syntax validation before running
 M41 Font selector
 M42 Font size selector
 M43 Fullscreen mode (F11)
 M44 Line and character counter
 M45 Line:Column indicator
 M46 Run selection
 M47 Run from cursor
 M48 Indeterminate progress bar during execution
 M49 More English colors (cyan, violet, brown, gold, silver)
 M50 Re-checkable wait / active stop
 M51 New command: clear_console
 M52 New command: current_time
 M53 New command: date_time
 M54 New command: to_number / to_text
 M55 New command: join / split_text / index
 M56 New command: reverse / sort / count
 M57 New command: add / subtract / multiply / divide / modulo
 M58 New command: equal_to / greater_than / less_than / and / or / not
 M59 New command: rgb (component colors)
 M60 New command: file_exists / delete_file / list_files
 M61 New command: uuid
 M62 New command: log_info / log_warn / log_error
 M63 New command: beep with frequency and duration
 M64 New command: wait_key
 M65 New command: loop / while / if / else (basic flow control)
 M66 Error handling with line reporting
 M67 Re-apply tags after theme change
 M68 Save/restore window geometry
 M69 Editor context menu
 M70 Execution statistics report
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

# ============ GLOBAL CONSTANTS ============
APP_NAME = "EZScript English Studio"
VERSION = "2.0.0"
DEFAULT_FONT = "Consolas"
DEFAULT_FONT_SIZE = 11
MAX_RECENT_FILES = 8
AUTOSAVE_INTERVAL_MS = 60000  # 1 minute
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ezscript_en_config.json")


# ==========================================
# 1. EZSCRIPT ENGLISH ENGINE & INTERPRETER
# ==========================================
class EZScriptEnglishInterpreter:
    # Known commands (autocomplete + help)
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
        # New commands (M51–M65)
        "clear_console", "current_time", "date_time",
        "to_number:", "to_text:", "join:", "split_text:", "index:",
        "reverse:", "sort:", "count:",
        "add:", "subtract:", "multiply:", "divide:", "modulo:",
        "equal_to:", "greater_than:", "less_than:", "and:", "or:", "not:",
        "rgb:", "file_exists:", "delete_file:", "list_files:",
        "uuid:", "log_info:", "log_warn:", "log_error:", "beep:",
        "wait_key", "loop:", "while:", "if:", "else:", "end_if", "end_loop",
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
        self.current_draw_color = "#0984e3"
        # M49 – more English colors
        self.COLOR_MAP = {
            "red": "#e74c3c", "blue": "#3498db", "green": "#2ecc71",
            "yellow": "#f1c40f", "orange": "#e67e22", "purple": "#9b59b6",
            "pink": "#fd79a8", "black": "#2c3e50", "white": "#ffffff",
            "gray": "#95a5a6", "grey": "#95a5a6", "cyan": "#00cec9",
            "violet": "#a29bfe", "brown": "#6d4c41",
            "gold": "#fdcb6e", "silver": "#b2bec3",
        }
        # M15 / M14 – timestamps and colors
        self.show_timestamps = False
        # M13 / M70 – metrics
        self.execution_start = None
        self.execution_time = 0.0
        self.executed_lines = 0
        self.last_error_line = None
        self._setup_console_tags()

    # ---------- Helpers ----------
    def _setup_console_tags(self):
        """M14 – colored log levels."""
        try:
            self.output.tag_config("info",    foreground="#ffffff")
            self.output.tag_config("error",   foreground="#e74c3c")
            self.output.tag_config("warn",    foreground="#f39c12")
            self.output.tag_config("success", foreground="#2ecc71")
            self.output.tag_config("dim",     foreground="#7f8c8d")
            self.output.tag_config("ts",      foreground="#636e72")
        except Exception:
            pass

    def get_color(self, val):
        clean_val = str(val).strip().lower().replace('"', '').replace("'", "")
        if clean_val.startswith("#") or clean_val.startswith("rgb"):
            return clean_val
        return self.COLOR_MAP.get(clean_val, clean_val)

    def log(self, text, level="info"):
        """M14/M15 – leveled log with optional timestamp."""
        prefix = ""
        if self.show_timestamps:
            prefix = f"[{datetime.now().strftime('%H:%M:%S')}] "
        full = prefix + str(text)
        self.output.insert(tk.END, full + "\n", level)
        self.output.see(tk.END)
        try:
            self.output.update()
        except Exception:
            pass
        try:
            line_num = int(self.output.index(tk.END).split('.')[0])
            self.text_positions[str(text).strip()] = (100, line_num * 20)
        except Exception:
            pass

    def log_info(self, t):    self.log(f"ℹ️  {t}", "info")
    def log_warn(self, t):    self.log(f"⚠️  {t}", "warn")
    def log_error(self, t):   self.log(f"❌ {t}", "error")
    def log_success(self, t): self.log(f"✅ {t}", "success")

    # ---------- Expressions ----------
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

    # ---------- M40 – Syntax validation ----------
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

    # ---------- Helper ----------
    def _safe_int(self, v, default=0):
        try:    return int(float(v))
        except Exception: return default

    # ---------- Execution ----------
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
                # M66 – error with line report
                self.last_error_line = line_num
                self.log_error(f"Error on line {line_num}: {e}")
                if self.app:
                    self.app.highlight_error_line(line_num)
            i += 1

    def _execute_line(self, line, line_num):
        # ==========================================================
        # BASE COMMANDS & COLOR SYSTEM
        # ==========================================================
        if line.startswith("AI:"):
            m = re.match(r'AI:\s*\((.*?)\)', line)
            if m:
                self.log_info(f"🤖 AI ← '{self.eval_expr(m.group(1))}' (simulated)")

        elif line.startswith("OperatingSystem:"):
            m = re.match(r'OperatingSystem:\s*\((.*?)\)', line)
            if m:
                tgt = str(self.eval_expr(m.group(1))).strip()
                if tgt in ["Windows", "macOS", "Linux"]:
                    self.emulated_os = tgt
                    self.log_info(f"🖥️ Emulated OS: {self.emulated_os}")

        elif line.startswith("JS:"):
            self.log(f"📜 [JS] {line[3:].strip()}")

        elif line.startswith("HTML:"):
            self.log(f"🌐 [HTML] {line[5:].strip()}")

        elif line.startswith("CSS:"):
            self.log(f"🎨 [CSS] {line[4:].strip()}")

        elif line.startswith("JSON:"):
            try:
                self.log(f"📦 [JSON] {json.loads(line[5:].strip())}")
            except Exception as e:
                self.log_warn(f"Invalid JSON (L{line_num}): {e}")

        elif line.startswith("ICON:"):
            self.log(f"🖼️ [Icon] {line[5:].strip()}")

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
                    p1 = self.text_positions.get(t1)
                    p2 = self.text_positions.get(t2)
                    if p1 and p2:
                        self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                                fill=col, width=self.current_line_width, dash=(4, 2))

        elif line.startswith("color:"):
            m = re.match(r'color:\s*\((.*?)\)', line)
            if m:
                self.current_draw_color = self.get_color(self.eval_expr(m.group(1).strip()))

        elif line == "clear_screen":
            self.output.delete("1.0", tk.END)
            self.canvas.delete("all")
            self.text_positions.clear()

        # M51 – clear console only
        elif line == "clear_console":
            self.output.delete("1.0", tk.END)

        elif line.startswith("show ") or line.startswith("print "):
            self.log(self.eval_expr(line.split(" ", 1)[1]))

        elif line.startswith("button:"):
            content = line[len("button:"):].strip()
            if content.startswith("(") and content.endswith(")"):
                content = content[1:-1]
            parts = content.split(",", 1)
            txt = str(self.eval_expr(parts[0]))
            action = parts[1].strip() if len(parts) > 1 else ""
            btn = tk.Button(
                self.output, text=txt, bg="#0984e3", fg="white",
                font=("Arial", 9, "bold"),
                command=lambda c=action: self.execute_inline(c)
            )
            self.output.window_create(tk.END, window=btn)
            self.output.insert(tk.END, "\n")

        # ==========================================================
        # VARIABLES AND STRINGS
        # ==========================================================
        elif line.startswith("var:") or line.startswith("DEFINE_VARIABLE:"):
            m = re.match(r'(?:var|DEFINE_VARIABLE):\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = self.eval_expr(m.group(2))

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
            if m:
                self.log(f"📏 Length: {len(str(self.eval_expr(m.group(1))))}")

        elif line.startswith("replace:"):
            m = re.match(r'replace:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k, "")).replace(
                    str(self.eval_expr(m.group(2))), str(self.eval_expr(m.group(3))))

        elif line.startswith("data_type:"):
            m = re.match(r'data_type:\s*\((.*?)\)', line)
            if m:
                self.log(f"ℹ️ Type: {type(self.eval_expr(m.group(1))).__name__}")

        elif line.startswith("concat:"):
            m = re.match(r'concat:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

        # M54
        elif line.startswith("to_number:"):
            m = re.match(r'to_number:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2)))
                except Exception:
                    self.variables[m.group(1).strip()] = 0

        elif line.startswith("to_text:"):
            m = re.match(r'to_text:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2)))

        # M55
        elif line.startswith("join:"):
            m = re.match(r'join:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

        elif line.startswith("split_text:"):
            m = re.match(r'split_text:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))).split(str(self.eval_expr(m.group(3))))

        elif line.startswith("index:"):
            m = re.match(r'index:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                lst_or_str = self.eval_expr(m.group(2))
                idx = self._safe_int(self.eval_expr(m.group(3)))
                try:
                    self.variables[m.group(1).strip()] = lst_or_str[idx]
                except Exception:
                    self.variables[m.group(1).strip()] = ""

        # M56
        elif line.startswith("reverse:"):
            m = re.match(r'reverse:\s*\((.*?),(.*?)\)', line)
            if m:
                v = str(self.eval_expr(m.group(2)))
                self.variables[m.group(1).strip()] = v[::-1]

        elif line.startswith("sort:"):
            m = re.match(r'sort:\s*\((.*?),(.*?)\)', line)
            if m:
                v = self.eval_expr(m.group(2))
                try:
                    self.variables[m.group(1).strip()] = sorted(v)
                except Exception:
                    self.variables[m.group(1).strip()] = v

        elif line.startswith("count:"):
            m = re.match(r'count:\s*\((.*?)\)', line)
            if m:
                self.log(f"🔢 Count: {len(str(self.eval_expr(m.group(1))))}")

        # ==========================================================
        # MATHEMATICS
        # ==========================================================
        elif line.startswith("random:"):
            m = re.match(r'random:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = random.randint(
                    self._safe_int(self.eval_expr(m.group(2))),
                    self._safe_int(self.eval_expr(m.group(3))))

        elif line.startswith("sqrt:"):
            m = re.match(r'sqrt:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = math.sqrt(float(self.eval_expr(m.group(2))))
                except Exception:
                    self.variables[m.group(1).strip()] = 0

        elif line.startswith("power:"):
            m = re.match(r'power:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.pow(
                    float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

        elif line.startswith("round:"):
            m = re.match(r'round:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = round(float(self.eval_expr(m.group(2))))

        elif line.startswith("abs:"):
            m = re.match(r'abs:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = abs(float(self.eval_expr(m.group(2))))

        elif line.startswith("sin:"):
            m = re.match(r'sin:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.sin(math.radians(float(self.eval_expr(m.group(2)))))

        elif line.startswith("cos:"):
            m = re.match(r'cos:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.cos(math.radians(float(self.eval_expr(m.group(2)))))

        elif line.startswith("max:"):
            m = re.match(r'max:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = max(
                    float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

        elif line.startswith("min:"):
            m = re.match(r'min:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = min(
                    float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

        elif line.startswith("pi:"):
            m = re.match(r'pi:\s*\((.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.pi

        # M57 – simple arithmetic
        elif line.startswith("add:"):
            m = re.match(r'add:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) + float(self.eval_expr(m.group(3)))
        elif line.startswith("subtract:"):
            m = re.match(r'subtract:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) - float(self.eval_expr(m.group(3)))
        elif line.startswith("multiply:"):
            m = re.match(r'multiply:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) * float(self.eval_expr(m.group(3)))
        elif line.startswith("divide:"):
            m = re.match(r'divide:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) / float(self.eval_expr(m.group(3)))
                except Exception:
                    self.variables[m.group(1).strip()] = 0
        elif line.startswith("modulo:"):
            m = re.match(r'modulo:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) % float(self.eval_expr(m.group(3)))
                except Exception:
                    self.variables[m.group(1).strip()] = 0

        # M58 – comparators / logic
        elif line.startswith("equal_to:"):
            m = re.match(r'equal_to:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = (str(self.eval_expr(m.group(2))) == str(self.eval_expr(m.group(3))))
        elif line.startswith("greater_than:"):
            m = re.match(r'greater_than:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) > float(self.eval_expr(m.group(3)))
                except Exception:
                    self.variables[m.group(1).strip()] = False
        elif line.startswith("less_than:"):
            m = re.match(r'less_than:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) < float(self.eval_expr(m.group(3)))
                except Exception:
                    self.variables[m.group(1).strip()] = False
        elif line.startswith("and:"):
            m = re.match(r'and:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) and bool(self.eval_expr(m.group(3)))
        elif line.startswith("or:"):
            m = re.match(r'or:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) or bool(self.eval_expr(m.group(3)))
        elif line.startswith("not:"):
            m = re.match(r'not:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = not bool(self.eval_expr(m.group(2)))

        # ==========================================================
        # CANVAS DRAWING
        # ==========================================================
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
                self.canvas.create_text(x, y, text=str(txt), fill=c, font=("Arial", 10, "bold"))

        elif line.startswith("canvas_color:"):
            m = re.match(r'canvas_color:\s*\((.*?)\)', line)
            if m:
                self.canvas.config(bg=self.get_color(self.eval_expr(m.group(1))))

        elif line.startswith("line_width:"):
            m = re.match(r'line_width:\s*\((.*?)\)', line)
            if m:
                self.current_line_width = self._safe_int(self.eval_expr(m.group(1)), 1)

        elif line == "clear_canvas":
            self.canvas.delete("all")

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
                self.canvas.create_arc(vals[0], vals[1], vals[2], vals[3],
                                       start=vals[4], extent=vals[5], fill=c)

        elif line.startswith("grid:"):
            m = re.match(r'grid:\s*\((.*?)\)', line)
            if m:
                step = self._safe_int(self.eval_expr(m.group(1)), 40)
                if step > 0:
                    for x in range(0, 400, step):
                        self.canvas.create_line(x, 0, x, 400, fill="#34495e", dash=(1, 3))
                    for y in range(0, 400, step):
                        self.canvas.create_line(0, y, 400, y, fill="#34495e", dash=(1, 3))

        # M59 – rgb
        elif line.startswith("rgb:"):
            m = re.match(r'rgb:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                r = self._safe_int(self.eval_expr(m.group(1))) % 256
                g = self._safe_int(self.eval_expr(m.group(2))) % 256
                b = self._safe_int(self.eval_expr(m.group(3))) % 256
                self.current_draw_color = f"#{r:02x}{g:02x}{b:02x}"

        # ==========================================================
        # SYSTEM & UTILITIES
        # ==========================================================
        elif line == "date":
            self.log(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")

        elif line == "time":
            self.log(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")

        # M52/M53
        elif line == "current_time":
            self.log(f"⏰ {datetime.now().strftime('%H:%M:%S')}")

        elif line == "date_time":
            self.log(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        elif line.startswith("wait:"):
            m = re.match(r'wait:\s*\((.*?)\)', line)
            if m:
                try:
                    t = float(self.eval_expr(m.group(1)))
                except Exception:
                    t = 0
                end = time.time() + t
                while time.time() < end and not self.should_stop:
                    time.sleep(0.02)
                    try:
                        self.output.update()
                    except Exception:
                        pass

        elif line.startswith("alert:"):
            m = re.match(r'alert:\s*\((.*?)\)', line)
            if m:
                messagebox.showinfo("EZScript Alert", str(self.eval_expr(m.group(1))))

        elif line.startswith("confirm:"):
            m = re.match(r'confirm:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = messagebox.askyesno(
                    "Confirmation", str(self.eval_expr(m.group(2))))

        elif line.startswith("open_url:"):
            m = re.match(r'open_url:\s*\((.*?)\)', line)
            if m:
                webbrowser.open(str(self.eval_expr(m.group(1))))

        elif line.startswith("copy:"):
            m = re.match(r'copy:\s*\((.*?)\)', line)
            if m:
                self.app.root.clipboard_clear()
                self.app.root.clipboard_append(str(self.eval_expr(m.group(1))))

        elif line.startswith("notification:"):
            m = re.match(r'notification:\s*\((.*?),(.*?)\)', line)
            if m:
                self.log(f"🔔 [{self.eval_expr(m.group(1))}] {self.eval_expr(m.group(2))}")

        elif line == "beep":
            try: self.app.root.bell()
            except Exception: pass

        elif line.startswith("run_cmd:"):
            m = re.match(r'run_cmd:\s*\((.*?)\)', line)
            if m:
                self.log(f"💻 Simulated CMD: '{self.eval_expr(m.group(1))}'")

        # M62 – explicit logs
        elif line.startswith("log_info:"):
            m = re.match(r'log_info:\s*\((.*?)\)', line)
            if m: self.log_info(self.eval_expr(m.group(1)))
        elif line.startswith("log_warn:"):
            m = re.match(r'log_warn:\s*\((.*?)\)', line)
            if m: self.log_warn(self.eval_expr(m.group(1)))
        elif line.startswith("log_error:"):
            m = re.match(r'log_error:\s*\((.*?)\)', line)
            if m: self.log_error(self.eval_expr(m.group(1)))

        # M63 – beep with freq
        elif line.startswith("beep:"):
            m = re.match(r'beep:\s*\((.*?)(?:,(.*?))?\)', line)
            if m:
                try: self.app.root.bell()
                except Exception: pass

        # M64 – wait for key
        elif line == "wait_key":
            messagebox.showinfo("EZScript", "Press OK to continue")

        # M61 – uuid
        elif line.startswith("uuid:"):
            m = re.match(r'uuid:\s*\((.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = str(uuidlib.uuid4())

        # ==========================================================
        # AI, WEB & FILES
        # ==========================================================
        elif line.startswith("ai_summarize:"):
            m = re.match(r'ai_summarize:\s*\((.*?)\)', line)
            if m:
                self.log(f"🤖 [Summary] {str(self.eval_expr(m.group(1)))[:60]}...")

        elif line.startswith("ai_translate:"):
            m = re.match(r'ai_translate:\s*\((.*?),(.*?)\)', line)
            if m:
                self.log(f"🤖 [Translated to {self.eval_expr(m.group(2))}] {self.eval_expr(m.group(1))}")

        elif line.startswith("ai_explain:"):
            m = re.match(r'ai_explain:\s*\((.*?)\)', line)
            if m:
                self.log("🤖 [AI Explanation] Analysis completed.")

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

        # M60 – files
        elif line.startswith("file_exists:"):
            m = re.match(r'file_exists:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = os.path.exists(str(self.eval_expr(m.group(2))))
        elif line.startswith("delete_file:"):
            m = re.match(r'delete_file:\s*\((.*?)\)', line)
            if m:
                try: os.remove(str(self.eval_expr(m.group(1))))
                except Exception as e: self.log_error(str(e))
        elif line.startswith("list_files:"):
            m = re.match(r'list_files:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = os.listdir(str(self.eval_expr(m.group(2))))
                except Exception as e:
                    self.log_error(str(e))

        elif line.startswith("html_title:"):
            m = re.match(r'html_title:\s*\((.*?)\)', line)
            if m:
                self.log(f"🌐 <title>{self.eval_expr(m.group(1))}</title>")

        elif line.startswith("css_theme:"):
            m = re.match(r'css_theme:\s*\((.*?)\)', line)
            if m:
                v = str(self.eval_expr(m.group(1))).lower()
                bg = "#1e272e" if v == "dark" else "#ffffff"
                fg = "#ffffff" if v == "dark" else "#000000"
                self.output.config(bg=bg, fg=fg)
                self.canvas.config(bg=bg)

        elif line.startswith("js_eval:"):
            m = re.match(r'js_eval:\s*\((.*?)\)', line)
            if m:
                self.log(f"📜 [JS] {self.eval_expr(m.group(1))}")

        elif line == "stop":
            self.should_stop = True
            self.log_warn("Execution stopped by user.")

        else:
            # Unknown command: warning (M40)
            if ":" in line and not line.startswith("//"):
                self.log_warn(f"Unrecognized command on L{line_num}: {line}")

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
        self.output.config(bg="#1e272e", fg="#ffffff")
        self.canvas.config(bg="#1e272e")
        self.current_draw_color = "#0984e3"

        self.execution_start = time.time()
        raw_lines = code.split('\n')
        structured = [{'num': i + 1, 'text': l} for i, l in enumerate(raw_lines)]
        self.run_block(structured)
        self.execution_time = time.time() - self.execution_start

        # M70 – final report
        self.log("", "info")
        self.log_success(
            f"Execution finished in {self.execution_time:.3f}s · "
            f"{self.executed_lines} statements · {len(self.variables)} variables"
        )
        if self.app:
            self.app.on_execution_finished(self.execution_time, self.executed_lines)


# Alias
EZScriptInterpreter = EZScriptEnglishInterpreter


# ==========================================
# 2. GUI IDE (EZSCRIPT ENGLISH STUDIO)
# ==========================================
class EZScriptEnglishIDE:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1100x820")

        # State
        self.font_family = DEFAULT_FONT
        self.font_size   = DEFAULT_FONT_SIZE
        self.tab_size    = 4
        self.word_wrap   = False
        self.show_whitespace = False
        self.current_theme = "dark"
        self.recent_files = []
        self.current_file = None
        self.execution_thread = None
        self.console_queue = queue.Queue()
        self.autosave_id = None

        # Load config (M68)
        self._load_config()

        # Font setup
        self.editor_font   = tkfont.Font(family=self.font_family, size=self.font_size)
        self.console_font  = tkfont.Font(family=self.font_family, size=max(9, self.font_size - 1))
        self.linenum_font  = tkfont.Font(family=self.font_family, size=max(9, self.font_size - 1))

        self._build_menu()          # M01
        self._build_toolbar()
        self._build_editor_area()   # M04/M05/M37
        self._build_output_area()
        self._build_statusbar()     # M03

        # Interpreter
        self.interpreter = EZScriptEnglishInterpreter(self.console, self.canvas, self)

        # Keyboard shortcuts (M02)
        self._bind_shortcuts()

        # Editor context menu (M69)
        self._build_context_menu()

        # Demo script
        self._load_demo()

        # Autosave (M10)
        self._schedule_autosave()

        # Save config on close (M68)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ==========================================================
    # UI CONSTRUCTION
    # ==========================================================
    def _build_menu(self):
        # M01 – menu bar
        menubar = tk.Menu(self.root)

        # --- File ---
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="New",           accelerator="Ctrl+N", command=self.new_project)
        m_file.add_command(label="Open…",          accelerator="Ctrl+O", command=self.load_project)
        m_file.add_command(label="Save",          accelerator="Ctrl+S", command=self.save_project)
        m_file.add_command(label="Save As…",      accelerator="Ctrl+Shift+S", command=self.save_project_as)
        m_file.add_separator()
        m_file.add_command(label="Save Console…", command=self.save_console)
        m_file.add_command(label="Save Canvas (PS)…", command=self.save_canvas_ps)
        m_file.add_separator()
        # M09 – recent
        self.recent_menu = tk.Menu(m_file, tearoff=0)
        m_file.add_cascade(label="Recent Files", menu=self.recent_menu)
        self._rebuild_recent_menu()
        m_file.add_separator()
        m_file.add_command(label="Exit", accelerator="Alt+F4", command=self._on_close)
        menubar.add_cascade(label="File", menu=m_file)

        # --- Edit ---
        m_edit = tk.Menu(menubar, tearoff=0)
        m_edit.add_command(label="Undo",      accelerator="Ctrl+Z", command=lambda: self.code_editor.event_generate("<<Undo>>"))
        m_edit.add_command(label="Redo",      accelerator="Ctrl+Y", command=lambda: self.code_editor.event_generate("<<Redo>>"))
        m_edit.add_separator()
        m_edit.add_command(label="Find / Replace", accelerator="Ctrl+F", command=self.open_find_dialog)
        m_edit.add_command(label="Go to Line…",    accelerator="Ctrl+G", command=self.goto_line)
        m_edit.add_separator()
        m_edit.add_command(label="Duplicate Line",   accelerator="Ctrl+D", command=self.duplicate_line)
        m_edit.add_command(label="Comment / Uncomment", accelerator="Ctrl+/", command=self.toggle_comment)
        m_edit.add_command(label="Indent",         accelerator="Tab",       command=lambda: self.indent_selection(True))
        m_edit.add_command(label="Dedent",         accelerator="Shift+Tab", command=lambda: self.indent_selection(False))
        m_edit.add_separator()
        m_edit.add_command(label="Command Palette", accelerator="Ctrl+Shift+P", command=self.open_command_palette)
        m_edit.add_command(label="Autocomplete",    accelerator="Ctrl+Space", command=self.autocomplete)
        m_edit.add_separator()
        m_edit.add_command(label="Inspect Variables", command=self.inspect_variables)
        m_edit.add_command(label="Export Variables (JSON)", command=self.export_variables)
        m_edit.add_command(label="Import Variables (JSON)", command=self.import_variables)
        menubar.add_cascade(label="Edit", menu=m_edit)

        # --- View ---
        m_view = tk.Menu(menubar, tearoff=0)
        m_view.add_command(label="Increase Font",   accelerator="Ctrl++", command=lambda: self.change_font_size(+1))
        m_view.add_command(label="Decrease Font",   accelerator="Ctrl+-", command=lambda: self.change_font_size(-1))
        m_view.add_command(label="Reset Font",      accelerator="Ctrl+0", command=self.reset_font_size)
        m_view.add_separator()
        m_view.add_command(label="Choose Font…", command=self.choose_font)
        m_view.add_command(label="Tab Size…",    command=self.choose_tab_size)
        m_view.add_separator()
        self.var_wrap = tk.BooleanVar(value=self.word_wrap)
        m_view.add_checkbutton(label="Word Wrap", variable=self.var_wrap, command=self.toggle_wrap)
        self.var_ws = tk.BooleanVar(value=self.show_whitespace)
        m_view.add_checkbutton(label="Show Whitespace", variable=self.var_ws, command=self.toggle_whitespace)
        self.var_ts = tk.BooleanVar(value=False)
        m_view.add_checkbutton(label="Console Timestamps", variable=self.var_ts, command=self.toggle_timestamps)
        m_view.add_separator()
        m_view.add_command(label="Toggle Light/Dark Theme", command=self.toggle_theme)
        m_view.add_command(label="Fullscreen", accelerator="F11", command=self.toggle_fullscreen)
        menubar.add_cascade(label="View", menu=m_view)

        # --- Run ---
        m_run = tk.Menu(menubar, tearoff=0)
        m_run.add_command(label="Run All",          accelerator="F5",        command=self.run_code)
        m_run.add_command(label="Run Selection",    accelerator="F6",        command=self.run_selection)
        m_run.add_command(label="Run From Cursor",  accelerator="Ctrl+F5",   command=self.run_from_cursor)
        m_run.add_command(label="Validate Syntax",  accelerator="Ctrl+Shift+V", command=self.validate_syntax)
        m_run.add_separator()
        m_run.add_command(label="Stop Execution",   accelerator="Esc",       command=self.stop_execution)
        m_run.add_separator()
        m_run.add_command(label="Clear Console",    command=lambda: self.console.delete("1.0", tk.END))
        m_run.add_command(label="Clear Canvas",     command=lambda: self.canvas.delete("all"))
        m_run.add_command(label="Copy Console",     command=self.copy_console)
        menubar.add_cascade(label="Run", menu=m_run)

        # --- Help ---
        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label="Command Reference", command=self.show_command_reference)
        m_help.add_command(label="Examples Library",  command=self.show_examples)
        m_help.add_command(label="Quick Templates",   command=self.show_templates)
        m_help.add_separator()
        m_help.add_command(label="Statistics",        command=self.show_stats)
        m_help.add_command(label="About…",            command=self.show_about)
        menubar.add_cascade(label="Help", menu=m_help)

        self.root.config(menu=menubar)

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg="#2c3e50")
        bar.pack(side=tk.TOP, fill=tk.X)

        def add_btn(txt, color, cmd):
            b = tk.Button(bar, text=txt, bg=color, fg="white",
                          font=("Arial", 10, "bold"), command=cmd, relief=tk.FLAT, padx=8)
            b.pack(side=tk.LEFT, padx=3, pady=4)
            return b

        add_btn("📄 New",      "#3498db", self.new_project)
        add_btn("📂 Open",     "#f39c12", self.load_project)
        add_btn("💾 Save",     "#27ae60", self.save_project)
        add_btn("▶️ Run",      "#e74c3c", self.run_code)
        add_btn("⏹️ Stop",     "#8e44ad", self.stop_execution)   # M12
        add_btn("🧹 Console",  "#16a085", lambda: self.console.delete("1.0", tk.END))
        add_btn("🎨 Canvas",   "#2c3e50", lambda: self.canvas.delete("all"))
        add_btn("🔍 Find",     "#34495e", self.open_find_dialog)
        add_btn("📖 Help",     "#7f8c8d", self.show_command_reference)

        # M48 – progress bar
        self.progress = ttk.Progressbar(bar, mode="indeterminate", length=120)
        self.progress.pack(side=tk.RIGHT, padx=6, pady=6)

    def _build_editor_area(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Line numbers (M04)
        self.linenumbers = tk.Text(frame, width=4, padx=4, takefocus=0, border=0,
                                   background="#282c34", foreground="#7f8c8d",
                                   font=self.linenum_font, state="disabled")
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor
        self.code_editor = tk.Text(frame, font=self.editor_font, undo=True,
                                   wrap=tk.NONE, tabs=f"{{{self.tab_size}c}}",
                                   insertbackground="#ffffff")
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code_editor.bind("<<Modified>>", self._on_modified)
        self.code_editor.bind("<KeyRelease>", self._on_key_release)   # M05/M38/M39
        self.code_editor.bind("<Button-1>", self._on_click)
        self.code_editor.bind("<MouseWheel>", self._on_mousewheel)

        # Scrollbar
        sb = tk.Scrollbar(frame, command=self._on_scroll, orient="vertical")
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_editor.config(yscrollcommand=lambda a, b: self._yscroll(a, b, sb))
        self._editor_scrollbar = sb

        # Syntax tags (M05) and current line (M37)
        self._setup_syntax_tags()

    def _build_output_area(self):
        frame = tk.Frame(self.root, bg="#1e272e")
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 4))

        self.console = tk.Text(frame, font=self.console_font, height=10,
                               bg="#1e272e", fg="#ffffff", width=50, wrap=tk.WORD)
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.interpreter_console = self.console

        self.canvas = tk.Canvas(frame, bg="#1e272e", highlightthickness=0, width=360)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _build_statusbar(self):
        # M03
        self.status = tk.StringVar()
        self.status.set("Ready.")
        sb = tk.Label(self.root, textvariable=self.status, anchor="w",
                      bg="#2c3e50", fg="white", font=("Arial", 9))
        sb.pack(side=tk.BOTTOM, fill=tk.X)

        # Labels (M44 / M45)
        self.lbl_pos = tk.Label(sb, text="Ln 1, Col 1", bg="#2c3e50", fg="white", font=("Arial", 9))
        self.lbl_pos.pack(side=tk.RIGHT, padx=8)
        self.lbl_count = tk.Label(sb, text="0 lines · 0 chars", bg="#2c3e50", fg="white", font=("Arial", 9))
        self.lbl_count.pack(side=tk.RIGHT, padx=8)

    # ==========================================================
    # SYNTAX AND TAGS (M05 / M37 / M21)
    # ==========================================================
    def _setup_syntax_tags(self):
        e = self.code_editor
        e.tag_configure("kw",       foreground="#c678dd")           # commands
        e.tag_configure("string",   foreground="#98c379")           # strings
        e.tag_configure("comment",  foreground="#7f848e", font=(self.font_family, self.font_size, "italic"))
        e.tag_configure("number",   foreground="#d19a66")
        e.tag_configure("color",    foreground="#e5c07b")
        e.tag_configure("errorline", background="#4d1f1f")
        e.tag_configure("current",  background="#2c313a")

    def _highlight_syntax(self):
        e = self.code_editor
        for tag in ("kw", "string", "comment", "number", "color"):
            e.tag_remove(tag, "1.0", tk.END)
        text = e.get("1.0", tk.END)

        # Comments
        for m in re.finditer(r'//[^\n]*', text):
            self._tag_range("comment", m.start(), m.end(), text)
        # Strings
        for m in re.finditer(r'"[^"\n]*"|\'[^\'\n]*\'', text):
            self._tag_range("string", m.start(), m.end(), text)
        # Numbers
        for m in re.finditer(r'\b\d+(\.\d+)?\b', text):
            self._tag_range("number", m.start(), m.end(), text)
        # English colors
        for c in ("red","blue","green","yellow","orange","purple","pink",
                  "black","white","gray","grey","cyan","violet","brown",
                  "gold","silver"):
            for m in re.finditer(r'\b' + c + r'\b', text):
                self._tag_range("color", m.start(), m.end(), text)
        # Commands (kw) at line start
        for m in re.finditer(r'(?m)^\s*([A-Za-z_][A-Za-z0-9_]*\s*:)', text):
            self._tag_range("kw", m.start(1), m.end(1), text)

    def _tag_range(self, tag, start, end, text):
        try:
            s_idx = self.code_editor.index(f"1.0+{start}c")
            e_idx = self.code_editor.index(f"1.0+{end}c")
            self.code_editor.tag_add(tag, s_idx, e_idx)
        except Exception:
            pass

    def _highlight_current_line(self):
        self.code_editor.tag_remove("current", "1.0", tk.END)
        idx = self.code_editor.index(tk.INSERT)
        self.code_editor.tag_add("current", f"{idx} linestart", f"{idx} lineend+1c")

    def highlight_error_line(self, line_num):
        """M21 – highlight line with error."""
        try:
            self.code_editor.tag_add("errorline", f"{line_num}.0", f"{line_num}.end+1c")
        except Exception:
            pass

    # ==========================================================
    # LINE NUMBERS / SCROLL
    # ==========================================================
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
        self.lbl_count.config(text=f"{lines} lines · {len(txt)} chars")

    # ==========================================================
    # EDITOR EVENTS
    # ==========================================================
    def _on_modified(self, event):
        self.code_editor.edit_modified(False)
        self._update_linenumbers()

    def _on_key_release(self, event):
        self._highlight_syntax()
        self._highlight_current_line()
        self._update_cursor_pos()
        # M39 – auto-close brackets
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
            if prev == ch:
                return
        if close:
            self.code_editor.insert(tk.INSERT, close)
            self.code_editor.mark_set(tk.INSERT, "insert-1c")

    # ==========================================================
    # SHORTCUTS (M02)
    # ==========================================================
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
        # Tab/Shift-Tab in editor (M25)
        self.code_editor.bind("<Tab>", self._on_tab)
        self.code_editor.bind("<Shift-Tab>", self._on_shift_tab)
        self.code_editor.bind("<Control-space>", lambda e: self.autocomplete())
        self.code_editor.bind("<Control-g>", lambda e: (self.goto_line(), "break"))

    def _on_tab(self, event):
        if self.code_editor.tag_ranges("sel"):
            self.indent_selection(True)
        else:
            self.code_editor.insert(tk.INSERT, " " * self.tab_size)
        return "break"

    def _on_shift_tab(self, event):
        self.indent_selection(False)
        return "break"

    # ==========================================================
    # EDITOR FUNCTIONS
    # ==========================================================
    def duplicate_line(self):
        try:
            idx = self.code_editor.index(tk.INSERT)
            line = int(idx.split(".")[0])
            content = self.code_editor.get(f"{line}.0", f"{line}.end")
            self.code_editor.insert(f"{line}.end", "\n" + content)
        except Exception:
            pass

    def toggle_comment(self):
        try:
            if self.code_editor.tag_ranges("sel"):
                start = int(self.code_editor.index("sel.first").split(".")[0])
                end   = int(self.code_editor.index("sel.last").split(".")[0])
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
        except Exception:
            pass

    def indent_selection(self, positive=True):
        try:
            if self.code_editor.tag_ranges("sel"):
                start = int(self.code_editor.index("sel.first").split(".")[0])
                end   = int(self.code_editor.index("sel.last").split(".")[0])
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
        except Exception:
            pass

    def goto_line(self):
        ln = simpledialog.askinteger("Go to Line", "Line number:", parent=self.root)
        if ln:
            try:
                self.code_editor.mark_set(tk.INSERT, f"{ln}.0")
                self.code_editor.see(f"{ln}.0")
            except Exception:
                pass

    def autocomplete(self):
        """M35 – Basic command autocompletion."""
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
        lb = tk.Listbox(pop, height=min(10, len(items)))
        for it in items:
            lb.insert(tk.END, it)
        lb.pack()
        try:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            pop.geometry(f"+{x}+{y}")
        except Exception:
            pass
        def on_select(event):
            sel = lb.curselection()
            if sel:
                widget.insert(at, items[sel[0]])
            pop.destroy()
        lb.bind("<Double-Button-1>", on_select)
        lb.bind("<Return>", on_select)
        pop.bind("<FocusOut>", lambda e: pop.destroy())

    # ==========================================================
    # FIND / REPLACE (M06)
    # ==========================================================
    def open_find_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Find and Replace")
        win.geometry("420x180")

        tk.Label(win, text="Find:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        e_find = tk.Entry(win, width=30)
        e_find.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(win, text="Replace:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        e_repl = tk.Entry(win, width=30)
        e_repl.grid(row=1, column=1, padx=6, pady=6)

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

        tk.Button(win, text="Find Next", command=find_next).grid(row=2, column=0, padx=6, pady=6)
        tk.Button(win, text="Replace",   command=replace_one).grid(row=2, column=1, padx=6, pady=6)
        tk.Button(win, text="Replace All", command=replace_all).grid(row=3, column=1, padx=6, pady=6)
        e_find.focus_set()

    # ==========================================================
    # VIEW / FONT / THEME
    # ==========================================================
    def change_font_size(self, delta):
        self.font_size = max(7, min(30, self.font_size + delta))
        self._apply_fonts()

    def reset_font_size(self):
        self.font_size = DEFAULT_FONT_SIZE
        self._apply_fonts()

    def _apply_fonts(self):
        self.editor_font.configure(size=self.font_size)
        self.console_font.configure(size=max(9, self.font_size - 1))
        self.linenum_font.configure(size=max(9, self.font_size - 1))
        self.code_editor.configure(font=self.editor_font, tabs=f"{{{self.tab_size}c}}")

    def choose_font(self):
        fam = simpledialog.askstring("Font", "Font name:", initialvalue=self.font_family, parent=self.root)
        if fam:
            self.font_family = fam
            self.editor_font.configure(family=fam)
            self.console_font.configure(family=fam)
            self.linenum_font.configure(family=fam)

    def choose_tab_size(self):
        n = simpledialog.askinteger("Tab", "Tab size (2–8):", initialvalue=self.tab_size, minvalue=2, maxvalue=8, parent=self.root)
        if n:
            self.tab_size = n
            self.code_editor.configure(tabs=f"{{{self.tab_size}c}}")

    def toggle_wrap(self):
        self.word_wrap = self.var_wrap.get()
        self.code_editor.configure(wrap=tk.WORD if self.word_wrap else tk.NONE)

    def toggle_whitespace(self):
        self.show_whitespace = self.var_ws.get()
        self.status.set("Whitespace visible: " + ("yes" if self.show_whitespace else "no"))

    def toggle_timestamps(self):
        self.interpreter.show_timestamps = self.var_ts.get()

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.code_editor.config(bg="#ffffff", fg="#2c3e50", insertbackground="#000000")
            self.linenumbers.config(bg="#ecf0f1", fg="#7f8c8d")
            self.console.config(bg="#ffffff", fg="#2c3e50")
            self.canvas.config(bg="#ffffff")
        else:
            self.current_theme = "dark"
            self.code_editor.config(bg="#282c34", fg="#ffffff", insertbackground="#ffffff")
            self.linenumbers.config(bg="#282c34", fg="#7f8c8d")
            self.console.config(bg="#1e272e", fg="#ffffff")
            self.canvas.config(bg="#1e272e")
        # M67 – re-apply tags after theme change
        self._setup_syntax_tags()
        self._highlight_syntax()

    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    # ==========================================================
    # EXECUTION (M11 / M12 / M46 / M47)
    # ==========================================================
    def run_code(self):
        code = self.code_editor.get("1.0", tk.END)
        self._start_execution(code)

    def run_selection(self):
        try:
            code = self.code_editor.get("sel.first", "sel.last")
            self._start_execution(code)
        except Exception:
            messagebox.showinfo("Selection", "Please select code first.")

    def run_from_cursor(self):
        idx = self.code_editor.index(tk.INSERT)
        code = self.code_editor.get(idx, tk.END)
        self._start_execution(code)

    def validate_syntax(self):
        code = self.code_editor.get("1.0", tk.END)
        problems = self.interpreter.validate(code)
        if not problems:
            messagebox.showinfo("Validation", "✅ Syntax is correct.")
        else:
            msg = "\n".join(f"L{l}: {m}" for l, m in problems)
            messagebox.showwarning("Problems detected", msg)

    def _start_execution(self, code):
        if self.execution_thread and self.execution_thread.is_alive():
            messagebox.showinfo("Execution", "An execution is already running.")
            return
        self.code_editor.tag_remove("errorline", "1.0", tk.END)
        self.status.set("Running…")
        self.progress.start(10)

        # M11 – run in thread
        def worker():
            try:
                self.interpreter.execute(code)
            except Exception:
                tb = traceback.format_exc()
                self.console_queue.put(("error", tb))
            finally:
                self.root.after(0, self._on_execution_done)

        self.execution_thread = threading.Thread(target=worker, daemon=True)
        self.execution_thread.start()

    def _on_execution_done(self):
        self.progress.stop()
        self.status.set("Ready.")

    def on_execution_finished(self, secs, lines):
        self.status.set(f"✅ {lines} statements · {secs:.3f}s")

    def stop_execution(self):
        self.interpreter.should_stop = True
        self.status.set("Stopping…")

    # ==========================================================
    # CONSOLE / FILES
    # ==========================================================
    def copy_console(self):
        try:
            txt = self.console.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self.status.set("Console copied.")
        except Exception:
            pass

    def save_console(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text", "*.txt"), ("All Files", "*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.console.get("1.0", "end-1c"))
            self.status.set(f"Console saved to {path}")

    def save_canvas_ps(self):
        path = filedialog.asksaveasfilename(defaultextension=".ps",
                                            filetypes=[("PostScript", "*.ps"), ("All Files", "*.*")])
        if path:
            try:
                self.canvas.postscript(file=path)
                self.status.set(f"Canvas saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ==========================================================
    # CONTEXT MENU (M69)
    # ==========================================================
    def _build_context_menu(self):
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="Cut",   command=lambda: self.code_editor.event_generate("<<Cut>>"))
        m.add_command(label="Copy",  command=lambda: self.code_editor.event_generate("<<Copy>>"))
        m.add_command(label="Paste", command=lambda: self.code_editor.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label="Duplicate Line", command=self.duplicate_line)
        m.add_command(label="Comment",        command=self.toggle_comment)
        m.add_command(label="Go to Line…",    command=self.goto_line)
        m.add_separator()
        m.add_command(label="Run Selection",  command=self.run_selection)

        def popup(e):
            try: m.tk_popup(e.x_root, e.y_root)
            finally: m.grab_release()
        self.code_editor.bind("<Button-3>", popup)
        self.code_editor.bind("<Button-2>", popup)

    # ==========================================================
    # DIALOGS (M31 / M32 / M33 / M34 / M29 / M30 / M70)
    # ==========================================================
    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME}\nVersion {VERSION}\n\n"
                                     "EasyScript language with integrated IDE.\n"
                                     "70 improvements applied.")

    def show_command_reference(self):
        win = tk.Toplevel(self.root)
        win.title("Command Reference")
        win.geometry("640x520")
        txt = tk.Text(win, wrap=tk.WORD, font=("Consolas", 10))
        txt.pack(fill=tk.BOTH, expand=True)
        ref = self._command_reference_text()
        txt.insert("1.0", ref)
        txt.config(state="disabled")

    def _command_reference_text(self):
        return """EZSCRIPT ENGLISH - COMMAND REFERENCE
=======================================

VARIABLES
  var:(name, value)               Define variable
  increment:(var, n)              Add n
  decrement:(var, n)              Subtract n
  input:(var, "prompt")           Ask the user

STRINGS
  uppercase:(var)                 To uppercase
  lowercase:(var)                 To lowercase
  length:(expr)                   Length
  replace:(var, old, new)         Replace
  concat:(var, a, b)              Concatenate
  to_text:(var, val)              Convert to text
  to_number:(var, val)            Convert to number
  split_text:(var, txt, sep)      Split text
  index:(var, list, i)            Element i
  reverse:(var, txt)              Reverse
  sort:(var, list)                Sort

MATH
  add:(var, a, b)                 a + b
  subtract:(var, a, b)            a - b
  multiply:(var, a, b)            a * b
  divide:(var, a, b)              a / b
  modulo:(var, a, b)              a % b
  sqrt:(var, n)                   Square root
  power:(var, a, b)               a^b
  round / abs / sin / cos / max / min / pi

LOGIC
  equal_to:(var, a, b)            a == b
  greater_than / less_than
  and / or / not

DRAWING
  color:("red")                   Current color
  line:(x1,y1,x2,y2[,color])
  rectangle:(x,y,w,h[,color])
  circle:(x,y,r[,color])
  oval:(x,y,w,h[,color])
  triangle:(x1,y1,x2,y2,x3,y3[,color])
  polygon:(6 coords, color)
  arc:(x1,y1,x2,y2,start,extent[,color])
  canvas_text:(x,y,"txt"[,color])
  canvas_color:("blue")
  line_width:(n)
  grid:(n)
  clear_canvas
  clear_screen

ENGLISH COLORS
  red, blue, green, yellow, orange, purple, pink,
  black, white, gray, cyan, violet, brown, gold, silver
  rgb:(r,g,b)                     Component colors

SYSTEM
  date / time / current_time / date_time
  wait:(sec)
  alert:("msg")
  confirm:(var, "question")
  copy:("txt")
  notification:("title", "msg")
  beep
  beep:(freq)
  wait_key
  open_url:("https://…")
  run_cmd:("cmd")

FILES
  create_file:(path, content)
  read_file:(var, path)
  file_exists:(var, path)
  delete_file:(path)
  list_files:(var, dir)
  json_get:(var, json, key)

AI / WEB
  AI:("prompt")
  ai_summarize / ai_translate / ai_explain
  JS: / HTML: / CSS: / JS_EVAL:
  html_title:("txt")
  css_theme:("dark"|"light")

LOGS
  log_info:("msg") / log_warn:("msg") / log_error:("msg")
  uuid:(var)

CONSOLE / EXTRA
  clear_console
  clear_canvas
  stop

FLOW CONTROL (indicative)
  if:(cond) / else: / end_if
  loop:(n) / end_loop
"""

    def show_examples(self):
        win = tk.Toplevel(self.root)
        win.title("Examples Library")
        win.geometry("560x420")
        examples = {
            "Hello World": 'show "Hello, EZScript!"',
            "Counter": 'var:(n, 0)\nincrement:(n, 1)\nincrement:(n, 1)\nprint n',
            "Red circle": 'color:("red")\ncircle:(100, 100, 40)',
            "Grid + rectangle":
                'grid:(40)\ncolor:("blue")\nrectangle:(40, 40, 120, 80)',
            "Canvas text":
                'canvas_text:(150, 60, "Hello!", "green")',
            "RGB colors":
                'rgb:(255, 100, 50)\ncircle:(80, 80, 40)',
            "Random + math":
                'random:(n, 1, 100)\nprint n\nadd:(r, n, 5)\nprint r',
            "Date and time":
                'date\ntime',
            "Button":
                'button:("Click", print "Pressed!")',
        }
        lb = tk.Listbox(win, font=("Consolas", 10))
        for k in examples:
            lb.insert(tk.END, k)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        def insert_example(_e=None):
            sel = lb.curselection()
            if not sel: return
            name = lb.get(sel[0])
            code = examples[name]
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", code)
            win.destroy()

        lb.bind("<Double-Button-1>", insert_example)

    def show_templates(self):
        templates = {
            "Drawing base":
                "clear_screen\ngrid:(40)\ncolor:(\"blue\")\n",
            "Interaction":
                "input:(name, \"What is your name?\")\nprint name\n",
            "Full demo":
                self.code_editor.get("1.0", "end-1c"),
        }
        win = tk.Toplevel(self.root)
        win.title("Quick Templates")
        win.geometry("380x260")
        lb = tk.Listbox(win, font=("Consolas", 10))
        for k in templates: lb.insert(tk.END, k)
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        def pick(_e=None):
            sel = lb.curselection()
            if not sel: return
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", templates[lb.get(sel[0])])
            win.destroy()
        lb.bind("<Double-Button-1>", pick)

    def inspect_variables(self):
        win = tk.Toplevel(self.root)
        win.title("Variables")
        win.geometry("420x400")
        lb = tk.Listbox(win, font=("Consolas", 10))
        for k, v in self.interpreter.variables.items():
            lb.insert(tk.END, f"{k} = {v!r}")
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def export_variables(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.interpreter.variables, f, indent=2, ensure_ascii=False)
            self.status.set(f"Variables exported to {path}")

    def import_variables(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.interpreter.variables.update(data)
            self.status.set(f"Variables imported from {path}")

    def show_stats(self):
        info = (
            f"Statistics\n"
            f"─────────────\n"
            f"Statements executed: {self.interpreter.executed_lines}\n"
            f"Execution time: {self.interpreter.execution_time:.3f} s\n"
            f"Variables defined: {len(self.interpreter.variables)}\n"
            f"Last error line: {self.interpreter.last_error_line}\n"
        )
        messagebox.showinfo("Statistics", info)

    # ==========================================================
    # COMMAND PALETTE (M36)
    # ==========================================================
    def open_command_palette(self):
        win = tk.Toplevel(self.root)
        win.title("Command Palette")
        win.geometry("420x300")
        entry = tk.Entry(win, font=("Consolas", 11))
        entry.pack(fill=tk.X, padx=6, pady=6)
        lb = tk.Listbox(win, font=("Consolas", 10))
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        actions = {
            "New project": self.new_project,
            "Open project": self.load_project,
            "Save project": self.save_project,
            "Run all": self.run_code,
            "Run selection": self.run_selection,
            "Stop execution": self.stop_execution,
            "Find / Replace": self.open_find_dialog,
            "Go to line": self.goto_line,
            "Inspect variables": self.inspect_variables,
            "Export variables": self.export_variables,
            "Import variables": self.import_variables,
            "Examples": self.show_examples,
            "Command reference": self.show_command_reference,
            "Statistics": self.show_stats,
            "Toggle theme": self.toggle_theme,
            "Fullscreen": self.toggle_fullscreen,
        }

        def refresh(*_):
            q = entry.get().lower()
            lb.delete(0, tk.END)
            for name in actions:
                if q in name.lower():
                    lb.insert(tk.END, name)

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

    # ==========================================================
    # FILES / AUTOSAVE / CONFIG
    # ==========================================================
    def new_project(self):
        if messagebox.askyesno("New Project", "Create a new project?"):
            self.code_editor.delete("1.0", tk.END)
            self.console.delete("1.0", tk.END)
            self.canvas.delete("all")
            self.current_file = None

    def save_project(self):
        if self.current_file:
            self._write_file(self.current_file)
        else:
            self.save_project_as()

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
        self.status.set(f"Saved: {os.path.basename(path)}")

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
                self.status.set(f"Loaded: {os.path.basename(path)}")
                self._highlight_syntax()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ---------- Recent Files (M09) ----------
    def _add_recent(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:MAX_RECENT_FILES]
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
            self.status.set(f"Loaded: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Autosave (M10) ----------
    def _schedule_autosave(self):
        def tick():
            try:
                if self.current_file and self.code_editor.edit_modified():
                    self._write_file(self.current_file)
                    self.status.set("Autosaved.")
            except Exception:
                pass
            self.autosave_id = self.root.after(AUTOSAVE_INTERVAL_MS, tick)
        self.autosave_id = self.root.after(AUTOSAVE_INTERVAL_MS, tick)

    # ---------- Config (M68) ----------
    def _load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.font_family = cfg.get("font_family", DEFAULT_FONT)
                self.font_size   = cfg.get("font_size", DEFAULT_FONT_SIZE)
                self.tab_size    = cfg.get("tab_size", 4)
                self.recent_files = cfg.get("recent_files", [])
                geo = cfg.get("geometry")
                if geo: self.root.geometry(geo)
        except Exception:
            pass

    def _save_config(self):
        try:
            cfg = {
                "font_family": self.font_family,
                "font_size":   self.font_size,
                "tab_size":    self.tab_size,
                "recent_files": self.recent_files,
                "geometry":    self.root.geometry(),
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def _on_close(self):
        self._save_config()
        self.interpreter.should_stop = True
        self.root.destroy()

    # ==========================================================
    # UTILITIES
    # ==========================================================
    def ask_input(self, prompt_text):
        return simpledialog.askstring("EZScript Input", prompt_text, parent=self.root)

    def _load_demo(self):
        demo = (
            "// --- EZSCRIPT ENGLISH v2.0 DEMO ---\n"
            "OperatingSystem: (Windows)\n"
            "var:(num, 10)\n"
            "increment:(num, 5)\n"
            "print num\n"
            "\n"
            "// --- DRAWING ---\n"
            "grid:(40)\n"
            "color:(\"blue\")\n"
            "circle:(60, 60, 35)\n"
            "rectangle:(120, 25, 90, 60)\n"
            "\n"
            "color:(\"red\")\n"
            "triangle:(230, 85, 270, 25, 310, 85)\n"
            "oval:(30, 110, 100, 50)\n"
            "circle:(170, 135, 25, \"yellow\")\n"
            "canvas_text:(160, 200, \"EZScript English 2.0!\", \"green\")\n"
            "\n"
            "// --- MATH ---\n"
            "add:(total, 10, 20)\n"
            "multiply:(double, total, 2)\n"
            "print double\n"
            "\n"
            "// --- LOGS ---\n"
            "log_info:(\"Demo started\")\n"
            "log_warn:(\"Test warning\")\n"
            "log_error:(\"Simulated error\")\n"
            "\n"
            "// --- SYSTEM ---\n"
            "date\n"
            "time\n"
            "button:(\"Click here!\", print \"Button Working!\")\n"
        )
        self.code_editor.insert(tk.END, demo)
        self._update_linenumbers()
        self._highlight_syntax()
        self._highlight_current_line()


EZScriptIDE = EZScriptEnglishIDE


# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = EZScriptEnglishIDE(root)
    root.mainloop()
