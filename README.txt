
======================================================================
         OPTIMIZER 1.0 — FERRAMENTA DE DIAGNÓSTICO E MANUTENÇÃO
======================================================================
Desenvolvido por: Gabriel Melo
Versão: 1.0 (2026)
Ambiente Alvo: Windows 10 / Windows 11 / Windows Server
======================================================================

O Optimizer 1.0 é um utilitário centralizado de TI desenvolvido em 
Python para otimização de sistema, monitoramento de infraestrutura,
diagnóstico de integridade e automação de deploys de software.

----------------------------------------------------------------------
ℹ️ REQUISITOS DE EXECUÇÃO (LEIA ANTES DE RODAR)
----------------------------------------------------------------------

1. PRIVILÉGIOS ADMINISTRATIVOS:
   O aplicativo executa alterações em chaves de registro do sistema, 
   manipula serviços nativos e dispara ferramentas profundas (como SFC 
   e DISM). Por isso, ele DEVE ser executado como Administrador.
   Se o sistema solicitar permissão do UAC, clique em "Sim".

2. CONEXÃO COM A INTERNET:
   Essencial para o funcionamento pleno das abas:
   - "Rede": Para realizar o Speedtest de banda em tempo real.
   - "Instaladores": Para baixar e instalar os pacotes oficiais.

3. SUPORTE AO WINGET:
   A aba de instaladores e atualização de drivers utiliza o motor nativo
   do Windows (Winget). Certifique-se de que o Gerenciador de Pacotes
   do Windows está ativo e atualizado na máquina operacional alvo.

----------------------------------------------------------------------
⚡ RECURSOS DISPONÍVEIS
----------------------------------------------------------------------

• Dashboard: Monitoramento gráfico em tempo real de CPU, RAM e Disco (C:).
• Otimizações: Perfil de desempenho máximo, desligamento de telemetria
  e motor dinâmico de limpeza de arquivos temporários e caches.
• Diagnóstico: Varredura sfc/dism, mapeamento de erros críticos do 
  Event Viewer e update de drivers via Winget com logs no console.
• Ferramentas Admin: Atalhos rápidos para consoles nativos (.msc).
• Central CMD: Atalhos automatizados para comandos de rede e disco.
• Instaladores: Instalação silenciosa de softwares utilitários padrões 
  corporativos (Chrome, WinRAR, AnyDesk, Revo, etc.).
• Rede: Velocímetro de banda com leitura do adaptador local/Wi-Fi.

----------------------------------------------------------------------
⚠️ ALERTA SOBRE FALSOS POSITIVOS (ANTIVÍRUS)
----------------------------------------------------------------------

Por ser uma ferramenta de administração de TI compilada de forma 
independente, alguns antivírus (como o Windows Defender) podem gerar 
alertas de "Falso Positivo" (geralmente rotulados como heurística ou 
Unwanted Application). 

Isso ocorre porque o Optimizer interage diretamente com o Prompt de 
Comando, desliga telemetria e gerencia processos em background. O código 
é 100% limpo, seguro e focado exclusivamente em manutenção. Se o seu 
antivírus bloquear o app, adicione o executável à lista de exceções.

----------------------------------------------------------------------
TERMO DE USO: Esta ferramenta foi desenvolvida para facilitar rotinas 
técnicas de suporte e infraestrutura. Certifique-se de que não há 
processos críticos abertos ou atualizações de sistema pendentes ao 
rodar rotinas de reparo profundo (SFC/DISM).
======================================================================