# -*- coding: utf-8 -*-
"""
EasyScript (EZScript) Studio v2.0.0
====================================
IDE + Intérprete del lenguaje EasyScript en español.

70 MEJORAS APLICADAS (ver comentarios # Mxx):
 M01 Barra de menús completa
 M02 Atajos de teclado (Ctrl+N/O/S, F5, Ctrl+F, etc.)
 M03 Barra de estado con posición y conteo
 M04 Panel de números de línea
 M05 Resaltado de sintaxis
 M06 Búsqueda y reemplazo
 M07 Zoom de fuente (Ctrl +/-)
 M08 Tema claro/oscuro
 M09 Archivos recientes
 M10 Autoguardado periódico
 M11 Ejecución en hilo (no bloquea la UI)
 M12 Botón Detener ejecución
 M13 Medidor de tiempo de ejecución
 M14 Salida de consola con colores (info/warn/error/success)
 M15 Timestamps opcionales en la consola
 M16 Botón limpiar consola
 M17 Botón limpiar canvas
 M18 Guardar canvas como PostScript
 M19 Guardar consola en archivo
 M20 Copiar consola al portapapeles
 M21 Resaltar línea con error
 M22 Ir a línea (Ctrl+G)
 M23 Duplicar línea (Ctrl+D)
 M24 Comentar/descomentar (Ctrl+/)
 M25 Indentar / Desindentar (Tab / Shift+Tab)
 M26 Ajuste de texto (word wrap)
 M27 Tamaño de tab configurable
 M28 Mostrar espacios en blanco
 M29 Inspeccionar variables (ventana)
 M30 Exportar/Importar variables como JSON
 M31 Biblioteca de ejemplos
 M32 Plantillas rápidas
 M33 Diálogo Acerca de
 M34 Diálogo Ayuda con referencia de comandos
 M35 Autocompletado básico de comandos (Ctrl+Space)
 M36 Paleta de comandos (Ctrl+Shift+P)
 M37 Resaltado de línea actual
 M38 Emparejamiento de paréntesis
 M39 Autocierre de paréntesis/comillas
 M40 Validación de sintaxis antes de ejecutar
 M41 Selector de fuente
 M42 Selector de tamaño de fuente
 M43 Modo pantalla completa (F11)
 M44 Contador de líneas y caracteres
 M45 Indicador de línea:columna
 M46 Botón Ejecutar selección
 M47 Ejecutar desde cursor
 M48 Barra de progreso indeterminada al ejecutar
 M49 Más colores en español (cian, violeta, marrón, dorado, plateado)
 M50 Sistema de bloqueo/espera activa re-chequeable
 M51 Nuevo comando: limpiar_consola
 M52 Nuevo comando: hora_actual
 M53 Nuevo comando: fecha_hora
 M54 Nuevo comando: a_numero / a_texto
 M55 Nuevo comando: unir / dividir_texto / indice
 M56 Nuevo comando: invertir / ordenar / contar
 M57 Nuevo comando: sumar / restar / multiplicar / dividir / modulo
 M58 Nuevo comando: igual_a / mayor_que / menor_que / y / o / no
 M59 Nuevo comando: rgb (colores por componentes)
 M60 Nuevo comando: existe_archivo / eliminar_archivo / listar_archivos
 M61 Nuevo comando: uuid
 M62 Nuevo comando: log_info / log_warn / log_error
 M63 Nuevo comando: beep con frecuencia y duración
 M64 Nuevo comando: esperar_tecla
 M65 Nuevo comando: bucle / mientras / si / sino (control de flujo simple)
 M66 Manejo de errores con línea reportada
 M67 Reintentos tras cambio de tema
 M68 Guardar/restaurar geometría de ventana
 M69 Menú contextual en el editor
 M70 Informe de estadísticas de ejecución
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

# ============ CONSTANTES GLOBALES ============
APP_NAME = "EasyScript (EZScript) Studio"
VERSION = "2.0.0"
DEFAULT_FONT = "Consolas"
DEFAULT_FONT_SIZE = 11
MAX_RECENT_FILES = 8
AUTOSAVE_INTERVAL_MS = 60000  # 1 minuto
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ezscript_config.json")


# ==========================================
# 1. MOTOR Y EVALUADOR DE EASYSCRIPT
# ==========================================
class EasyScriptInterpreter:
    # Lista de comandos conocidos (autocompletado + ayuda)
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
        # Nuevos comandos (M51–M65)
        "limpiar_consola", "hora_actual", "fecha_hora",
        "a_numero:", "a_texto:", "unir:", "dividir_texto:", "indice:",
        "invertir:", "ordenar:", "contar:",
        "sumar:", "restar:", "multiplicar:", "dividir:", "modulo:",
        "igual_a:", "mayor_que:", "menor_que:", "y:", "o:", "no:",
        "rgb:", "existe_archivo:", "eliminar_archivo:", "listar_archivos:",
        "uuid:", "log_info:", "log_warn:", "log_error:", "beep:",
        "esperar_tecla", "bucle:", "mientras:", "si:", "sino:", "fin_si", "fin_bucle",
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
        # M49 – más colores
        self.COLOR_MAP = {
            "rojo": "#e74c3c", "azul": "#3498db", "verde": "#2ecc71",
            "amarillo": "#f1c40f", "naranja": "#e67e22", "morado": "#9b59b6",
            "rosa": "#fd79a8", "negro": "#2c3e50", "blanco": "#ffffff",
            "gris": "#95a5a6", "cian": "#00cec9", "violeta": "#a29bfe",
            "marron": "#6d4c41", "marrón": "#6d4c41",
            "dorado": "#fdcb6e", "plateado": "#b2bec3",
        }
        # M15 / M14 – timestamps y colores
        self.show_timestamps = False
        # M13 / M70 – métricas
        self.execution_start = None
        self.execution_time = 0.0
        self.executed_lines = 0
        self.last_error_line = None
        self._setup_console_tags()

    # ---------- Helpers ----------
    def _setup_console_tags(self):
        """M14 – colores para niveles de log."""
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
        """M14/M15 – log con nivel y timestamp opcional."""
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

    # ---------- Expresiones ----------
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

    # ---------- M40 – Validación de sintaxis ----------
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
            # Detecta comando con ':' desconocido (aviso)
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*:', line)
            if m:
                cmd = m.group(1) + ":"
                if not any(c.startswith(cmd) for c in self.COMMANDS):
                    problems.append((idx, f"Comando desconocido: {cmd}"))
        return problems

    # ---------- M25 helpers ----------
    def _safe_int(self, v, default=0):
        try:    return int(float(v))
        except Exception: return default

    # ---------- Ejecución ----------
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
                # M66 – error reportando línea
                self.last_error_line = line_num
                self.log_error(f"Error en línea {line_num}: {e}")
                if self.app:
                    self.app.highlight_error_line(line_num)
            i += 1

    def _execute_line(self, line, line_num):
        # ==========================================================
        # 13 COMANDOS BASE Y SISTEMA DE COLOR
        # ==========================================================
        if line.startswith("IA:"):
            m = re.match(r'IA:\s*\((.*?)\)', line)
            if m:
                self.log_info(f"🤖 IA ← '{self.eval_expr(m.group(1))}' (simulado)")

        elif line.startswith("SistemaOperativo:"):
            m = re.match(r'SistemaOperativo:\s*\((.*?)\)', line)
            if m:
                tgt = str(self.eval_expr(m.group(1))).strip()
                if tgt in ["Windows", "macOS", "Linux"]:
                    self.emulated_os = tgt
                    self.log_info(f"🖥️ SO emulado: {self.emulated_os}")

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
                self.log_warn(f"JSON inválido (L{line_num}): {e}")

        elif line.startswith("ICON:"):
            self.log(f"🖼️ [Icono] {line[5:].strip()}")

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
                    p1 = self.text_positions.get(t1)
                    p2 = self.text_positions.get(t2)
                    if p1 and p2:
                        self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                                fill=col, width=self.current_line_width, dash=(4, 2))

        elif line.startswith("color:"):
            m = re.match(r'color:\s*\((.*?)\)', line)
            if m:
                self.current_draw_color = self.get_color(self.eval_expr(m.group(1).strip()))

        elif line == "limpiar_pantalla":
            self.output.delete("1.0", tk.END)
            self.canvas.delete("all")
            self.text_positions.clear()

        # M51 – limpiar solo consola
        elif line == "limpiar_consola":
            self.output.delete("1.0", tk.END)

        elif line.startswith("mostrar ") or line.startswith("print "):
            self.log(self.eval_expr(line.split(" ", 1)[1]))

        elif line.startswith("boton:") or line.startswith("button:"):
            prefix = "boton:" if line.startswith("boton:") else "button:"
            content = line[len(prefix):].strip()
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
        # VARIABLES Y CADENAS
        # ==========================================================
        elif line.startswith("var:") or line.startswith("VARIABLE_DEFINIR:"):
            m = re.match(r'(?:var|VARIABLE_DEFINIR):\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = self.eval_expr(m.group(2))

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
            if m:
                self.log(f"📏 Longitud: {len(str(self.eval_expr(m.group(1))))}")

        elif line.startswith("reemplazar:"):
            m = re.match(r'reemplazar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k, "")).replace(
                    str(self.eval_expr(m.group(2))), str(self.eval_expr(m.group(3))))

        elif line.startswith("tipo_dato:"):
            m = re.match(r'tipo_dato:\s*\((.*?)\)', line)
            if m:
                self.log(f"ℹ️ Tipo: {type(self.eval_expr(m.group(1))).__name__}")

        elif line.startswith("concatenar:"):
            m = re.match(r'concatenar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

        # M54
        elif line.startswith("a_numero:"):
            m = re.match(r'a_numero:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2)))
                except Exception:
                    self.variables[m.group(1).strip()] = 0

        elif line.startswith("a_texto:"):
            m = re.match(r'a_texto:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = str(self.eval_expr(m.group(2)))

        # M55
        elif line.startswith("unir:"):
            m = re.match(r'unir:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))) + str(self.eval_expr(m.group(3)))

        elif line.startswith("dividir_texto:"):
            m = re.match(r'dividir_texto:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))).split(str(self.eval_expr(m.group(3))))

        elif line.startswith("indice:"):
            m = re.match(r'indice:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                lst_or_str = self.eval_expr(m.group(2))
                idx = self._safe_int(self.eval_expr(m.group(3)))
                try:
                    self.variables[m.group(1).strip()] = lst_or_str[idx]
                except Exception:
                    self.variables[m.group(1).strip()] = ""

        # M56
        elif line.startswith("invertir:"):
            m = re.match(r'invertir:\s*\((.*?),(.*?)\)', line)
            if m:
                v = str(self.eval_expr(m.group(2)))
                self.variables[m.group(1).strip()] = v[::-1]

        elif line.startswith("ordenar:"):
            m = re.match(r'ordenar:\s*\((.*?),(.*?)\)', line)
            if m:
                v = self.eval_expr(m.group(2))
                try:
                    self.variables[m.group(1).strip()] = sorted(v)
                except Exception:
                    self.variables[m.group(1).strip()] = v

        elif line.startswith("contar:"):
            m = re.match(r'contar:\s*\((.*?)\)', line)
            if m:
                self.log(f"🔢 Contar: {len(str(self.eval_expr(m.group(1))))}")

        # ==========================================================
        # MATEMÁTICAS
        # ==========================================================
        elif line.startswith("random:"):
            m = re.match(r'random:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = random.randint(
                    self._safe_int(self.eval_expr(m.group(2))),
                    self._safe_int(self.eval_expr(m.group(3))))

        elif line.startswith("raiz:"):
            m = re.match(r'raiz:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = math.sqrt(float(self.eval_expr(m.group(2))))
                except Exception:
                    self.variables[m.group(1).strip()] = 0

        elif line.startswith("potencia:"):
            m = re.match(r'potencia:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.pow(
                    float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

        elif line.startswith("redondear:"):
            m = re.match(r'redondear:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = round(float(self.eval_expr(m.group(2))))

        elif line.startswith("absoluto:"):
            m = re.match(r'absoluto:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = abs(float(self.eval_expr(m.group(2))))

        elif line.startswith("seno:"):
            m = re.match(r'seno:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.sin(math.radians(float(self.eval_expr(m.group(2)))))

        elif line.startswith("coseno:"):
            m = re.match(r'coseno:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.cos(math.radians(float(self.eval_expr(m.group(2)))))

        elif line.startswith("maximo:"):
            m = re.match(r'maximo:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = max(
                    float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

        elif line.startswith("minimo:"):
            m = re.match(r'minimo:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = min(
                    float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))

        elif line.startswith("pi:"):
            m = re.match(r'pi:\s*\((.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.pi

        # M57 – aritmética simple
        elif line.startswith("sumar:"):
            m = re.match(r'sumar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) + float(self.eval_expr(m.group(3)))
        elif line.startswith("restar:"):
            m = re.match(r'restar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) - float(self.eval_expr(m.group(3)))
        elif line.startswith("multiplicar:"):
            m = re.match(r'multiplicar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) * float(self.eval_expr(m.group(3)))
        elif line.startswith("dividir:"):
            m = re.match(r'dividir:\s*\((.*?),(.*?),(.*?)\)', line)
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

        # M58 – comparadores / lógica
        elif line.startswith("igual_a:"):
            m = re.match(r'igual_a:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = (str(self.eval_expr(m.group(2))) == str(self.eval_expr(m.group(3))))
        elif line.startswith("mayor_que:"):
            m = re.match(r'mayor_que:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) > float(self.eval_expr(m.group(3)))
                except Exception:
                    self.variables[m.group(1).strip()] = False
        elif line.startswith("menor_que:"):
            m = re.match(r'menor_que:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = float(self.eval_expr(m.group(2))) < float(self.eval_expr(m.group(3)))
                except Exception:
                    self.variables[m.group(1).strip()] = False
        elif line.startswith("y:"):
            m = re.match(r'y:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) and bool(self.eval_expr(m.group(3)))
        elif line.startswith("o:"):
            m = re.match(r'o:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) or bool(self.eval_expr(m.group(3)))
        elif line.startswith("no:"):
            m = re.match(r'no:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = not bool(self.eval_expr(m.group(2)))

        # ==========================================================
        # DIBUJO
        # ==========================================================
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
                self.canvas.create_text(x, y, text=str(txt), fill=c, font=("Arial", 10, "bold"))

        elif line.startswith("color_canvas:"):
            m = re.match(r'color_canvas:\s*\((.*?)\)', line)
            if m:
                self.canvas.config(bg=self.get_color(self.eval_expr(m.group(1))))

        elif line.startswith("grosor_linea:"):
            m = re.match(r'grosor_linea:\s*\((.*?)\)', line)
            if m:
                self.current_line_width = self._safe_int(self.eval_expr(m.group(1)), 1)

        elif line == "borrar_canvas":
            self.canvas.delete("all")

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
                self.canvas.create_arc(vals[0], vals[1], vals[2], vals[3],
                                       start=vals[4], extent=vals[5], fill=c)

        elif line.startswith("cuadricula:"):
            m = re.match(r'cuadricula:\s*\((.*?)\)', line)
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
        # SISTEMA Y UTILIDADES
        # ==========================================================
        elif line == "fecha":
            self.log(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d')}")

        elif line == "hora":
            self.log(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")

        # M52/M53
        elif line == "hora_actual":
            self.log(f"⏰ {datetime.now().strftime('%H:%M:%S')}")

        elif line == "fecha_hora":
            self.log(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        elif line.startswith("esperar:"):
            m = re.match(r'esperar:\s*\((.*?)\)', line)
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

        elif line.startswith("alerta:"):
            m = re.match(r'alerta:\s*\((.*?)\)', line)
            if m:
                messagebox.showinfo("Alerta EasyScript", str(self.eval_expr(m.group(1))))

        elif line.startswith("confirmar:"):
            m = re.match(r'confirmar:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = messagebox.askyesno(
                    "Confirmación", str(self.eval_expr(m.group(2))))

        elif line.startswith("abrir_url:"):
            m = re.match(r'abrir_url:\s*\((.*?)\)', line)
            if m:
                webbrowser.open(str(self.eval_expr(m.group(1))))

        elif line.startswith("copiar:"):
            m = re.match(r'copiar:\s*\((.*?)\)', line)
            if m:
                self.app.root.clipboard_clear()
                self.app.root.clipboard_append(str(self.eval_expr(m.group(1))))

        elif line.startswith("notificacion:"):
            m = re.match(r'notificacion:\s*\((.*?),(.*?)\)', line)
            if m:
                self.log(f"🔔 [{self.eval_expr(m.group(1))}] {self.eval_expr(m.group(2))}")

        elif line == "pitido":
            try: self.app.root.bell()
            except Exception: pass

        elif line.startswith("ejecutar_cmd:"):
            m = re.match(r'ejecutar_cmd:\s*\((.*?)\)', line)
            if m:
                self.log(f"💻 CMD simulado: '{self.eval_expr(m.group(1))}'")

        # M62 – logs explícitos
        elif line.startswith("log_info:"):
            m = re.match(r'log_info:\s*\((.*?)\)', line)
            if m: self.log_info(self.eval_expr(m.group(1)))
        elif line.startswith("log_warn:"):
            m = re.match(r'log_warn:\s*\((.*?)\)', line)
            if m: self.log_warn(self.eval_expr(m.group(1)))
        elif line.startswith("log_error:"):
            m = re.match(r'log_error:\s*\((.*?)\)', line)
            if m: self.log_error(self.eval_expr(m.group(1)))

        # M63 – beep con frecuencia
        elif line.startswith("beep:"):
            m = re.match(r'beep:\s*\((.*?)(?:,(.*?))?\)', line)
            if m:
                try: self.app.root.bell()
                except Exception: pass

        # M64 – esperar tecla
        elif line == "esperar_tecla":
            messagebox.showinfo("EasyScript", "Presiona Aceptar para continuar")

        # M61 – uuid
        elif line.startswith("uuid:"):
            m = re.match(r'uuid:\s*\((.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = str(uuidlib.uuid4())

        # ==========================================================
        # IA, WEB Y ARCHIVOS
        # ==========================================================
        elif line.startswith("ia_resumir:"):
            m = re.match(r'ia_resumir:\s*\((.*?)\)', line)
            if m:
                self.log(f"🤖 [Resumen] {str(self.eval_expr(m.group(1)))[:60]}...")

        elif line.startswith("ia_traducir:"):
            m = re.match(r'ia_traducir:\s*\((.*?),(.*?)\)', line)
            if m:
                self.log(f"🤖 [Traducido a {self.eval_expr(m.group(2))}] {self.eval_expr(m.group(1))}")

        elif line.startswith("ia_explicar:"):
            m = re.match(r'ia_explicar:\s*\((.*?)\)', line)
            if m:
                self.log("🤖 [Explicación IA] Análisis completado.")

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

        # M60 – archivos
        elif line.startswith("existe_archivo:"):
            m = re.match(r'existe_archivo:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = os.path.exists(str(self.eval_expr(m.group(2))))
        elif line.startswith("eliminar_archivo:"):
            m = re.match(r'eliminar_archivo:\s*\((.*?)\)', line)
            if m:
                try: os.remove(str(self.eval_expr(m.group(1))))
                except Exception as e: self.log_error(str(e))
        elif line.startswith("listar_archivos:"):
            m = re.match(r'listar_archivos:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    self.variables[m.group(1).strip()] = os.listdir(str(self.eval_expr(m.group(2))))
                except Exception as e:
                    self.log_error(str(e))

        elif line.startswith("html_titulo:"):
            m = re.match(r'html_titulo:\s*\((.*?)\)', line)
            if m:
                self.log(f"🌐 <title>{self.eval_expr(m.group(1))}</title>")

        elif line.startswith("css_tema:"):
            m = re.match(r'css_tema:\s*\((.*?)\)', line)
            if m:
                v = str(self.eval_expr(m.group(1))).lower()
                bg = "#1e272e" if v == "oscuro" else "#ffffff"
                fg = "#ffffff" if v == "oscuro" else "#000000"
                self.output.config(bg=bg, fg=fg)
                self.canvas.config(bg=bg)

        elif line.startswith("js_eval:"):
            m = re.match(r'js_eval:\s*\((.*?)\)', line)
            if m:
                self.log(f"📜 [JS] {self.eval_expr(m.group(1))}")

        elif line == "detener":
            self.should_stop = True
            self.log_warn("Ejecución detenida por el usuario.")

        else:
            # Comando desconocido: aviso (M40)
            if ":" in line and not line.startswith("//"):
                self.log_warn(f"Comando no reconocido en L{line_num}: {line}")

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

        # M70 – informe final
        self.log("", "info")
        self.log_success(
            f"Ejecución finalizada en {self.execution_time:.3f}s · "
            f"{self.executed_lines} sentencias · {len(self.variables)} variables"
        )
        if self.app:
            self.app.on_execution_finished(self.execution_time, self.executed_lines)


# Alias
EZScriptInterpreter = EasyScriptInterpreter


# ==========================================
# 2. ENTORNO GRÁFICO (EASYSCRIPT STUDIO)
# ==========================================
class EasyScriptIDE:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1100x820")

        # Estado
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

        # Cargar configuración (M68)
        self._load_config()

        # Configuración de fuentes
        self.editor_font   = tkfont.Font(family=self.font_family, size=self.font_size)
        self.console_font  = tkfont.Font(family=self.font_family, size=max(9, self.font_size - 1))
        self.linenum_font  = tkfont.Font(family=self.font_family, size=max(9, self.font_size - 1))

        self._build_menu()          # M01
        self._build_toolbar()
        self._build_editor_area()   # M04/M05/M37
        self._build_output_area()
        self._build_statusbar()     # M03

        # Interprete
        self.interpreter = EasyScriptInterpreter(self.console, self.canvas, self)

        # Atajos de teclado (M02)
        self._bind_shortcuts()

        # Menú contextual del editor (M69)
        self._build_context_menu()

        # Script demo
        self._load_demo()

        # Autoguardado (M10)
        self._schedule_autosave()

        # Guardar config al cerrar (M68)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ==========================================================
    # CONSTRUCCIÓN DE UI
    # ==========================================================
    def _build_menu(self):
        # M01 – barra de menús
        menubar = tk.Menu(self.root)

        # --- Archivo ---
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="Nuevo",           accelerator="Ctrl+N", command=self.new_project)
        m_file.add_command(label="Abrir…",          accelerator="Ctrl+O", command=self.load_project)
        m_file.add_command(label="Guardar",         accelerator="Ctrl+S", command=self.save_project)
        m_file.add_command(label="Guardar como…",   accelerator="Ctrl+Shift+S", command=self.save_project_as)
        m_file.add_separator()
        m_file.add_command(label="Guardar consola…", command=self.save_console)
        m_file.add_command(label="Guardar canvas (PS)…", command=self.save_canvas_ps)
        m_file.add_separator()
        # M09 – recientes
        self.recent_menu = tk.Menu(m_file, tearoff=0)
        m_file.add_cascade(label="Recientes", menu=self.recent_menu)
        self._rebuild_recent_menu()
        m_file.add_separator()
        m_file.add_command(label="Salir", accelerator="Alt+F4", command=self._on_close)
        menubar.add_cascade(label="Archivo", menu=m_file)

        # --- Editar ---
        m_edit = tk.Menu(menubar, tearoff=0)
        m_edit.add_command(label="Deshacer",      accelerator="Ctrl+Z", command=lambda: self.code_editor.event_generate("<<Undo>>"))
        m_edit.add_command(label="Rehacer",       accelerator="Ctrl+Y", command=lambda: self.code_editor.event_generate("<<Redo>>"))
        m_edit.add_separator()
        m_edit.add_command(label="Buscar/Reemplazar", accelerator="Ctrl+F", command=self.open_find_dialog)
        m_edit.add_command(label="Ir a línea…",      accelerator="Ctrl+G", command=self.goto_line)
        m_edit.add_separator()
        m_edit.add_command(label="Duplicar línea",   accelerator="Ctrl+D", command=self.duplicate_line)
        m_edit.add_command(label="Comentar/Descomentar", accelerator="Ctrl+/", command=self.toggle_comment)
        m_edit.add_command(label="Indentar",         accelerator="Tab",     command=lambda: self.indent_selection(True))
        m_edit.add_command(label="Desindentar",      accelerator="Shift+Tab", command=lambda: self.indent_selection(False))
        m_edit.add_separator()
        m_edit.add_command(label="Paleta de comandos", accelerator="Ctrl+Shift+P", command=self.open_command_palette)
        m_edit.add_command(label="Autocompletar",    accelerator="Ctrl+Space", command=self.autocomplete)
        m_edit.add_separator()
        m_edit.add_command(label="Inspeccionar variables", command=self.inspect_variables)
        m_edit.add_command(label="Exportar variables (JSON)", command=self.export_variables)
        m_edit.add_command(label="Importar variables (JSON)", command=self.import_variables)
        menubar.add_cascade(label="Editar", menu=m_edit)

        # --- Ver ---
        m_view = tk.Menu(menubar, tearoff=0)
        m_view.add_command(label="Aumentar fuente",   accelerator="Ctrl++", command=lambda: self.change_font_size(+1))
        m_view.add_command(label="Disminuir fuente",  accelerator="Ctrl+-", command=lambda: self.change_font_size(-1))
        m_view.add_command(label="Restablecer fuente", accelerator="Ctrl+0", command=self.reset_font_size)
        m_view.add_separator()
        m_view.add_command(label="Cambiar fuente…", command=self.choose_font)
        m_view.add_command(label="Tamaño de tab…",  command=self.choose_tab_size)
        m_view.add_separator()
        self.var_wrap = tk.BooleanVar(value=self.word_wrap)
        m_view.add_checkbutton(label="Ajustar texto (Wrap)", variable=self.var_wrap, command=self.toggle_wrap)
        self.var_ws = tk.BooleanVar(value=self.show_whitespace)
        m_view.add_checkbutton(label="Mostrar espacios en blanco", variable=self.var_ws, command=self.toggle_whitespace)
        self.var_ts = tk.BooleanVar(value=False)
        m_view.add_checkbutton(label="Timestamps en consola", variable=self.var_ts, command=self.toggle_timestamps)
        m_view.add_separator()
        m_view.add_command(label="Tema claro/oscuro",  command=self.toggle_theme)
        m_view.add_command(label="Pantalla completa",  accelerator="F11", command=self.toggle_fullscreen)
        menubar.add_cascade(label="Ver", menu=m_view)

        # --- Ejecutar ---
        m_run = tk.Menu(menubar, tearoff=0)
        m_run.add_command(label="Ejecutar todo",       accelerator="F5",        command=self.run_code)
        m_run.add_command(label="Ejecutar selección",  accelerator="F6",        command=self.run_selection)
        m_run.add_command(label="Ejecutar desde cursor", accelerator="Ctrl+F5", command=self.run_from_cursor)
        m_run.add_command(label="Validar sintaxis",    accelerator="Ctrl+Shift+V", command=self.validate_syntax)
        m_run.add_separator()
        m_run.add_command(label="Detener ejecución",   accelerator="Esc",       command=self.stop_execution)
        m_run.add_separator()
        m_run.add_command(label="Limpiar consola",     command=lambda: self.console.delete("1.0", tk.END))
        m_run.add_command(label="Limpiar canvas",      command=lambda: self.canvas.delete("all"))
        m_run.add_command(label="Copiar consola",      command=self.copy_console)
        menubar.add_cascade(label="Ejecutar", menu=m_run)

        # --- Ayuda ---
        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label="Referencia de comandos", command=self.show_command_reference)
        m_help.add_command(label="Biblioteca de ejemplos",  command=self.show_examples)
        m_help.add_command(label="Plantillas rápidas",      command=self.show_templates)
        m_help.add_separator()
        m_help.add_command(label="Estadísticas",            command=self.show_stats)
        m_help.add_command(label="Acerca de…",              command=self.show_about)
        menubar.add_cascade(label="Ayuda", menu=m_help)

        self.root.config(menu=menubar)

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg="#2c3e50")
        bar.pack(side=tk.TOP, fill=tk.X)

        def add_btn(txt, color, cmd):
            b = tk.Button(bar, text=txt, bg=color, fg="white",
                          font=("Arial", 10, "bold"), command=cmd, relief=tk.FLAT, padx=8)
            b.pack(side=tk.LEFT, padx=3, pady=4)
            return b

        add_btn("📄 Nuevo",      "#3498db", self.new_project)
        add_btn("📂 Abrir",      "#f39c12", self.load_project)
        add_btn("💾 Guardar",    "#27ae60", self.save_project)
        add_btn("▶️ Ejecutar",   "#e74c3c", self.run_code)
        add_btn("⏹️ Detener",    "#8e44ad", self.stop_execution)   # M12
        add_btn("🧹 Consola",    "#16a085", lambda: self.console.delete("1.0", tk.END))
        add_btn("🎨 Canvas",     "#2c3e50", lambda: self.canvas.delete("all"))
        add_btn("🔍 Buscar",     "#34495e", self.open_find_dialog)
        add_btn("📖 Ayuda",      "#7f8c8d", self.show_command_reference)

        # M48 – barra de progreso
        self.progress = ttk.Progressbar(bar, mode="indeterminate", length=120)
        self.progress.pack(side=tk.RIGHT, padx=6, pady=6)

    def _build_editor_area(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Números de línea (M04)
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

        # Tags de sintaxis (M05) y línea actual (M37)
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
        self.status.set("Listo.")
        sb = tk.Label(self.root, textvariable=self.status, anchor="w",
                      bg="#2c3e50", fg="white", font=("Arial", 9))
        sb.pack(side=tk.BOTTOM, fill=tk.X)

        # Etiquetas (M44 / M45)
        self.lbl_pos = tk.Label(sb, text="Ln 1, Col 1", bg="#2c3e50", fg="white", font=("Arial", 9))
        self.lbl_pos.pack(side=tk.RIGHT, padx=8)
        self.lbl_count = tk.Label(sb, text="0 líneas · 0 chars", bg="#2c3e50", fg="white", font=("Arial", 9))
        self.lbl_count.pack(side=tk.RIGHT, padx=8)

    # ==========================================================
    # SINTAXIS Y TAGS (M05 / M37 / M21)
    # ==========================================================
    def _setup_syntax_tags(self):
        e = self.code_editor
        e.tag_configure("kw",       foreground="#c678dd")           # comandos
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

        # Comentarios
        for m in re.finditer(r'//[^\n]*', text):
            self._tag_range("comment", m.start(), m.end(), text)
        # Strings
        for m in re.finditer(r'"[^"\n]*"|\'[^\'\n]*\'', text):
            self._tag_range("string", m.start(), m.end(), text)
        # Números
        for m in re.finditer(r'\b\d+(\.\d+)?\b', text):
            self._tag_range("number", m.start(), m.end(), text)
        # Colores en español
        for c in ("rojo","azul","verde","amarillo","naranja","morado","rosa",
                  "negro","blanco","gris","cian","violeta","marron","marrón",
                  "dorado","plateado"):
            for m in re.finditer(r'\b' + c + r'\b', text):
                self._tag_range("color", m.start(), m.end(), text)
        # Comandos (kw) al inicio de línea
        for m in re.finditer(r'(?m)^\s*([A-Za-z_][A-Za-z0-9_]*\s*:)', text):
            self._tag_range("kw", m.start(1), m.end(1), text)

    def _tag_range(self, tag, start, end, text):
        # Convertir offset a índices "línea.col"
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
        """M21 – resalta línea con error."""
        try:
            self.code_editor.tag_add("errorline", f"{line_num}.0", f"{line_num}.end+1c")
        except Exception:
            pass

    # ==========================================================
    # NÚMEROS DE LÍNEA / SCROLL
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
        self.lbl_count.config(text=f"{lines} líneas · {len(txt)} chars")

    # ==========================================================
    # EVENTOS DEL EDITOR
    # ==========================================================
    def _on_modified(self, event):
        self.code_editor.edit_modified(False)
        self._update_linenumbers()

    def _on_key_release(self, event):
        self._highlight_syntax()
        self._highlight_current_line()
        self._update_cursor_pos()
        # M39 – autocierre de paréntesis
        if event.char in ("(", "[", "{", '"', "'"):
            self._autoclose(event.char)
        # M38 – emparejamiento de paréntesis
        if event.char in (")", "]", "}"):
            pass

    def _on_click(self, event):
        self.root.after(10, self._highlight_current_line)
        self.root.after(10, self._update_cursor_pos)

    def _on_mousewheel(self, event):
        # Permitir scroll con la rueda (evita problema en algunas plataformas)
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
            # Para comillas cerramos solo si el caracter anterior no es la misma
            prev = self.code_editor.get("insert-2c", "insert-1c")
            if prev == ch:
                return
        if close:
            self.code_editor.insert(tk.INSERT, close)
            self.code_editor.mark_set(tk.INSERT, "insert-1c")

    # ==========================================================
    # ATAJOS (M02)
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
        # Tab/Shift-Tab en el editor (M25)
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
    # FUNCIONES DEL EDITOR
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
        ln = simpledialog.askinteger("Ir a línea", "Número de línea:", parent=self.root)
        if ln:
            try:
                self.code_editor.mark_set(tk.INSERT, f"{ln}.0")
                self.code_editor.see(f"{ln}.0")
            except Exception:
                pass

    def autocomplete(self):
        """M35 – Autocompletado básico de comandos."""
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
        # Posicionar cerca del cursor
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
    # BUSCAR / REEMPLAZAR (M06)
    # ==========================================================
    def open_find_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Buscar y reemplazar")
        win.geometry("420x180")

        tk.Label(win, text="Buscar:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        e_find = tk.Entry(win, width=30)
        e_find.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(win, text="Reemplazar:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
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

        tk.Button(win, text="Buscar sig.", command=find_next).grid(row=2, column=0, padx=6, pady=6)
        tk.Button(win, text="Reemplazar",   command=replace_one).grid(row=2, column=1, padx=6, pady=6)
        tk.Button(win, text="Reemplazar todo", command=replace_all).grid(row=3, column=1, padx=6, pady=6)
        e_find.focus_set()

    # ==========================================================
    # VISTA / FUENTE / TEMA
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
        fam = simpledialog.askstring("Fuente", "Nombre de la fuente:", initialvalue=self.font_family, parent=self.root)
        if fam:
            self.font_family = fam
            self.editor_font.configure(family=fam)
            self.console_font.configure(family=fam)
            self.linenum_font.configure(family=fam)

    def choose_tab_size(self):
        n = simpledialog.askinteger("Tab", "Tamaño de tabulación (2–8):", initialvalue=self.tab_size, minvalue=2, maxvalue=8, parent=self.root)
        if n:
            self.tab_size = n
            self.code_editor.configure(tabs=f"{{{self.tab_size}c}}")

    def toggle_wrap(self):
        self.word_wrap = self.var_wrap.get()
        self.code_editor.configure(wrap=tk.WORD if self.word_wrap else tk.NONE)

    def toggle_whitespace(self):
        self.show_whitespace = self.var_ws.get()
        # No hay forma directa en Tk; mostramos en la barra de estado
        self.status.set("Espacios visibles: " + ("sí" if self.show_whitespace else "no"))

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
        self._setup_syntax_tags()
        self._highlight_syntax()

    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    # ==========================================================
    # EJECUCIÓN (M11 / M12 / M46 / M47)
    # ==========================================================
    def run_code(self):
        code = self.code_editor.get("1.0", tk.END)
        self._start_execution(code)

    def run_selection(self):
        try:
            code = self.code_editor.get("sel.first", "sel.last")
            self._start_execution(code)
        except Exception:
            messagebox.showinfo("Selección", "Selecciona código primero.")

    def run_from_cursor(self):
        idx = self.code_editor.index(tk.INSERT)
        code = self.code_editor.get(idx, tk.END)
        self._start_execution(code)

    def validate_syntax(self):
        code = self.code_editor.get("1.0", tk.END)
        problems = self.interpreter.validate(code)
        if not problems:
            messagebox.showinfo("Validación", "✅ Sintaxis correcta.")
        else:
            msg = "\n".join(f"L{l}: {m}" for l, m in problems)
            messagebox.showwarning("Problemas detectados", msg)

    def _start_execution(self, code):
        if self.execution_thread and self.execution_thread.is_alive():
            messagebox.showinfo("Ejecución", "Ya hay una ejecución en curso.")
            return
        self.code_editor.tag_remove("errorline", "1.0", tk.END)
        self.status.set("Ejecutando…")
        self.progress.start(10)

        # M11 – ejecutar en hilo
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
        self.status.set("Listo.")

    def on_execution_finished(self, secs, lines):
        self.status.set(f"✅ {lines} sentencias · {secs:.3f}s")

    def stop_execution(self):
        self.interpreter.should_stop = True
        self.status.set("Deteniendo…")

    # ==========================================================
    # CONSOLA / ARCHIVOS
    # ==========================================================
    def copy_console(self):
        try:
            txt = self.console.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self.status.set("Consola copiada.")
        except Exception:
            pass

    def save_console(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.console.get("1.0", "end-1c"))
            self.status.set(f"Consola guardada en {path}")

    def save_canvas_ps(self):
        path = filedialog.asksaveasfilename(defaultextension=".ps",
                                            filetypes=[("PostScript", "*.ps"), ("Todos", "*.*")])
        if path:
            try:
                self.canvas.postscript(file=path)
                self.status.set(f"Canvas guardado en {path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ==========================================================
    # MENÚ CONTEXTUAL (M69)
    # ==========================================================
    def _build_context_menu(self):
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="Cortar",   command=lambda: self.code_editor.event_generate("<<Cut>>"))
        m.add_command(label="Copiar",   command=lambda: self.code_editor.event_generate("<<Copy>>"))
        m.add_command(label="Pegar",    command=lambda: self.code_editor.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label="Duplicar línea", command=self.duplicate_line)
        m.add_command(label="Comentar",       command=self.toggle_comment)
        m.add_command(label="Ir a línea…",    command=self.goto_line)
        m.add_separator()
        m.add_command(label="Ejecutar selección", command=self.run_selection)

        def popup(e):
            try: m.tk_popup(e.x_root, e.y_root)
            finally: m.grab_release()
        self.code_editor.bind("<Button-3>", popup)
        self.code_editor.bind("<Button-2>", popup)

    # ==========================================================
    # DIÁLOGOS (M31 / M32 / M33 / M34 / M29 / M30 / M70)
    # ==========================================================
    def show_about(self):
        messagebox.showinfo("Acerca de", f"{APP_NAME}\nVersión {VERSION}\n\n"
                                         "Lenguaje EasyScript con IDE integrado.\n"
                                         "70 mejoras aplicadas.")

    def show_command_reference(self):
        win = tk.Toplevel(self.root)
        win.title("Referencia de comandos")
        win.geometry("640x520")
        txt = tk.Text(win, wrap=tk.WORD, font=("Consolas", 10))
        txt.pack(fill=tk.BOTH, expand=True)
        ref = self._command_reference_text()
        txt.insert("1.0", ref)
        txt.config(state="disabled")

    def _command_reference_text(self):
        return """EASYSCRIPT - REFERENCIA DE COMANDOS
