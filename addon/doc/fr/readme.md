# Columns Review #

* Auteur : Alberto Buffolino, Łukasz Golonka, autres contributeurs
* Télécharger [version stable][stable]
* Télécharger [version de développement][dev]
* Compatibilité NVDA : 2017.3 et au-delà

Columns Review est une extension améliorant l'expérience NVDA avec les
listes.

Ses fonctionnalités incluent :

* actions personnalisables sur l'en-tête de colonne et/ou le contenu (les
  actions disponibles sont lire, copier, épeler et afficher en mode
  navigation) ;
* possibilité de parcourir les colonnes à intervalles de dix par dix ;
* gestion simplifiée des en-têtes (clics de souris) ;
* lecture à la demande de la position actuelle relative de l'élément (ex :
  élément 7 sur 10);
* gestes personnalisables avec ou sans le pavé numérique ;
* Annonce "0 éléments" lorsque la liste est vide (ne fonctionne
  malheureusement pas dans les dossiers Win8/10) ;
* support de dire tout ;
* annonce des éléments sélectionnés (quantité et noms des éléments) ;
* recherche par liste (avec sélection multiple d'éléments, si cochée/prise
  en charge).

## Gestes

Les touches par défaut pour les colonnes, les en-têtes et la position sont
NVDA+contrôle, mais vous pouvez les personnaliser à partir des paramètres de
l'extension (pas du dialogue « Gestes de commandes » !).

Notez que votre clavier peut avoir des problèmes pour traiter certaines
combinaisons de touches, alors essayez tous les gestes de l'extension et
ajustez-les pour de meilleurs résultats.

Voir également les préférences de l'extension pour le mode pavé numérique,
la disposition du clavier (sans pavé numérique) et les quatre actions
disponibles pour les colonnes.

* NVDA+contrôle+chiffres de 1 à 0 (mode clavier) ou de 1 à 9 (mode pavé
  numérique) : par défaut, lecture de la colonne choisie si pressé une fois,
  copie si pressé deux fois ;
* NVDA+ctrl+pavnum Moins (mode pavé numérique) : ou NVDA+ctrl+0 en mode
  clavier, lit ou copie la 10e, 20e, etc. colonne ;
* NVDA+contrôle+- (mode clavier, disposition EN-US) : dans une liste de plus
  de 10 colonnes, modifiez les colonnes d'intervalle et de traitement de 11
  à 20, de 21 à 30, et ainsi de suite (modifiez le dernier caractère en
  fonction de votre disposition, à partir des paramètres);
* NVDA+contrôle+Plus du clavier numérique (mode pavé numérique): comme la
  commande précédente ;
* NVDA+contrôle+entrée (Entrée du clavier numérique en mode pavé numérique):
  ouvre le gestionnaire des en-têtes de colonne ;
* NVDA+contrôle+effacement (PavnumEffac en mode pavé numérique) : lire la
  position relative actuelle de l'élément (ex : élément 7 sur 10) ;
* Flèches et NVDA+tab (dans la liste vide): répète le message "0 éléments".
* NVDA+flècheBas (disposition de bureau) ou NVDA+a (disposition d'ordinateur
  portable) : démarrer dire tout (ce geste dépend de celui d'origine sous
  "Gestes de commandes"/"Curseur système");
* NVDA+maj+flècheHaut (disposition de bureau) ou NVDA+maj+s (disposition
  d'ordinateur portable) : annoncer la quantité et les noms des éléments de
  liste actuellement sélectionnés (comme la commande précédente pour la
  personnalisation) ;
* NVDA+contrôle+f : ouvre le dialogue de recherche (non personnalisable) ;
* NVDA+f3 : recherche la prochaine occurrence du texte précédemment saisi
  (non personnalisable) ;
* NVDA+maj+f3 : trouver l'occurrence précédente (non personnalisable).

## Support

Cette extension fournit un support général pour les listes les plus
courantes (voir ci-dessous) et certaines applications spécifiques. L'auteur
principal (Alberto Buffolino) ne peut pas garantir la
compatibilité/fonctionnalité des applications qu'il n'utilise pas, comme
Outlook et Windows Mail, mais il sera heureux de collaborer avec leurs
utilisateurs ou d'accepter une pull request pour eux.

Les types de liste pris en charge sont les suivants:

* SysListView32 ;
* DirectUIHWND (présent dans les systèmes 64 bits) ;
* WindowsForms10.SysListView32.* (applications utilisant .NET) ;
* arborescence multi-colonnes comme celle présente dans RSSOwlnix ;
* Tableau Mozilla (en particulier, la liste de messages Thunderbird, pris en
  charge pour regroupement par fil).


[[!tag dev stable]]


[stable]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview

[dev]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview-dev
