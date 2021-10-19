# Columns Review #

* Autor: Alberto Buffolino, Łukasz Golonka y otros colaboradores
* Descargar  [Versión estable][stable]
* Descargar [versión de desarrollo][dev]
* Compatibilidad con NVDA: de 2017.3 en adelante

Columns Review es un complemento para mejorar la experiencia con NVDA en
listas.

Entre sus funciones se incluyen:

* acciones personalizables en la cabecera o el contenido de la columna (las
  acciones disponibles son leer, copiar, deletrear y mostrar en modo
  exploración);
* capacidad de circular por las columnas en intervalos de diez en diez;
* gestión simplificada de las cabeceras (clics de ratón);
* lectura bajo demanda de la posición relativa actual del elemento (por
  ejemplo, elemento 7 de 10);
* gestos personalizables con o sin bloque numérico;
* anuncio de "0 elementos" cuando la lista está vacía (no funciona en
  carpetas en Windows 8 y 10, por desgracia);
* soporte para verbalizar todo;
* anuncio de los elementos seleccionados (cantidad y nombre de los
  elementos);
* búsqueda en listas (con selección múltiple de elementos, si se marca y
  está soportada).

## Gestos

Las teclas por defecto para columnas, cabeceras y posición son NVDA+control,
pero puedes personalizarlas desde las opciones del complemento (¡no en el
diálogo "Gestos de entrada"!).

Ten en cuenta que tu teclado podría tener problemas procesando algunas
combinaciones de teclado, por lo que deberías probar todos los gestos del
complemento y ajustarlos para unos mejores resultados.

Consulta también las preferencias del complemento para el modo bloque
numérico, distribución de teclado (sin bloque numérico), y las cuatro
acciones disponibles para las columnas.

* NVDA+control+dígitos del 1 al 0 (modo teclado) o del 1 al 9 (modo bloque
  numérico): por defecto, lee la columna elegida si se pulsa una vez, la
  copia si se pulsa dos veces;
* NVDA+control+menos del teclado numérico (modo bloque numérico): como
  NVDA+control+0 en el modo teclado, lee o copia la 10ª, 20ª, etc. columna;
* NVDA+control+- (distribución de inglés de Estados Unidos, modo teclado):
  en una lista con más de 10 columnas, cambia el intervalo y procesa
  columnas de la 11 a la 20, de la 21 a la 30, y así sucesivamente (cambia
  el último carácter en función de tu distribución desde las opciones);
* NVDA+control+más del teclado numérico (modo bloque numérico): como la
  orden anterior;
* NVDA+control+intro (intro del teclado numérico en el modo bloque
  numérico): abre el gestor de cabeceras;
* NVDA+control+suprimir (suprimir del teclado numérico en el modo bloque
  numérico): lee la posición relativa del elemento actual (por ejemplo,
  elemento 7 de 10);
* Flechas y NVDA+tab (en una lista vacía): repite el mensaje "0 elementos";
* NVDA+flecha abajo (distribución de escritorio) o NVDA+a (distribución
  portátil): inicia Verbalizar todo (este gesto depende del original que hay
  bajo "Gestos de entrada/Cursor del sistema");
* NVDA+shift+flecha arriba (distribución de escritorio) o NVDA+shift+s
  (distribución portátil): anuncia la cantidad y los nombres de los
  elementos de lista actualmente seleccionados (al igual que la orden
  anterior en cuanto a personalización);
* NVDA+control+f: abre el diálogo de búsqueda (no personalizable);
* NVDA+f3: busca la siguiente coincidencia del texto introducido
  anteriormente (no personalizable);
* NVDA+shift+f3: busca la coincidencia anterior (no personalizable).

## Soporte

Este complemento proporciona soporte general para más listas comunes (mira
debajo) y algunas aplicaciones concretas. El autor principal (Alberto
Buffolino) no puede garantizar la compatibilidad o funcionalidad en aquellas
aplicaciones que no usa, como Outlook o Windows Mail, pero estará encantado
de colaborar con sus usuarios o aceptar una solicitud de cambio para ellos.

Las listas soportadas son:

* SysListView32;
* DirectUIHWND (presente en sistemas de 64 bits);
* WindowsForms10.SysListView32.* (aplicaciones que usan .NET);
* la vista en árbol de varias columnas, como la que hay presente en
  RSSOwlnix;
* Tabla de Mozilla (normalmente, la lista de mensajes de Thunderbird, con
  soporte para agrupación por hilos).


[[!tag dev stable]]


[stable]: https://addons.nvda-project.org/files/get.php?file=cr

[dev]: https://addons.nvda-project.org/files/get.php?file=cr-dev
