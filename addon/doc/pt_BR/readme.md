# Revisão de Colunas (Columns Review) #

* Autores: Alberto Buffolino, Łukasz Golonka, outros colaboradores
* Download [stable version][stable]
* Download [development version][dev]
* Compatibilidade com NVDA: 2017.3 e posterior

O Columns Review é um complemento para aprimorar a experiência do NVDA com
listas.

Seus recursos incluem:

* ações personalizáveis no cabeçalho e/ou no conteúdo da coluna (as ações
  disponíveis são ler, copiar, soletrar e mostrar no modo de navegação);
* capacidade de alternar entre colunas em intervalos de dez por dez;
* Gerenciamento simplificado do cabeçalho (cliques do mouse);
* leitura sob demanda da posição relativa do item atual (ou seja, item 7 de
  10);
* gestos personalizáveis com ou sem teclado numérico;
* Anúncio de “0 itens” quando a lista está vazia (infelizmente, não está
  funcionando nas pastas do Win8/10);
* diga todo o apoio;
* relatório dos itens selecionados (valor e nomes dos itens);
* pesquisa de lista (com seleção múltipla de itens, se marcada/suportada).

## Gestos

Default keys for columns, headers and position are NVDA+control, but you can
customize them from add-on settings (not "Input gestures" dialog!).

Note que seu teclado pode ter problemas para processar algumas combinações
de teclas, portanto, experimente todos os gestos adicionais e ajuste-os para
obter melhores resultados.

Consulte também as preferências de complemento para o modo de teclado
numérico, o layout do teclado (sem teclado numérico) e as quatro ações
disponíveis para colunas.

* NVDA+control+digits from 1 to 0 (keyboard mode) or from 1 to 9 (numpad
  mode): by default, read the chosen column if pressed once, copy it if
  pressed twice;
* NVDA+control+numpadMinus (numpad mode): like NVDA+control+0 in keyboard
  mode, read or copy the 10th, 20th, etc column;
* NVDA+control+- (keyboard mode, EN-US layout): in a list with 10+ columns,
  change interval and process columns from 11 to 20, from 21 to 30, and so
  on (change last char according to your layout, from settings);
* NVDA+control+numpadPlus (numpad mode): like previous command;
* NVDA+control+enter (numpadEnter in numpad mode): open header manager;
* NVDA+control+delete (numpadDelete no modo numpad): lê a posição relativa
  do item atual (ou seja, item 7 de 10);
* Setas e NVDA+tab (em uma lista vazia): repete a mensagem “0 itens”;
* NVDA+seta para baixo (layout de área de trabalho) ou NVDA+a (layout de
  laptop): iniciar dizer tudo (esse gesto depende do gesto original em
  “Gestos de entrada”/“Caret do sistema”);
* NVDA+shift+seta para cima (layout de desktop) ou NVDA+shift+s (layout de
  laptop): informa a quantidade e os nomes dos itens da lista atualmente
  selecionados (como o comando anterior para personalização);
* NVDA+control+f: abre a caixa de diálogo localizar (não personalizável);
* NVDA+f3: localiza a próxima ocorrência do texto inserido anteriormente
  (não personalizável);
* NVDA+shift+f3: localiza a ocorrência anterior (não personalizável).

## Suporte

Esse complemento fornece um suporte geral para listas mais comuns (veja
abaixo) e alguns aplicativos específicos. O autor principal (Alberto
Buffolino) não pode garantir a compatibilidade/funcionalidade dos
aplicativos que ele não usa, como o Outlook e o Windows Mail, mas ficará
feliz em colaborar com seus usuários ou aceitar um pull request para eles.

Lists supported are:

* SysListView32;
* DirectUIHWND (presente em sistemas de  64-bit);
* WindowsForms10.SysListView32.* (aplicações que usam .NET);
* visualização em árvore com várias colunas, como a apresentada no
  RSSOwlnix;
* Mozilla table (tipicamente, Lista de mensagens do Thunderbird, suportado
  thread-grouping).


[[!tag dev stable]]


[stable]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview

[dev]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview-dev