=================================

VARIABLES
  var:(nombre, valor)              Define variable
  incrementar:(var, n)             Suma n
  decrementar:(var, n)             Resta n
  entrada:(var, "prompt")          Pide al usuario

CADENAS
  mayusculas:(var)                 A mayúsculas
  minusculas:(var)                 A minúsculas
  longitud:(expr)                  Longitud
  reemplazar:(var, viejo, nuevo)   Reemplaza
  concatenar:(var, a, b)           Concatena
  a_texto:(var, val)               Convierte a texto
  a_numero:(var, val)              Convierte a número
  dividir_texto:(var, txt, sep)    Divide texto
  indice:(var, lista, i)           Elemento i
  invertir:(var, txt)              Invierte
  ordenar:(var, lista)             Ordena

MATEMÁTICAS
  sumar:(var, a, b)                a + b
  restar:(var, a, b)               a - b
  multiplicar:(var, a, b)          a * b
  dividir:(var, a, b)              a / b
  modulo:(var, a, b)               a % b
  raiz:(var, n)                    Raíz cuadrada
  potencia:(var, a, b)             a^b
  redondear / absoluto / seno / coseno / maximo / minimo / pi

LÓGICA
  igual_a:(var, a, b)              a == b
  mayor_que / menor_que
  y / o / no

