# Columns Review #

* Autor: Alberto Buffolino, Łukasz Golonka, outros contribuíntes
* Descargar [versión de desenvolvemento][stable]
* Descargar [versión de desenvolvemento][dev]
* Compatibilidade con NVDA: 2017.3 en diante

Columns Review é un complemento para mellorar a experiencia en NVDA coas
listas.

As súas características inclúen:

* accións persoalizables na cabeceira e/ou o contido de columnas (as accións
  dispoñibles son ler, copiar, deletrear e amosar en modo exploración);
* capacidade de alternar entre columnas en intervalos de dez en dez;
* administración de cabeceiras simplificada (clicks do rato);
* lectura a demanda de posición relativa do elemento actual (p.ex. elemento
  7 de 10);
* xestos persoalizables con ou sen teclado numérico;
* anuncio "0 elementos" cando a lista está baleira (non funciona en
  cartafoles de Win8/10, lamentablemente);
* soporte para a fundionalidade ler todo;
* anuncio dos elementos seleccionados (cantidade e nomes);
* procura en listas (con multiselección de elementos, se está
  activada/soportada).

## Xestos

As teclas por defecto para as columnas, as cabeceiras e a posición son
NVDA+control, pero podes personalizalas dende os axustes do complemento (non
dende o diálogo "Xestos de entrada").

Ten en conta que o teu teclado podería ter problemas procesando certas
combinacións de teclas, así que proba todos os xestos do complemento e
axústaos para mellores resultados.

Consulta tamén as preferencias do complemento para o modo do teclado
numérico, disposición de teclado (sen teclado numérico), e as catro accións
dispoñibles para columnas.

* NVDA+control+díxitos do 1 ó 0 (modo teclado) ou do 1 ó 9 (modo teclado
  numérico): por defecto, premido unha vez le a columna elixida, premido
  dúas veces cópiaa;
* NVDA+control+menosTecladoNumérico (modo teclado numérico): de forma
  semellante a NVDA+control+0 en modo teclado, ler ou copiar a columna
  décima, vixésima, etc.;
* NVDA+control+- (modo teclado, distribución EN-US): nunha listaxe con 10+
  columnas, cambiar o intervalo e procesar columnas da 11 á 20, da 21 á 30,
  e así (cambia o último carácter de acordo coa túa distribución, nas
  opcións);
* NVDA+control+máisTecladoNumérico (modo teclado numérico): igual á orde
  anterior;
* NVDA+control+intro (introTecladoNumérico en modo teclado numérico): abrir
  administrador de cabeceiras;
* NVDA+control+suprimir (suprimirTecladoNumérico en modo teclado numérico):
  ler posición relativa do elemento actual (p.ex. elemento 7 de 10);
* Frechas e NVDA+tab (en lista baleira): repetir mensaxe "0 elementos"
* NVDA+frechaAbaixo (disposición de escritorio) ou NVDA+a (disposición
  portátil): comezar ler todo (este xesto depende do orixinal, baixo "Xestos
  de entrada"/"Cursor do sistema");
* NVDA+shift+frechaArriba (disposición de escritorio) ou NVDA+shift+s
  (disposición portátil): anunciar cantidade e nomes dos elementos de lista
  actualmente seleccionados (semellante ó comando anterior para
  persoalización);
* NVDA+control+f: abrir diálogo de procura (non persoalizable);
* NVDA+f3: buscar seguinte ocorrencia do texto anteriormente introducido
  (non persoalizable);
* NVDA+shift+f3: buscar anterior ocorrencia (non persoalizable).

## Soporte

Este complemento fornece soporte xeral para as listas máis comúns (ver
abaixo), e algunhas aplicacións específicas. O autor principal (Alberto
Buffolino) non pode garantir a compatibilidade/funcionalidade para aquelas
aplicacións que non utiliza, como Outlook e Windows Mail, mais estará
encantado de colaborar cos seus usuarios ou aceptar unha solicitude de
integración (pull request) para elas.

As listas soportadas son:

* SysListView32;
* DirectUIHWND (presente en sistemas de 64 bits);
* WindowsForms10.SysListView32.* (aplicacións que usen .net);
* vista de multicolumna, como a presente en RSSOwlnix;
* Tabla Mozilla (normalmente a listaxe de mensaxes do Thunderbird,
  soportándose a agrupación por fío).


[[!tag dev stable]]


[stable]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview

[dev]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview-dev
