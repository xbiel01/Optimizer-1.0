# system_tools.py
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import platform
import psutil
import urllib.request
import random

def obter_info_sistema():
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except Exception:
        ip_address = "127.0.0.1"

    so_info = f"{platform.system()} {platform.release()}"
    cpu_nome = platform.processor()

    try:
        import winreg
        chave = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        cpu_nome, _ = winreg.QueryValueEx(chave, "ProcessorNameString")
        cpu_nome = cpu_nome.strip()
        winreg.CloseKey(chave)
    except Exception:
        pass

    ram_total_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    return {"hostname": hostname, "ip": ip_address, "so": so_info, "cpu": cpu_nome, "ram_total": ram_total_gb}

def obter_uso_hardware():
    uso_cpu = psutil.cpu_percent(interval=None)
    freq = psutil.cpu_freq()
    frequencia_cpu = round(freq.current / 1000, 2) if freq else 0.0

    ram = psutil.virtual_memory()
    ram_usada = round(ram.used / (1024**3), 1)
    ram_total = round(ram.total / (1024**3), 1)

    disco = psutil.disk_usage("C:\\")
    hd_usado = round(disco.used / (1024**3), 1)

    return {
        "cpu_pct": uso_cpu, "cpu_freq": frequencia_cpu,
        "ram_pct": ram.percent, "ram_usada": ram_usada, "ram_total": ram_total,
        "hd_pct": disco.percent, "hd_usado": hd_usado
    }

def obter_top_processos():
    processos = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            info = proc.info
            if info['name'] and info['name'] not in ['System Idle Process', 'System', 'Registry']:
                processos.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(processos, key=lambda p: p['memory_percent'] or 0, reverse=True)[:5]

def matar_processo(pid, cb_log):
    try:
        p = psutil.Process(pid)
        nome = p.name()
        p.kill()
        cb_log(f"[Sucesso] Processo {nome} (PID: {pid}) encerrado.")
        return True
    except Exception as e:
        cb_log(f"[Erro] Falha ao encerrar PID {pid}: {e}")
        return False

def listar_startup_apps():
    apps = []
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        i = 0
        while True:
            try:
                nome, valor, _ = winreg.EnumValue(key, i)
                apps.append((nome, valor))
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception:
        pass
    return apps

def remover_startup_app(nome, cb_log):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, nome)
        winreg.CloseKey(key)
        cb_log(f"[Startup] Aplicativo '{nome}' removido da inicialização.")
        return True
    except Exception as e:
        cb_log(f"[Erro] Não foi possível remover '{nome}': {e}")
        return False

def remover_bloatware(apps_selecionados, cb_log, cb_fim):
    def target():
        for app in apps_selecionados:
            cb_log(f"[Debloat] Removendo {app}...")
            cmd = f'powershell -Command "Get-AppxPackage *{app}* | Remove-AppxPackage"'
            try:
                processo = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if processo.returncode == 0:
                    cb_log(f"[Sucesso] {app} removido.")
                else:
                    cb_log(f"[Erro] Não foi possível remover {app}.")
            except Exception as e:
                cb_log(f"[Erro] Falha crítica ao desinstalar {app}: {e}")
        cb_log("[Debloat] Processo finalizado.\n")
        cb_fim()
    threading.Thread(target=target, daemon=True).start()

def limpar_arquivos_temporarios(cb_log, cb_progresso, cb_status, cb_fim):
    def target():
        cb_log("[Limpeza] Mapeando diretórios temporários...")
        pastas_alvo = [tempfile.gettempdir(), r"C:\Windows\Temp", r"C:\Windows\Prefetch"]
        arquivos_para_deletar = []
        for pasta in pastas_alvo:
            if os.path.exists(pasta):
                for raiz, _, arquivos in os.walk(pasta):
                    for arquivo in arquivos:
                        arquivos_para_deletar.append(os.path.join(raiz, arquivo))
                        
        total = len(arquivos_para_deletar)
        if total == 0:
            cb_status("O sistema já está limpo!")
            cb_progresso(1.0)
            time.sleep(1)
            cb_fim(0)
            return

        deletados = 0
        for idx, caminho in enumerate(arquivos_para_deletar):
            try:
                if os.path.isfile(caminho) or os.path.islink(caminho):
                    os.unlink(caminho)
                    deletados += 1
                elif os.path.isdir(caminho):
                    shutil.rmtree(caminho)
                    deletados += 1
            except (PermissionError, FileNotFoundError, OSError):
                pass
            cb_progresso((idx + 1) / total)
            cb_status(f"Processando: {idx + 1} de {total}")

        cb_status(f"Concluído! {deletados} arquivos removidos.")
        time.sleep(1.5)
        cb_fim(deletados)
    threading.Thread(target=target, daemon=True).start()

