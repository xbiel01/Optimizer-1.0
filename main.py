# main.py
import os
import sys
import threading
import time
import subprocess
import customtkinter as ctk
import numpy as np
from PIL import Image

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import styles 
import system_tools

def obter_caminho_recurso(caminho_relativo):
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, caminho_relativo)

class OptimizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da Janela Principal
        self.configure(fg_color=styles.COLOR_BACKGROUND)
        self.title(styles.WINDOW_TITLE)
        self.geometry(styles.WINDOW_GEOMETRY)
        self.minsize(styles.WINDOW_MIN_WIDTH, styles.WINDOW_MIN_HEIGHT)
        
        try: 
            self.iconbitmap(obter_caminho_recurso("meu_icone.ico"))
        except Exception: 
            pass

        self.v_atual_sub_thread = 0.0
        self.testando_rede = False
        self.sidebar_expandida = True
        self.info_sys = system_tools.obter_info_sistema()

        # Layout Principal
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=styles.COLOR_SIDEBAR)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.btn_toggle = ctk.CTkButton(
            self.sidebar_frame, text="☰", width=30, height=30, fg_color="transparent", 
            text_color=styles.COLOR_TEXT_MAIN, font=(styles.FONT_FAMILY, 18), hover_color=styles.COLOR_CARD_BG, command=self.alternar_sidebar
        )
        self.btn_toggle.pack(anchor="e", padx=15, pady=(15, 0))

        # --- LOGO E BRANDING CORPORATIVO NA SIDEBAR ---
        self.logo_img = self.carregar_icone("logo.png", size=(120, 32))
        self.logo_icone_sm = self.carregar_icone("logo.png", size=(28, 28))
        
        self.lbl_logo = ctk.CTkLabel(
            self.sidebar_frame, 
            text="" if self.logo_img else "Optimizer 1.0", 
            image=self.logo_img,
            font=styles.FONT_HEADER_ID, 
            text_color=styles.COLOR_TEXT_MAIN
        )
        self.lbl_logo.pack(pady=(10, 20))

        self.right_main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_main_frame.pack(side="right", fill="both", expand=True)

        # Console / Terminal de Eventos Global
        self.console_frame = ctk.CTkFrame(self.right_main_frame, height=140, border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        self.console_frame.pack(side="bottom", fill="x", padx=25, pady=(0, 20))
        self.console_frame.pack_propagate(False)

        header_console = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        header_console.pack(fill="x", padx=15, pady=(5, 0))

        ctk.CTkLabel(header_console, text=" TERMINAL DE EVENTOS", font=(styles.FONT_FAMILY, 11, "bold"), text_color=styles.COLOR_TEXT_MUTED).pack(side="left")
        
        # Mini Marca d'água no Console
        if self.logo_icone_sm:
            ctk.CTkLabel(header_console, text="", image=self.logo_icone_sm).pack(side="right")

        self.log_textbox = ctk.CTkTextbox(self.console_frame, fg_color=styles.COLOR_BACKGROUND, text_color=styles.COLOR_TEXT_MAIN)
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(5, 10))
        self.log_textbox.insert("0.0", "Optimizer 1.0 inicializado e pronto.\n")
        self.log_textbox.configure(state="disabled")

        self.main_container = ctk.CTkFrame(self.right_main_frame, fg_color="transparent")
        self.main_container.pack(side="top", fill="both", expand=True, padx=25, pady=(20, 15))

        # Menu e Views
        telas_botoes = [
            ("Inicio", "Inicio", "dashboard.png"), ("Otimizações", "Otimizações", "otimiza.png"),
            ("Diagnóstico", "Diagnostico", "diag.png"), ("Ferramentas Admin", "Admin", "admin.png"),
            ("Central CMD", "CMD", "cmd.png"), ("Instaladores", "Instalador", "install.png"),
            ("Inicialização (Boot)", "Startup", "startup.png"), ("Rede", "Rede", "rede.png")
        ]

        self.botoes_menu, self.textos_originais_menu = {}, {}
        scroll_sidebar = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        scroll_sidebar.pack(fill="both", expand=True)

        for txt, key, img in telas_botoes:
            texto_fmt = f"  {txt}"
            self.textos_originais_menu[key] = texto_fmt
            btn = ctk.CTkButton(
                scroll_sidebar, text=texto_fmt, fg_color="transparent", text_color="#C0CCEA", 
                font=styles.FONT_MENU_BUTTON, height=40, anchor="w", image=self.carregar_icone(img), compound="left",
                hover_color=styles.COLOR_CARD_BG, command=lambda k=key: self.alternar_janelas(k)
            )
            btn.pack(fill="x", padx=5, pady=2)
            self.botoes_menu[key] = btn

        self.lbl_assinatura = ctk.CTkLabel(self.sidebar_frame, text="© 2026 Gabriel Melo", font=(styles.FONT_FAMILY, 10, "italic"), text_color=styles.COLOR_TEXT_MUTED)
        self.lbl_assinatura.pack(side="bottom", pady=15)

        self.views = { k: ctk.CTkFrame(self.main_container, fg_color="transparent") for _, k, _ in telas_botoes }

        # Inicialização das Views
        self.configurar_tela_Inicio()
        self.configurar_aba_otimizacoes()
        self.configurar_aba_diagnostico()
        self.configurar_aba_admin()
        self.configurar_aba_cmd()
        self.configurar_aba_apps()
        self.configurar_aba_startup()
        self.configurar_aba_rede()

        self.alternar_janelas("Inicio")
        self.atualizar_hardware_tempo_real()

    # --- UI & UTILITÁRIOS ---
    def alternar_sidebar(self):
        self.sidebar_expandida = not self.sidebar_expandida
        self.sidebar_frame.configure(width=230 if self.sidebar_expandida else 65)
        
        if self.sidebar_expandida:
            if self.logo_img:
                self.lbl_logo.configure(image=self.logo_img, text="")
            else:
                self.lbl_logo.configure(text="Optimizer 1.0")
            self.btn_toggle.configure(text="☰")
            for key, btn in self.botoes_menu.items(): 
                btn.configure(text=self.textos_originais_menu[key])
            self.lbl_assinatura.pack(side="bottom", pady=15)
        else:
            if self.logo_icone_sm:
                self.lbl_logo.configure(image=self.logo_icone_sm, text="")
            else:
                self.lbl_logo.configure(text="OP")
            self.btn_toggle.configure(text="▶")
            self.lbl_assinatura.pack_forget()
            for btn in self.botoes_menu.values(): 
                btn.configure(text="")

    def carregar_icone(self, nome_arquivo, size=(20, 20)):
        caminho = obter_caminho_recurso(os.path.join("assets", nome_arquivo))
        if os.path.exists(caminho):
            try:
                img = Image.open(caminho)
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            except Exception: 
                pass
        return None

    def atualizar_log(self, texto):
        self.after(0, lambda: (
            self.log_textbox.configure(state="normal"),
            self.log_textbox.insert("end", texto + "\n"),
            self.log_textbox.see("end"),
            self.log_textbox.configure(state="disabled")
        ))

    def alternar_janelas(self, nome_tela):
        for frame in self.views.values(): 
            frame.pack_forget()
        for key, btn in self.botoes_menu.items(): 
            btn.configure(fg_color="transparent", text_color="#C0CCEA")
            
        self.views[nome_tela].pack(fill="both", expand=True)
        self.botoes_menu[nome_tela].configure(fg_color=styles.COLOR_ACCENT, text_color=styles.COLOR_TEXT_MAIN)
        if nome_tela == "Startup": 
            self.carregar_lista_startup()

    # ================= 1. INICIO =================
    def configurar_tela_Inicio(self):
        inicio_view = self.views["Inicio"]

        info_frame = ctk.CTkFrame(inicio_view, border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        info_frame.pack(fill="x", pady=(0, 15))
        info_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(info_frame, text="HARDWARE & SISTEMA", font=styles.FONT_BLOCO1_TITULO, text_color=styles.COLOR_TEXT_MUTED).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(15, 8))

        dados_sistema = [
            (1, 0, "pc.png", "🖥️", f"Máquina: {self.info_sys['hostname']}"), 
            (1, 1, "os.png", "🔷", f"SO: {self.info_sys['so']}"),
            (1, 2, "ip.png", "🌐", f"IP: {self.info_sys['ip']}"), 
            (2, 0, "cpu.png", "🔲", f"CPU: {self.info_sys['cpu']}"),
            (2, 1, "ram.png", "📟", f"RAM: {self.info_sys['ram_total']} GB")
        ]

        for r, c, img, emoji, txt in dados_sistema:
            icone = self.carregar_icone(img)
            fonte = styles.FONT_BLOCO1_TEXTO_BOLD if "Máquina" in txt or "SO" in txt else styles.FONT_BLOCO1_TEXTO
            item_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            item_frame.grid(row=r, column=c, sticky="w", padx=20, pady=6)
            
            if icone:
                ctk.CTkLabel(item_frame, text=f"  {txt}", image=icone, compound="left", font=fonte, text_color=styles.COLOR_TEXT_MAIN).pack(side="left")
            else:
                ctk.CTkLabel(item_frame, text=f"{emoji}  {txt}", font=fonte, text_color=styles.COLOR_TEXT_MAIN).pack(side="left")

        charts_frame = ctk.CTkFrame(inicio_view, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True)
        charts_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="charts")
        charts_frame.grid_rowconfigure(0, weight=1)

        self.charts = {}
        for idx, (key, title) in enumerate([("cpu", "DESEMPENHO DA CPU"), ("ram", "MEMÓRIA RAM"), ("hd", "ARMAZENAMENTO C:")]):
            card = ctk.CTkFrame(charts_frame, border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
            card.grid(row=0, column=idx, padx=4 if idx == 1 else (0 if idx == 0 else (4, 0)), sticky="nsew")
            ctk.CTkLabel(card, text=title, font=styles.FONT_SECTION_TITLE, text_color=styles.COLOR_TEXT_MUTED).pack(pady=(15, 0))
            
            fig = Figure(figsize=(2.5, 2.5), dpi=100, facecolor='none')
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
            ax = fig.add_subplot(111)
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
            canvas.get_tk_widget().configure(bg=styles.COLOR_CARD_BG)
            self.charts[key] = (ax, canvas)

    def atualizar_hardware_tempo_real(self):
        hw = system_tools.obter_uso_hardware()
        configs = [
            (self.charts["cpu"], hw["cpu_pct"], styles.COLOR_GRAPH_CPU, f"{hw['cpu_pct']}%", f"{hw['cpu_freq']} GHz\nEm Uso"),
            (self.charts["ram"], hw["ram_pct"], styles.COLOR_GRAPH_RAM, f"{hw['ram_usada']} GB", f"Total: {hw['ram_total']} GB"),
            (self.charts["hd"], hw["hd_pct"], styles.COLOR_GRAPH_HD, f"{hw['hd_pct']}%", f"{hw['hd_usado']} GB\nUsados")
        ]
        
        for (ax, canvas), pct, cor, txt_p, txt_s in configs:
            ax.clear()
            ax.set_facecolor('none')
            ax.pie([pct, max(0, 100 - pct)], colors=[cor, styles.COLOR_GRAPH_EMPTY], startangle=90, wedgeprops=dict(width=0.14, edgecolor='none'))
            ax.text(0, 0, txt_p, ha='center', va='center', color='white', fontname=styles.FONT_FAMILY, fontsize=15, weight='bold')
            ax.text(0, -0.35, txt_s, ha='center', va='center', color=styles.COLOR_TEXT_MUTED, fontname=styles.FONT_FAMILY, fontsize=9, weight='medium')
            ax.axis('equal')
            canvas.draw_idle()

        if hasattr(self, 'container_processos'):
            for widget in self.container_processos.winfo_children(): 
                widget.destroy()
            for p in system_tools.obter_top_processos():
                linha = ctk.CTkFrame(self.container_processos, fg_color="transparent")
                linha.pack(fill="x", pady=2)
                ctk.CTkLabel(linha, text=p['name'], width=200, anchor="w", font=(styles.FONT_FAMILY, 12, "bold"), text_color=styles.COLOR_TEXT_MAIN).pack(side="left")
                ctk.CTkLabel(linha, text=f"RAM: {round(p['memory_percent'], 1)}%", width=100, anchor="w", text_color=styles.COLOR_TEXT_MUTED).pack(side="left")
                ctk.CTkButton(linha, text="Encerrar", width=90, height=24, fg_color="#C0392B", hover_color="#A93226", command=lambda pid=p['pid']: self.acionar_kill(pid)).pack(side="right")

        self.after(5000, self.atualizar_hardware_tempo_real)

    def acionar_kill(self, pid):
        system_tools.matar_processo(pid, self.atualizar_log)
        self.atualizar_log("[Sistema] Recalculando processos em uso...")

    # ================= 2. OTIMIZAÇÕES =================
    def configurar_aba_otimizacoes(self):
        scroll_otim = ctk.CTkScrollableFrame(self.views["Otimizações"], fg_color="transparent")
        scroll_otim.pack(fill="both", expand=True)

        sub = ctk.CTkFrame(scroll_otim, border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        sub.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(sub, text="Ativar Perfil de Desempenho", fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, command=lambda: system_tools.executar_cmd_background("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61", "Desempenho", self.atualizar_log), height=45, font=styles.FONT_MENU_BUTTON).grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        ctk.CTkButton(sub, text="Desativar Telemetria", fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, command=lambda: system_tools.executar_cmd_background('sc config DiagTrack start= disabled && sc stop DiagTrack && reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f', "Telemetria", self.atualizar_log), height=45, font=styles.FONT_MENU_BUTTON).grid(row=0, column=1, padx=20, pady=15, sticky="ew")
        
        self.btn_limpeza = ctk.CTkButton(sub, text="Limpar Arquivos Temporários", fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, command=self.disparar_limpeza, height=45, font=styles.FONT_MENU_BUTTON)
        self.btn_limpeza.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        ctk.CTkButton(sub, text="Otimizar Inicialização & Cache", fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, command=lambda: system_tools.otimizar_inicializacao(self.atualizar_log), height=45, font=styles.FONT_MENU_BUTTON).grid(row=1, column=1, padx=20, pady=15, sticky="ew")
        
        self.lbl_status_limpeza = ctk.CTkLabel(sub, text="", font=(styles.FONT_FAMILY, 11, "italic"), text_color=styles.COLOR_TEXT_MUTED)
        self.lbl_status_limpeza.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 0))
        self.barra_limpeza = ctk.CTkProgressBar(sub, width=500, height=12, progress_color=styles.COLOR_ACCENT)
        self.barra_limpeza.set(0)
        sub.grid_columnconfigure((0, 1), weight=1)

        # Processos Top 5
        self.frame_top_processos = ctk.CTkFrame(scroll_otim, border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        self.frame_top_processos.pack(fill="x", padx=5, pady=(15, 5))
        ctk.CTkLabel(self.frame_top_processos, text="⚠️ CAÇADOR DE RECURSOS (TOP 5 CONSUMIDORES DE RAM)", font=(styles.FONT_FAMILY, 11, "bold"), text_color=styles.COLOR_TEXT_MUTED).pack(pady=(12, 5))
        self.container_processos = ctk.CTkFrame(self.frame_top_processos, fg_color="transparent")
        self.container_processos.pack(fill="both", expand=True, padx=20, pady=5)

        # Debloater
        frame_debloat = ctk.CTkFrame(scroll_otim, border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        frame_debloat.pack(fill="x", padx=5, pady=(15, 10))
        ctk.CTkLabel(frame_debloat, text="🗑️ Remover Aplicativos Nativos Inúteis (Bloatware)", font=(styles.FONT_FAMILY, 12, "bold"), text_color=styles.COLOR_TEXT_MAIN).pack(anchor="w", padx=25, pady=(15, 5))
        
        self.dict_bloatware = {
            "Xbox App / Game Bar": "Microsoft.XboxApp", "Clima (Bing Weather)": "Microsoft.BingWeather",
            "Dicas do Windows": "Microsoft.Getstarted", "Construtor 3D": "Microsoft.3DBuilder",
            "Ajuda do Windows": "Microsoft.GetHelp", "Gravador de Voz": "Microsoft.WindowsSoundRecorder",
            "Hub de Comentários": "Microsoft.WindowsFeedbackHub", "Coleção Solitaire": "Microsoft.MicrosoftSolitaireCollection"
        }
        
        chk_frame = ctk.CTkFrame(frame_debloat, fg_color="transparent")
        chk_frame.pack(fill="x", padx=25)
        self.check_bloat = {}
        for i, nome_app in enumerate(self.dict_bloatware.keys()):
            self.check_bloat[nome_app] = ctk.BooleanVar()
            ctk.CTkCheckBox(chk_frame, text=nome_app, variable=self.check_bloat[nome_app], font=(styles.FONT_FAMILY, 13), text_color=styles.COLOR_TEXT_MAIN, checkmark_color=styles.COLOR_TEXT_MAIN, fg_color=styles.COLOR_ACCENT).grid(row=i//2, column=i%2, padx=10, pady=10, sticky="w")
        
        self.btn_debloat = ctk.CTkButton(frame_debloat, text="Desinstalar Bloatware Selecionado", width=300, height=45, fg_color="#C0392B", hover_color="#A93226", font=styles.FONT_MENU_BUTTON, command=self.acionar_debloater)
        self.btn_debloat.pack(pady=(15, 20))

    def disparar_limpeza(self):
        self.btn_limpeza.configure(state="disabled", text="Analisando arquivos...")
        self.barra_limpeza.grid(row=3, column=0, columnspan=2, padx=20, pady=10)
        self.barra_limpeza.set(0)
        system_tools.limpar_arquivos_temporarios(
            self.atualizar_log, 
            lambda p: self.after(0, lambda: self.barra_limpeza.set(p)), 
            lambda t: self.after(0, lambda: self.lbl_status_limpeza.configure(text=t)), 
            lambda q: self.after(0, lambda: [self.barra_limpeza.grid_forget(), self.lbl_status_limpeza.configure(text=""), self.btn_limpeza.configure(state="normal", text="Limpar Arquivos Temporários")])
        )

    def acionar_debloater(self):
        apps = [self.dict_bloatware[k] for k, v in self.check_bloat.items() if v.get()]
        if not apps: return
        self.btn_debloat.configure(state="disabled", text="Desinstalando...")
        system_tools.remover_bloatware(apps, self.atualizar_log, lambda: self.after(0, lambda: self.btn_debloat.configure(state="normal", text="Desinstalar Bloatware Selecionado")))

    # ================= 3. DIAGNÓSTICO =================
    def configurar_aba_diagnostico(self):
        sub = ctk.CTkFrame(self.views["Diagnostico"], border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        sub.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(sub, text="Ferramentas Avançadas de Varredura e Reparo de Imagem:", font=(styles.FONT_FAMILY, 12, "bold"), text_color=styles.COLOR_TEXT_MAIN).pack(anchor="w", padx=25, pady=(20, 15))
        
        self.btn_reparo = ctk.CTkButton(sub, text="Verificar Integridade (SFC / DISM)", fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, command=self.disparar_reparo_sistema, width=350, height=40, font=styles.FONT_MENU_BUTTON)
        self.btn_reparo.pack(pady=8)
        self.btn_event_viewer = ctk.CTkButton(sub, text="Mapear Últimos Erros do Event Viewer", fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, command=self.diagnosticar_erros_criticos, width=350, height=40, font=styles.FONT_MENU_BUTTON)
        self.btn_event_viewer.pack(pady=8)
        self.btn_winget_drivers = ctk.CTkButton(sub, text="Atualizar Drivers & Runtimes (Winget)", fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, command=self.atualizar_drivers_sistema, width=350, height=40, font=styles.FONT_MENU_BUTTON)
        self.btn_winget_drivers.pack(pady=8)

    def disparar_reparo_sistema(self):
        self.btn_reparo.configure(state="disabled", text="⚙️ Reparando...")
        self.atualizar_log("\n" + "="*50 + "\n[Reparo] Iniciando DISM / SFC...")
        system_tools.executar_cmd_background("DISM.exe /Online /Cleanup-image /Restorehealth && sfc /scannow", "Reparo do Sistema", self.atualizar_log, lambda: self.after(0, lambda: self.btn_reparo.configure(state="normal", text="Verificar Integridade (SFC / DISM)")))

    def diagnosticar_erros_criticos(self):
        self.btn_event_viewer.configure(state="disabled", text="🔍 Coletando Erros...")
        system_tools.executar_cmd_background('powershell -Command "Get-WinEvent -LogName System -MaxEvents 10 | Where-Object {$_.Level -eq 1 -or $_.Level -eq 2} | Select-Object TimeCreated, ProviderName, Message | Format-List"', "Diagnóstico Event Viewer", self.atualizar_log, lambda: self.after(0, lambda: self.btn_event_viewer.configure(state="normal", text="Mapear Últimos Erros do Event Viewer")))

    def atualizar_drivers_sistema(self):
        self.btn_winget_drivers.configure(state="disabled", text="📥 Baixando Updates...")
        system_tools.executar_cmd_background("winget upgrade --all --include-unknown --silent --accept-package-agreements", "Winget Update", self.atualizar_log, lambda: self.after(0, lambda: self.btn_winget_drivers.configure(state="normal", text="Atualizar Drivers & Runtimes (Winget)")))

    # ================= 4. STARTUP =================
    def configurar_aba_startup(self):
        sub = ctk.CTkFrame(self.views["Startup"], border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        sub.pack(fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(sub, text="🚀 Gerenciador de Inicialização do Windows", font=(styles.FONT_FAMILY, 12, "bold"), text_color=styles.COLOR_TEXT_MAIN).pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(sub, text="Aplicativos abaixo atrasam o ligamento do PC. Remova os que não são essenciais.", text_color=styles.COLOR_TEXT_MUTED).pack(anchor="w", padx=25, pady=(0, 10))
        
        self.scroll_startup = ctk.CTkScrollableFrame(sub, fg_color=styles.COLOR_BACKGROUND)
        self.scroll_startup.pack(fill="both", expand=True, padx=25, pady=10)

    def carregar_lista_startup(self):
        for widget in self.scroll_startup.winfo_children(): 
            widget.destroy()
        apps = system_tools.listar_startup_apps()
        if not apps:
            ctk.CTkLabel(self.scroll_startup, text="Nenhum aplicativo de terceiros na inicialização do registro.", text_color=styles.COLOR_TEXT_MUTED).pack(pady=20)
            return
        for nome, caminho in apps:
            linha = ctk.CTkFrame(self.scroll_startup, fg_color="transparent")
            linha.pack(fill="x", pady=4)
            ctk.CTkLabel(linha, text=nome, width=150, anchor="w", font=(styles.FONT_FAMILY, 12, "bold"), text_color=styles.COLOR_TEXT_MAIN).pack(side="left")
            caminho_curto = (caminho[:50] + '...') if len(caminho) > 50 else caminho
            ctk.CTkLabel(linha, text=caminho_curto, width=300, anchor="w", text_color=styles.COLOR_TEXT_MUTED).pack(side="left", padx=10)
            ctk.CTkButton(linha, text="Desativar", width=80, height=24, fg_color="#C0392B", hover_color="#A93226", command=lambda n=nome: self.desativar_startup(n)).pack(side="right")

    def desativar_startup(self, nome):
        if system_tools.remover_startup_app(nome, self.atualizar_log): 
            self.carregar_lista_startup()

    # ================= 5. FERRAMENTAS ADMIN =================
    def configurar_aba_admin(self):
        sub = ctk.CTkFrame(self.views["Admin"], border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        sub.pack(fill="both", expand=True, padx=5, pady=5)
        btn_frame = ctk.CTkFrame(sub, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        ferramentas = [
            ("Gerenciamento do Computador", "compmgmt.msc"), ("Gerenciador de Dispositivos", "devmgmt.msc"),
            ("Visualizador de Eventos", "eventvwr.msc"), ("Serviços do Windows", "services.msc"),
            ("Conexões de Rede", "ncpa.cpl"), ("Gerenciamento de Disco", "diskmgmt.msc"),
            ("Editor de Registro", "regedit.exe"), ("Monitor de Recursos", "resmon.exe"),
            ("Gerenciador de Tarefas", "taskmgr.exe")
        ]
        for idx, (nome, msc) in enumerate(ferramentas):
            ctk.CTkButton(btn_frame, text=nome, width=220, height=38, fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, font=styles.FONT_MENU_BUTTON, command=lambda m=msc: subprocess.Popen(m, shell=True)).grid(row=idx//3, column=idx%3, padx=10, pady=8)

    # ================= 6. CENTRAL CMD =================
    def configurar_aba_cmd(self):
        sub = ctk.CTkFrame(self.views["CMD"], border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        sub.pack(fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(sub, text="Comandos Rápidos do Windows CMD:", font=(styles.FONT_FAMILY, 12, "bold"), text_color=styles.COLOR_TEXT_MAIN).pack(anchor="w", padx=25, pady=(20, 10))
        
        grid_frame = ctk.CTkFrame(sub, fg_color="transparent")
        grid_frame.pack(fill="x", padx=25)
        comandos = [
            ("Rodar 'ipconfig/all'", "ipconfig/all"), ("Limpar DNS (flushdns)", "ipconfig /flushdns"),
            ("Testar Ping (8.8.8.8)", "ping 8.8.8.8"), ("Ver Conexões (netstat)", "netstat -an"),
            ("Info Detalhada", "systeminfo"), ("Verificar Disco", "chkdsk")
        ]
        for idx, (lbl, cmd) in enumerate(comandos):
            ctk.CTkButton(grid_frame, text=lbl, height=38, fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, font=styles.FONT_MENU_BUTTON, command=lambda cm=cmd: subprocess.Popen(f"start cmd /k {cm}", shell=True)).grid(row=idx//3, column=idx%3, padx=5, pady=8, sticky="ew")

    # ================= 7. INSTALADORES =================
    def configurar_aba_apps(self):
        sub = ctk.CTkFrame(self.views["Instalador"], border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        sub.pack(fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(sub, text="Marque os aplicativos que deseja instalar:", font=(styles.FONT_FAMILY, 12, "bold"), text_color=styles.COLOR_TEXT_MAIN).pack(anchor="w", padx=25, pady=(20, 5))
        
        self.dict_apps = {
            "Google Chrome": "Google.Chrome", "Adobe Acrobat": "Adobe.Acrobat.Reader.64-bit",
            "WinRAR": "RARLab.WinRAR", "AnyDesk": "AnyDeskSoftwareGmbH.AnyDesk",
            "VLC Player": "VideoLAN.VLC", "Notepad++": "Notepad++.Notepad++",
            "Revo Uninstaller": "RevoCompiler.RevoUninstaller", "IP Scanner": "Famatech.AdvancedIPScanner"
        }
        
        chk_frame = ctk.CTkFrame(sub, fg_color="transparent")
        chk_frame.pack(fill="x", padx=25)
        self.checkbox_vars = {}
        for i, nome_app in enumerate(self.dict_apps.keys()):
            self.checkbox_vars[nome_app] = ctk.BooleanVar()
            ctk.CTkCheckBox(chk_frame, text=nome_app, variable=self.checkbox_vars[nome_app], font=(styles.FONT_FAMILY, 13), text_color=styles.COLOR_TEXT_MAIN, checkmark_color=styles.COLOR_TEXT_MAIN, fg_color=styles.COLOR_ACCENT).grid(row=i//2, column=i%2, padx=10, pady=12, sticky="w")
        
        self.btn_instalar = ctk.CTkButton(sub, text="Instalar Programas", width=300, height=45, fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, font=styles.FONT_MENU_BUTTON, command=self.instalar_apps_selecionados)
        self.btn_instalar.pack(pady=(20, 5))
        self.progress_bar = ctk.CTkProgressBar(sub, width=400, mode="indeterminate", progress_color=styles.COLOR_ACCENT)

    def instalar_apps_selecionados(self):
        apps = [name for name, var in self.checkbox_vars.items() if var.get()]
        if not apps: return
        self.progress_bar.pack(pady=10); self.progress_bar.start(); self.btn_instalar.configure(state="disabled")
        system_tools.instalar_apps_winget(self.dict_apps, apps, self.atualizar_log, lambda: self.after(0, lambda: [self.progress_bar.stop(), self.progress_bar.pack_forget(), self.btn_instalar.configure(state="normal")]))

    # ================= 8. REDE =================
    def configurar_aba_rede(self):
        sub = ctk.CTkFrame(self.views["Rede"], border_width=1, border_color=styles.COLOR_CARD_BORDER, fg_color=styles.COLOR_CARD_BG)
        sub.pack(fill="both", expand=True, padx=5, pady=5)
        sub.grid_columnconfigure((0, 1), weight=1, uniform="rede_cols")

        frame_esq = ctk.CTkFrame(sub, fg_color="transparent")
        frame_esq.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(frame_esq, text="Velocímetro de Banda Principal", font=(styles.FONT_FAMILY, 12, "bold"), text_color=styles.COLOR_TEXT_MAIN).pack(pady=5)
        
        self.fig_rede = Figure(figsize=(3.5, 2.0), dpi=100, facecolor=styles.COLOR_CARD_BG)
        self.fig_rede.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax_rede = self.fig_rede.add_subplot(111, polar=True)
        self.canvas_rede = FigureCanvasTkAgg(self.fig_rede, master=frame_esq)
        self.canvas_rede.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        frame_dir = ctk.CTkFrame(sub, fg_color="transparent")
        frame_dir.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.lbl_rede_status = ctk.CTkLabel(frame_dir, text=system_tools.checar_rede_local(), font=(styles.FONT_FAMILY, 11, "italic"), text_color=styles.COLOR_TEXT_MUTED)
        self.lbl_rede_status.pack(pady=5)
        self.btn_speed = ctk.CTkButton(frame_dir, text="Executar Speedtest", height=40, fg_color=styles.COLOR_ACCENT, hover_color=styles.COLOR_ACCENT_HOVER, command=self.disparar_speedtest, font=styles.FONT_MENU_BUTTON)
        self.btn_speed.pack(pady=5)
        
        self.fig_gauge = Figure(figsize=(3.5, 1.5), dpi=100, facecolor=styles.COLOR_CARD_BG)
        self.fig_gauge.subplots_adjust(left=0, right=1, top=0.9, bottom=0, wspace=0.35)
        self.ax_g1 = self.fig_gauge.add_subplot(121, polar=True)
        self.ax_g2 = self.fig_gauge.add_subplot(122, polar=True)
        self.canvas_gauge = FigureCanvasTkAgg(self.fig_gauge, master=frame_dir)
        self.canvas_gauge.get_tk_widget().pack(fill="both", expand=True, pady=5)

        self.lbl_resultados = ctk.CTkLabel(frame_dir, text="Ping: -- ms  |  Jitter: -- ms", font=(styles.FONT_FAMILY, 11), text_color=styles.COLOR_TEXT_MAIN)
        self.lbl_resultados.pack(pady=2)
        
        self.desenhar_velocimetro_principal(0.0)
        self.desenhar_velocimetros_vazios()

    def disparar_speedtest(self):
        if self.testando_rede: return
        self.testando_rede = True
        self.btn_speed.configure(state="disabled", text="Medindo...")
        self.desenhar_velocimetro_principal(0.0)
        self.desenhar_velocimetros_vazios()
        self.canvas_rede.draw_idle()
        self.canvas_gauge.draw_idle()
        
        self.v_atual_sub_thread = 0.0
        threading.Thread(target=self._worker_animacao_grafico, daemon=True).start()

        def fim_cb(down, up, erro=False):
            self.testando_rede = False
            self.v_atual_sub_thread = down
            def att_ui():
                self.btn_speed.configure(state="normal", text="Executar Speedtest")
                if not erro:
                    self._renderizar_gauges_finais(down, up)
                    self.atualizar_log(f"[Speedtest] Down: {down:.2f} Mbps | Up: {up:.2f} Mbps\n")
            self.after(0, att_ui)

        system_tools.executar_speedtest(
            lambda: self.testando_rede, self.atualizar_log, 
            lambda v: setattr(self, 'v_atual_sub_thread', v), 
            lambda txt: self.after(0, lambda: self.lbl_resultados.configure(text=txt)), 
            fim_cb
        )

    def _worker_animacao_grafico(self):
        while self.testando_rede:
            self.after(0, lambda: (self.desenhar_velocimetro_principal(self.v_atual_sub_thread), self.canvas_rede.draw_idle()))
            time.sleep(0.15)

    def desenhar_velocimetro_principal(self, valor):
        self.ax_rede.clear()
        self.ax_rede.set_facecolor('none')
        self.ax_rede.set_theta_zero_location("W")
        self.ax_rede.set_theta_direction(-1)
        self.ax_rede.set_thetamin(0)
        self.ax_rede.set_thetamax(180)
        
        limite = 1000 if valor > 100 else 100
        ang = (min(valor, limite) / limite) * np.pi
        self.ax_rede.bar(np.linspace(0, np.pi, 100), [1]*100, width=np.pi/100, bottom=2.0, color=styles.COLOR_GRAPH_EMPTY, edgecolor=styles.COLOR_GRAPH_EMPTY, align='edge')
        if ang > 0: 
            self.ax_rede.bar(np.linspace(0, ang, 100), [1]*100, width=ang/100, bottom=2.0, color=styles.COLOR_ACCENT, edgecolor=styles.COLOR_ACCENT, align='edge')
        
        self.ax_rede.annotate('', xy=(ang, 2.9), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="#FFFFFF", lw=3, mutation_scale=8))
        self.ax_rede.plot(0, 0, color="#FFFFFF", marker='o', markersize=8)
        self.ax_rede.text(np.pi/2, -0.4, f"{valor:.1f}", ha='center', va='center', color='white', fontname=styles.FONT_FAMILY, fontsize=18, weight='bold')
        self.ax_rede.grid(False)
        self.ax_rede.set_xticks([])
        self.ax_rede.set_yticks([])
        self.ax_rede.set_ylim(-1.5, 3.8)
        self.ax_rede.spines['polar'].set_visible(False)

    def desenhar_velocimetros_vazios(self):
        for ax, titulo in zip([self.ax_g1, self.ax_g2], ["DOWNLOAD", "UPLOAD"]):
            ax.clear()
            ax.set_facecolor('none')
            ax.set_theta_zero_location("W")
            ax.set_theta_direction(-1)
            ax.set_thetamin(0)
            ax.set_thetamax(180)
            ax.bar(np.linspace(0, np.pi, 100), [1]*100, width=np.pi/100, bottom=2.0, color=styles.COLOR_GRAPH_EMPTY, edgecolor=styles.COLOR_GRAPH_EMPTY, align='edge')
            ax.text(np.pi/2, -0.4, "0.0", ha='center', va='center', color='white', fontname=styles.FONT_FAMILY, fontsize=13, weight='bold')
            ax.text(np.pi/2, -1.5, titulo, ha='center', va='center', color=styles.COLOR_TEXT_MUTED, fontname=styles.FONT_FAMILY, fontsize=8, weight='bold')
            ax.grid(False)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_ylim(-1.8, 3.8)
            ax.spines['polar'].set_visible(False)

    def _renderizar_gauges_finais(self, down, up):
        self.desenhar_velocimetro_principal(down)
        self.canvas_rede.draw_idle()
        for ax, valor, cor, label in zip([self.ax_g1, self.ax_g2], [down, up], [styles.COLOR_GRAPH_DOWN, styles.COLOR_GRAPH_UP], ["DOWNLOAD", "UPLOAD"]):
            ax.clear()
            ax.set_facecolor('none')
            ax.set_theta_zero_location("W")
            ax.set_theta_direction(-1)
            ax.set_thetamin(0)
            ax.set_thetamax(180)
            
            escala = 1000 if max(down, up) > 100 else 100
            ang = (min(max(valor, 0), escala) / escala) * np.pi
            ax.bar(np.linspace(0, np.pi, 100), [1]*100, width=np.pi/100, bottom=2.0, color=styles.COLOR_GRAPH_EMPTY, edgecolor=styles.COLOR_GRAPH_EMPTY, align='edge')
            if ang > 0: 
                ax.bar(np.linspace(0, ang, 100), [1]*100, width=ang/100, bottom=2.0, color=cor, edgecolor=cor, align='edge')
            
            ax.annotate('', xy=(ang, 2.9), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="#FFFFFF", lw=2.5, mutation_scale=6))
            ax.plot(0, 0, color="#FFFFFF", marker='o', markersize=6)
            ax.text(np.pi/2, -0.4, f"{valor:.1f}", ha='center', va='center', color='white', fontname=styles.FONT_FAMILY, fontsize=13, weight='bold')
            ax.text(np.pi/2, -1.5, f"{label} Mbps", ha='center', va='center', color=cor, fontname=styles.FONT_FAMILY, fontsize=8, weight='bold')
            ax.grid(False)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_ylim(-1.8, 3.8)
            ax.spines['polar'].set_visible(False)
        self.canvas_gauge.draw_idle()

if __name__ == "__main__":
    app = OptimizerApp()
    app.mainloop()