# Campo Minado (Minesweeper) — Manual do Usuário

Um jogo Campo Minado (Minesweeper) em Python com interface gráfica (Tkinter).  
Este manual descreve como instalar, executar, configurar e jogar a aplicação, além de explicações sobre funcionalidades, estrutura de código e resolução de problemas.

Índice
- Introdução
- Requisitos
- Instalação e execução
- Visão geral da interface (GUI)
- Como jogar
- Configurações e opções
- Comportamentos especiais
- Estrutura do projeto / descrição dos arquivos
- Personalização e empacotamento
- Resolução de problemas (Troubleshooting)
- Perguntas frequentes (FAQ)
- Créditos

---

## Introdução
Campo Minado - ChatDev é uma implementação do clássico jogo Campo Minado com:
- Configuração do número de linhas, colunas e bombas.
- Escolha de dificuldade (Easy / Medium / Hard) que sugere quantidade de bombas e define se o primeiro clique é seguro.
- Interface com botões em grade, timer, contador de bombas restantes, reiniciar e voltar às configurações.
- Suporte a tabuleiros grandes através de canvas com barras de rolagem.
- Recursos de usabilidade: sinalizadores (flags), flood-fill em células vazias, "chording" ao clicar em célula revelada cujo número corresponde às flags ao redor.

---

## Requisitos

- Python 3.8+ (recomendado 3.8–3.12).
- Tkinter (incluído na maioria das distribuições Python, mas separado em alguns sistemas).
- Sistema operacional: Windows, macOS, Linux (compatível, desde que Tk esteja instalado).

Observações:
- Não há dependências externas via pip para a versão fornecida; usa apenas a biblioteca padrão (tkinter).
- Em algumas instalações Linux, é necessário instalar pacote extra (p.ex. python3-tk).

---

## Como instalar e executar

1. Clone ou faça download do repositório com os arquivos:
   - main.py
   - gui.py
   - game.py
   - config.py

2. (Opcional) Crie um ambiente virtual:
   - Unix/macOS:
     python3 -m venv venv
     source venv/bin/activate
   - Windows:
     python -m venv venv
     venv\Scripts\activate

3. Instale Tk (se necessário):
   - Debian/Ubuntu:
     sudo apt update
     sudo apt install python3-tk
   - Fedora:
     sudo dnf install python3-tkinter
   - Arch:
     sudo pacman -S tk
   - macOS:
     - Python distribuído pelo Homebrew geralmente já traz Tk compatível. Caso haja problemas, instale a versão oficial do Tcl/Tk ou use o Python do instalador oficial que inclui Tk.
   - Windows:
     - Normalmente Tk vem com o instalador oficial do Python.

4. Execute a aplicação:
   - No diretório que contém os arquivos:
     python main.py

   A janela do jogo será aberta.

---

## Visão geral da interface (GUI)

Tela inicial (Start Screen)
- Linhas: spinbox para escolher número de linhas (5–30).
- Colunas: spinbox para escolher número de colunas (5–30).
- Bombas: spinbox para escolher número de bombas (1 até linhas*colunas - 1).
  - O valor sugerido para bombas é atualizado quando se escolhe uma dificuldade, mas se você editar manualmente o campo Bombas, sua escolha permanece (não é sobrescrita pela seleção de dificuldade).
- Dificuldade: combobox com presets ("Easy", "Medium", "Hard").
  - Cada preset possui uma fração sugerida de bombas e um parâmetro first_click_safe (garantia de que o primeiro clique não explode).
- Botões:
  - Iniciar: inicializa o jogo com as configurações escolhidas.
  - Sair: fecha o aplicativo.
- Informações: mensagens de status e validações sobre tamanho do tabuleiro.

Tela de jogo (Game Screen)
- Contadores no topo:
  - Bombas restantes: mostra bombas totais menos flags usadas.
  - Tempo: timer em segundos desde o primeiro clique.
  - Reiniciar: reinicia o mesmo jogo com as mesmas configurações.
  - Voltar: volta à tela de configurações (perde o estado atual).
- Tabuleiro:
  - Botões representando as células (grade).
  - Canvas com barras de rolagem para suportar tabuleiros grandes.

---

## Como jogar (regras e controles)

Regras básicas:
- Objetivo: revelar todas as células sem bombas. Ganha-se quando todas as células não-mina forem reveladas.
- Se você revelar uma mina, perde o jogo.
- Números indicam quantas minas estão nas 8 células vizinhas.
- Células sem número (0) abrem automaticamente uma região (flood-fill).

