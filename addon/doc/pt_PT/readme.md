# Revisão de colunas #

* Autor: Alberto Buffolino, Łukasz Golonka, outros colaboradores
* Descarregar [versão estável][estável]
* Descarregar [versão de desenvolvimento][dev]
* Compatibilidade com o NVDA: 2017.3 e posteriores

O Columns Review é um extra para melhorar a experiência do NVDA com listas.

As suas funcionalidades incluem:

* acções personalizáveis no cabeçalho da coluna e/ou conteúdo (as acções
  disponíveis são: lidas, copiadas, soletradas e mostradas no modo de
  navegação);
* capacidade de circular entre colunas em intervalos de dez por dez;
* gestão simplificada do cabeçalho (cliques do rato);
* leitura, a pedido do utilizador, da posição relativa do item actual (por
  exemplo: item 7 de 10);
* comandos personalizáveis com ou sem bloco numérico;
* Anúncio de "0 itens" quando a lista está vazia (não funciona em pastas
  Win8/10, infelizmente);
* diz todas as possibilidades;
* relatório dos itens seleccionados (tamanho e nomes dos itens);
* pesquisa da lista (com multi-selecção do item, se verificada/suportada).

## Comandos

As teclas predefinidas para colunas, cabeçalhos e posição são NVDA+control,
mas pode personalizá-las a partir de definições adicionais (não do menu
"Definir Comandos"!).

Note que o seu teclado pode ter problemas em processar algumas combinações
de teclas, por isso experimente todos os comandos adicionais e ajuste-os
para melhores resultados.

Ver também as preferências adicionais para o numpad mode, disposição do
teclado (sem numpad), e as quatro acções disponíveis para as colunas.

* NVDA + control + dígitos de 1 a 0 (modo teclado) ou de 1 a 9 (modo
  numérico): pressionado uma vez, lê a coluna escolhida, pressionado duas
  vezes, copia-a;
* NVDA+control+- do bloco numérico (no modo bloco numérico): como
  NVDA+control+0 no modo de teclado, lê ou copia as 10, 20 colunas, etc.
* NVDA+control+- (padrão, no sistema americano, modo de teclado): numa lista
  com mais de 10 colunas, permite que altere o intervalo e leia as colunas
  de 11 a 20, de 21 a 30, e assim por diante; veja as configurações para
  alterar o último caractere de acordo com o seu idioma;
* NVDA+control+numpadPlus (modo numpad): como comando anterior;
* NVDA+control+enter (eventualmente enter do bloco numéricono no modo de
  bloco numérico): abre o gestor de cabeçalhos de colunas;
* NVDA+control+delete (numpadDelete em modo numpad): ler a posição relativa
  do item actual (ou seja: item 7 de 10);
* Setas e NVDA+tab (em lista vazia): repetir a mensagem "0 itens";
* NVDA+seta abaixo (teclado do computador de secretária) ou NVDA+a (teclado
  do portátil): começa por dizer tudo (este comando depende do original em
  "Definir Comandos"/"Cursor do sistema");
* NVDA+shift+seta acima (teclado do computador de secretária) ou
  NVDA+shift+s (teclado do portátil): Informa a quantidade e os nomes dos
  actuais itens da lista seleccionada (como o comando anterior, para
  personalização);
* NVDA+control+f: Abre o diálogo de pesquisa (não personalizável);
* NVDA+f3: encontrar a próxima ocorrência de texto anteriormente introduzido
  (não personalizável);
* NVDA+shift+f3: encontrar ocorrência anterior (não personalizável).

## Suporte

Este extra fornece um suporte geral para listas mais comuns (ver abaixo), e
algumas aplicações específicas. O autor principal (Alberto Buffolino) não
pode garantir a compatibilidade/funcionalidade para as aplicações que não
utiliza, como Outlook e Windows Mail, mas terá todo o prazer em colaborar
com os seus utilizadores ou aceitar uma solicitação feita por eles.

As listas suportadas são:

* SysListView32;
* DirectUIHWND (presente em sistemas de  64-bit);
* WindowsForms10.SysListView32.* (aplicações que usam .NET);
* vista em árvore multicoluna como a que se apresenta no RSSOwlnix;
* Mozilla table (tipicamente, Lista de mensagens do Thunderbird, suportado
  thread-grouping).


[[!tag dev stable]]


[stable]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview

[dev]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview-dev
