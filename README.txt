===============================================================================
  _______ _____ __  __ ______ _____     _______ _____ __  __ ______ _____  
 |__   __|_   _|  \/  |  ____|  __ \   |__   __|_   _|  \/  |  ____|  __ \ 
    | |    | | | \  / | |__  | |__) |     | |    | | | \  / | |__  | |__) |
    | |    | | | |\/| |  __| |  _  /      | |    | | | |\/| |  __| |  _  / 
    | |   _| |_| |  | | |____| | \ \      | |   _| |_| |  | | |____| | \ \ 
    |_|  |_____|_|  |_|______|_|  \_\     |_|  |_____|_|  |_|______|_|  \_\
                                                                           

                             >> TIMER TIMER <<
        "Um protótipo Arduino+Python para medição de tempos de timers"
===============================================================================

-------------------------------------------------------------------------------
1. VISÃO GERAL
-------------------------------------------------------------------------------
Interface Gráfica (GUI) em Python para monitoramento e controle em tempo real 
de 20 portas de leitura serial conectadas via Arduino.

O sistema processa pacotes binários recebidos via Serial, gerencia o estado 
das portas através de uma máquina de estados (aceitando comandos pela GUI ou 
pelo botão físico do dispositivo) e salva o histórico de medições em arquivos 
.csv e .xlsx.


-------------------------------------------------------------------------------
2. REQUISITOS DE SISTEMA E DEPENDÊNCIAS
-------------------------------------------------------------------------------
Para execução com .exe:
  - Nenhum

Para execução com .py e/ou atualização do código do Arduino:
  - Python 3.8 ou superior
  - Biblioteca PySerial
  - Tkinter (Geralmente incluído no Python para Windows/macOS. No Linux, instale 
    via: sudo apt install python3-tkinter)
  - Arduino IDE


-------------------------------------------------------------------------------
3. GUIA DE USO
-------------------------------------------------------------------------------
1. Conecte o Arduino à porta USB do computador.
2. Execute o programa "TimerTimer.exe" (na pasta "dist").

   2.1. Seleção de Porta Serial:
        - O sistema tenta detectar a porta do Arduino automaticamente.
        - Caso existam múltiplas portas (ou nenhuma identificada), escolha o 
          número da porta correspondente no menu do terminal.

   2.2. Operação pela Interface Gráfica (GUI):
        - Leitura de Status (ON/OFF): Indica em tempo real o estado do pino de 
          medição (GTR).
        - Botão [Enable / Disable]: Alterna a porta entre Enabled (Habilitada, 
          realiza leituras) e Disabled (Desabilitada).
        - Botão [Reset]: Registra um ponto de reset no arquivo e limpa os 
          dados da amostragem atual.
          * NOTA: O botão [Reset] fica desativado (cinza) se a porta estiver 
            Desabilitada (Disabled).
          * NOTA: Os comandos de [Enable / Disable] e [Reset] também podem ser 
            acionados pelos botões físicos da caixa (vide seção 7).


-------------------------------------------------------------------------------
4. ESTRUTURA DE DIRETÓRIOS E ARQUIVOS
-------------------------------------------------------------------------------
1. O software cria e gerencia automaticamente a seguinte estrutura de pastas:

  <Diretório do Projeto>/
  │
  ├── data/                  Guarda os pacotes binários brutos (.bin)
  │
  └── medicoes/              Histórico e exportação dos dados (.xlsx)
      └── .temp/             Arquivos de backup salvos a cada leitura (.csv)

2. Os arquivos são salvos da seguinte forma:
   - Arquivos são salvos nas pastas /data/ e /medicoes/.temp/ a cada pacote 
     do Arduino (a cada 0.1s), para as portas que estão Habilitadas.
   - Arquivos são salvos na pasta /medicoes/ sempre que uma porta é Resetada 
     ou Desligada.
   * NOTA: Portas Desabilitadas não salvam arquivos.


-------------------------------------------------------------------------------
5. FORMATO DOS DADOS SALVOS (.CSV ou .XLSX)
-------------------------------------------------------------------------------
Cada arquivo .csv ou .xlsx gerado possui o seguinte formato:

  Linha 1: Tempos decorridos (em segundos) em relação à primeira leitura.
  Linha 2: Registros de eventos ("LIGADO", "On", "Off", "RESET").


-------------------------------------------------------------------------------
6. ESTRUTURA DE NOMENCLATURA DOS ARQUIVOS
-------------------------------------------------------------------------------
1. Os arquivos .csv e .xlsx seguem a convenção de nomenclatura:
   port-N--YYYY-MM-DD--HHhMMmSSs, onde:

     N:          Número da porta.
     YYYY-MM-DD: Ano-Mês-Dia.
     HHhMMmSSs:  Hora-Minuto-Segundo.

   * NOTA: O instante refere-se ao momento em que a porta foi Resetada.
   * NOTA: Arquivos .csv (na pasta /medicoes/.temp/) são salvos com décimos de 
     segundo; arquivos .xlsx (em /medicoes/) são salvos com segundos cheios.

2. Os arquivos .bin são salvos conforme o tempo Unix em milissegundos do 
   momento de recebimento do pacote binário.


-------------------------------------------------------------------------------
7. INTERAÇÃO VIA BOTÃO FÍSICO (DISPOSITIVO)
-------------------------------------------------------------------------------
O sistema também responde ao pressionamento do botão físico (pino SWT):
  - Manter pressionado por 0.2 segundo  -> Habilita (Enable) ou Reseta (Reset).
  - Manter pressionado por 1.0 segundo  -> Desabilita (Disable).

===============================================================================