Controles:
- Clique esquerdo (Button-1): revelar a célula.
  - Se for o primeiro clique e a opção "first_click_safe" estiver ativa, as minas são colocadas garantindo que a primeira célula e suas vizinhas fiquem seguras.
  - Se você clicar em célula já revelada, há suporte a "chording": se o número da célula for igual às flags vizinhas, o jogo irá revelar as células vizinhas não marcadas (padrão do Minesweeper).
- Clique direito (Button-3) ou botão do meio (Button-2): alternar flag (sinalizador) na célula.
- Timer: começa no primeiro clique do jogador.
- Reiniciar: cria novo Minefield com as mesmas configurações (linhas/colunas/bombas/first_click_safe) e reseta o timer e a grade.
- Voltar: retorna à tela de configuração, permitindo ajustar linhas/colunas/bombas/dificuldade.

Indicadores visuais:
- Células não-reveladas aparecem como botões levantados.
- Células reveladas ficam "afundadas" (sunken) e desativadas.
- Flags aparecem como emoji 🚩 (ou texto fallback "F" caso o ambiente não suporte emoji).
- Minas aparecem como emoji 💣 (ou "B" como fallback).
- Célula explodida é destacada (emoji 💥 ou "X" como fallback).
- Cores para números são usadas quando suportado.

Limites do tabuleiro:
- Linhas e colunas: mínimo 5 e máximo 30.
- Bombas: mínimo 1 e máximo (linhas*colunas - 1).

---

## Configurações e opções de dificuldade

Arquivo de configuração: config.py

Presets:
- Easy:
  - suggest_fraction: 0.10 (10% de bombas sugerido)
  - first_click_safe: True
- Medium:
  - suggest_fraction: 0.15
  - first_click_safe: True
- Hard:
  - suggest_fraction: 0.25
  - first_click_safe: False (primeiro clique não necessariamente seguro)

Comportamento:
- Ao selecionar dificuldade, a aplicação sugere automaticamente um número de bombas com base nos valores de linhas e colunas.
- Se você modificar manualmente o campo Bombas (spinbox), esta escolha não será substituída automaticamente ao mudar de dificuldade — isto permite controle manual. Entretanto, mudanças que resultem em valores inválidos para o tamanho do tabuleiro serão automaticamente ajustadas (por exemplo, excedendo máximo permitido).

---

## Comportamentos especiais e detalhes de usabilidade

- Scrollável: o tabuleiro é colocado dentro de um Canvas com scrollbars para que tabuleiros grandes (p.ex. 30x30) possam ser navegados mesmo em telas pequenas.
- Segurança do primeiro clique: se ativada (nas dificuldades Easy e Medium por padrão), as minas são colocadas apenas no primeiro reveal, evitando o primeiro clique cair em mina. O algoritmo tenta também proteger as células vizinhas do primeiro clique.
- Flags e contador: o rótulo "Bombas restantes" mostra quantas flags ainda podem ser usadas (bombas totais menos flags ativas). Esse contador não impede marcar a mais, mas o valor exibido é o restante (não negativo).
- Emojis e fallbacks: em alguns ambientes Tk, emoji ou cores hex podem causar erro. O GUI contém fallback seguro que exibe texto simples (B, F, X) e cores padrão quando necessário.
- Reiniciar: recria o campo com as mesmas configurações e reinicia timer/estado.

---

## Estrutura do projeto / descrição dos arquivos

- main.py
  - Ponto de entrada. Inicializa a raiz Tk e instancia MinesweeperGUI.

- gui.py
  - Implementa a interface gráfica com Tkinter (MinesweeperGUI).
  - Principais responsabilidades:
    - Tela inicial de configuração.
    - Criação da grade de botões dentro de Canvas com barras de rolagem.
    - Tratar cliques esquerdo/direito, timer, exibição de flags/minas/números.
    - Fallbacks gráficos para ambientes que não suportam certos recursos.
  - Variáveis visuais e mapeamento de cores/emoji definidos no topo deste arquivo.

- game.py
  - Lógica do jogo (Minefield).
  - Gerenciamento de minas, contagem de vizinhos, revelação (inclui flood-fill), flags, verificação de vitória/perda.
  - Suporta colocar minas no primeiro clique (first_click_safe).

