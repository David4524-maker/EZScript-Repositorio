# -*- coding: utf-8 -*-
"""
EasyScript (EZScript) Studio v4.1.0
====================================
IDE + Intérprete multilenguaje, retro y autosuficiente.

Novedad v4.1.0:
 * Cambio de idioma TOTAL: se retraduce toda la ventana en caliente
   (menús, toolbar, statusbar, sidebar, pestañas y Referencia de comandos).
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk, font as tkfont
import re, platform, json, random, math, time, webbrowser, os, sys, threading
import queue, traceback, uuid as uuidlib, hashlib, base64, csv, io, urllib.request
import urllib.parse, socket, subprocess, zipfile, tempfile, shutil, difflib
from datetime import datetime

APP_NAME = "EasyScript (EZScript) Studio"
VERSION  = "4.1.0"
DEFAULT_FONT = "Consolas"
DEFAULT_FONT_SIZE = 11
MAX_RECENT_FILES = 8
AUTOSAVE_INTERVAL_MS = 60000
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ezscript_config.json")
PLUGINS_DIR = os.path.join(os.path.expanduser("~"), ".ezscript_plugins")
SNIPPETS_FILE = os.path.join(os.path.expanduser("~"), ".ezscript_snippets.json")

DEFAULT_LANGUAGE = "es"
DEFAULT_VIDEO_MODE = "normal"
DEFAULT_PALETTE = "nes"


# ==========================================================
# 0) i18n (ampliado con textos de referencia y diálogos)
# ==========================================================
class I18n:
    LANGS = ("es", "en", "pt")

    UI = {
        "es": {
            # Menús
            "file":"Archivo","edit":"Editar","view":"Ver","run":"Ejecutar","help":"Ayuda",
            "language":"Idioma","video_mode":"Modo gráfico",
            # Archivo
            "new":"Nuevo","new_tab":"Nueva pestaña","open":"Abrir…","save":"Guardar",
            "save_as":"Guardar como…","close_tab":"Cerrar pestaña","exit":"Salir",
            "recent":"Recientes","console_save":"Guardar consola…","canvas_save":"Guardar canvas (PS)…",
            "pack":"Empaquetar proyecto (.ezp)","unpack":"Importar .ezp","export_html":"Exportar a HTML",
            # Editar
            "undo":"Deshacer","redo":"Rehacer",
            "find":"Buscar/Reemplazar","search_all":"Buscar en todas las pestañas",
            "goto":"Ir a línea…","dup":"Duplicar línea","comment":"Comentar/Descomentar",
            "indent":"Indentar","unindent":"Desindentar",
            "format":"Formatear código","rename_var":"Renombrar variable…",
            "extract_fn":"Extraer a función…","cmd_palette":"Paleta de comandos",
            "autocomplete":"Autocompletar","inspect":"Inspeccionar variables",
            "export_vars":"Exportar variables (JSON)","import_vars":"Importar variables (JSON)",
            # Ver
            "font_up":"Aumentar fuente","font_down":"Disminuir fuente","font_reset":"Restablecer fuente",
            "font_pick":"Cambiar fuente…","tab_size":"Tamaño de tab…",
            "wrap":"Ajustar texto (Wrap)","whitespace":"Mostrar espacios",
            "timestamps":"Timestamps en consola","theme":"Tema claro/oscuro",
            "fullscreen":"Pantalla completa","presentation":"Modo presentación",
            "bookmarks":"Marcadores","toggle_bm":"Alternar marcador",
            "next_bm":"Siguiente marcador","prev_bm":"Marcador anterior",
            # Ejecutar
            "run_all":"Ejecutar todo","run_sel":"Ejecutar selección","run_cursor":"Ejecutar desde cursor",
            "validate":"Validar sintaxis","stop":"Detener ejecución",
            "debugger":"Depurador","watch":"Watch","callstack":"Call stack",
            "profile":"Perfilado","profile_chart":"Gráfica",
            "macro_rec":"Grabar macro","macro_play":"Reproducir macro",
            "test_runner":"Ejecutar tests",
            "clear_console":"Limpiar consola","clear_canvas":"Limpiar canvas",
            "copy_console":"Copiar consola","history":"Historial de ejecuciones",
            "diff":"Comparar versiones","commit":"Commit local",
            # Ayuda
            "cmd_ref":"Referencia de comandos","examples":"Biblioteca de ejemplos",
            "templates":"Plantillas rápidas","snippet_mgr":"Gestor de snippets",
            "tutorials":"Tutoriales interactivos","doc_gen":"Generar documentación HTML",
            "plugins":"Plugins","install_plugin":"Instalar plugin…",
            "achievements":"Logros","stats":"Estadísticas","about":"Acerca de…",
            # Estado
            "ready":"Listo.","running":"Ejecutando…","stopping":"Deteniendo…",
            "validate_ok":"✅ Sintaxis correcta.","vars":"Variables","stats_title":"Estadísticas",
            "about_body":"EasyScript v4.1.0 — autosuficiente.\nCambio de idioma total en caliente.",
            "language_changed":"Idioma:","lang_reset":"↩ Idioma restablecido:",
            "mode_reset":"↩ Modo restablecido:","palette_reset":"↩ Paleta restablecida:",
            "mode_set":"Modo:","palette_set":"Paleta:",
            # Sidebar
            "sidebar":"Explorador","project":"Proyecto","refresh":"Recargar",
            # Tabs
            "new_tab_title":"Sin título",
            # Toolbar
            "btn_new":"Nuevo","btn_open":"Abrir","btn_save":"Guardar","btn_run":"Ejecutar",
            "btn_stop":"Detener","btn_console":"Consola","btn_canvas":"Canvas",
            "btn_find":"Buscar","btn_help":"Ayuda","btn_debug":"Depurar","btn_step":"Paso",
            "btn_format":"Formatear","btn_test":"Tests","btn_snippets":"Snippets",
            # Diálogos
            "dlg_search":"Buscar:","dlg_replace":"Reemplazar:","dlg_regex":"Regex",
            "dlg_find_btn":"Buscar","dlg_replace_all":"Reemplazar todo",
            "dlg_watch_add":"Añadir","dlg_close":"Cerrar",
            "msg_select_code":"Selecciona código primero.",
            "msg_confirm_close":"El documento tiene cambios sin guardar. ¿Cerrar?",
            "msg_already_running":"Ya hay una ejecución en curso.",
            "msg_extract_hint":"Selecciona el bloque a extraer.",
            "dlg_tab_size":"Tamaño de tabulación (2-8):","dlg_font_prompt":"Nombre de la fuente:",
            "dlg_goto":"Ir a línea","dlg_goto_num":"Número:",
            "dlg_rename_old":"Variable actual:","dlg_rename_new":"Nuevo nombre:",
            "dlg_extract_name":"Nombre de la función:",
            "search_placeholder":"Texto:",
            "results_title":"Resultados","no_matches":"Sin coincidencias.",
            # Reference sections
            "ref_title":"REFERENCIA DE COMANDOS",
            "ref_intro":"Comandos funcionan en ES / EN / PT. Ej: mostrar / show / exibir.",
            "ref_control":"CONTROL DE FLUJO",
            "ref_funcs":"FUNCIONES",
            "ref_classes":"CLASES Y OBJETOS",
            "ref_tests":"TESTS",
            "ref_events":"EVENTOS Y TIMERS",
            "ref_sprites":"SPRITES Y JUEGO",
            "ref_modules":"MÓDULOS",
            "ref_stdlib":"LIBRERÍA ESTÁNDAR",
            "ref_audio":"AUDIO",
            "ref_video":"IDIOMA Y VIDEO",
            "ref_achievements":"LOGROS",
            "ref_shortcuts":"ATAJOS DEL IDE",
            "ref_toggle":"COMPORTAMIENTO TOGGLE",
            "ref_toggle_help":
                "Pulsa el idioma YA activo (≠ Español) → vuelve a Español.\n"
                "Pulsa el modo YA activo (≠ Normal) → vuelve a Normal.\n"
                "Pulsa la paleta YA activa (≠ NES) → vuelve a NES.",
        },
        "en": {
            "file":"File","edit":"Edit","view":"View","run":"Run","help":"Help",
            "language":"Language","video_mode":"Video mode",
            "new":"New","new_tab":"New tab","open":"Open…","save":"Save","save_as":"Save as…",
            "close_tab":"Close tab","exit":"Exit","recent":"Recent",
            "console_save":"Save console…","canvas_save":"Save canvas (PS)…",
            "pack":"Pack project (.ezp)","unpack":"Import .ezp","export_html":"Export to HTML",
            "undo":"Undo","redo":"Redo",
            "find":"Find/Replace","search_all":"Search in all tabs",
            "goto":"Go to line…","dup":"Duplicate line","comment":"Toggle comment",
            "indent":"Indent","unindent":"Unindent",
            "format":"Format code","rename_var":"Rename variable…",
            "extract_fn":"Extract to function…","cmd_palette":"Command palette",
            "autocomplete":"Autocomplete","inspect":"Inspect variables",
            "export_vars":"Export variables (JSON)","import_vars":"Import variables (JSON)",
            "font_up":"Increase font","font_down":"Decrease font","font_reset":"Reset font",
            "font_pick":"Change font…","tab_size":"Tab size…",
            "wrap":"Word wrap","whitespace":"Show whitespace",
            "timestamps":"Console timestamps","theme":"Light/dark theme",
            "fullscreen":"Fullscreen","presentation":"Presentation mode",
            "bookmarks":"Bookmarks","toggle_bm":"Toggle bookmark",
            "next_bm":"Next bookmark","prev_bm":"Previous bookmark",
            "run_all":"Run all","run_sel":"Run selection","run_cursor":"Run from cursor",
            "validate":"Validate syntax","stop":"Stop execution",
            "debugger":"Debugger","watch":"Watch","callstack":"Call stack",
            "profile":"Profiling","profile_chart":"Chart",
            "macro_rec":"Record macro","macro_play":"Play macro",
            "test_runner":"Run tests",
            "clear_console":"Clear console","clear_canvas":"Clear canvas",
            "copy_console":"Copy console","history":"Execution history",
            "diff":"Compare versions","commit":"Local commit",
            "cmd_ref":"Command reference","examples":"Examples library",
            "templates":"Quick templates","snippet_mgr":"Snippet manager",
            "tutorials":"Interactive tutorials","doc_gen":"Generate HTML docs",
            "plugins":"Plugins","install_plugin":"Install plugin…",
            "achievements":"Achievements","stats":"Statistics","about":"About…",
            "ready":"Ready.","running":"Running…","stopping":"Stopping…",
            "validate_ok":"✅ Syntax OK.","vars":"Variables","stats_title":"Statistics",
            "about_body":"EasyScript v4.1.0 — self-contained.\nFull live language switch.",
            "language_changed":"Language:","lang_reset":"↩ Language reset:",
            "mode_reset":"↩ Mode reset:","palette_reset":"↩ Palette reset:",
            "mode_set":"Mode:","palette_set":"Palette:",
            "sidebar":"Explorer","project":"Project","refresh":"Refresh",
            "new_tab_title":"Untitled",
            "btn_new":"New","btn_open":"Open","btn_save":"Save","btn_run":"Run",
            "btn_stop":"Stop","btn_console":"Console","btn_canvas":"Canvas",
            "btn_find":"Find","btn_help":"Help","btn_debug":"Debug","btn_step":"Step",
            "btn_format":"Format","btn_test":"Tests","btn_snippets":"Snippets",
            "dlg_search":"Find:","dlg_replace":"Replace:","dlg_regex":"Regex",
            "dlg_find_btn":"Find","dlg_replace_all":"Replace all",
            "dlg_watch_add":"Add","dlg_close":"Close",
            "msg_select_code":"Select code first.",
            "msg_confirm_close":"The document has unsaved changes. Close?",
            "msg_already_running":"An execution is already running.",
            "msg_extract_hint":"Select the block to extract.",
            "dlg_tab_size":"Tab size (2-8):","dlg_font_prompt":"Font name:",
            "dlg_goto":"Go to line","dlg_goto_num":"Number:",
            "dlg_rename_old":"Current variable:","dlg_rename_new":"New name:",
            "dlg_extract_name":"Function name:",
            "search_placeholder":"Text:",
            "results_title":"Results","no_matches":"No matches.",
            "ref_title":"COMMAND REFERENCE",
            "ref_intro":"Commands work in EN / ES / PT. Ex: show / mostrar / exibir.",
            "ref_control":"CONTROL FLOW",
            "ref_funcs":"FUNCTIONS",
            "ref_classes":"CLASSES AND OBJECTS",
            "ref_tests":"TESTS",
            "ref_events":"EVENTS AND TIMERS",
            "ref_sprites":"SPRITES AND GAME",
            "ref_modules":"MODULES",
            "ref_stdlib":"STANDARD LIBRARY",
            "ref_audio":"AUDIO",
            "ref_video":"LANGUAGE AND VIDEO",
            "ref_achievements":"ACHIEVEMENTS",
            "ref_shortcuts":"IDE SHORTCUTS",
            "ref_toggle":"TOGGLE BEHAVIOR",
            "ref_toggle_help":
                "Click the language already active (≠ Spanish) → returns to Spanish.\n"
                "Click the mode already active (≠ Normal) → returns to Normal.\n"
                "Click the palette already active (≠ NES) → returns to NES.",
        },
        "pt": {
            "file":"Arquivo","edit":"Editar","view":"Ver","run":"Executar","help":"Ajuda",
            "language":"Idioma","video_mode":"Modo gráfico",
            "new":"Novo","new_tab":"Nova aba","open":"Abrir…","save":"Salvar","save_as":"Salvar como…",
            "close_tab":"Fechar aba","exit":"Sair","recent":"Recentes",
            "console_save":"Salvar console…","canvas_save":"Salvar canvas (PS)…",
            "pack":"Empacotar projeto (.ezp)","unpack":"Importar .ezp","export_html":"Exportar para HTML",
            "undo":"Desfazer","redo":"Refazer",
            "find":"Localizar/Substituir","search_all":"Buscar em todas as abas",
            "goto":"Ir para linha…","dup":"Duplicar linha","comment":"Comentar/Descomentar",
            "indent":"Indentar","unindent":"Desindentar",
            "format":"Formatar código","rename_var":"Renomear variável…",
            "extract_fn":"Extrair para função…","cmd_palette":"Paleta de comandos",
            "autocomplete":"Autocompletar","inspect":"Inspecionar variáveis",
            "export_vars":"Exportar variáveis (JSON)","import_vars":"Importar variáveis (JSON)",
            "font_up":"Aumentar fonte","font_down":"Diminuir fonte","font_reset":"Redefinir fonte",
            "font_pick":"Trocar fonte…","tab_size":"Tamanho do tab…",
            "wrap":"Quebra de linha","whitespace":"Mostrar espaços",
            "timestamps":"Timestamps no console","theme":"Tema claro/escuro",
            "fullscreen":"Tela cheia","presentation":"Modo apresentação",
            "bookmarks":"Marcadores","toggle_bm":"Alternar marcador",
            "next_bm":"Próximo marcador","prev_bm":"Marcador anterior",
            "run_all":"Executar tudo","run_sel":"Executar seleção","run_cursor":"Executar do cursor",
            "validate":"Validar sintaxe","stop":"Parar execução",
            "debugger":"Depurador","watch":"Watch","callstack":"Call stack",
            "profile":"Perfil","profile_chart":"Gráfico",
            "macro_rec":"Gravar macro","macro_play":"Reproduzir macro",
            "test_runner":"Executar testes",
            "clear_console":"Limpar console","clear_canvas":"Limpar canvas",
            "copy_console":"Copiar console","history":"Histórico de execuções",
            "diff":"Comparar versões","commit":"Commit local",
            "cmd_ref":"Referência de comandos","examples":"Biblioteca de exemplos",
            "templates":"Modelos rápidos","snippet_mgr":"Gerenciador de snippets",
            "tutorials":"Tutoriais interativos","doc_gen":"Gerar documentação HTML",
            "plugins":"Plugins","install_plugin":"Instalar plugin…",
            "achievements":"Conquistas","stats":"Estatísticas","about":"Sobre…",
            "ready":"Pronto.","running":"Executando…","stopping":"Parando…",
            "validate_ok":"✅ Sintaxe OK.","vars":"Variáveis","stats_title":"Estatísticas",
            "about_body":"EasyScript v4.1.0 — autossuficiente.\nTroca total de idioma ao vivo.",
            "language_changed":"Idioma:","lang_reset":"↩ Idioma restabelecido:",
            "mode_reset":"↩ Modo restabelecido:","palette_reset":"↩ Paleta restabelecida:",
            "mode_set":"Modo:","palette_set":"Paleta:",
            "sidebar":"Explorador","project":"Projeto","refresh":"Recarregar",
            "new_tab_title":"Sem título",
            "btn_new":"Novo","btn_open":"Abrir","btn_save":"Salvar","btn_run":"Executar",
            "btn_stop":"Parar","btn_console":"Console","btn_canvas":"Canvas",
            "btn_find":"Localizar","btn_help":"Ajuda","btn_debug":"Depurar","btn_step":"Passo",
            "btn_format":"Formatar","btn_test":"Testes","btn_snippets":"Snippets",
            "dlg_search":"Localizar:","dlg_replace":"Substituir:","dlg_regex":"Regex",
            "dlg_find_btn":"Localizar","dlg_replace_all":"Substituir tudo",
            "dlg_watch_add":"Adicionar","dlg_close":"Fechar",
            "msg_select_code":"Selecione o código primeiro.",
            "msg_confirm_close":"O documento tem alterações não salvas. Fechar?",
            "msg_already_running":"Já existe uma execução em andamento.",
            "msg_extract_hint":"Selecione o bloco a extrair.",
            "dlg_tab_size":"Tamanho do tab (2-8):","dlg_font_prompt":"Nome da fonte:",
            "dlg_goto":"Ir para linha","dlg_goto_num":"Número:",
            "dlg_rename_old":"Variável atual:","dlg_rename_new":"Novo nome:",
            "dlg_extract_name":"Nome da função:",
            "search_placeholder":"Texto:",
            "results_title":"Resultados","no_matches":"Sem correspondências.",
            "ref_title":"REFERÊNCIA DE COMANDOS",
            "ref_intro":"Comandos funcionam em PT / ES / EN. Ex: exibir / mostrar / show.",
            "ref_control":"CONTROLE DE FLUXO",
            "ref_funcs":"FUNÇÕES",
            "ref_classes":"CLASSES E OBJETOS",
            "ref_tests":"TESTES",
            "ref_events":"EVENTOS E TIMERS",
            "ref_sprites":"SPRITES E JOGO",
            "ref_modules":"MÓDULOS",
            "ref_stdlib":"BIBLIOTECA PADRÃO",
            "ref_audio":"ÁUDIO",
            "ref_video":"IDIOMA E VÍDEO",
            "ref_achievements":"CONQUISTAS",
            "ref_shortcuts":"ATALHOS DA IDE",
            "ref_toggle":"COMPORTAMENTO TOGGLE",
            "ref_toggle_help":
                "Clique no idioma já ativo (≠ Espanhol) → volta ao Espanhol.\n"
                "Clique no modo já ativo (≠ Normal) → volta ao Normal.\n"
                "Clique na paleta já ativa (≠ NES) → volta à NES.",
        },
    }

    CMD = {
        "mostrar":{"en":"show","pt":"exibir"}, "print":{"en":"print","pt":"imprimir"},
        "limpiar_pantalla":{"en":"clear_screen","pt":"limpar_tela"},
        "limpiar_consola":{"en":"clear_console","pt":"limpar_console"},
        "var":{"en":"let","pt":"var"}, "incrementar":{"en":"increment","pt":"incrementar"},
        "decrementar":{"en":"decrement","pt":"decrementar"}, "entrada":{"en":"input","pt":"entrada"},
        "mayusculas":{"en":"uppercase","pt":"maiusculas"}, "minusculas":{"en":"lowercase","pt":"minusculas"},
        "longitud":{"en":"length","pt":"comprimento"}, "reemplazar":{"en":"replace","pt":"substituir"},
        "concatenar":{"en":"concat","pt":"concatenar"}, "tipo_dato":{"en":"data_type","pt":"tipo_dado"},
        "a_numero":{"en":"to_number","pt":"para_numero"}, "a_texto":{"en":"to_text","pt":"para_texto"},
        "unir":{"en":"join","pt":"unir"}, "dividir_texto":{"en":"split_text","pt":"dividir_texto"},
        "indice":{"en":"index","pt":"indice"}, "invertir":{"en":"reverse","pt":"inverter"},
        "ordenar":{"en":"sort","pt":"ordenar"}, "contar":{"en":"count","pt":"contar"},
        "random":{"en":"random","pt":"aleatorio"}, "raiz":{"en":"sqrt","pt":"raiz"},
        "potencia":{"en":"power","pt":"potencia"}, "redondear":{"en":"round","pt":"arredondar"},
        "absoluto":{"en":"abs","pt":"absoluto"}, "seno":{"en":"sin","pt":"seno"},
        "coseno":{"en":"cos","pt":"cosseno"}, "maximo":{"en":"max","pt":"maximo"},
        "minimo":{"en":"min","pt":"minimo"}, "pi":{"en":"pi","pt":"pi"},
        "sumar":{"en":"add","pt":"somar"}, "restar":{"en":"subtract","pt":"subtrair"},
        "multiplicar":{"en":"multiply","pt":"multiplicar"}, "dividir":{"en":"divide","pt":"dividir"},
        "modulo":{"en":"modulo","pt":"modulo"}, "igual_a":{"en":"equals","pt":"igual_a"},
        "mayor_que":{"en":"greater_than","pt":"maior_que"}, "menor_que":{"en":"less_than","pt":"menor_que"},
        "y":{"en":"and","pt":"e"}, "o":{"en":"or","pt":"ou"}, "no":{"en":"not","pt":"nao"},
        "color":{"en":"color","pt":"cor"}, "linea":{"en":"line","pt":"linha"},
        "conectar":{"en":"connect","pt":"conectar"}, "rectangulo":{"en":"rectangle","pt":"retangulo"},
        "circulo":{"en":"circle","pt":"circulo"}, "ovalo":{"en":"oval","pt":"oval"},
        "triangulo":{"en":"triangle","pt":"triangulo"}, "poligono":{"en":"polygon","pt":"poligono"},
        "arco":{"en":"arc","pt":"arco"}, "texto_canvas":{"en":"canvas_text","pt":"texto_canvas"},
        "color_canvas":{"en":"canvas_color","pt":"cor_canvas"},
        "grosor_linea":{"en":"line_width","pt":"espessura_linha"},
        "borrar_canvas":{"en":"clear_canvas","pt":"apagar_canvas"},
        "cuadricula":{"en":"grid","pt":"grade"}, "rgb":{"en":"rgb","pt":"rgb"},
        "pixel":{"en":"pixel","pt":"pixel"}, "modo_grafico":{"en":"video_mode","pt":"modo_grafico"},
        "paleta":{"en":"palette","pt":"paleta"},
        "fecha":{"en":"date","pt":"data"}, "hora":{"en":"time","pt":"hora"},
        "hora_actual":{"en":"current_time","pt":"hora_atual"},
        "fecha_hora":{"en":"datetime","pt":"data_hora"}, "esperar":{"en":"wait","pt":"esperar"},
        "alerta":{"en":"alert","pt":"alerta"}, "confirmar":{"en":"confirm","pt":"confirmar"},
        "abrir_url":{"en":"open_url","pt":"abrir_url"}, "copiar":{"en":"copy","pt":"copiar"},
        "notificacion":{"en":"notify","pt":"notificacao"}, "pitido":{"en":"beep","pt":"apito"},
        "beep":{"en":"tone","pt":"tom"}, "esperar_tecla":{"en":"wait_key","pt":"esperar_tecla"},
        "ejecutar_cmd":{"en":"run_cmd","pt":"executar_cmd"}, "detener":{"en":"stop","pt":"parar"},
        "crear_archivo":{"en":"create_file","pt":"criar_arquivo"},
        "leer_archivo":{"en":"read_file","pt":"ler_arquivo"},
        "existe_archivo":{"en":"file_exists","pt":"arquivo_existe"},
        "eliminar_archivo":{"en":"delete_file","pt":"deletar_arquivo"},
        "listar_archivos":{"en":"list_files","pt":"listar_arquivos"},
        "json_obtener":{"en":"json_get","pt":"json_obter"},
        "uuid":{"en":"uuid","pt":"uuid"},
        "log_info":{"en":"log_info","pt":"log_info"}, "log_warn":{"en":"log_warn","pt":"log_warn"},
        "log_error":{"en":"log_error","pt":"log_error"},
        "si":{"en":"if","pt":"se"}, "sino":{"en":"else","pt":"senao"},
        "fin_si":{"en":"end_if","pt":"fim_se"}, "mientras":{"en":"while","pt":"enquanto"},
        "fin_mientras":{"en":"end_while","pt":"fim_enquanto"},
        "bucle":{"en":"loop","pt":"loop"}, "fin_bucle":{"en":"end_loop","pt":"fim_loop"},
        "romper":{"en":"break","pt":"quebrar"}, "continuar":{"en":"continue","pt":"continuar"},
        "funcion":{"en":"function","pt":"funcao"}, "fin_funcion":{"en":"end_function","pt":"fim_funcao"},
        "llamar":{"en":"call","pt":"chamar"}, "retornar":{"en":"return","pt":"retornar"},
        "lista":{"en":"list","pt":"lista"}, "matriz":{"en":"matrix","pt":"matriz"},
        "mapa":{"en":"map","pt":"mapa"}, "agregar":{"en":"append","pt":"adicionar"},
        "quitar":{"en":"remove","pt":"remover"}, "obtener":{"en":"get","pt":"obter"},
        "asignar":{"en":"set","pt":"definir"},
        "hash_md5":{"en":"md5","pt":"md5"}, "hash_sha256":{"en":"sha256","pt":"sha256"},
        "base64_cod":{"en":"b64_encode","pt":"b64_codificar"},
        "base64_dec":{"en":"b64_decode","pt":"b64_decodificar"},
        "regex_buscar":{"en":"regex_find","pt":"regex_buscar"},
        "regex_reemplazar":{"en":"regex_replace","pt":"regex_substituir"},
        "csv_parsear":{"en":"csv_parse","pt":"csv_parsear"},
        "csv_generar":{"en":"csv_build","pt":"csv_gerar"},
        "http_get":{"en":"http_get","pt":"http_get"}, "http_post":{"en":"http_post","pt":"http_post"},
        "longitud_lista":{"en":"list_len","pt":"comprimento_lista"},
        "suma_lista":{"en":"list_sum","pt":"soma_lista"},
        "max_lista":{"en":"list_max","pt":"max_lista"}, "min_lista":{"en":"list_min","pt":"min_lista"},
        "contiene":{"en":"contains","pt":"contem"}, "idioma":{"en":"language","pt":"idioma"},
        "clase":{"en":"class","pt":"classe"}, "fin_clase":{"en":"end_class","pt":"fim_classe"},
        "hereda":{"en":"inherits","pt":"herda"},
        "nuevo":{"en":"new","pt":"novo"}, "llamar_metodo":{"en":"method","pt":"metodo"},
        "propiedad":{"en":"property","pt":"propriedade"},
        "emitir":{"en":"emit","pt":"emitir"}, "al":{"en":"on","pt":"ao"},
        "cada":{"en":"every","pt":"cada"}, "cancelar_timer":{"en":"cancel_timer","pt":"cancelar_timer"},
        "animar":{"en":"animate","pt":"animar"},
        "sprite":{"en":"sprite","pt":"sprite"}, "mover_sprite":{"en":"move_sprite","pt":"mover_sprite"},
        "dibujar_sprite":{"en":"draw_sprite","pt":"desenhar_sprite"},
        "colisiona":{"en":"collides","pt":"colide"},
        "gravedad":{"en":"gravity","pt":"gravidade"},
        "importar":{"en":"import","pt":"importar"},
        "afirmar_igual":{"en":"assert_equal","pt":"afirmar_igual"},
        "afirmar_verdad":{"en":"assert_true","pt":"afirmar_verdade"},
        "afirmar_falso":{"en":"assert_false","pt":"afirmar_falso"},
        "test":{"en":"test","pt":"teste"}, "fin_test":{"en":"end_test","pt":"fim_teste"},
        "logro":{"en":"achievement","pt":"conquista"},
        "musica":{"en":"music","pt":"musica"}, "nota":{"en":"note","pt":"nota"},
        "tecla_al":{"en":"on_key","pt":"tecla_ao"},
        "raton_al":{"en":"on_mouse","pt":"rato_ao"},
        "generar":{"en":"yield_gen","pt":"gerar"},
        "tarea":{"en":"task","pt":"tarefa"},
    }

    def __init__(self, lang="es"):
        self.lang = lang
        self._rebuild_reverse()

    def set_lang(self, lang):
        if lang in self.LANGS:
            self.lang = lang
            self._rebuild_reverse()

    def _rebuild_reverse(self):
        self.reverse = {}
        for canonical, aliases in self.CMD.items():
            self.reverse[canonical] = canonical
            if self.lang != "es":
                a = aliases.get(self.lang)
                if a: self.reverse[a] = canonical

    def t(self, key):
        return self.UI.get(self.lang, self.UI["es"]).get(key, key)

    def translate_line(self, line):
        m = re.match(r'^(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*[: ])(.*)$', line)
        if not m: return line
        indent, cmd, sep, rest = m.groups()
        canonical = self.reverse.get(cmd)
        if canonical and canonical != cmd:
            return f"{indent}{canonical}{sep}{rest}"
        return line

    def command_list(self):
        out = set()
        for canonical, aliases in self.CMD.items():
            out.add(canonical + ":")
            a = aliases.get(self.lang)
            if a: out.add(a + ":")
        return sorted(out)


# ==========================================================
# 1) Modos gráficos retro
# ==========================================================
class RetroVideoMode:
    PALETTES = {
        "nes": {"negro":"#000000","blanco":"#fcfcfc","gris":"#bcbcbc","rojo":"#f83800",
                "verde":"#00a800","azul":"#0058f8","amarillo":"#f8b800","naranja":"#f87858",
                "morado":"#b800b8","cian":"#3cbcfc","rosa":"#f878f8","marron":"#503000",
                "dorado":"#fce0a8","plateado":"#c4c4c4","violeta":"#9878f8"},
        "gameboy": {"negro":"#0f380f","blanco":"#9bbc0f","gris":"#8bac0f","rojo":"#306230",
                    "verde":"#8bac0f","azul":"#0f380f","amarillo":"#9bbc0f","naranja":"#306230",
                    "morado":"#306230","cian":"#8bac0f","rosa":"#9bbc0f","marron":"#0f380f",
                    "dorado":"#9bbc0f","plateado":"#8bac0f","violeta":"#306230"},
        "cga": {"negro":"#000000","blanco":"#ffffff","gris":"#aaaaaa","rojo":"#ff55ff",
                "verde":"#55ffff","azul":"#5555ff","amarillo":"#ffff55","naranja":"#ff5555",
                "morado":"#ff55ff","cian":"#55ffff","rosa":"#ff55ff","marron":"#aa5500",
                "dorado":"#ffff55","plateado":"#aaaaaa","violeta":"#ff55ff"},
        "snes": {"negro":"#000000","blanco":"#f8f8f8","gris":"#a0a0a0","rojo":"#e02020",
                 "verde":"#20b020","azul":"#2040d0","amarillo":"#f0d020","naranja":"#f07020",
                 "morado":"#a020a0","cian":"#20c0c0","rosa":"#f090a0","marron":"#704020",
                 "dorado":"#e0c060","plateado":"#c8c8c8","violeta":"#8050c0"},
        "vga": {"negro":"#000000","blanco":"#ffffff","gris":"#a0a0a0","rojo":"#a80000",
                "verde":"#00a800","azul":"#0000a8","amarillo":"#a8a800","naranja":"#a85400",
                "morado":"#a800a8","cian":"#00a8a8","rosa":"#ff80c0","marron":"#804000",
                "dorado":"#ffd700","plateado":"#c0c0c0","violeta":"#8000ff"},
        "sinclair": {"negro":"#000000","blanco":"#ffffff","gris":"#c0c0c0","rojo":"#d00000",
                     "verde":"#00d000","azul":"#0000d0","amarillo":"#d0d000","naranja":"#d06000",
                     "morado":"#d000d0","cian":"#00d0d0","rosa":"#d08080","marron":"#804000",
                     "dorado":"#d0c000","plateado":"#c0c0c0","violeta":"#8000d0"},
    }
    MODES = {
        "normal": {"name":"Normal (24-bit)","pixel_scale":1,"scanlines":False,
                   "bg":"#1e272e","fg":"#ffffff"},
        "8bit":   {"name":"8-bit (256 col.)","pixel_scale":2,"scanlines":True,
                   "bg":"#101010","fg":"#fcfcfc"},
        "16bit":  {"name":"16-bit (65 K col.)","pixel_scale":1,"scanlines":False,
                   "bg":"#000020","fg":"#f8f8f8"},
    }
    def __init__(self):
        self.mode = "normal"; self.palette_name = "nes"
    @staticmethod
    def _hex_to_rgb(c):
        c = c.lstrip("#")
        if len(c) == 3: c = "".join(ch*2 for ch in c)
        return int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
    @staticmethod
    def _rgb_to_hex(r,g,b): return f"#{r:02x}{g:02x}{b:02x}"
    def _nearest_in_palette(self, color, palette):
        try: r,g,b = self._hex_to_rgb(color)
        except Exception: return color
        best,bd = None, 10**9
        for name,hexc in palette.items():
            pr,pg,pb = self._hex_to_rgb(hexc)
            d = (r-pr)**2+(g-pg)**2+(b-pb)**2
            if d < bd: bd,best = d,hexc
        return best or color
    def quantize(self, color):
        if self.mode == "normal" or not color: return color
        if self.mode == "8bit":
            pal = self.PALETTES.get(self.palette_name, self.PALETTES["nes"])
            return self._nearest_in_palette(color, pal)
        if self.mode == "16bit":
            try: r,g,b = self._hex_to_rgb(color)
            except Exception: return color
            r = (r>>3)<<3; g = (g>>3)<<3; b = (b>>3)<<3
            return self._rgb_to_hex(r,g,b)
        return color
    def apply_to_canvas(self, canvas):
        cfg = self.MODES[self.mode]
        canvas.config(bg=cfg["bg"])
        self._draw_scanlines(canvas, cfg)
    def _draw_scanlines(self, canvas, cfg):
        canvas.delete("scanlines")
        if not cfg.get("scanlines"): return
        try:
            h = int(canvas.winfo_height()) or 400
            w = int(canvas.winfo_width()) or 400
        except Exception: return
        for y in range(0, h, 3):
            canvas.create_line(0, y, w, y, fill="#000000", stipple="gray25", tags="scanlines")


# ==========================================================
# 2) Señales internas
# ==========================================================
class _ReturnSignal(Exception):
    def __init__(self, value): self.value = value
class _BreakSignal(Exception): pass
class _ContinueSignal(Exception): pass


# ==========================================================
# 3) Sprites
# ==========================================================
class Sprite:
    def __init__(self, name, x=0, y=0, w=8, h=8, color="#ffffff", vx=0, vy=0):
        self.name=name; self.x=x; self.y=y; self.w=w; self.h=h
        self.color=color; self.vx=vx; self.vy=vy
        self.canvas_ids=[]
    def rect(self): return (self.x, self.y, self.x+self.w, self.y+self.h)
    def intersects(self, other):
        ax1,ay1,ax2,ay2 = self.rect()
        bx1,by1,bx2,by2 = other.rect()
        return not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1)


# ==========================================================
# 4) Objeto / Clase EZScript
# ==========================================================
class EZObject:
    def __init__(self, cls_name):
        self.cls_name = cls_name
        self.fields = {}
        self.methods = {}
    def __repr__(self): return f"<{self.cls_name} {self.fields}>"


# ==========================================================
# 5) Intérprete
# ==========================================================
class EasyScriptInterpreter:
    def __init__(self, output_widget, canvas_widget, app, i18n=None):
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.sprites = {}
        self.events = {}
        self.timers = {}
        self.modules = {}
        self.breakpoints = set()
        self.debug_mode = False
        self.step_mode = False
        self._debug_gate = None
        self.call_stack = []
        self.line_times = {}
        self.output = output_widget
        self.canvas = canvas_widget
        self.app = app
        self.i18n = i18n or I18n("es")
        self.retro = RetroVideoMode()
        self.should_stop = False
        self.text_positions = {}
        self.emulated_os = platform.system()
        self.current_line_width = 3
        self.current_draw_color = "#0984e3"
        self.show_timestamps = False
        self.execution_start = None; self.execution_time = 0.0
        self.executed_lines = 0; self.last_error_line = None
        self.test_results = []
        self.achievements = []
        self.COLOR_MAP = {
            "rojo":"#e74c3c","azul":"#3498db","verde":"#2ecc71","amarillo":"#f1c40f",
            "naranja":"#e67e22","morado":"#9b59b6","rosa":"#fd79a8","negro":"#2c3e50",
            "blanco":"#ffffff","gris":"#95a5a6","cian":"#00cec9","violeta":"#a29bfe",
            "marron":"#6d4c41","marrón":"#6d4c41","dorado":"#fdcb6e","plateado":"#b2bec3",
        }
        self._setup_console_tags()
        self._init_audio()

    def _init_audio(self):
        self.audio_enabled = True
        try:
            if platform.system() == "Windows":
                import winsound  # noqa
        except Exception:
            self.audio_enabled = False

    def _beep(self, freq=440, dur_ms=80):
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.Beep(int(freq), int(dur_ms)); return
        except Exception: pass
        try: self.app.root.bell()
        except Exception: pass

    def _setup_console_tags(self):
        try:
            self.output.tag_config("info", foreground="#ffffff")
            self.output.tag_config("error", foreground="#e74c3c")
            self.output.tag_config("warn", foreground="#f39c12")
            self.output.tag_config("success", foreground="#2ecc71")
            self.output.tag_config("dim", foreground="#7f8c8d")
            self.output.tag_config("ts", foreground="#636e72")
            self.output.tag_config("test_pass", foreground="#00b894")
            self.output.tag_config("test_fail", foreground="#d63031")
        except Exception: pass

    def get_color(self, val):
        c = str(val).strip().lower().replace('"','').replace("'","")
        if c.startswith("#") or c.startswith("rgb"): return self.retro.quantize(c)
        return self.retro.quantize(self.COLOR_MAP.get(c, c))

    def log(self, text, level="info"):
        prefix = f"[{datetime.now().strftime('%H:%M:%S')}] " if self.show_timestamps else ""
        full = prefix + str(text)
        self.output.insert(tk.END, full + "\n", level)
        self.output.see(tk.END)
        try: self.output.update()
        except Exception: pass
        try:
            ln = int(self.output.index(tk.END).split('.')[0])
            self.text_positions[str(text).strip()] = (100, ln*20)
        except Exception: pass
    def log_info(self,t):    self.log(f"ℹ️  {t}", "info")
    def log_warn(self,t):    self.log(f"⚠️  {t}", "warn")
    def log_error(self,t):   self.log(f"❌ {t}", "error")
    def log_success(self,t): self.log(f"✅ {t}", "success")

    def eval_expr(self, expr):
        expr = str(expr).strip()
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        tokens = re.split(r'(\s+|[+\-*/()==><!]+)', expr)
        out = []
        for token in tokens:
            t = token.strip()
            if t in self.variables:
                v = self.variables[t]
                if isinstance(v, EZObject): out.append(repr(v))
                elif isinstance(v, str):    out.append(f'"{v}"')
                else:                        out.append(repr(v))
            else:
                out.append(token)
        parsed = "".join(out)
        try:
            return eval(parsed, {"__builtins__": {}}, {})
        except Exception:
            return expr

    def _eval_cond(self, expr):
        expr = expr.strip()
        if expr.startswith("(") and expr.endswith(")"): expr = expr[1:-1].strip()
        v = self.eval_expr(expr)
        if isinstance(v, str):
            if v.lower() in ("true","verdadero","1"): return True
            if v.lower() in ("false","falso","0",""): return False
            return bool(v)
        return bool(v)

    def validate(self, code):
        problems = []
        canon = [self.i18n.translate_line(l) for l in code.split("\n")]
        for idx,line in enumerate(canon, start=1):
            s = line.strip()
            if not s or s.startswith("//"): continue
            if s.count("(") != s.count(")"): problems.append((idx,"Paréntesis desbalanceados"))
            if s.count("[") != s.count("]"): problems.append((idx,"Corchetes desbalanceados"))
        return problems

    def _safe_int(self,v,d=0):
        try: return int(float(v))
        except Exception: return d
    def _safe_float(self,v,d=0.0):
        try: return float(v)
        except Exception: return d

    def _debug_hook(self, line_num):
        if not self.debug_mode: return
        if line_num in self.breakpoints or self.step_mode:
            self.step_mode = False
            self._debug_gate = threading.Event()
            if self.app:
                self.app.root.after(0, lambda: self.app._on_debug_pause(line_num, self))
            self._debug_gate.wait(timeout=60)
            self._debug_gate = None
            if self.should_stop:
                raise _BreakSignal()

    def continue_debug(self):
        if self._debug_gate: self._debug_gate.set()
    def step_next(self):
        self.step_mode = True
        if self._debug_gate: self._debug_gate.set()

    def _find_block_end(self, lines, start, end, open_kw, close_kw):
        depth = 1
        for j in range(start+1, end):
            t = self.i18n.translate_line(lines[j]['text'].strip())
            if t.startswith(open_kw): depth += 1
            elif t.startswith(close_kw):
                depth -= 1
                if depth == 0: return j
        return end

    def _find_if_structure(self, lines, start, end):
        depth = 1; else_idx = None
        for j in range(start+1, end):
            t = self.i18n.translate_line(lines[j]['text'].strip())
            if t.startswith("si:"): depth += 1
            elif t.startswith("fin_si"):
                depth -= 1
                if depth == 0: return j, else_idx
            elif depth == 1 and t.startswith("sino"): else_idx = j
        return end, else_idx

    def run_block(self, lines, start=0, end=None):
        if end is None: end = len(lines)
        i = start
        while i < end and not self.should_stop:
            raw = lines[i]['text']; ln = lines[i]['num']
            line = self.i18n.translate_line(raw.strip())
            if not line or line.startswith("//") or line.startswith("///"):
                i += 1; continue

            try: self._debug_hook(ln)
            except _BreakSignal: return

            if line.startswith("si:"):
                cond = line[3:].strip()
                end_si, else_idx = self._find_if_structure(lines, i, end)
                if self._eval_cond(cond):
                    self.run_block(lines, i+1, else_idx if else_idx else end_si)
                elif else_idx is not None:
                    self.run_block(lines, else_idx+1, end_si)
                i = end_si + 1; continue

            if line.startswith("mientras:"):
                cond = line[8:].strip()
                end_w = self._find_block_end(lines, i, end, "mientras:", "fin_mientras")
                guard = 0
                while self._eval_cond(cond) and not self.should_stop and guard < 1_000_000:
                    try: self.run_block(lines, i+1, end_w)
                    except _BreakSignal: break
                    except _ContinueSignal: pass
                    guard += 1
                i = end_w + 1; continue

            if line.startswith("bucle:"):
                cnt = line[6:].strip()
                end_b = self._find_block_end(lines, i, end, "bucle:", "fin_bucle")
                n = self._safe_int(self.eval_expr(cnt))
                for _ in range(max(0,n)):
                    if self.should_stop: break
                    try: self.run_block(lines, i+1, end_b)
                    except _BreakSignal: break
                    except _ContinueSignal: continue
                i = end_b + 1; continue

            if line.startswith("funcion:"):
                end_f = self._find_block_end(lines, i, end, "funcion:", "fin_funcion")
                m = re.match(r'funcion:\s*\((.*?)\)', line)
                if m:
                    parts = m.group(1).split(",",1)
                    name = parts[0].strip()
                    params = [p.strip() for p in parts[1].split(",")] if len(parts)>1 else []
                    self.functions[name] = {"params": params, "body": lines[i+1:end_f]}
                i = end_f + 1; continue

            if line.startswith("clase:"):
                end_c = self._find_block_end(lines, i, end, "clase:", "fin_clase")
                m = re.match(r'clase:\s*\((.*?)\)', line)
                if m:
                    parts = [p.strip() for p in m.group(1).split(",")]
                    name = parts[0]
                    parent = parts[1] if len(parts) > 1 else None
                    body = lines[i+1:end_c]
                    methods = {}; fields = {}
                    j = 0
                    while j < len(body):
                        t = self.i18n.translate_line(body[j]['text'].strip())
                        if t.startswith("funcion:"):
                            me = self._find_block_end(body, j, len(body), "funcion:", "fin_funcion")
                            mm = re.match(r'funcion:\s*\((.*?)\)', t)
                            if mm:
                                pp = mm.group(1).split(",",1)
                                mname = pp[0].strip()
                                mparams = [p.strip() for p in pp[1].split(",")] if len(pp)>1 else []
                                methods[mname] = {"params": mparams, "body": body[j+1:me]}
                            j = me + 1
                        elif t.startswith("propiedad:"):
                            pm = re.match(r'propiedad:\s*\((.*?),(.*?)\)', t)
                            if pm:
                                fields[pm.group(1).strip()] = self.eval_expr(pm.group(2))
                            j += 1
                        else:
                            j += 1
                    self.classes[name] = {"parent": parent, "methods": methods, "fields": fields}
                i = end_c + 1; continue

            if line.startswith("test:"):
                end_t = self._find_block_end(lines, i, end, "test:", "fin_test")
                m = re.match(r'test:\s*\((.*?)\)', line)
                name = m.group(1).strip().strip('"').strip("'") if m else "test"
                try:
                    self.run_block(lines, i+1, end_t)
                    self.test_results.append((name, True, ""))
                    self.log(f"  ✅ {name}", "test_pass")
                except AssertionError as e:
                    self.test_results.append((name, False, str(e)))
                    self.log(f"  ❌ {name}: {e}", "test_fail")
                except Exception as e:
                    self.test_results.append((name, False, str(e)))
                    self.log(f"  ❌ {name}: {e}", "test_fail")
                i = end_t + 1; continue

            if line.startswith("romper"): raise _BreakSignal()
            if line.startswith("continuar"): raise _ContinueSignal()
            if line.startswith("retornar"):
                val = line[8:].strip()
                raise _ReturnSignal(self.eval_expr(val) if val else None)

            self.executed_lines += 1
            t0 = time.time()
            try:
                self._execute_line(line, ln)
            except (_ReturnSignal, _BreakSignal, _ContinueSignal): raise
            except AssertionError: raise
            except Exception as e:
                self.last_error_line = ln
                self.log_error(f"Error L{ln}: {e}")
                if self.app: self.app.highlight_error_line(ln)
            self.line_times[ln] = self.line_times.get(ln, 0.0) + (time.time() - t0)
            i += 1

    def _execute_line(self, line, line_num):
        # --- Salida ---
        if line.startswith("mostrar ") or line.startswith("print "):
            self.log(self.eval_expr(line.split(" ",1)[1]))
        elif line == "limpiar_pantalla":
            self.output.delete("1.0", tk.END); self.canvas.delete("all")
            self.text_positions.clear()
        elif line == "limpiar_consola":
            self.output.delete("1.0", tk.END)
        elif line.startswith("boton:") or line.startswith("button:"):
            prefix = "boton:" if line.startswith("boton:") else "button:"
            content = line[len(prefix):].strip()
            if content.startswith("(") and content.endswith(")"): content = content[1:-1]
            parts = content.split(",",1)
            txt = str(self.eval_expr(parts[0]))
            action = parts[1].strip() if len(parts)>1 else ""
            btn = tk.Button(self.output, text=txt, bg="#0984e3", fg="white",
                            font=("Arial",9,"bold"),
                            command=lambda c=action: self.execute_inline(c))
            self.output.window_create(tk.END, window=btn)
            self.output.insert(tk.END, "\n")
        # --- Variables ---
        elif line.startswith("var:") or line.startswith("VARIABLE_DEFINIR:"):
            m = re.match(r'(?:var|VARIABLE_DEFINIR):\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = self.eval_expr(m.group(2))
        elif line.startswith("incrementar:"):
            m = re.match(r'incrementar:\s*\((.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = self.variables.get(k,0) + self._safe_int(self.eval_expr(m.group(2)),1)
        elif line.startswith("decrementar:"):
            m = re.match(r'decrementar:\s*\((.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = self.variables.get(k,0) - self._safe_int(self.eval_expr(m.group(2)),1)
        elif line.startswith("entrada:"):
            m = re.match(r'entrada:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = self.app.ask_input(str(self.eval_expr(m.group(2)))) or ""
        # --- Cadenas ---
        elif line.startswith("mayusculas:"):
            m = re.match(r'mayusculas:\s*\((.*?)\)', line)
            if m:
                k = m.group(1).strip(); self.variables[k] = str(self.variables.get(k,"")).upper()
        elif line.startswith("minusculas:"):
            m = re.match(r'minusculas:\s*\((.*?)\)', line)
            if m:
                k = m.group(1).strip(); self.variables[k] = str(self.variables.get(k,"")).lower()
        elif line.startswith("longitud:"):
            m = re.match(r'longitud:\s*\((.*?)\)', line)
            if m: self.log(f"📏 Longitud: {len(str(self.eval_expr(m.group(1))))}")
        elif line.startswith("reemplazar:"):
            m = re.match(r'reemplazar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                self.variables[k] = str(self.variables.get(k,"")).replace(
                    str(self.eval_expr(m.group(2))), str(self.eval_expr(m.group(3))))
        elif line.startswith("tipo_dato:"):
            m = re.match(r'tipo_dato:\s*\((.*?)\)', line)
            if m: self.log(f"ℹ️ Tipo: {type(self.eval_expr(m.group(1))).__name__}")
        elif line.startswith("concatenar:") or line.startswith("unir:"):
            m = re.match(r'(?:concatenar|unir):\s*\((.*?),(.*?),(.*?)\)', line)
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
        elif line.startswith("dividir_texto:"):
            m = re.match(r'dividir_texto:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = \
                    str(self.eval_expr(m.group(2))).split(str(self.eval_expr(m.group(3))))
        elif line.startswith("indice:"):
            m = re.match(r'indice:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                obj = self.eval_expr(m.group(2))
                idx = self._safe_int(self.eval_expr(m.group(3)))
                try: self.variables[m.group(1).strip()] = obj[idx]
                except Exception: self.variables[m.group(1).strip()] = ""
        elif line.startswith("invertir:"):
            m = re.match(r'invertir:\s*\((.*?),(.*?)\)', line)
            if m:
                v = str(self.eval_expr(m.group(2)))
                self.variables[m.group(1).strip()] = v[::-1]
        elif line.startswith("ordenar:"):
            m = re.match(r'ordenar:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = sorted(self.eval_expr(m.group(2)))
                except Exception: pass
        elif line.startswith("contar:"):
            m = re.match(r'contar:\s*\((.*?)\)', line)
            if m: self.log(f"🔢 Contar: {len(str(self.eval_expr(m.group(1))))}")
        # --- Matemáticas ---
        elif line.startswith("random:"):
            m = re.match(r'random:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = random.randint(
                    self._safe_int(self.eval_expr(m.group(2))),
                    self._safe_int(self.eval_expr(m.group(3))))
        elif line.startswith("raiz:"):
            m = re.match(r'raiz:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = math.sqrt(float(self.eval_expr(m.group(2))))
                except Exception: self.variables[m.group(1).strip()] = 0
        elif line.startswith("potencia:"):
            m = re.match(r'potencia:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = math.pow(
                    float(self.eval_expr(m.group(2))), float(self.eval_expr(m.group(3))))
        elif line.startswith("redondear:"):
            m = re.match(r'redondear:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = round(float(self.eval_expr(m.group(2))))
                except Exception: pass
        elif line.startswith("absoluto:"):
            m = re.match(r'absoluto:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = abs(float(self.eval_expr(m.group(2))))
                except Exception: pass
        elif line.startswith("seno:"):
            m = re.match(r'seno:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = math.sin(math.radians(float(self.eval_expr(m.group(2)))))
                except Exception: pass
        elif line.startswith("coseno:"):
            m = re.match(r'coseno:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = math.cos(math.radians(float(self.eval_expr(m.group(2)))))
                except Exception: pass
        elif line.startswith("maximo:"):
            m = re.match(r'maximo:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = max(
                    self._safe_float(self.eval_expr(m.group(2))),
                    self._safe_float(self.eval_expr(m.group(3))))
        elif line.startswith("minimo:"):
            m = re.match(r'minimo:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = min(
                    self._safe_float(self.eval_expr(m.group(2))),
                    self._safe_float(self.eval_expr(m.group(3))))
        elif line.startswith("pi:"):
            m = re.match(r'pi:\s*\((.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = math.pi
        elif line.startswith("sumar:"):
            m = re.match(r'sumar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = self._safe_float(self.eval_expr(m.group(2))) + self._safe_float(self.eval_expr(m.group(3)))
        elif line.startswith("restar:"):
            m = re.match(r'restar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = self._safe_float(self.eval_expr(m.group(2))) - self._safe_float(self.eval_expr(m.group(3)))
        elif line.startswith("multiplicar:"):
            m = re.match(r'multiplicar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = self._safe_float(self.eval_expr(m.group(2))) * self._safe_float(self.eval_expr(m.group(3)))
        elif line.startswith("dividir:"):
            m = re.match(r'dividir:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = self._safe_float(self.eval_expr(m.group(2))) / self._safe_float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = 0
        elif line.startswith("modulo:"):
            m = re.match(r'modulo:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = self._safe_float(self.eval_expr(m.group(2))) % self._safe_float(self.eval_expr(m.group(3)))
                except Exception: self.variables[m.group(1).strip()] = 0
        # --- Lógica ---
        elif line.startswith("igual_a:"):
            m = re.match(r'igual_a:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = (str(self.eval_expr(m.group(2))) == str(self.eval_expr(m.group(3))))
        elif line.startswith("mayor_que:"):
            m = re.match(r'mayor_que:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = self._safe_float(self.eval_expr(m.group(2))) > self._safe_float(self.eval_expr(m.group(3)))
        elif line.startswith("menor_que:"):
            m = re.match(r'menor_que:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = self._safe_float(self.eval_expr(m.group(2))) < self._safe_float(self.eval_expr(m.group(3)))
        elif line.startswith("y:"):
            m = re.match(r'y:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) and bool(self.eval_expr(m.group(3)))
        elif line.startswith("o:"):
            m = re.match(r'o:\s*\((.*?),(.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = bool(self.eval_expr(m.group(2))) or bool(self.eval_expr(m.group(3)))
        elif line.startswith("no:"):
            m = re.match(r'no:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = not bool(self.eval_expr(m.group(2)))
        # --- Dibujo ---
        elif line.startswith("color:"):
            m = re.match(r'color:\s*\((.*?)\)', line)
            if m: self.current_draw_color = self.get_color(self.eval_expr(m.group(1).strip()))
        elif line.startswith("linea:"):
            m = re.match(r'linea:\s*\((.*?)\)', line)
            if m:
                a = [x.strip() for x in m.group(1).split(',')]
                if len(a) >= 4:
                    c = self.get_color(self.eval_expr(a[4])) if len(a)>4 else self.current_draw_color
                    self.canvas.create_line(
                        self._safe_int(self.eval_expr(a[0])), self._safe_int(self.eval_expr(a[1])),
                        self._safe_int(self.eval_expr(a[2])), self._safe_int(self.eval_expr(a[3])),
                        fill=c, width=self.current_line_width)
        elif line.startswith("rectangulo:"):
            m = re.match(r'rectangulo:\s*\((.*?)\)', line)
            if m:
                a = [self.eval_expr(x.strip()) for x in m.group(1).split(',')]
                x,y = self._safe_int(a[0]), self._safe_int(a[1])
                w,h = self._safe_int(a[2]), self._safe_int(a[3])
                c = self.get_color(a[4]) if len(a)>4 else self.current_draw_color
                self.canvas.create_rectangle(x,y,x+w,y+h,fill=c,outline="")
        elif line.startswith("circulo:"):
            m = re.match(r'circulo:\s*\((.*?)\)', line)
            if m:
                a = [self.eval_expr(x.strip()) for x in m.group(1).split(',')]
                x,y = self._safe_int(a[0]), self._safe_int(a[1]); r = self._safe_int(a[2])
                c = self.get_color(a[3]) if len(a)>3 else self.current_draw_color
                self.canvas.create_oval(x-r,y-r,x+r,y+r,fill=c,outline="")
        elif line.startswith("ovalo:"):
            m = re.match(r'ovalo:\s*\((.*?)\)', line)
            if m:
                a = [self.eval_expr(x.strip()) for x in m.group(1).split(',')]
                x,y = self._safe_int(a[0]), self._safe_int(a[1])
                w,h = self._safe_int(a[2]), self._safe_int(a[3])
                c = self.get_color(a[4]) if len(a)>4 else self.current_draw_color
                self.canvas.create_oval(x,y,x+w,y+h,fill=c,outline="")
        elif line.startswith("triangulo:"):
            m = re.match(r'triangulo:\s*\((.*?)\)', line)
            if m:
                a = [self.eval_expr(x.strip()) for x in m.group(1).split(',')]
                pts = [self._safe_int(a[i]) for i in range(6)]
                c = self.get_color(a[6]) if len(a)>6 else self.current_draw_color
                self.canvas.create_polygon(pts,fill=c,outline="")
        elif line.startswith("texto_canvas:"):
            m = re.match(r'texto_canvas:\s*\((.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                x = self._safe_int(self.eval_expr(m.group(1)))
                y = self._safe_int(self.eval_expr(m.group(2)))
                txt = self.eval_expr(m.group(3))
                c = self.get_color(self.eval_expr(m.group(4))) if m.group(4) else self.current_draw_color
                self.canvas.create_text(x,y,text=str(txt),fill=c,font=("Arial",10,"bold"))
        elif line.startswith("grosor_linea:"):
            m = re.match(r'grosor_linea:\s*\((.*?)\)', line)
            if m: self.current_line_width = self._safe_int(self.eval_expr(m.group(1)),1)
        elif line == "borrar_canvas":
            self.canvas.delete("all")
        elif line.startswith("cuadricula:"):
            m = re.match(r'cuadricula:\s*\((.*?)\)', line)
            if m:
                step = self._safe_int(self.eval_expr(m.group(1)),40)
                if step > 0:
                    gc = self.retro.quantize("#34495e")
                    for x in range(0,400,step): self.canvas.create_line(x,0,x,400,fill=gc,dash=(1,3))
                    for y in range(0,400,step): self.canvas.create_line(0,y,400,y,fill=gc,dash=(1,3))
        elif line.startswith("rgb:"):
            m = re.match(r'rgb:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                r = self._safe_int(self.eval_expr(m.group(1))) % 256
                g = self._safe_int(self.eval_expr(m.group(2))) % 256
                b = self._safe_int(self.eval_expr(m.group(3))) % 256
                self.current_draw_color = self.retro.quantize(f"#{r:02x}{g:02x}{b:02x}")
        elif line.startswith("pixel:"):
            m = re.match(r'pixel:\s*\((.*?)\)', line)
            if m:
                a = [x.strip() for x in m.group(1).split(',')]
                x = self._safe_int(self.eval_expr(a[0])); y = self._safe_int(self.eval_expr(a[1]))
                c = self.get_color(self.eval_expr(a[2])) if len(a)>2 else self.current_draw_color
                s = self.retro.MODES[self.retro.mode]["pixel_scale"]
                self.canvas.create_rectangle(x,y,x+s,y+s,fill=c,outline="")
        # --- Modos gráficos ---
        elif line.startswith("modo_grafico:"):
            m = re.match(r'modo_grafico:\s*\((.*?)\)', line)
            if m:
                mode = str(self.eval_expr(m.group(1))).strip().lower()
                if mode in ("8bit","8-bit","8"): mode = "8bit"
                elif mode in ("16bit","16-bit","16"): mode = "16bit"
                else: mode = "normal"
                self.retro.mode = mode
                if self.app: self.app.apply_video_mode(mode, from_script=True)
        elif line.startswith("paleta:"):
            m = re.match(r'paleta:\s*\((.*?)\)', line)
            if m:
                name = str(self.eval_expr(m.group(1))).strip().lower()
                if name in RetroVideoMode.PALETTES:
                    self.retro.palette_name = name
                    if self.app: self.app.apply_palette(name, from_script=True)
        # --- Estructuras ---
        elif line.startswith("lista:"):
            m = re.match(r'lista:\s*\((.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = []
        elif line.startswith("mapa:"):
            m = re.match(r'mapa:\s*\((.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = {}
        elif line.startswith("matriz:"):
            m = re.match(r'matriz:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                rows = self._safe_int(self.eval_expr(m.group(2)))
                cols = self._safe_int(self.eval_expr(m.group(3)))
                self.variables[m.group(1).strip()] = [[0]*cols for _ in range(rows)]
        elif line.startswith("agregar:"):
            m = re.match(r'agregar:\s*\((.*?),(.*?)\)', line)
            if m:
                k = m.group(1).strip()
                if isinstance(self.variables.get(k), list):
                    self.variables[k].append(self.eval_expr(m.group(2)))
        elif line.startswith("asignar:"):
            m = re.match(r'asignar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                obj = self.variables.get(m.group(1).strip())
                key = self.eval_expr(m.group(2)); val = self.eval_expr(m.group(3))
                try:
                    if isinstance(obj, dict): obj[key] = val
                    elif isinstance(obj, list): obj[int(key)] = val
                    elif isinstance(obj, EZObject): obj.fields[str(key)] = val
                except Exception: pass
        # --- Funciones / clases ---
        elif line.startswith("llamar:"):
            m = re.match(r'llamar:\s*\((.*?)\)', line)
            if m:
                parts = [p.strip() for p in m.group(1).split(',')]
                fname = parts[0].strip('"').strip("'")
                args = parts[1:]
                self._call_function(fname, args)
        elif line.startswith("nuevo:"):
            m = re.match(r'nuevo:\s*\((.*?),(.*?)\)', line)
            if m:
                var = m.group(1).strip(); cls = m.group(2).strip().strip('"').strip("'")
                self.variables[var] = self._instantiate(cls)
        elif line.startswith("llamar_metodo:"):
            m = re.match(r'llamar_metodo:\s*\((.*?),(.*?)(?:,(.*))?\)', line)
            if m:
                var = m.group(1).strip(); meth = m.group(2).strip().strip('"').strip("'")
                args = [a.strip() for a in m.group(3).split(",")] if m.group(3) else []
                obj = self.variables.get(var)
                if isinstance(obj, EZObject):
                    self._invoke_method(obj, meth, args)
        # --- Eventos / timers ---
        elif line.startswith("al:"):
            m = re.match(r'al:\s*\((.*?),(.*?)\)', line)
            if m:
                ev = m.group(1).strip().strip('"').strip("'")
                fn = m.group(2).strip().strip('"').strip("'")
                self.events.setdefault(ev, []).append(fn)
        elif line.startswith("emitir:"):
            m = re.match(r'emitir:\s*\((.*?)(?:,(.*))?\)', line)
            if m:
                ev = m.group(1).strip().strip('"').strip("'")
                payload = self.eval_expr(m.group(2)) if m.group(2) else None
                for h in self.events.get(ev, []):
                    try: self._invoke_handler(h, payload)
                    except Exception as e: self.log_warn(f"Handler {ev}: {e}")
        elif line.startswith("cada:"):
            m = re.match(r'cada:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                tid = m.group(1).strip().strip('"').strip("'")
                ms = self._safe_int(self.eval_expr(m.group(2)),1000)
                fn = m.group(3).strip().strip('"').strip("'")
                self._start_timer(tid, ms, fn)
        # --- Sprites ---
        elif line.startswith("sprite:"):
            m = re.match(r'sprite:\s*\((.*?),(.*?),(.*?),(.*?),(.*?)(?:,(.*?))?\)', line)
            if m:
                name = m.group(1).strip().strip('"').strip("'")
                x = self._safe_int(self.eval_expr(m.group(2)))
                y = self._safe_int(self.eval_expr(m.group(3)))
                w = self._safe_int(self.eval_expr(m.group(4)),8)
                h = self._safe_int(self.eval_expr(m.group(5)),8)
                c = self.get_color(self.eval_expr(m.group(6))) if m.group(6) else "#ffffff"
                self.sprites[name] = Sprite(name,x,y,w,h,c)
                self._draw_sprite(self.sprites[name])
        elif line.startswith("mover_sprite:"):
            m = re.match(r'mover_sprite:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                name = m.group(1).strip().strip('"').strip("'")
                dx = self._safe_int(self.eval_expr(m.group(2)))
                dy = self._safe_int(self.eval_expr(m.group(3)))
                s = self.sprites.get(name)
                if s:
                    s.x += dx; s.y += dy; self._draw_sprite(s)
        elif line.startswith("colisiona:"):
            m = re.match(r'colisiona:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                var = m.group(1).strip()
                a = self.sprites.get(m.group(2).strip().strip('"').strip("'"))
                b = self.sprites.get(m.group(3).strip().strip('"').strip("'"))
                self.variables[var] = bool(a and b and a.intersects(b))
        # --- Sonido ---
        elif line.startswith("musica:"):
            m = re.match(r'musica:\s*\((.*?)\)', line)
            if m: self._play_music(str(self.eval_expr(m.group(1))))
        elif line.startswith("nota:"):
            m = re.match(r'nota:\s*\((.*?),(.*?)\)', line)
            if m:
                f = self._safe_int(self.eval_expr(m.group(1)), 440)
                d = self._safe_int(self.eval_expr(m.group(2)), 120)
                self._beep(f, d)
        elif line == "pitido":
            try: self.app.root.bell()
            except Exception: pass
        elif line.startswith("beep:"):
            m = re.match(r'beep:\s*\((.*?)(?:,(.*?))?\)', line)
            if m:
                f = self._safe_int(self.eval_expr(m.group(1)), 440)
                d = self._safe_int(self.eval_expr(m.group(2)), 80) if m.group(2) else 80
                self._beep(f, d)
        # --- Tests ---
        elif line.startswith("afirmar_igual:"):
            m = re.match(r'afirmar_igual:\s*\((.*?),(.*?)(?:,(.*))?\)', line)
            if m:
                a = self.eval_expr(m.group(1)); b = self.eval_expr(m.group(2))
                msg = self.eval_expr(m.group(3)) if m.group(3) else f"{a!r} != {b!r}"
                assert str(a) == str(b), msg
        elif line.startswith("afirmar_verdad:"):
            m = re.match(r'afirmar_verdad:\s*\((.*?)(?:,(.*))?\)', line)
            if m:
                v = self.eval_expr(m.group(1))
                msg = self.eval_expr(m.group(2)) if m.group(2) else f"no es verdadero: {v}"
                assert bool(v), msg
        elif line.startswith("afirmar_falso:"):
            m = re.match(r'afirmar_falso:\s*\((.*?)(?:,(.*))?\)', line)
            if m:
                v = self.eval_expr(m.group(1))
                msg = self.eval_expr(m.group(2)) if m.group(2) else f"no es falso: {v}"
                assert not bool(v), msg
        # --- Librería estándar ---
        elif line.startswith("hash_md5:"):
            m = re.match(r'hash_md5:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = hashlib.md5(str(self.eval_expr(m.group(2))).encode()).hexdigest()
        elif line.startswith("hash_sha256:"):
            m = re.match(r'hash_sha256:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = hashlib.sha256(str(self.eval_expr(m.group(2))).encode()).hexdigest()
        elif line.startswith("base64_cod:"):
            m = re.match(r'base64_cod:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = base64.b64encode(str(self.eval_expr(m.group(2))).encode()).decode("ascii")
        elif line.startswith("base64_dec:"):
            m = re.match(r'base64_dec:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = base64.b64decode(str(self.eval_expr(m.group(2))).encode()).decode("utf-8")
                except Exception as e: self.log_warn(str(e))
        elif line.startswith("regex_buscar:"):
            m = re.match(r'regex_buscar:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try:
                    txt = str(self.eval_expr(m.group(2))); pat = str(self.eval_expr(m.group(3)))
                    self.variables[m.group(1).strip()] = re.findall(pat, txt)
                except Exception as e: self.log_warn(str(e))
        elif line.startswith("csv_parsear:"):
            m = re.match(r'csv_parsear:\s*\((.*?),(.*?)\)', line)
            if m:
                txt = str(self.eval_expr(m.group(2)))
                self.variables[m.group(1).strip()] = list(csv.reader(io.StringIO(txt)))
        elif line.startswith("http_get:"):
            m = re.match(r'http_get:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    with urllib.request.urlopen(str(self.eval_expr(m.group(2))), timeout=8) as r:
                        self.variables[m.group(1).strip()] = r.read().decode("utf-8","replace")
                except Exception as e:
                    self.log_warn(f"HTTP: {e}"); self.variables[m.group(1).strip()] = ""
        elif line.startswith("suma_lista:"):
            m = re.match(r'suma_lista:\s*\((.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = sum(self.eval_expr(m.group(2)))
                except Exception: self.variables[m.group(1).strip()] = 0
        elif line.startswith("longitud_lista:"):
            m = re.match(r'longitud_lista:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = len(self.eval_expr(m.group(2)))
        elif line.startswith("contiene:"):
            m = re.match(r'contiene:\s*\((.*?),(.*?),(.*?)\)', line)
            if m:
                try: self.variables[m.group(1).strip()] = self.eval_expr(m.group(3)) in self.eval_expr(m.group(2))
                except Exception: self.variables[m.group(1).strip()] = False
        # --- Idioma ---
        elif line.startswith("idioma:"):
            m = re.match(r'idioma:\s*\((.*?)\)', line)
            if m:
                lang = str(self.eval_expr(m.group(1))).strip().lower()[:2]
                self.i18n.set_lang(lang)
                if self.app: self.app.change_language(lang, from_script=True)
        # --- Sistema ---
        elif line == "fecha":   self.log(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
        elif line == "hora":    self.log(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        elif line == "hora_actual": self.log(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        elif line == "fecha_hora":  self.log(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        elif line.startswith("esperar:"):
            m = re.match(r'esperar:\s*\((.*?)\)', line)
            if m:
                t = self._safe_float(self.eval_expr(m.group(1)))
                end = time.time() + t
                while time.time() < end and not self.should_stop:
                    time.sleep(0.02)
                    try: self.output.update()
                    except Exception: pass
        elif line.startswith("alerta:"):
            m = re.match(r'alerta:\s*\((.*?)\)', line)
            if m: messagebox.showinfo("EasyScript", str(self.eval_expr(m.group(1))))
        elif line.startswith("confirmar:"):
            m = re.match(r'confirmar:\s*\((.*?),(.*?)\)', line)
            if m:
                self.variables[m.group(1).strip()] = messagebox.askyesno("Confirmar",
                                                                          str(self.eval_expr(m.group(2))))
        elif line.startswith("abrir_url:"):
            m = re.match(r'abrir_url:\s*\((.*?)\)', line)
            if m: webbrowser.open(str(self.eval_expr(m.group(1))))
        elif line.startswith("copiar:"):
            m = re.match(r'copiar:\s*\((.*?)\)', line)
            if m:
                self.app.root.clipboard_clear()
                self.app.root.clipboard_append(str(self.eval_expr(m.group(1))))
        elif line.startswith("uuid:"):
            m = re.match(r'uuid:\s*\((.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = str(uuidlib.uuid4())
        elif line.startswith("log_info:"):
            m = re.match(r'log_info:\s*\((.*?)\)', line)
            if m: self.log_info(self.eval_expr(m.group(1)))
        elif line.startswith("log_warn:"):
            m = re.match(r'log_warn:\s*\((.*?)\)', line)
            if m: self.log_warn(self.eval_expr(m.group(1)))
        elif line.startswith("log_error:"):
            m = re.match(r'log_error:\s*\((.*?)\)', line)
            if m: self.log_error(self.eval_expr(m.group(1)))
        elif line.startswith("logro:"):
            m = re.match(r'logro:\s*\((.*?)\)', line)
            if m:
                ach = str(self.eval_expr(m.group(1)))
                if ach not in self.achievements:
                    self.achievements.append(ach)
                    self.log(f"🏆 {ach}", "success")
        # --- Archivos ---
        elif line.startswith("crear_archivo:"):
            m = re.match(r'crear_archivo:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    with open(self.eval_expr(m.group(1)), "w", encoding="utf-8") as f:
                        f.write(str(self.eval_expr(m.group(2))))
                    self.log_success(f"OK: {self.eval_expr(m.group(1))}")
                except Exception as e: self.log_error(str(e))
        elif line.startswith("leer_archivo:"):
            m = re.match(r'leer_archivo:\s*\((.*?),(.*?)\)', line)
            if m:
                try:
                    with open(self.eval_expr(m.group(2)), "r", encoding="utf-8") as f:
                        self.variables[m.group(1).strip()] = f.read()
                except Exception as e: self.log_error(str(e))
        elif line.startswith("existe_archivo:"):
            m = re.match(r'existe_archivo:\s*\((.*?),(.*?)\)', line)
            if m: self.variables[m.group(1).strip()] = os.path.exists(str(self.eval_expr(m.group(2))))
        elif line == "detener":
            self.should_stop = True
        elif line.startswith("importar:"):
            m = re.match(r'importar:\s*\((.*?)\)', line)
            if m:
                path = str(self.eval_expr(m.group(1)))
                self._import_module(path)
        else:
            if ":" in line and not line.startswith("//"):
                self.log_warn(f"Comando no reconocido L{line_num}: {line}")

    # ---------------- funciones / objetos ----------------
    def _call_function(self, fname, args):
        if fname not in self.functions:
            self.log_warn(f"Función no definida: {fname}")
            return None
        spec = self.functions[fname]
        saved = dict(self.variables)
        for i,p in enumerate(spec["params"]):
            if i < len(args): self.variables[p] = self.eval_expr(args[i])
        self.call_stack.append(fname)
        result = None
        try:
            self.run_block(spec["body"])
        except _ReturnSignal as r: result = r.value
        except _BreakSignal: pass
        finally:
            self.call_stack.pop()
            self.variables = saved
        return result

    def _instantiate(self, cls_name):
        if cls_name not in self.classes:
            self.log_warn(f"Clase no definida: {cls_name}")
            return EZObject(cls_name)
        spec = self.classes[cls_name]
        obj = EZObject(cls_name)
        if spec.get("parent") in self.classes:
            parent = self._instantiate(spec["parent"])
            obj.fields.update(parent.fields)
            obj.methods.update(parent.methods)
        obj.fields.update(dict(spec["fields"]))
        obj.methods.update(dict(spec["methods"]))
        if "constructor" in obj.methods:
            self._invoke_method(obj, "constructor", [])
        return obj

    def _invoke_method(self, obj, meth, args):
        if meth not in obj.methods:
            self.log_warn(f"Método no existe: {meth}")
            return None
        spec = obj.methods[meth]
        saved_vars = dict(self.variables)
        self.variables["self"] = obj
        for i,p in enumerate(spec["params"]):
            if i < len(args): self.variables[p] = self.eval_expr(args[i])
        self.call_stack.append(f"{obj.cls_name}.{meth}")
        result = None
        try:
            self.run_block(spec["body"])
        except _ReturnSignal as r: result = r.value
        finally:
            self.call_stack.pop()
            self.variables = saved_vars
        return result

    def _invoke_handler(self, fn, payload):
        if fn in self.functions:
            saved = dict(self.variables)
            self.variables["_event"] = payload
            try: self._call_function(fn, [])
            finally: self.variables = saved

    def _import_module(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f: code = f.read()
        except Exception as e:
            self.log_error(f"Import: {e}"); return
        lines = [{'num':i+1,'text':l} for i,l in enumerate(code.split("\n"))]
        modname = os.path.splitext(os.path.basename(path))[0]
        saved_vars = dict(self.variables)
        try: self.run_block(lines)
        finally:
            exported = {k:v for k,v in self.variables.items() if k not in saved_vars}
            self.modules[modname] = exported
            self.variables = saved_vars
        self.log_info(f"📦 OK: {modname}")

    def _start_timer(self, tid, ms, fn):
        def tick():
            if self.should_stop: return
            try: self._call_function(fn, [])
            except Exception as e: self.log_warn(f"Timer {tid}: {e}")
            if tid in self.timers:
                self.timers[tid]["job"] = self.app.root.after(ms, tick)
        job = self.app.root.after(ms, tick)
        self.timers[tid] = {"job": job, "ms": ms, "fn": fn}

    def _draw_sprite(self, sp):
        for cid in sp.canvas_ids:
            try: self.canvas.delete(cid)
            except Exception: pass
        sp.canvas_ids.clear()
        cid = self.canvas.create_rectangle(sp.x, sp.y, sp.x+sp.w, sp.y+sp.h,
                                           fill=sp.color, outline="#000000",
                                           tags=("sprite", sp.name))
        sp.canvas_ids.append(cid)

    def _play_music(self, seq):
        notes = {"do":262,"re":294,"mi":330,"fa":349,"sol":392,"la":440,"si":494,"do5":523}
        parts = [p.strip() for p in seq.split(",") if p.strip()]
        def play(i=0):
            if i >= len(parts) or self.should_stop: return
            p = parts[i]
            if ":" in p:
                f,d = p.split(":"); f = self._safe_int(f,440); d = self._safe_int(d,150)
            else:
                key = p.lower(); f = notes.get(key, 440); d = 150
            self._beep(f, d)
            self.app.root.after(d+20, lambda: play(i+1))
        play()

    def execute(self, code):
        self.variables = {}
        self.should_stop = False
        self.executed_lines = 0
        self.last_error_line = None
        self.call_stack = []
        self.line_times = {}
        self.test_results = []
        self.output.delete("1.0", tk.END)
        self.canvas.delete("all")
        self.text_positions.clear()
        self.canvas.config(bg=self.retro.MODES[self.retro.mode]["bg"])
        self.current_draw_color = "#0984e3"

        self.execution_start = time.time()
        raw = code.split('\n')
        structured = [{'num':i+1,'text':l} for i,l in enumerate(raw)]
        try: self.run_block(structured)
        except _ReturnSignal: pass
        except _BreakSignal: pass
        self.execution_time = time.time() - self.execution_start

        self.log("", "info")
        passed = sum(1 for _,ok,_ in self.test_results if ok)
        total  = len(self.test_results)
        extra = f" · Tests {passed}/{total}" if total else ""
        self.log_success(
            f"{self.execution_time:.3f}s · {self.executed_lines} stmt · "
            f"{len(self.variables)} vars{extra}"
        )
        if self.app: self.app.on_execution_finished(self.execution_time, self.executed_lines)

    def execute_inline(self, single_line):
        if single_line:
            try: self.run_block([{'num':0,'text':single_line}])
            except Exception as e: self.log_error(str(e))


EZScriptInterpreter = EasyScriptInterpreter


# ==========================================================
# 6) Documento (pestaña)
# ==========================================================
class Document:
    def __init__(self, notebook, title="Sin título", untitled=True):
        self.frame = tk.Frame(notebook)
        self.path = None
        self.modified = False
        self.untitled = untitled
        wrap_frame = tk.Frame(self.frame); wrap_frame.pack(fill=tk.BOTH, expand=True)
        self.linenumbers = tk.Text(wrap_frame, width=4, padx=4, takefocus=0, border=0,
                                   background="#282c34", foreground="#7f8c8d",
                                   font=("Consolas", 10), state="disabled")
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.editor = tk.Text(wrap_frame, font=("Consolas", 11), undo=True,
                              wrap=tk.NONE, insertbackground="#ffffff", bg="#282c34", fg="#ffffff")
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll = tk.Scrollbar(wrap_frame, orient="vertical", command=self._on_scroll)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=self._on_scroll_set)
        self.minimap = tk.Text(wrap_frame, width=8, bg="#1e2227", fg="#7f8c8d",
                               font=("Consolas", 3), state="disabled", border=0)
        self.minimap.pack(side=tk.RIGHT, fill=tk.Y)
        self.bookmarks = set()
        self.editor.tag_configure("kw", foreground="#c678dd")
        self.editor.tag_configure("string", foreground="#98c379")
        self.editor.tag_configure("comment", foreground="#7f848e", font=("Consolas", 11, "italic"))
        self.editor.tag_configure("number", foreground="#d19a66")
        self.editor.tag_configure("color", foreground="#e5c07b")
        self.editor.tag_configure("errorline", background="#4d1f1f")
        self.editor.tag_configure("current", background="#2c313a")
        self.editor.tag_configure("bookmark", background="#3d2b00")
        self.editor.tag_configure("bp", background="#4d1f3f")
    def _on_scroll(self, *args):
        self.editor.yview(*args); self.linenumbers.yview(*args)
    def _on_scroll_set(self, a, b):
        self.scroll.set(a, b); self.linenumbers.yview_moveto(a)
    def update_linenumbers(self):
        lines = int(self.editor.index("end-1c").split(".")[0])
        self.linenumbers.config(state="normal")
        self.linenumbers.delete("1.0", tk.END)
        self.linenumbers.insert("1.0", "\n".join(str(i) for i in range(1, lines+1)))
        self.linenumbers.config(state="disabled")
        self._update_minimap()
    def _update_minimap(self):
        try:
            txt = self.editor.get("1.0", "end-1c")
            self.minimap.config(state="normal")
            self.minimap.delete("1.0", tk.END)
            self.minimap.insert("1.0", txt)
            self.minimap.config(state="disabled")
        except Exception: pass
    def highlight_syntax(self):
        e = self.editor
        for t in ("kw","string","comment","number","color"):
            e.tag_remove(t, "1.0", tk.END)
        text = e.get("1.0", tk.END)
        for m in re.finditer(r'//[^\n]*', text): self._tag("comment", m.start(), m.end())
        for m in re.finditer(r'"[^"\n]*"|\'[^\'\n]*\'', text): self._tag("string", m.start(), m.end())
        for m in re.finditer(r'\b\d+(\.\d+)?\b', text): self._tag("number", m.start(), m.end())
        for c in ("rojo","azul","verde","amarillo","naranja","morado","rosa",
                  "negro","blanco","gris","cian","violeta","marron","marrón",
                  "dorado","plateado"):
            for m in re.finditer(r'\b'+c+r'\b', text): self._tag("color", m.start(), m.end())
        for m in re.finditer(r'(?m)^\s*([A-Za-z_][A-Za-z0-9_]*\s*:)', text):
            self._tag("kw", m.start(1), m.end(1))
    def _tag(self, tag, s, e):
        try:
            self.editor.tag_add(tag, f"1.0+{s}c", f"1.0+{e}c")
        except Exception: pass
    def highlight_current_line(self):
        self.editor.tag_remove("current", "1.0", tk.END)
        idx = self.editor.index(tk.INSERT)
        self.editor.tag_add("current", f"{idx} linestart", f"{idx} lineend+1c")
    def toggle_bookmark(self, line):
        if line in self.bookmarks:
            self.bookmarks.discard(line)
            self.editor.tag_remove("bookmark", f"{line}.0", f"{line}.end+1c")
        else:
            self.bookmarks.add(line)
            self.editor.tag_add("bookmark", f"{line}.0", f"{line}.end+1c")


# ==========================================================
# 7) IDE
# ==========================================================
class EasyScriptIDE:
    def __init__(self, root):
        self.root = root
        self.i18n = I18n(DEFAULT_LANGUAGE)
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1280x860")

        self.font_family = DEFAULT_FONT
        self.font_size   = DEFAULT_FONT_SIZE
        self.tab_size    = 4
        self.word_wrap   = False
        self.current_theme = "dark"
        self.recent_files = []
        self.execution_thread = None
        self.console_queue = queue.Queue()
        self.autosave_id = None
        self.language = DEFAULT_LANGUAGE
        self.video_mode = DEFAULT_VIDEO_MODE
        self.palette_name = DEFAULT_PALETTE
        self.documents = []
        self.active_doc = None
        self.macro_events = []
        self.macro_recording = False
        self.session_stats = {"ejecuciones":0, "tiempo":0.0, "sentencias":0}
        self.history = []

        self._load_config()
        self._ensure_plugins_dir()

        # Vars Tk compartidas por los Radiobutton (persisten entre rebuilds)
        self.lang_var    = tk.StringVar(value=self.language)
        self.video_var   = tk.StringVar(value=self.video_mode)
        self.palette_var = tk.StringVar(value=self.palette_name)

        # Referencias a etiquetas que cambian con el idioma
        self.ui_refs = {"labels": {}, "buttons": {}}

        self._build_menu()
        self._build_toolbar()
        self._build_main_split()
        self._build_statusbar()

        self.interpreter = EasyScriptInterpreter(self.console, self.canvas, self, self.i18n)
        self.interpreter.retro.mode = self.video_mode
        self.interpreter.retro.palette_name = self.palette_name

        self._bind_shortcuts()
        self._build_context_menu()
        self._load_snippets()
        self._new_document(title=None, with_demo=True)
        self._schedule_autosave()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ======================================================
    # MENÚ (reconstruible en caliente)
    # ======================================================
    def _build_menu(self):
        t = self.i18n.t
        menubar = tk.Menu(self.root)

        # Archivo
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label=t("new"), accelerator="Ctrl+N", command=self._new_document)
        m_file.add_command(label=t("new_tab"), accelerator="Ctrl+T", command=lambda: self._new_document())
        m_file.add_command(label=t("open"), accelerator="Ctrl+O", command=self.load_project)
        m_file.add_command(label=t("save"), accelerator="Ctrl+S", command=self.save_project)
        m_file.add_command(label=t("save_as"), accelerator="Ctrl+Shift+S", command=self.save_project_as)
        m_file.add_separator()
        m_file.add_command(label=t("close_tab"), accelerator="Ctrl+W", command=self._close_current_tab)
        m_file.add_separator()
        m_file.add_command(label=t("console_save"), command=self.save_console)
        m_file.add_command(label=t("canvas_save"),  command=self.save_canvas_ps)
        m_file.add_separator()
        m_file.add_command(label=t("pack"),   command=self.pack_project)
        m_file.add_command(label=t("unpack"), command=self.unpack_project)
        m_file.add_command(label=t("export_html"), command=self.export_html)
        m_file.add_separator()
        self.recent_menu = tk.Menu(m_file, tearoff=0)
        m_file.add_cascade(label=t("recent"), menu=self.recent_menu)
        self._rebuild_recent_menu()
        m_file.add_separator()
        m_file.add_command(label=t("exit"), accelerator="Alt+F4", command=self._on_close)
        menubar.add_cascade(label=t("file"), menu=m_file)

        # Editar
        m_edit = tk.Menu(menubar, tearoff=0)
        m_edit.add_command(label=t("undo"), accelerator="Ctrl+Z", command=lambda: self._doc_editor().event_generate("<<Undo>>"))
        m_edit.add_command(label=t("redo"), accelerator="Ctrl+Y", command=lambda: self._doc_editor().event_generate("<<Redo>>"))
        m_edit.add_separator()
        m_edit.add_command(label=t("find"),   accelerator="Ctrl+F", command=self.open_find_dialog)
        m_edit.add_command(label=t("search_all"), accelerator="Ctrl+Shift+F", command=self.search_all_tabs)
        m_edit.add_command(label=t("goto"),   accelerator="Ctrl+G", command=self.goto_line)
        m_edit.add_command(label=t("dup"),    accelerator="Ctrl+D", command=self.duplicate_line)
        m_edit.add_command(label=t("comment"), accelerator="Ctrl+/", command=self.toggle_comment)
        m_edit.add_command(label=t("indent"),   accelerator="Tab", command=lambda: self.indent_selection(True))
        m_edit.add_command(label=t("unindent"), accelerator="Shift+Tab", command=lambda: self.indent_selection(False))
        m_edit.add_separator()
        m_edit.add_command(label=t("format"), accelerator="Ctrl+Alt+F", command=self.format_code)
        m_edit.add_command(label=t("rename_var"), command=self.rename_variable)
        m_edit.add_command(label=t("extract_fn"), command=self.extract_function)
        m_edit.add_separator()
        m_edit.add_command(label=t("cmd_palette"),   accelerator="Ctrl+Shift+P", command=self.open_command_palette)
        m_edit.add_command(label=t("autocomplete"), accelerator="Ctrl+Space", command=self.autocomplete)
        m_edit.add_separator()
        m_edit.add_command(label=t("inspect"),     command=self.inspect_variables)
        m_edit.add_command(label=t("export_vars"), command=self.export_variables)
        m_edit.add_command(label=t("import_vars"), command=self.import_variables)
        menubar.add_cascade(label=t("edit"), menu=m_edit)

        # Ver
        m_view = tk.Menu(menubar, tearoff=0)
        m_view.add_command(label=t("font_up"), accelerator="Ctrl++", command=lambda: self.change_font_size(+1))
        m_view.add_command(label=t("font_down"), accelerator="Ctrl+-", command=lambda: self.change_font_size(-1))
        m_view.add_command(label=t("font_reset"), accelerator="Ctrl+0", command=self.reset_font_size)
        m_view.add_command(label=t("font_pick"), command=self.choose_font)
        m_view.add_command(label=t("tab_size"),  command=self.choose_tab_size)
        m_view.add_separator()
        self.var_wrap = tk.BooleanVar(value=self.word_wrap)
        m_view.add_checkbutton(label=t("wrap"), variable=self.var_wrap, command=self.toggle_wrap)
        self.var_ts = tk.BooleanVar(value=False)
        m_view.add_checkbutton(label=t("timestamps"), variable=self.var_ts, command=self.toggle_timestamps)
        m_view.add_separator()
        m_view.add_command(label=t("theme"),      command=self.toggle_theme)
        m_view.add_command(label=t("fullscreen"), accelerator="F11", command=self.toggle_fullscreen)
        m_view.add_command(label=t("presentation"), command=self.toggle_presentation)
        m_view.add_separator()
        m_view.add_command(label=t("bookmarks"), command=self.list_bookmarks)
        m_view.add_command(label=t("toggle_bm"), accelerator="Ctrl+F2", command=self.toggle_bookmark)
        m_view.add_command(label=t("next_bm"), accelerator="F2", command=lambda: self.jump_bookmark(+1))
        m_view.add_command(label=t("prev_bm"), accelerator="Shift+F2", command=lambda: self.jump_bookmark(-1))
        menubar.add_cascade(label=t("view"), menu=m_view)

        # Idioma
        m_lang = tk.Menu(menubar, tearoff=0)
        self.lang_var.set(self.language)
        for code, label in (("es","🇪🇸 Español"),("en","🇬🇧 English"),("pt","🇵🇹 Português")):
            m_lang.add_radiobutton(label=label, value=code, variable=self.lang_var,
                                   command=lambda c=code: self.change_language(c))
        menubar.add_cascade(label=t("language"), menu=m_lang)

        # Modo gráfico
        m_vid = tk.Menu(menubar, tearoff=0)
        self.video_var.set(self.video_mode)
        for code, label in (("normal","Normal 24-bit"),("8bit","8-bit retro"),("16bit","16-bit retro")):
            m_vid.add_radiobutton(label=label, value=code, variable=self.video_var,
                                  command=lambda c=code: self.apply_video_mode(c))
        m_vid.add_separator()
        self.palette_var.set(self.palette_name)
        for pal in ("nes","gameboy","cga","snes","vga","sinclair"):
            m_vid.add_radiobutton(label=f"Paleta {pal.upper()}", value=pal,
                                  variable=self.palette_var,
                                  command=lambda p=pal: self.apply_palette(p))
        menubar.add_cascade(label=t("video_mode"), menu=m_vid)

        # Ejecutar
        m_run = tk.Menu(menubar, tearoff=0)
        m_run.add_command(label=t("run_all"), accelerator="F5", command=self.run_code)
        m_run.add_command(label=t("run_sel"), accelerator="F6", command=self.run_selection)
        m_run.add_command(label=t("run_cursor"), accelerator="Ctrl+F5", command=self.run_from_cursor)
        m_run.add_command(label=t("validate"), accelerator="Ctrl+Shift+V", command=self.validate_syntax)
        m_run.add_separator()
        m_run.add_command(label=t("stop"), accelerator="Esc", command=self.stop_execution)
        m_run.add_separator()
        m_run.add_command(label=t("debugger"), command=self.show_debugger)
        m_run.add_command(label=t("watch"), command=self.show_watch)
        m_run.add_command(label=t("callstack"), command=self.show_callstack)
        m_run.add_separator()
        m_run.add_command(label=t("profile"), command=self.show_profile)
        m_run.add_command(label=t("profile_chart"), command=self.show_profile_chart)
        m_run.add_separator()
        m_run.add_command(label=t("macro_rec"), command=self.toggle_macro_recording)
        m_run.add_command(label=t("macro_play"), command=self.play_macro)
        m_run.add_separator()
        m_run.add_command(label=t("test_runner"), command=self.run_tests)
        m_run.add_separator()
        m_run.add_command(label=t("clear_console"), command=lambda: self.console.delete("1.0", tk.END))
        m_run.add_command(label=t("clear_canvas"),  command=lambda: self.canvas.delete("all"))
        m_run.add_command(label=t("copy_console"),  command=self.copy_console)
        menubar.add_cascade(label=t("run"), menu=m_run)

        # Ayuda
        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label=t("cmd_ref"),   command=self.show_command_reference)
        m_help.add_command(label=t("examples"),  command=self.show_examples)
        m_help.add_command(label=t("templates"), command=self.show_templates)
        m_help.add_command(label=t("snippet_mgr"), command=self.show_snippets)
        m_help.add_command(label=t("tutorials"), command=self.show_tutorials)
        m_help.add_separator()
        m_help.add_command(label=t("doc_gen"), command=self.generate_docs)
        m_help.add_separator()
        m_help.add_command(label=t("plugins"), command=self.show_plugins)
        m_help.add_command(label=t("install_plugin"), command=self.install_plugin)
        m_help.add_separator()
        m_help.add_command(label=t("achievements"), command=self.show_achievements)
        m_help.add_command(label=t("stats"), command=self.show_stats)
        m_help.add_command(label=t("about"), command=self.show_about)
        menubar.add_cascade(label=t("help"), menu=m_help)

        self.root.config(menu=menubar)
        self.menubar = menubar

    # ======================================================
    # Toolbar
    # ======================================================
    def _build_toolbar(self):
        if hasattr(self, "toolbar_bar"):
            self.toolbar_bar.destroy()
        bar = tk.Frame(self.root, bg="#2c3e50")
        bar.pack(side=tk.TOP, fill=tk.X, before=getattr(self, "pw_main", None))
        self.toolbar_bar = bar
        self.toolbar_buttons = {}
        t = self.i18n.t

        def add_btn(key, icon, color, cmd):
            b = tk.Button(bar, text=f"{icon} {t(key)}", bg=color, fg="white",
                          font=("Arial", 10, "bold"), command=cmd,
                          relief=tk.FLAT, padx=8, cursor="hand2")
            b.pack(side=tk.LEFT, padx=3, pady=4)
            self.toolbar_buttons[key] = (b, icon)
            return b

        add_btn("btn_new",     "📄", "#3498db", self._new_document)
        add_btn("btn_open",    "📂", "#f39c12", self.load_project)
        add_btn("btn_save",    "💾", "#27ae60", self.save_project)
        add_btn("btn_run",     "▶️", "#e74c3c", self.run_code)
        add_btn("btn_stop",    "⏹️", "#8e44ad", self.stop_execution)
        add_btn("btn_debug",   "🐞", "#c0392b", self.show_debugger)
        add_btn("btn_step",    "➡️", "#d35400", self.debug_step)
        add_btn("btn_format",  "✨", "#16a085", self.format_code)
        add_btn("btn_test",    "🧪", "#2980b9", self.run_tests)
        add_btn("btn_snippets","✂️", "#8e44ad", self.show_snippets)
        add_btn("btn_console", "🧹", "#16a085", lambda: self.console.delete("1.0", tk.END))
        add_btn("btn_canvas",  "🎨", "#2c3e50", lambda: self.canvas.delete("all"))
        add_btn("btn_find",    "🔍", "#34495e", self.open_find_dialog)
        add_btn("btn_help",    "📖", "#7f8c8d", self.show_command_reference)

        self.progress = ttk.Progressbar(bar, mode="indeterminate", length=120)
        self.progress.pack(side=tk.RIGHT, padx=6, pady=6)

    def _refresh_toolbar_labels(self):
        if not hasattr(self, "toolbar_buttons"): return
        t = self.i18n.t
        for key,(btn,icon) in self.toolbar_buttons.items():
            try: btn.config(text=f"{icon} {t(key)}")
            except Exception: pass

    # ======================================================
    # Split principal
    # ======================================================
    def _build_main_split(self):
        self.pw_main = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, bg="#2c3e50")
        self.pw_main.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(self.pw_main, bg="#2c3e50", width=200)
        self.pw_main.add(self.sidebar, minsize=120)
        self._build_sidebar()

        self.notebook = ttk.Notebook(self.pw_main)
        self.pw_main.add(self.notebook)

        bottom = tk.Frame(self.root, bg="#1e272e")
        bottom.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0,4))
        self.console = tk.Text(bottom, font=("Consolas", 10), height=10,
                               bg="#1e272e", fg="#ffffff", width=50, wrap=tk.WORD)
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(bottom, bg="#1e272e", highlightthickness=0, width=380)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _build_sidebar(self):
        t = self.i18n.t
        self.lbl_sidebar = tk.Label(self.sidebar, text=t("project"),
                                    bg="#1f2a35", fg="white", font=("Arial", 10, "bold"))
        self.lbl_sidebar.pack(fill=tk.X)
        self.sidebar_tree = ttk.Treeview(self.sidebar, show="tree")
        self.sidebar_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        btn_frame = tk.Frame(self.sidebar, bg="#2c3e50"); btn_frame.pack(fill=tk.X)
        self.btn_sidebar_open = tk.Button(btn_frame, text="📂 "+t("open"),
                                          bg="#34495e", fg="white", relief=tk.FLAT,
                                          command=self.open_folder_in_sidebar)
        self.btn_sidebar_open.pack(fill=tk.X, padx=4, pady=2)
        self.btn_sidebar_refresh = tk.Button(btn_frame, text="🔄 "+t("refresh"),
                                             bg="#34495e", fg="white", relief=tk.FLAT,
                                             command=self.refresh_sidebar)
        self.btn_sidebar_refresh.pack(fill=tk.X, padx=4, pady=2)
        self.sidebar_root = None
        self.sidebar_tree.bind("<Double-Button-1>", self._on_sidebar_open)

    def _doc_editor(self): return self.active_doc.editor if self.active_doc else None

    def _build_statusbar(self):
        self.status = tk.StringVar(value=self.i18n.t("ready"))
        self.sb = tk.Label(self.root, textvariable=self.status, anchor="w",
                           bg="#2c3e50", fg="white", font=("Arial", 9))
        self.sb.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_pos = tk.Label(self.sb, text="Ln 1, Col 1", bg="#2c3e50", fg="white", font=("Arial", 9))
        self.lbl_pos.pack(side=tk.RIGHT, padx=8)
        self.lbl_count = tk.Label(self.sb, text="0 / 0", bg="#2c3e50", fg="white", font=("Arial", 9))
        self.lbl_count.pack(side=tk.RIGHT, padx=8)
        self.lbl_dbg = tk.Label(self.sb, text="", bg="#2c3e50", fg="#f39c12", font=("Arial", 9))
        self.lbl_dbg.pack(side=tk.RIGHT, padx=8)

    # ======================================================
    # NUEVO: refresco TOTAL de la UI al cambiar idioma
    # ======================================================
    def _refresh_all_ui_texts(self):
        """Retraduce toda la ventana al idioma actual."""
        # 1) Menú completo
        self._build_menu()

        # 2) Toolbar
        self._refresh_toolbar_labels()

        # 3) Sidebar
        t = self.i18n.t
        if hasattr(self, "lbl_sidebar"):
            self.lbl_sidebar.config(text=t("project"))
        if hasattr(self, "btn_sidebar_open"):
            self.btn_sidebar_open.config(text="📂 "+t("open"))
        if hasattr(self, "btn_sidebar_refresh"):
            self.btn_sidebar_refresh.config(text="🔄 "+t("refresh"))

        # 4) Status
        self.status.set(t("ready"))

        # 5) Nombres de pestañas sin título
        for idx, doc in enumerate(self.documents):
            if doc.untitled and doc.path is None:
                self.notebook.tab(idx, text=t("new_tab_title"))

        # 6) Forzar redibujado del menú
        try: self.root.update_idletasks()
        except Exception: pass

    # ======================================================
    # Documentos
    # ======================================================
    def _new_document(self, title=None, with_demo=False):
        untitled = (title is None)
        if title is None: title = self.i18n.t("new_tab_title")
        doc = Document(self.notebook, title, untitled=untitled)
        self.notebook.add(doc.frame, text=title)
        self.documents.append(doc)
        self._wire_document(doc)
        self.notebook.select(doc.frame)
        self.active_doc = doc
        if with_demo: self._load_demo(doc)
        doc.update_linenumbers()
        doc.highlight_syntax()
        return doc

    def _wire_document(self, doc):
        doc.editor.bind("<<Modified>>", lambda e, d=doc: self._on_modified(d))
        doc.editor.bind("<KeyRelease>", lambda e, d=doc: self._on_key_release(d, e))
        doc.editor.bind("<Button-1>", lambda e, d=doc: self._on_click(d))
        doc.editor.bind("<MouseWheel>", self._on_mousewheel)
        doc.editor.bind("<Tab>", lambda e, d=doc: self._on_tab(d))
        doc.editor.bind("<Shift-Tab>", lambda e, d=doc: self._on_shift_tab(d))
        doc.editor.bind("<Control-space>", lambda e: self.autocomplete())
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self._on_tab_changed())

    def _on_tab_changed(self):
        idx = self.notebook.index(self.notebook.select())
        if 0 <= idx < len(self.documents):
            self.active_doc = self.documents[idx]
            self._update_status_counts()
            self._update_cursor_pos()

    def _close_current_tab(self):
        if not self.active_doc: return
        if self.active_doc.modified:
            if not messagebox.askyesno(self.i18n.t("close_tab"),
                                       self.i18n.t("msg_confirm_close")):
                return
        idx = self.notebook.index(self.notebook.select())
        self.notebook.forget(idx)
        self.documents.pop(idx)
        if self.documents:
            self.active_doc = self.documents[min(idx, len(self.documents)-1)]
        else:
            self.active_doc = None

    # ======================================================
    # Eventos del editor
    # ======================================================
    def _on_modified(self, doc):
        try: doc.editor.edit_modified(False)
        except Exception: return
        doc.modified = True
        doc.update_linenumbers()
        self._update_status_counts()
    def _on_key_release(self, doc, event):
        doc.highlight_syntax()
        doc.highlight_current_line()
        self._update_cursor_pos()
        if event.char in ("(", "[", "{", '"', "'"):
            self._autoclose(doc, event.char)
        if self.macro_recording and event.char:
            self.macro_events.append(("ins", event.char))
    def _on_click(self, doc):
        self.root.after(10, doc.highlight_current_line)
        self.root.after(10, self._update_cursor_pos)
    def _on_mousewheel(self, event):
        d = int(-1 * (event.delta / 120))
        if self.active_doc:
            self.active_doc.editor.yview_scroll(d, "units")
            self.active_doc.linenumbers.yview_scroll(d, "units")
        return "break"
    def _update_cursor_pos(self):
        if not self.active_doc: return
        idx = self.active_doc.editor.index(tk.INSERT)
        ln, col = idx.split(".")
        self.lbl_pos.config(text=f"Ln {ln}, Col {int(col)+1}")
    def _update_status_counts(self):
        if not self.active_doc: return
        t = self.active_doc.editor.get("1.0", "end-1c")
        self.lbl_count.config(text=f"{t.count(chr(10))+1} L · {len(t)} c")
    def _autoclose(self, doc, ch):
        pairs = {"(":")","[":"]","{":"}","\"":"\"","'":"'"}
        c = pairs.get(ch)
        if c and ch in ('"',"'"):
            prev = doc.editor.get("insert-2c", "insert-1c")
            if prev == ch: return
        if c:
            doc.editor.insert(tk.INSERT, c)
            doc.editor.mark_set(tk.INSERT, "insert-1c")
    def _on_tab(self, doc):
        if doc.editor.tag_ranges("sel"): self.indent_selection(True)
        else: doc.editor.insert(tk.INSERT, " " * self.tab_size)
        return "break"
    def _on_shift_tab(self, doc):
        self.indent_selection(False); return "break"

    # ======================================================
    # Atajos
    # ======================================================
    def _bind_shortcuts(self):
        b = self.root.bind
        b("<Control-n>", lambda e: self._new_document())
        b("<Control-t>", lambda e: self._new_document())
        b("<Control-o>", lambda e: self.load_project())
        b("<Control-s>", lambda e: self.save_project())
        b("<Control-w>", lambda e: self._close_current_tab())
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
        b("<F9>", lambda e: self.toggle_breakpoint())
        b("<F10>", lambda e: self.debug_step())
        b("<F11>", lambda e: self.toggle_fullscreen())
        b("<F2>", lambda e: self.jump_bookmark(+1))
        b("<Shift-F2>", lambda e: self.jump_bookmark(-1))
        b("<Control-F2>", lambda e: self.toggle_bookmark())
        b("<Escape>", lambda e: self.stop_execution())

    # ======================================================
    # Acciones editor
    # ======================================================
    def duplicate_line(self):
        e = self._doc_editor()
        if not e: return
        try:
            ln = int(e.index(tk.INSERT).split(".")[0])
            c = e.get(f"{ln}.0", f"{ln}.end")
            e.insert(f"{ln}.end", "\n" + c)
        except Exception: pass
    def toggle_comment(self):
        e = self._doc_editor()
        if not e: return
        try:
            if e.tag_ranges("sel"):
                s = int(e.index("sel.first").split(".")[0])
                en = int(e.index("sel.last").split(".")[0])
            else:
                s = en = int(e.index(tk.INSERT).split(".")[0])
            for ln in range(s, en+1):
                line = e.get(f"{ln}.0", f"{ln}.end")
                new = re.sub(r'^(\s*)//\s?', r'\1', line) if line.strip().startswith("//") \
                      else re.sub(r'^(\s*)', r'\1// ', line)
                e.delete(f"{ln}.0", f"{ln}.end"); e.insert(f"{ln}.0", new)
        except Exception: pass
    def indent_selection(self, positive=True):
        e = self._doc_editor()
        if not e: return
        try:
            if e.tag_ranges("sel"):
                s = int(e.index("sel.first").split(".")[0])
                en = int(e.index("sel.last").split(".")[0])
            else:
                s = en = int(e.index(tk.INSERT).split(".")[0])
            for ln in range(s, en+1):
                line = e.get(f"{ln}.0", f"{ln}.end")
                new = (" " * self.tab_size + line) if positive \
                      else re.sub(r'^ {1,' + str(self.tab_size) + r'}', '', line)
                e.delete(f"{ln}.0", f"{ln}.end"); e.insert(f"{ln}.0", new)
        except Exception: pass
    def goto_line(self):
        ln = simpledialog.askinteger(self.i18n.t("dlg_goto"),
                                     self.i18n.t("dlg_goto_num"), parent=self.root)
        if ln and self.active_doc:
            try:
                self.active_doc.editor.mark_set(tk.INSERT, f"{ln}.0")
                self.active_doc.editor.see(f"{ln}.0")
            except Exception: pass
    def autocomplete(self):
        if not self.active_doc: return
        e = self.active_doc.editor
        idx = e.index(tk.INSERT)
        start = e.index(f"{idx} linestart")
        prefix = e.get(start, idx).strip()
        cmds = self.i18n.command_list()
        matches = [c for c in cmds if c.startswith(prefix)] if prefix else []
        if len(matches) == 1:
            e.insert(tk.INSERT, matches[0][len(prefix):])
        elif len(matches) > 1:
            self._show_popup_list(matches, e, idx)
    def _show_popup_list(self, items, widget, at):
        pop = tk.Toplevel(self.root); pop.overrideredirect(True)
        lb = tk.Listbox(pop, height=min(10, len(items)))
        for it in items: lb.insert(tk.END, it)
        lb.pack()
        try: pop.geometry(f"+{self.root.winfo_pointerx()}+{self.root.winfo_pointery()}")
        except Exception: pass
        def on_sel(_e=None):
            s = lb.curselection()
            if s: widget.insert(at, items[s[0]])
            pop.destroy()
        lb.bind("<Double-Button-1>", on_sel); lb.bind("<Return>", on_sel)
        pop.bind("<FocusOut>", lambda e: pop.destroy())

    def format_code(self):
        e = self._doc_editor()
        if not e: return
        src = e.get("1.0", "end-1c")
        out_lines = []
        indent = 0
        for raw in src.split("\n"):
            s = raw.strip()
            if s.startswith("fin_") or s.startswith("sino"):
                indent = max(0, indent-1)
            out_lines.append(" " * (indent*self.tab_size) + s)
            low = s.lower()
            if (low.startswith("si:") or low.startswith("mientras:") or low.startswith("bucle:")
                or low.startswith("funcion:") or low.startswith("clase:") or low.startswith("sino")
                or low.startswith("test:")):
                indent += 1
        new = "\n".join(out_lines)
        e.delete("1.0", tk.END); e.insert("1.0", new)

    def rename_variable(self):
        e = self._doc_editor()
        if not e: return
        old = simpledialog.askstring(self.i18n.t("rename_var"),
                                     self.i18n.t("dlg_rename_old"), parent=self.root)
        if not old: return
        new = simpledialog.askstring(self.i18n.t("rename_var"),
                                     self.i18n.t("dlg_rename_new"), parent=self.root)
        if not new: return
        code = e.get("1.0", "end-1c")
        new_code = re.sub(r'\b'+re.escape(old)+r'\b', new, code)
        e.delete("1.0", tk.END); e.insert("1.0", new_code)

    def extract_function(self):
        e = self._doc_editor()
        if not e: return
        try: sel = e.get("sel.first", "sel.last")
        except Exception:
            messagebox.showinfo(self.i18n.t("extract_fn"), self.i18n.t("msg_extract_hint")); return
        fn = simpledialog.askstring(self.i18n.t("extract_fn"),
                                    self.i18n.t("dlg_extract_name"), parent=self.root)
        if not fn: return
        body = "\n".join("  " + l for l in sel.split("\n"))
        new_block = f"funcion:({fn})\n{body}\nfin_funcion"
        e.delete("sel.first", "sel.last")
        e.insert("sel.first", new_block)

    def toggle_bookmark(self):
        if not self.active_doc: return
        ln = int(self.active_doc.editor.index(tk.INSERT).split(".")[0])
        self.active_doc.toggle_bookmark(ln)
    def jump_bookmark(self, dirn):
        if not self.active_doc or not self.active_doc.bookmarks: return
        cur = int(self.active_doc.editor.index(tk.INSERT).split(".")[0])
        bms = sorted(self.active_doc.bookmarks)
        target = None
        if dirn > 0:
            for l in bms:
                if l > cur: target = l; break
            if target is None: target = bms[0]
        else:
            for l in reversed(bms):
                if l < cur: target = l; break
            if target is None: target = bms[-1]
        self.active_doc.editor.mark_set(tk.INSERT, f"{target}.0")
        self.active_doc.editor.see(f"{target}.0")
    def list_bookmarks(self):
        if not self.active_doc: return
        if not self.active_doc.bookmarks:
            messagebox.showinfo(self.i18n.t("bookmarks"), "—")
            return
        messagebox.showinfo(self.i18n.t("bookmarks"),
            "\n".join(str(l) for l in sorted(self.active_doc.bookmarks)))

    def toggle_breakpoint(self):
        if not self.active_doc: return
        ln = int(self.active_doc.editor.index(tk.INSERT).split(".")[0])
        e = self.active_doc.editor
        if ln in self.interpreter.breakpoints:
            self.interpreter.breakpoints.discard(ln)
            e.tag_remove("bp", f"{ln}.0", f"{ln}.end+1c")
        else:
            self.interpreter.breakpoints.add(ln)
            e.tag_add("bp", f"{ln}.0", f"{ln}.end+1c")

    # ======================================================
    # Búsqueda
    # ======================================================
    def open_find_dialog(self):
        t = self.i18n.t
        win = tk.Toplevel(self.root); win.title(t("find")); win.geometry("440x230")
        tk.Label(win, text=t("dlg_search")).grid(row=0, column=0, sticky="e", padx=6, pady=6)
        e_find = tk.Entry(win, width=30); e_find.grid(row=0, column=1, padx=6, pady=6)
        tk.Label(win, text=t("dlg_replace")).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        e_repl = tk.Entry(win, width=30); e_repl.grid(row=1, column=1, padx=6, pady=6)
        var_rx = tk.BooleanVar(value=False)
        tk.Checkbutton(win, text=t("dlg_regex"), variable=var_rx).grid(row=2, column=0, padx=6)

        def find_next():
            if not self.active_doc: return
            e = self.active_doc.editor
            n = e_find.get()
            if not n: return
            try:
                if var_rx.get():
                    content = e.get("1.0", "end-1c")
                    m = re.search(n, content)
                    if m:
                        s_idx = e.index(f"1.0+{m.start()}c"); e_idx = e.index(f"1.0+{m.end()}c")
                        e.tag_add("sel", s_idx, e_idx); e.see(s_idx)
                else:
                    idx = e.search(n, tk.INSERT, stopindex=tk.END) or e.search(n, "1.0", stopindex=tk.END)
                    if idx:
                        end = f"{idx}+{len(n)}c"
                        e.tag_add("sel", idx, end); e.mark_set(tk.INSERT, end); e.see(idx)
            except Exception as ex: messagebox.showerror("Regex", str(ex))
        def replace_all():
            if not self.active_doc: return
            e = self.active_doc.editor
            n = e_find.get()
            if not n: return
            c = e.get("1.0", "end-1c")
            if var_rx.get():
                try: new = re.sub(n, e_repl.get(), c)
                except Exception as ex: messagebox.showerror("Regex", str(ex)); return
            else: new = c.replace(n, e_repl.get())
            e.delete("1.0", tk.END); e.insert("1.0", new)
        tk.Button(win, text=t("dlg_find_btn"), command=find_next).grid(row=3, column=0, padx=6, pady=6)
        tk.Button(win, text=t("dlg_replace_all"), command=replace_all).grid(row=3, column=1, padx=6, pady=6)
        e_find.focus_set()

    def search_all_tabs(self):
        needle = simpledialog.askstring(self.i18n.t("search_all"),
                                        self.i18n.t("search_placeholder"), parent=self.root)
        if not needle: return
        hits = []
        for d in self.documents:
            t = d.editor.get("1.0", "end-1c")
            for i,l in enumerate(t.split("\n"), start=1):
                if needle in l:
                    hits.append(f"tab {self.documents.index(d)+1} L{i}: {l.strip()}")
        messagebox.showinfo(self.i18n.t("results_title"),
                            "\n".join(hits) or self.i18n.t("no_matches"))

    # ======================================================
    # Fuente / tema
    # ======================================================
    def change_font_size(self, delta):
        self.font_size = max(7, min(30, self.font_size+delta)); self._apply_fonts()
    def reset_font_size(self):
        self.font_size = DEFAULT_FONT_SIZE; self._apply_fonts()
    def _apply_fonts(self):
        for d in self.documents:
            d.editor.config(font=(self.font_family, self.font_size))
            d.linenumbers.config(font=(self.font_family, max(9, self.font_size-1)))
        self.console.config(font=(self.font_family, max(9, self.font_size-1)))
    def choose_font(self):
        fam = simpledialog.askstring(self.i18n.t("font_pick"),
                                     self.i18n.t("dlg_font_prompt"),
                                     initialvalue=self.font_family, parent=self.root)
        if fam:
            self.font_family = fam; self._apply_fonts()
    def choose_tab_size(self):
        n = simpledialog.askinteger(self.i18n.t("tab_size"),
                                    self.i18n.t("dlg_tab_size"),
                                    initialvalue=self.tab_size,
                                    minvalue=2, maxvalue=8, parent=self.root)
        if n: self.tab_size = n
    def toggle_wrap(self):
        self.word_wrap = self.var_wrap.get()
        for d in self.documents:
            d.editor.configure(wrap=tk.WORD if self.word_wrap else tk.NONE)
    def toggle_timestamps(self):
        self.interpreter.show_timestamps = self.var_ts.get()
    def toggle_theme(self):
        themes = {
            "dark":   {"bg":"#282c34","fg":"#ffffff","ln_bg":"#282c34"},
            "light":  {"bg":"#ffffff","fg":"#2c3e50","ln_bg":"#ecf0f1"},
            "mono":   {"bg":"#1e1e1e","fg":"#d4d4d4","ln_bg":"#1e1e1e"},
            "solar":  {"bg":"#fdf6e3","fg":"#586e75","ln_bg":"#eee8d5"},
            "dracula":{"bg":"#282a36","fg":"#f8f8f2","ln_bg":"#282a36"},
        }
        order = ["dark","light","mono","solar","dracula"]
        idx = order.index(self.current_theme) if self.current_theme in order else 0
        self.current_theme = order[(idx+1) % len(order)]
        cfg = themes[self.current_theme]
        for d in self.documents:
            d.editor.config(bg=cfg["bg"], fg=cfg["fg"])
            d.linenumbers.config(bg=cfg["ln_bg"], fg="#7f8c8d")
        self.console.config(bg=cfg["bg"], fg=cfg["fg"])
        self.status.set(f"Theme: {self.current_theme}")
    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))
    def toggle_presentation(self):
        try:
            cur = self.root.attributes("-fullscreen")
            self.root.attributes("-fullscreen", not cur)
            self.font_size = 18 if not cur else DEFAULT_FONT_SIZE
            self._apply_fonts()
        except Exception: pass

    # ======================================================
    # Idioma / Video / Paleta (con TOGGLE + REFRESCO TOTAL)
    # ======================================================
    def change_language(self, code, from_script=False):
        reset = False
        if not from_script and code == self.language and code != DEFAULT_LANGUAGE:
            code = DEFAULT_LANGUAGE; reset = True
        self.language = code
        self.i18n.set_lang(code)
        self.lang_var.set(code)
        # *** REFRESCO TOTAL DE LA VENTANA ***
        self._refresh_all_ui_texts()
        if reset:
            self.status.set(f"{self.i18n.t('lang_reset')} {code}")
        else:
            self.status.set(f"{self.i18n.t('language_changed')} {code}")

    def apply_video_mode(self, mode, from_script=False):
        reset = False
        if not from_script and mode == self.video_mode and mode != DEFAULT_VIDEO_MODE:
            mode = DEFAULT_VIDEO_MODE; reset = True
        self.video_mode = mode
        self.video_var.set(mode)
        self.interpreter.retro.mode = mode
        cfg = RetroVideoMode.MODES[mode]
        self.interpreter.retro.apply_to_canvas(self.canvas)
        self.canvas.config(bg=cfg["bg"])
        key = "mode_reset" if reset else "mode_set"
        self.status.set(f"{self.i18n.t(key)} {cfg['name']}")

    def apply_palette(self, pal, from_script=False):
        reset = False
        if not from_script and pal == self.palette_name and pal != DEFAULT_PALETTE:
            pal = DEFAULT_PALETTE; reset = True
        self.palette_name = pal
        self.palette_var.set(pal)
        self.interpreter.retro.palette_name = pal
        key = "palette_reset" if reset else "palette_set"
        self.status.set(f"{self.i18n.t(key)} {pal.upper()}")

    # ======================================================
    # Ejecución / debug
    # ======================================================
    def run_code(self):
        if not self.active_doc: return
        self._start_execution(self.active_doc.editor.get("1.0", tk.END))
    def run_selection(self):
        if not self.active_doc: return
        try:
            self._start_execution(self.active_doc.editor.get("sel.first", "sel.last"))
        except Exception:
            messagebox.showinfo("", self.i18n.t("msg_select_code"))
    def run_from_cursor(self):
        if not self.active_doc: return
        idx = self.active_doc.editor.index(tk.INSERT)
        self._start_execution(self.active_doc.editor.get(idx, tk.END))
    def validate_syntax(self):
        if not self.active_doc: return
        problems = self.interpreter.validate(self.active_doc.editor.get("1.0", tk.END))
        if not problems: messagebox.showinfo("", self.i18n.t("validate_ok"))
        else: messagebox.showwarning("", "\n".join(f"L{l}: {m}" for l,m in problems))
    def _start_execution(self, code):
        if self.execution_thread and self.execution_thread.is_alive():
            messagebox.showinfo("", self.i18n.t("msg_already_running")); return
        if self.active_doc:
            self.active_doc.editor.tag_remove("errorline", "1.0", tk.END)
        self.status.set(self.i18n.t("running")); self.progress.start(10)
        self.session_stats["ejecuciones"] += 1
        self.history.append({"t": datetime.now().isoformat(), "code": code})
        if len(self.history) > 50: self.history = self.history[-50:]
        def worker():
            try: self.interpreter.execute(code)
            except Exception: self.console_queue.put(("error", traceback.format_exc()))
            finally: self.root.after(0, self._on_execution_done)
        self.execution_thread = threading.Thread(target=worker, daemon=True)
        self.execution_thread.start()
    def _on_execution_done(self):
        self.progress.stop(); self.status.set(self.i18n.t("ready"))
    def on_execution_finished(self, secs, lines):
        self.session_stats["tiempo"] += secs
        self.session_stats["sentencias"] += lines
        self.status.set(f"✅ {lines} stmt · {secs:.3f}s")
    def stop_execution(self):
        self.interpreter.should_stop = True
        try: self.interpreter.continue_debug()
        except Exception: pass
        self.status.set(self.i18n.t("stopping"))

    def show_debugger(self):
        self.interpreter.debug_mode = not self.interpreter.debug_mode
        self.status.set(f"🐞 Debug: {'ON' if self.interpreter.debug_mode else 'OFF'}")
    def debug_step(self):
        self.interpreter.step_mode = True
        self.interpreter.continue_debug()
    def _on_debug_pause(self, line_num, interp):
        if self.active_doc:
            self.active_doc.editor.mark_set(tk.INSERT, f"{line_num}.0")
            self.active_doc.editor.see(f"{line_num}.0")
        self.lbl_dbg.config(text=f"⏸ L{line_num}")

    def show_watch(self):
        win = tk.Toplevel(self.root); win.title(self.i18n.t("watch")); win.geometry("360x260")
        var = tk.StringVar()
        e = tk.Entry(win, textvariable=var); e.pack(fill=tk.X, padx=6, pady=6)
        lb = tk.Listbox(win); lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        def add(_=None):
            expr = var.get().strip()
            if expr:
                lb.insert(tk.END, f"{expr} = {self.interpreter.eval_expr(expr)!r}")
                var.set("")
        e.bind("<Return>", add)
        tk.Button(win, text=self.i18n.t("dlg_watch_add"), command=add).pack(pady=4)

    def show_callstack(self):
        stack = " → ".join(self.interpreter.call_stack) or "(—)"
        messagebox.showinfo(self.i18n.t("callstack"), stack)

    def show_profile(self):
        if not self.interpreter.line_times:
            messagebox.showinfo(self.i18n.t("profile"), "—"); return
        rows = sorted(self.interpreter.line_times.items(), key=lambda kv: -kv[1])
        txt = "\n".join(f"L{l}: {t*1000:.2f} ms" for l,t in rows[:40])
        messagebox.showinfo(self.i18n.t("profile"), txt)
    def show_profile_chart(self):
        if not self.interpreter.line_times:
            messagebox.showinfo(self.i18n.t("profile_chart"), "—"); return
        win = tk.Toplevel(self.root); win.title(self.i18n.t("profile_chart")); win.geometry("600x400")
        cv = tk.Canvas(win, bg="#1e272e"); cv.pack(fill=tk.BOTH, expand=True)
        items = sorted(self.interpreter.line_times.items())
        maxt = max(t for _,t in items) or 1
        w = 580 / max(1, len(items))
        for i,(ln,t) in enumerate(items):
            h = (t/maxt) * 320
            x0 = 10 + i*w; x1 = x0 + w - 2
            cv.create_rectangle(x0, 360-h, x1, 360, fill="#e74c3c", outline="")
            cv.create_text(x0+w/2, 375, text=str(ln), fill="white", font=("Arial", 7))

    def toggle_macro_recording(self):
        self.macro_recording = not self.macro_recording
        self.macro_events.clear()
    def play_macro(self):
        if not self.macro_events or not self.active_doc: return
        e = self.active_doc.editor
        for kind,data in self.macro_events:
            if kind == "ins": e.insert(tk.INSERT, data)

    def run_tests(self):
        if not self.active_doc: return
        self.interpreter.test_results = []
        code = self.active_doc.editor.get("1.0", tk.END)
        self._start_execution(code)
        self.root.after(500, self._report_tests)
    def _report_tests(self):
        res = self.interpreter.test_results
        if not res: return
        passed = sum(1 for _,ok,_ in res if ok)
        messagebox.showinfo(self.i18n.t("test_runner"),
            f"{passed}/{len(res)}\n\n" +
            "\n".join(f"{'✅' if ok else '❌'} {n}: {msg}" for n,ok,msg in res))

    def show_history(self):
        if not self.history:
            messagebox.showinfo(self.i18n.t("history"), "—"); return
        win = tk.Toplevel(self.root); win.title(self.i18n.t("history")); win.geometry("560x420")
        lb = tk.Listbox(win); lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        for h in reversed(self.history):
            lb.insert(tk.END, f"{h['t']} · {len(h['code'])} chars")
    def show_diff(self):
        if len(self.history) < 2:
            messagebox.showinfo(self.i18n.t("diff"), "—"); return
        a = self.history[-2]["code"].split("\n")
        b = self.history[-1]["code"].split("\n")
        win = tk.Toplevel(self.root); win.title(self.i18n.t("diff")); win.geometry("700x500")
        txt = tk.Text(win, font=("Consolas", 10)); txt.pack(fill=tk.BOTH, expand=True)
        for line in difflib.unified_diff(a, b, "before", "after", lineterm=""):
            txt.insert(tk.END, line + "\n")
        txt.config(state="disabled")
    def local_commit(self):
        if not self.active_doc: return
        path = os.path.join(os.path.expanduser("~"), ".ezscript_commits")
        os.makedirs(path, exist_ok=True)
        fname = f"commit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ez"
        p = os.path.join(path, fname)
        with open(p, "w", encoding="utf-8") as f:
            f.write(self.active_doc.editor.get("1.0", tk.END))
        messagebox.showinfo(self.i18n.t("commit"), p)

    def _load_snippets(self):
        self.snippets = {
            "Bucle":    "bucle:(10)\n  \nfin_bucle",
            "Condicional": "si:(condicion)\n  \nsino:\n  \nfin_si",
            "Función":  "funcion:(nombre, a)\n  retornar:(a)\nfin_funcion",
            "Clase":    "clase:(Nombre)\n  funcion:(constructor)\n    propiedad:(x, 0)\n  fin_funcion\nfin_clase",
            "Test":     'test:("mi test")\n  afirmar_verdad:(1)\nfin_test',
            "Sprite":   'sprite:(jugador, 50, 50, 16, 16, "rojo")',
            "Timer":    "cada:(t1, 1000, mi_funcion)",
            "Evento":   'al:("click", mi_handler)',
        }
        try:
            if os.path.exists(SNIPPETS_FILE):
                with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
                    self.snippets.update(json.load(f))
        except Exception: pass
    def show_snippets(self):
        win = tk.Toplevel(self.root); win.title(self.i18n.t("snippet_mgr")); win.geometry("420x420")
        lb = tk.Listbox(win); lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        for k in self.snippets: lb.insert(tk.END, k)
        def ins(_e=None):
            s = lb.curselection()
            if s and self.active_doc:
                self.active_doc.editor.insert(tk.INSERT, self.snippets[lb.get(s[0])])
                win.destroy()
        lb.bind("<Double-Button-1>", ins)

    def show_tutorials(self):
        tuts = [
            ("1. Hola mundo", 'mostrar "¡Hola!"'),
            ("2. Variables", 'var:(x, 10)\nincrementar:(x, 5)\nmostrar x'),
            ("3. Condicional", 'si:(1 == 1)\n  mostrar "sí"\nfin_si'),
            ("4. Bucle", 'bucle:(3)\n  mostrar "vez"\nfin_bucle'),
            ("5. Función", 'funcion:(saluda, n)\n  mostrar "hola"\nfin_funcion\nllamar:(saluda)'),
            ("6. Clase", 'clase:(Perro)\n  funcion:(ladra)\n    mostrar "guau"\n  fin_funcion\nfin_clase\nnuevo:(p, Perro)\nllamar_metodo:(p, ladra)'),
            ("7. Test", 'test:("suma")\n  sumar:(r, 2, 2)\n  afirmar_igual:(r, 4)\nfin_test'),
            ("8. Sprite", 'sprite:(a, 20, 20, 16, 16, "rojo")\nmover_sprite:(a, 30, 0)'),
        ]
        win = tk.Toplevel(self.root); win.title(self.i18n.t("tutorials")); win.geometry("520x360")
        lb = tk.Listbox(win); lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        for tt,_ in tuts: lb.insert(tk.END, tt)
        def load(_e=None):
            s = lb.curselection()
            if s:
                code = tuts[s[0]][1]
                self._new_document(title=tuts[s[0]][0])
                self.active_doc.editor.insert("1.0", code)
                win.destroy()
        lb.bind("<Double-Button-1>", load)

    def _ensure_plugins_dir(self):
        try: os.makedirs(PLUGINS_DIR, exist_ok=True)
        except Exception: pass
    def show_plugins(self):
        win = tk.Toplevel(self.root); win.title(self.i18n.t("plugins")); win.geometry("480x320")
        lb = tk.Listbox(win); lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        try:
            for f in os.listdir(PLUGINS_DIR):
                if f.endswith((".ez",".py")): lb.insert(tk.END, f)
        except Exception: pass
        def run_plugin(_e=None):
            s = lb.curselection()
            if not s: return
            path = os.path.join(PLUGINS_DIR, lb.get(s[0]))
            with open(path, "r", encoding="utf-8", errors="replace") as f: code = f.read()
            self._new_document(title=os.path.basename(path))
            self.active_doc.editor.insert("1.0", code)
            win.destroy()
        lb.bind("<Double-Button-1>", run_plugin)
    def install_plugin(self):
        p = filedialog.askopenfilename(filetypes=[("EasyScript","*.ez"),("Python","*.py"),("Todos","*.*")])
        if p:
            try:
                shutil.copy(p, PLUGINS_DIR)
                messagebox.showinfo(self.i18n.t("plugins"), "OK")
            except Exception as e: messagebox.showerror("Error", str(e))

    def show_achievements(self):
        ach = self.interpreter.achievements
        messagebox.showinfo(self.i18n.t("achievements"),
            "\n".join("🏆 "+a for a in ach) or "(—)")

    def open_folder_in_sidebar(self):
        p = filedialog.askdirectory()
        if not p: return
        self.sidebar_root = p
        self.refresh_sidebar()
    def refresh_sidebar(self):
        if not self.sidebar_root: return
        for i in self.sidebar_tree.get_children(): self.sidebar_tree.delete(i)
        root = self.sidebar_tree.insert("", "end", text=os.path.basename(self.sidebar_root),
                                        values=[self.sidebar_root], open=True)
        self._populate_tree(root, self.sidebar_root)
    def _populate_tree(self, parent, path):
        try: entries = sorted(os.listdir(path))
        except Exception: return
        for e in entries:
            if e.startswith("."): continue
            full = os.path.join(path, e)
            node = self.sidebar_tree.insert(parent, "end", text=e, values=[full])
            if os.path.isdir(full):
                self._populate_tree(node, full)
    def _on_sidebar_open(self, event):
        sel = self.sidebar_tree.selection()
        if not sel: return
        vals = self.sidebar_tree.item(sel[0], "values")
        if not vals: return
        path = vals[0]
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                doc = self._new_document(title=os.path.basename(path))
                doc.path = path; doc.untitled = False
                doc.editor.delete("1.0", tk.END)
                doc.editor.insert("1.0", content)
                doc.highlight_syntax()
            except Exception as e: messagebox.showerror("Error", str(e))

    def new_project(self):
        self._new_document()
    def save_project(self):
        if not self.active_doc: return
        if self.active_doc.path: self._write_file(self.active_doc, self.active_doc.path)
        else: self.save_project_as()
    def save_project_as(self):
        p = filedialog.asksaveasfilename(defaultextension=".ez",
                                         filetypes=[("EasyScript","*.ez"),("Todos","*.*")])
        if p and self.active_doc:
            self._write_file(self.active_doc, p); self._add_recent(p)
    def _write_file(self, doc, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc.editor.get("1.0", tk.END))
        doc.path = path; doc.modified = False; doc.untitled = False
        idx = self.documents.index(doc)
        self.notebook.tab(idx, text=os.path.basename(path))
        self.status.set(f"OK: {os.path.basename(path)}")
    def load_project(self):
        p = filedialog.askopenfilename(filetypes=[("EasyScript","*.ez"),("Todos","*.*")])
        if not p: return
        try:
            with open(p, "r", encoding="utf-8") as f: content = f.read()
            doc = self._new_document(title=os.path.basename(p))
            doc.path = p; doc.untitled = False
            doc.editor.delete("1.0", tk.END)
            doc.editor.insert("1.0", content)
            doc.highlight_syntax()
            self._add_recent(p)
        except Exception as e: messagebox.showerror("Error", str(e))

    def pack_project(self):
        if not self.active_doc: return
        p = filedialog.asksaveasfilename(defaultextension=".ezp")
        if not p: return
        try:
            with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr("main.ez", self.active_doc.editor.get("1.0", tk.END))
                z.writestr("meta.json", json.dumps({"v": VERSION, "lang": self.language}))
            messagebox.showinfo(self.i18n.t("pack"), p)
        except Exception as e: messagebox.showerror("Error", str(e))
    def unpack_project(self):
        p = filedialog.askopenfilename(filetypes=[("EZP","*.ezp"),("Todos","*.*")])
        if not p: return
        try:
            with zipfile.ZipFile(p, "r") as z:
                code = z.read("main.ez").decode("utf-8")
            doc = self._new_document(title=os.path.basename(p))
            doc.untitled = False
            doc.editor.insert("1.0", code)
        except Exception as e: messagebox.showerror("Error", str(e))

    def export_html(self):
        if not self.active_doc: return
        p = filedialog.asksaveasfilename(defaultextension=".html")
        if not p: return
        code = self.active_doc.editor.get("1.0", "end-1c")
        esc = code.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>EasyScript</title>
<style>body{{background:#1e272e;color:#eee;font-family:Consolas,monospace;padding:20px}}
pre{{background:#282c34;padding:16px;border-radius:8px;white-space:pre-wrap}}</style>
</head><body><h2>EasyScript Studio v{VERSION}</h2><pre>{esc}</pre></body></html>"""
        with open(p, "w", encoding="utf-8") as f: f.write(html)
        messagebox.showinfo(self.i18n.t("export_html"), p)

    def generate_docs(self):
        if not self.active_doc: return
        p = filedialog.asksaveasfilename(defaultextension=".html")
        if not p: return
        code = self.active_doc.editor.get("1.0", "end-1c")
        items = []
        for m in re.finditer(r'(?m)^\s*funcion:\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:,([^)]*))?\)', code):
            items.append(("Función", m.group(1), (m.group(2) or "").strip()))
        for m in re.finditer(r'(?m)^\s*clase:\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)', code):
            items.append(("Clase", m.group(1), ""))
        html = f"<html><head><meta charset='utf-8'><title>Docs</title></head><body>"
        html += f"<h1>{APP_NAME} v{VERSION}</h1><ul>"
        for kind,name,args in items:
            html += f"<li><b>{kind}</b> {name}({args})</li>"
        html += "</ul></body></html>"
        with open(p, "w", encoding="utf-8") as f: f.write(html)
        messagebox.showinfo(self.i18n.t("doc_gen"), p)

    def copy_console(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.console.get("1.0", "end-1c"))
        except Exception: pass
    def save_console(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self.console.get("1.0", "end-1c"))
    def save_canvas_ps(self):
        p = filedialog.asksaveasfilename(defaultextension=".ps")
        if p:
            try: self.canvas.postscript(file=p)
            except Exception as e: messagebox.showerror("Error", str(e))

    def _build_context_menu(self):
        m = tk.Menu(self.root, tearoff=0)
        t = self.i18n.t
        m.add_command(label=t("dup"), command=self.duplicate_line)
        m.add_command(label=t("comment"), command=self.toggle_comment)
        m.add_command(label=t("toggle_bm"), command=self.toggle_bookmark)
        m.add_separator()
        m.add_command(label=t("goto"), command=self.goto_line)
        m.add_command(label=t("format"), command=self.format_code)
        m.add_separator()
        m.add_command(label=t("run_sel"), command=self.run_selection)
        self._ctx_menu = m

    def bind_canvas_key(self, key, handler):
        def wrapper(_e=None): handler()
        self.canvas.bind(f"<KeyPress-{key}>", wrapper)
        self.canvas.focus_set()
    def bind_canvas_mouse(self, ev, handler):
        mapping = {"click":"<Button-1>","move":"<Motion>","dblclick":"<Double-Button-1>"}
        tkev = mapping.get(ev, "<Button-1>")
        self.canvas.bind(tkev, lambda e: handler())

    # ======================================================
    # Diálogos
    # ======================================================
    def show_about(self):
        messagebox.showinfo(self.i18n.t("about"),
                            f"{APP_NAME}\nVersión {VERSION}\n\n{self.i18n.t('about_body')}")

    def show_command_reference(self):
        t = self.i18n.t
        win = tk.Toplevel(self.root); win.title(t("cmd_ref")); win.geometry("780x620")
        txt = tk.Text(win, wrap=tk.WORD, font=("Consolas", 10))
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", self._reference_text())
        txt.config(state="disabled")

    def _reference_text(self):
        t = self.i18n.t
        return f"""{t('ref_title')} — {APP_NAME} v{VERSION}
=====================================
{t('ref_intro')}

─── {t('ref_control')} ───
si:(cond) · sino: · fin_si
mientras:(cond) · fin_mientras
bucle:(n) · fin_bucle
romper · continuar

─── {t('ref_funcs')} ───
funcion:(nombre, args...) · retornar:(x) · fin_funcion
llamar:(nombre, args...)

─── {t('ref_classes')} ───
clase:(Nombre[, Padre]) · funcion:(método, args...) · fin_clase
nuevo:(var, Clase) · llamar_metodo:(var, metodo, args...)
propiedad:(nombre, valor)

─── {t('ref_tests')} ───
test:("nombre") ... fin_test
afirmar_igual:(a, b) · afirmar_verdad:(x) · afirmar_falso:(x)

─── {t('ref_events')} ───
al:("evento", funcion) · emitir:("evento")
cada:(id, ms, funcion) · cancelar_timer:(id)
tecla_al:("a", evento, funcion) · raton_al:("click"|"move", funcion)

─── {t('ref_sprites')} ───
sprite:(nombre, x, y, w, h, color)
mover_sprite:(nombre, dx, dy) · dibujar_sprite:(nombre)
animar:(sprite, dx, dy, pasos, delay)
colisiona:(var, s1, s2) · gravedad:(sprite, g)

─── {t('ref_modules')} ───
importar:("ruta.ez")

─── {t('ref_stdlib')} ───
hash_md5 · hash_sha256 · base64_cod/dec
regex_buscar/reemplazar · csv_parsear/generar
http_get/post · longitud_lista · suma_lista · max_lista · min_lista · contiene

─── {t('ref_audio')} ───
nota:(freq, ms) · musica:("do,re,mi")
beep:(freq, ms) · pitido

─── {t('ref_video')} ───
idioma:("es"|"en"|"pt")
modo_grafico:("8bit"|"16bit"|"normal")
paleta:("nes"|"gameboy"|"cga"|"snes"|"vga"|"sinclair")
pixel:(x,y,color)

─── {t('ref_achievements')} ───
logro:("nombre")

─── {t('ref_shortcuts')} ───
F5 run · F6 selección · F9 breakpoint · F10 paso · F2 bookmark
Ctrl+T nueva pestaña · Ctrl+W cerrar · Esc detener

─── {t('ref_toggle')} ───
{t('ref_toggle_help')}
"""

    def show_examples(self):
        win = tk.Toplevel(self.root); win.title(self.i18n.t("examples")); win.geometry("640x500")
        examples = {
            "Hola mundo":     'mostrar "¡Hola, EasyScript!"',
            "Multi-idioma":   'idioma:("en")\nshow "Hello!"\nidioma:("pt")\nexibir "Olá!"\nidioma:("es")',
            "Condicional":    'var:(n, 5)\nsi:(n > 3)\n  mostrar "Grande"\nsino:\n  mostrar "Pequeño"\nfin_si',
            "Bucle":          'bucle:(5)\n  mostrar "Iter"\nfin_bucle',
            "Función":        'funcion:(doble, x)\n  multiplicar:(r, x, 2)\n  retornar:(r)\nfin_funcion\nllamar:(doble, 21)\nmostrar r',
            "Clase":          'clase:(Saludo)\n  funcion:(constructor)\n    propiedad:(veces, 0)\n  fin_funcion\n  funcion:(di, quien)\n    mostrar "Hola"\n  fin_funcion\nfin_clase\nnuevo:(g, Saludo)\nllamar_metodo:(g, di, "mundo")',
            "Test":           'test:("suma")\n  sumar:(r, 2, 2)\n  afirmar_igual:(r, 4)\nfin_test',
            "Modo 8-bit":     'modo_grafico:("8bit")\npaleta:("nes")\ncuadricula:(16)\ncolor:("rojo")\nrectangulo:(40,40,80,60)',
            "Modo 16-bit":    'modo_grafico:("16bit")\npaleta:("snes")\ncirculo:(150,150,80,"dorado")',
            "Sprite":         'sprite:(nave, 50, 50, 20, 20, "cian")\nmover_sprite:(nave, 60, 0)\nnota:(440, 100)',
            "Hash+Base64":    'hash_sha256:(h, "hola")\nmostrar h\nbase64_cod:(b, "hola mundo")\nmostrar b',
            "Música":         'musica:("do,re,mi,fa,sol,la,si")',
        }
        lb = tk.Listbox(win, font=("Consolas", 10))
        for k in examples: lb.insert(tk.END, k)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)
        def ins(_e=None):
            s = lb.curselection()
            if s:
                self._new_document(title=lb.get(s[0]))
                self.active_doc.untitled = False
                self.active_doc.editor.insert("1.0", examples[lb.get(s[0])])
                win.destroy()
        lb.bind("<Double-Button-1>", ins)

    def show_templates(self):
        win = tk.Toplevel(self.root); win.title(self.i18n.t("templates")); win.geometry("420x280")
        templates = {
            "Dibujo base": 'limpiar_pantalla\ncuadricula:(40)\ncolor:("azul")\n',
            "Retro 8-bit":  'modo_grafico:("8bit")\npaleta:("nes")\ncuadricula:(16)\n',
            "Retro 16-bit": 'modo_grafico:("16bit")\npaleta:("snes")\n',
            "Juego base":   'modo_grafico:("8bit")\nsprite:(jugador, 100, 200, 20, 20, "verde")\ntecla_al:("Left","", mover_izq)\ntecla_al:("Right","", mover_der)\nfuncion:(mover_izq)\n  mover_sprite:(jugador, -20, 0)\nfin_funcion\nfuncion:(mover_der)\n  mover_sprite:(jugador, 20, 0)\nfin_funcion\n',
        }
        lb = tk.Listbox(win); lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        for k in templates: lb.insert(tk.END, k)
        def pick(_e=None):
            s = lb.curselection()
            if s:
                self._new_document(title=lb.get(s[0]))
                self.active_doc.untitled = False
                self.active_doc.editor.insert("1.0", templates[lb.get(s[0])])
                win.destroy()
        lb.bind("<Double-Button-1>", pick)

    def inspect_variables(self):
        win = tk.Toplevel(self.root); win.title(self.i18n.t("vars")); win.geometry("480x400")
        lb = tk.Listbox(win, font=("Consolas", 10))
        for k,v in self.interpreter.variables.items():
            lb.insert(tk.END, f"{k} = {v!r}")
        lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def export_variables(self):
        p = filedialog.asksaveasfilename(defaultextension=".json")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(self.interpreter.variables, f, indent=2, ensure_ascii=False, default=str)
    def import_variables(self):
        p = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if p:
            with open(p, "r", encoding="utf-8") as f:
                self.interpreter.variables.update(json.load(f))

    def show_stats(self):
        i = self.interpreter; s = self.session_stats
        messagebox.showinfo(self.i18n.t("stats_title"),
            f"stmt: {i.executed_lines} · t: {i.execution_time:.3f}s\n"
            f"vars: {len(i.variables)} · classes: {len(i.classes)} · sprites: {len(i.sprites)}\n"
            f"lang: {self.language} · mode: {self.video_mode} · palette: {self.palette_name}\n"
            f"--- Session ---\nRuns: {s['ejecuciones']} · T: {s['tiempo']:.2f}s · stmt: {s['sentencias']}")

    # ======================================================
    # Paleta de comandos
    # ======================================================
    def open_command_palette(self):
        win = tk.Toplevel(self.root); win.title(self.i18n.t("cmd_palette")); win.geometry("500x360")
        e = tk.Entry(win, font=("Consolas", 11)); e.pack(fill=tk.X, padx=6, pady=6)
        lb = tk.Listbox(win, font=("Consolas", 10)); lb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        actions = {
            "New": self._new_document, "Open": self.load_project, "Save": self.save_project,
            "Run": self.run_code, "RunSel": self.run_selection, "Stop": self.stop_execution,
            "Find": self.open_find_dialog, "SearchAll": self.search_all_tabs,
            "Format": self.format_code, "Vars": self.inspect_variables,
            "Examples": self.show_examples, "Reference": self.show_command_reference,
            "Tutorials": self.show_tutorials, "Snippets": self.show_snippets,
            "Stats": self.show_stats, "Theme": self.toggle_theme,
            "Fullscreen": self.toggle_fullscreen, "Presentation": self.toggle_presentation,
            "8-bit": lambda: self.apply_video_mode("8bit"),
            "16-bit": lambda: self.apply_video_mode("16bit"),
            "Normal": lambda: self.apply_video_mode("normal"),
            "NES": lambda: self.apply_palette("nes"),
            "SNES": lambda: self.apply_palette("snes"),
            "ES": lambda: self.change_language("es"),
            "EN": lambda: self.change_language("en"),
            "PT": lambda: self.change_language("pt"),
            "Debug": self.show_debugger, "Watch": self.show_watch,
            "Callstack": self.show_callstack, "Profile": self.show_profile,
            "Tests": self.run_tests, "History": self.show_history,
            "Diff": self.show_diff, "Commit": self.local_commit,
            "Pack": self.pack_project, "Unpack": self.unpack_project,
            "ExportHTML": self.export_html, "Docs": self.generate_docs,
            "Plugins": self.show_plugins, "Achievements": self.show_achievements,
        }
        def refresh(*_):
            q = e.get().lower(); lb.delete(0, tk.END)
            for n in actions:
                if q in n.lower(): lb.insert(tk.END, n)
        def run(_e=None):
            s = lb.curselection()
            if s:
                name = lb.get(s[0]); win.destroy(); actions[name]()
        e.bind("<KeyRelease>", refresh); e.bind("<Return>", run)
        lb.bind("<Double-Button-1>", run)
        refresh(); e.focus_set()

    # ======================================================
    # Recientes / autosave / config
    # ======================================================
    def _add_recent(self, path):
        if path in self.recent_files: self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:MAX_RECENT_FILES]
        self._rebuild_recent_menu(); self._save_config()
    def _rebuild_recent_menu(self):
        if not hasattr(self, "recent_menu"): return
        self.recent_menu.delete(0, tk.END)
        if not self.recent_files:
            self.recent_menu.add_command(label="(—)", state="disabled")
        for p in self.recent_files:
            self.recent_menu.add_command(label=p, command=lambda pp=p: self._open_recent(pp))
    def _open_recent(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f: content = f.read()
            doc = self._new_document(title=os.path.basename(path))
            doc.path = path; doc.untitled = False
            doc.editor.insert("1.0", content)
        except Exception as e: messagebox.showerror("Error", str(e))

    def _schedule_autosave(self):
        def tick():
            try:
                if self.active_doc and self.active_doc.path and self.active_doc.modified:
                    self._write_file(self.active_doc, self.active_doc.path)
            except Exception: pass
            self.autosave_id = self.root.after(AUTOSAVE_INTERVAL_MS, tick)
        self.autosave_id = self.root.after(AUTOSAVE_INTERVAL_MS, tick)

    def _load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: cfg = json.load(f)
                self.font_family  = cfg.get("font_family", DEFAULT_FONT)
                self.font_size    = cfg.get("font_size", DEFAULT_FONT_SIZE)
                self.tab_size     = cfg.get("tab_size", 4)
                self.recent_files = cfg.get("recent_files", [])
                self.language     = cfg.get("language", DEFAULT_LANGUAGE)
                self.video_mode   = cfg.get("video_mode", DEFAULT_VIDEO_MODE)
                self.palette_name = cfg.get("palette", DEFAULT_PALETTE)
                if self.language in self.i18n.LANGS: self.i18n.set_lang(self.language)
                geo = cfg.get("geometry")
                if geo: self.root.geometry(geo)
        except Exception: pass
    def _save_config(self):
        try:
            cfg = {"font_family":self.font_family,"font_size":self.font_size,
                   "tab_size":self.tab_size,"recent_files":self.recent_files,
                   "language":self.language,"video_mode":self.video_mode,
                   "palette":self.palette_name,"geometry":self.root.geometry()}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=2)
        except Exception: pass
    def _on_close(self):
        self._save_config()
        self.interpreter.should_stop = True
        self.root.destroy()

    def ask_input(self, prompt_text):
        return simpledialog.askstring("EasyScript", prompt_text, parent=self.root)

    def _load_demo(self, doc):
        demo = (
            "// --- EASYSCRIPT v4.1.0 ---\n"
            "// Cambia el idioma desde el menú Idioma → se retraduce toda la ventana\n\n"
            "var:(n, 0)\n"
            "bucle:(3)\n"
            "  incrementar:(n, 1)\n"
            "  mostrar n\n"
            "fin_bucle\n\n"
            "funcion:(doble, x)\n"
            "  multiplicar:(r, x, 2)\n"
            "  retornar:(r)\n"
            "fin_funcion\n"
            "llamar:(doble, 21)\n"
            "mostrar r\n\n"
            "test:(\"suma básica\")\n"
            "  sumar:(r, 2, 2)\n"
            "  afirmar_igual:(r, 4)\n"
            "fin_test\n\n"
            "modo_grafico:(\"8bit\")\n"
            "paleta:(\"nes\")\n"
            "cuadricula:(16)\n"
            "color:(\"rojo\")\n"
            "rectangulo:(40, 40, 80, 60)\n"
            "circulo:(220, 90, 40, \"azul\")\n"
            "sprite:(nave, 300, 200, 20, 20, \"cian\")\n"
            "nota:(440, 100)\n"
            "musica:(\"do,mi,sol,do5\")\n"
            "logro:(\"Primera ejecución v4.1\")\n"
        )
        doc.editor.insert(tk.END, demo)


EZScriptIDE = EasyScriptIDE


# ==========================================
# ENTRADA
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = EasyScriptIDE(root)
    root.mainloop()
