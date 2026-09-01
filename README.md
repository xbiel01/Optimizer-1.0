# Optimizer 1.0 🚀

O **Optimizer 1.0** é uma aplicação desktop desenvolvida em Python para otimização, manutenção, diagnóstico e gerenciamento de ambientes Windows. A ferramenta conta com interface gráfica moderna e responsiva (CustomTkinter), monitoramento de hardware em tempo real, gerenciador de processos, ferramentas de rede com teste de velocidade, desinstalador de *bloatwares*, instalador de softwares e utilitários de reparo do sistema.

---

## 🛠️ Pré-requisitos e Dependências

Para executar o projeto diretamente através do código-fonte (sem o executável compilado), é necessário ter o **Python 3.9+** instalado na máquina.

### 📦 Bibliotecas Python Necessárias

As seguintes bibliotecas de terceiros devem ser instaladas para ter acesso ao Optimizer:

| Biblioteca | Comando de Instalação | Finalidade no App |

| **CustomTkinter** | `pip install customtkinter` | Interface gráfica (GUI) moderna baseada em Tkinter |
| **Pillow (PIL)** | `pip install Pillow` | Manipulação e exibição de imagens e ícones PNG/ICO |
| **Matplotlib** | `pip install matplotlib` | Renderização dos gráficos circular e velocímetros |
| **NumPy** | `pip install numpy` | Cálculos matemáticos para geração dos gráficos vetoriais |
| **Psutil** | `pip install psutil` | Leitura de métricas do sistema (CPU, RAM, Disco e Processos) |
| **Speedtest-cli** | `pip install speedtest-cli` | Execução dos testes de velocidade de rede |

### ⚡ Comando Único para Instalação das Dependências

Você pode instalar todas as dependências rodando o seguinte comando no terminal (CMD ou PowerShell):

```bash
pip install customtkinter Pillow matplotlib numpy psutil speedtest-cli