- config.py
  - Presets de dificuldade (fração sugerida de bombas e first_click_safe).
  - Modifique aqui para adicionar ou ajustar dificuldades.

---

## Personalização / desenvolvimento

Algumas coisas que você pode querer ajustar:

- Ajustar limites de linhas/colunas:
  - Em gui.py, alterar valores `from_` e `to` nas Spinboxes e as validações.
- Alterar cores e emojis:
  - Em gui.py, no bloco de constantes (NUM_COLOR_MAP, BOMB_EMOJI, etc).
- Adicionar novas dificuldades:
  - Em config.py, adicionar novas chaves ao dicionário DIFFICULTY_PRESETS.
- Adicionar teclas de atalho:
  - Pode-se ligar eventos de teclado ao root (bind) para ações como reiniciar (por exemplo, tecla R), alternar flags via teclado, etc.
- Empacotar em executável:
  - PyInstaller:
    pip install pyinstaller
    pyinstaller --onefile main.py
  - Note que aplicações Tk exigem tratamento de recursos adicionais; teste o binário em sistema alvo.

---

## Resolução de problemas (Troubleshooting)

1. A janela não abre / erro ao importar tkinter:
   - No Linux, instale python3-tk (Debian/Ubuntu):
     sudo apt install python3-tk
   - No Fedora:
     sudo dnf install python3-tkinter
   - Reinicie o terminal/IDE após instalação.

2. Emojis (💣, 🚩, 💥) aparecem como quadrados ou geram erro:
   - O programa já contém fallbacks que trocam emojis por textos (B, F, X). Se ainda houver problemas gráficos, verifique a fonte padrão do Tk. Em última instância, edite constantes em gui.py e force texto simples.

3. Exceções de configuração de cor (TclError) em alguns ambientes:
   - O GUI tenta configurar estilos de cores usando hex codes e usa blocos try/except com fallback para nomes de cores padrão. Se ocorrerem erros persistentes, ajuste as constantes de cor em gui.py para cores como "white", "black", "red".

4. Tabuleiro muito grande / botões minúsculos / desempenho:
   - O código usa botões Tk por célula. Para tabuleiros muito grandes, o número de widgets pode afetar desempenho. Para otimizar, considere:
     - Reduzir o tamanho máximo do tabuleiro.
     - Usar canvas desenhando retângulos em vez de botões.
     - Limitar atualizações visuais frequentes.

5. Ao reiniciar, o timer não reinicia:
   - O botão Reiniciar recria o Minefield e reseta o timer. Se algo ficar preso, feche e reabra o jogo. Verifique se há múltiplos jobs agendados com `after`; o código cancela jobs anteriores.

---

## FAQ

- Posso jogar apenas com teclado?
  - Atualmente não — o controle principal é por mouse (esquerdo/direito/centro). É possível adicionar bindings de teclado no gui.py.

- Como garantir que o primeiro clique nunca exploda?
  - Use dificuldades com first_click_safe = True (Easy, Medium por padrão). Isso faz com que minas sejam colocadas apenas no primeiro reveal e evite a célula inicial e suas vizinhas.

- Posso aumentar tabuleiro acima de 30x30?
  - Os limites foram definidos para segurança e usabilidade (5–30). Você pode alterar esses limites no gui.py (Spinbox `from_` e `to`) e nas validações.

---

## Boas práticas para desenvolvedores

- Separação de responsabilidades:
  - game.py cuida da lógica; gui.py cuida da apresentação. Para mudanças na lógica do jogo, prefira modificar game.py e manter a GUI sem acoplamento profundo.
- Testes:
  - Você pode escrever testes unitários para o Minefield (revelação, contagem, is_won, toggle_flag, place_mines) usando pytest ou unittest.
- Internacionalização:
  - Atualmente strings estão em Português; para suportar múltiplos idiomas, extraia textos para um módulo de recursos.

---

## Créditos
Aplicação desenvolvida por ChatDev (multi-agente). Componentes:
- GUI: gui.py (Tkinter)
- Lógica: game.py
- Config: config.py
- Entrada: main.py

---

Se quiser, eu posso:
- Gerar um instalador (PyInstaller) passo-a-passo para seu SO.
- Fazer um build otimizado (substituir botões por desenho em Canvas para melhorar desempenho em tabuleiros grandes).
- Adicionar atalhos de teclado, som, ou salvar placares (high-scores).

Deseja que eu gere um script PyInstaller ou um README simplificado com os comandos exatos para empacotar em .exe/.app?