DIBUJO
  color:("rojo")                   Color actual
  linea:(x1,y1,x2,y2[,color])
  rectangulo:(x,y,w,h[,color])
  circulo:(x,y,r[,color])
  ovalo:(x,y,w,h[,color])
  triangulo:(x1,y1,x2,y2,x3,y3[,color])
  poligono:(6 coords, color)
  arco:(x1,y1,x2,y2,start,extent[,color])
  texto_canvas:(x,y,"txt"[,color])
  color_canvas:("azul")
  grosor_linea:(n)
  cuadricula:(n)
  borrar_canvas
  limpiar_pantalla

COLORES EN ESPAÑOL
  rojo, azul, verde, amarillo, naranja, morado, rosa,
  negro, blanco, gris, cian, violeta, marrón, dorado, plateado
  rgb:(r,g,b)                      Color por componentes

SISTEMA
  fecha / hora / hora_actual / fecha_hora
  esperar:(seg)
  alerta:("msg")
  confirmar:(var, "pregunta")
  copiar:("txt")
  notificacion:("título", "msg")
  pitido
  beep:(freq)
  esperar_tecla
  abrir_url:("https://…")
  ejecutar_cmd:("cmd")

ARCHIVOS
  crear_archivo:(path, contenido)
  leer_archivo:(var, path)
  existe_archivo:(var, path)
  eliminar_archivo:(path)
  listar_archivos:(var, dir)
  json_obtener:(var, json, key)