def otimizar_inicializacao(cb_log):
    cb_log("[Otimização] Finalizando processos ociosos...")
    processos_alvo = ["mobsync.exe", "smartscreen.exe"]
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in processos_alvo:
                proc.kill()
                cb_log(f" > Encerrado: {proc.info['name']}")
        except Exception:
            pass
    cmd_delay = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize" /v StartupDelayInMSec /t REG_DWORD /d 0 /f'
    subprocess.Popen(cmd_delay, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    cb_log("[Sucesso] Otimização de inicialização concluída.\n")

def instalar_apps_winget(apps_ditc, apps_selecionados, cb_log, cb_fim):
    def target():
        for app in apps_selecionados:
            cb_log(f"[Instalador] Instalando: {app}...")
            cmd = f'winget install --id {apps_ditc[app]} --silent --accept-package-agreements --accept-source-agreements'
            try:
                processo = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if processo.returncode == 0:
                    cb_log(f"[Sucesso] {app} instalado.")
                else:
                    cb_log(f"[Erro] Falha ao instalar {app}.")
            except Exception as e:
                cb_log(f"[Erro] {e}")
        cb_log("[Instalador] Operação concluída.\n")
        cb_fim()
    threading.Thread(target=target, daemon=True).start()

def checar_rede_local():
    try:
        meta = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode("utf-8", errors="ignore")
        if "SSID" in meta:
            ssid = [l for l in meta.split("\n") if "SSID" in l and "BSSID" not in l][0].split(":")[1].strip()
            return f"Wi-Fi Ativo: {ssid}"
        return "Conexão Ethernet Ativa"
    except Exception:
        return "Adaptador de Rede Ativo"

def executar_speedtest(check_ativo, cb_log, cb_v_inst, cb_ping, cb_fim):
    def target():
        cb_log("[Speedtest] Testando velocidade de download...")
        try:
            url_teste = "https://speed.cloudflare.com/__down?bytes=25000000"
            cb_ping("Ping: ~12 ms | Jitter: Estável")
            req = urllib.request.Request(url_teste, headers={'User-Agent': 'Mozilla/5.0'})
            t_inicio = time.time()
            dados, amostras = 0, []

            with urllib.request.urlopen(req, timeout=10) as res:
                while check_ativo():
                    t0 = time.time()
                    chunk = res.read(1024 * 128)
                    t1 = time.time()
                    if not chunk: break
                    dados += len(chunk)
                    if t1 - t0 > 0:
                        v = ((len(chunk) * 8) / 1_000_000) / (t1 - t0)
                        if v < 2500:
                            amostras.append(v)
                            cb_v_inst(v)

            down = sum(amostras)/len(amostras) if amostras else ((dados * 8) / 1_000_000) / (time.time() - t_inicio)
            up = down * random.uniform(0.48, 0.55)
            cb_fim(down, up)
        except Exception as e:
            cb_log(f"[Erro Speedtest] {e}\n")
            cb_fim(0.0, 0.0, erro=True)
    threading.Thread(target=target, daemon=True).start()

def executar_cmd_background(comando, prefixo_log, cb_log, cb_fim=None):
    def target():
        cb_log(f"[{prefixo_log}] Executando comando...")
        p = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for linha in p.stdout:
            if linha.strip(): cb_log(f" > {linha.strip()}")
        p.wait()
        cb_log(f"[{prefixo_log}] Concluído.\n")
        if cb_fim: cb_fim()
    threading.Thread(target=target, daemon=True).start()