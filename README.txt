===============================================================================
  _______ _____ __  __ ______ _____    _______ _____ __  __ ______ _____  
 |__   __|_   _|  \/  |  ____|  __ \  |__   __|_   _|  \/  |  ____|  __ \ 
    | |    | | | \  / | |__  | |__) |    | |    | | | \  / | |__  | |__) |
    | |    | | | |\/| |  __| |  _  /     | |    | | | |\/| |  __| |  _  / 
    | |   _| |_| |  | | |____| | \ \     | |   _| |_| |  | | |____| | \ \ 
    |_|  |_____|_|  |_|______|_|  \_\    |_|  |_____|_|  |_|______|_|  \_\
                                                                          
                                                                           
                                                                                
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
.csv.


-------------------------------------------------------------------------------
2. REQUISITOS DE SISTEMA E DEPENDÊNCIAS
-------------------------------------------------------------------------------
- Python 3.8 ou superior
- Biblioteca PySerial
  Instalação via terminal:
    pip install pyserial

- Tkinter (Geralmente incluído no Python para Windows/macOS. No Linux, instale 
  via: sudo apt install python3-tkinter)


-------------------------------------------------------------------------------
3. GUIA DE USO
-------------------------------------------------------------------------------
1. Conecte o Arduino à porta USB do computador.
2. Execute o script principal pelo terminal:
     python python.py

3. Seleção de Porta Serial:
   - O sistema tenta detectar a porta do Arduino automaticamente.
   - Caso existam múltiplas portas (ou nenhuma identificada), escolha o número 
     da porta correspondente no menu do terminal.

4. Operação pela Interface Gráfica (GUI):
   - Leitura de Status (ON/OFF): Indica em tempo real o estado do pino de 
     medição (GTR).
   - Botão [Enable / Disable]: Alterna a porta entre Enabled (Habilitada,
     realiza leituras) e Disabled (Desabilitada).
   - Botão [Reset]: Registra um ponto de reset no arquivo e limpa os dados da 
     amostragem atual.
     * NOTA: O botão [Reset] fica desativado (cinza) se a porta estiver 
       Desabilitada (Disabled).
	 * NOTA: Os comandos de [Enable / Disable] e [Reset] também podem ser
	   acionados pelos botões da caixa (vide orientações abaixo).


-------------------------------------------------------------------------------
4. ESTRUTURA DE DIRETÓRIOS E ARQUIVOS
-------------------------------------------------------------------------------
O software cria e gerencia automaticamente a seguinte estrutura de pastas:

  <Diretório do Projeto>/
  │
  ├── data/                  Guarda os pacotes binários brutos (.bin)
  │
  └── medicoes/              Histórico e exportação dos dados (.csv)
      └── .temp/             Arquivos de backup salvos a cada leitura (.csv)


-------------------------------------------------------------------------------
5. FORMATO DOS DADOS SALVOS (.CSV)
-------------------------------------------------------------------------------
Cada arquivo .csv gerado na pasta de medições possui o seguinte formato:

  Linha 1: Tempos decorridos (em segundos) em relação à primeira leitura.
  Linha 2: Registros de eventos ("LIGADO", "On", "Off", "RESET").


-------------------------------------------------------------------------------
6. INTERAÇÃO VIA BOTÃO FÍSICO (DISPOSITIVO)
-------------------------------------------------------------------------------
O sistema também responde ao pressionamento do botão físico (pino SWT):
- Manter pressionado por 0.2 segundo  -> Habilita (Enable) ou Reseta (Reset).
- Manter pressionado por 1 segundo    -> Desabilita (Disable).

===============================================================================