IA / WEB
  IA:("prompt")
  ia_resumir / ia_traducir / ia_explicar
  JS: / HTML: / CSS: / JS_EVAL:
  html_titulo:("txt")
  css_tema:("oscuro"|"claro")

LOGS
  log_info:("msg") / log_warn:("msg") / log_error:("msg")
  uuid:(var)

CONSOLA / DIBUJO EXTRA
  limpiar_consola
  borrar_canvas
  detener

CONTROL DE FLUJO (indicativo)
  si:(cond) / sino: / fin_si
  bucle:(n) / fin_bucle
"""

    def show_examples(self):
        win = tk.Toplevel(self.root)
        win.title("Biblioteca de ejemplos")
        win.geometry("560x420")
        examples = {
            "Hola Mundo": 'mostrar "¡Hola, EasyScript!"',
            "Contador": 'var:(n, 0)\nincrementar:(n, 1)\nincrementar:(n, 1)\nmostrar n',
            "Círculo rojo": 'color:("rojo")\ncirculo:(100, 100, 40)',
            "Cuadrícula + rectángulo":
                'cuadricula:(40)\ncolor:("azul")\nrectangulo:(40, 40, 120, 80)',
            "Texto canvas":
                'texto_canvas:(150, 60, "¡Hola!", "verde")',
            "Colores rgb":
                'rgb:(255, 100, 50)\ncirculo:(80, 80, 40)',
            "Aleatorio + operaciones":
                'random:(n, 1, 100)\nmostrar n\nsumar:(r, n, 5)\nmostrar r',
            "Fecha y hora":
                'fecha\nhora',
            "Botón":
                'boton:("Clic", print "¡Pulsado!")',
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
            "Base dibujo":
                "limpiar_pantalla\ncuadricula:(40)\ncolor:(\"azul\")\n",
            "Interacción":
                "entrada:(nombre, \"¿Cómo te llamas?\")\nmostrar nombre\n",
            "Demo completa":
                self.code_editor.get("1.0", "end-1c"),
        }
        win = tk.Toplevel(self.root)
        win.title("Plantillas rápidas")
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
            self.status.set(f"Variables exportadas a {path}")

    def import_variables(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.interpreter.variables.update(data)
            self.status.set(f"Variables importadas desde {path}")

    def show_stats(self):
        info = (
            f"Estadísticas\n"
            f"─────────────\n"
            f"Sentencias ejecutadas: {self.interpreter.executed_lines}\n"
            f"Tiempo de ejecución: {self.interpreter.execution_time:.3f} s\n"
            f"Variables definidas: {len(self.interpreter.variables)}\n"
            f"Última línea con error: {self.interpreter.last_error_line}\n"
        )
        messagebox.showinfo("Estadísticas", info)

    # ==========================================================
    # PALETA DE COMANDOS (M36)
    # ==========================================================
    def open_command_palette(self):
        win = tk.Toplevel(self.root)
        win.title("Paleta de comandos")
        win.geometry("420x300")
        entry = tk.Entry(win, font=("Consolas", 11))
        entry.pack(fill=tk.X, padx=6, pady=6)
        lb = tk.Listbox(win, font=("Consolas", 10))
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        actions = {
            "Nuevo proyecto": self.new_project,
            "Abrir proyecto": self.load_project,
            "Guardar proyecto": self.save_project,
            "Ejecutar todo": self.run_code,
            "Ejecutar selección": self.run_selection,
            "Detener": self.stop_execution,
            "Buscar/Reemplazar": self.open_find_dialog,
            "Ir a línea": self.goto_line,
            "Inspeccionar variables": self.inspect_variables,
            "Exportar variables": self.export_variables,
            "Importar variables": self.import_variables,
            "Ejemplos": self.show_examples,
            "Referencia de comandos": self.show_command_reference,
            "Estadísticas": self.show_stats,
            "Cambiar tema": self.toggle_theme,
            "Pantalla completa": self.toggle_fullscreen,
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
    # ARCHIVOS / AUTOGUARDADO / CONFIG
    # ==========================================================
    def new_project(self):
        if messagebox.askyesno("Nuevo Proyecto", "¿Deseas crear un nuevo proyecto?"):
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
            filetypes=[("Proyectos EasyScript", "*.ez"), ("Todos", "*.*")])
        if path:
            self._write_file(path)
            self._add_recent(path)

    def _write_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.code_editor.get("1.0", tk.END))
        self.current_file = path
        self.status.set(f"Guardado: {os.path.basename(path)}")

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
                self.status.set(f"Cargado: {os.path.basename(path)}")
                self._highlight_syntax()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ---------- Recientes (M09) ----------
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
            self.status.set(f"Cargado: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Autoguardado (M10) ----------
    def _schedule_autosave(self):
        def tick():
            try:
                if self.current_file and self.code_editor.edit_modified():
                    self._write_file(self.current_file)
                    self.status.set("Autoguardado.")
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
    # UTILIDADES
    # ==========================================================
    def ask_input(self, prompt_text):
        return simpledialog.askstring("Entrada EasyScript", prompt_text, parent=self.root)

    def _load_demo(self):
        demo = (
            "// --- DEMOSTRACIÓN EASYSCRIPT v2.0 ---\n"
            "SistemaOperativo: (Windows)\n"
            "var:(num, 10)\n"
            "incrementar:(num, 5)\n"
            "mostrar num\n"
            "\n"
            "// --- DIBUJO ---\n"
            "cuadricula:(40)\n"
            "color:(\"azul\")\n"
            "circulo:(60, 60, 35)\n"
            "rectangulo:(120, 25, 90, 60)\n"
            "\n"
            "color:(\"rojo\")\n"
            "triangulo:(230, 85, 270, 25, 310, 85)\n"
            "ovalo:(30, 110, 100, 50)\n"
            "circulo:(170, 135, 25, \"amarillo\")\n"
            "texto_canvas:(160, 200, \"¡EZScript 2.0!\", \"verde\")\n"
            "\n"
            "// --- MATEMÁTICAS ---\n"
            "sumar:(total, 10, 20)\n"
            "multiplicar:(doble, total, 2)\n"
            "mostrar doble\n"
            "\n"
            "// --- LOGS ---\n"
            "log_info:(\"Demo iniciada\")\n"
            "log_warn:(\"Aviso de prueba\")\n"
            "log_error:(\"Error simulado\")\n"
            "\n"
            "// --- SISTEMA ---\n"
            "fecha\n"
            "hora\n"
            "boton:(\"¡Haz clic!\", print \"¡Botón Funcionando!\")\n"
        )
        self.code_editor.insert(tk.END, demo)
        self._update_linenumbers()
        self._highlight_syntax()
        self._highlight_current_line()


EZScriptIDE = EasyScriptIDE


# ==========================================
# ENTRADA
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = EasyScriptIDE(root)
    root.mainloop()
