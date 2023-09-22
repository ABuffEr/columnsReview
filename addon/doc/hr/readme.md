# Pregled stupaca (Columns Review) #

* Autor: Alberto Buffolino, Łukasz Golonka, ostali suradnici
* Preuzmi [stabilnu verziju][stable]
* Preuzmi [razvojnu verziju][dev]
* NVDA kompatibilnost: 2017.3 i nadalje

Pregled stupaca je dodatak za poboljšanje NVDA iskustva s popisima.

Its features include:

* customizable actions on column header and/or content (available actions
  are read, copy, spell and show in browse mode);
* ability to cycle between columns in ten-by-ten intervals;
* simplified header management (mouse clicks);
* on-demand reading of relative current item position (i.e.: item 7 of 10);
* customizable gestures with or without numpad;
* "0 items" announcement when list is empty (not working in Win8/10 folders,
  unfortunately);
* say all support;
* report of selected items (amount and item names);
* list search (with item multiselection, if checked/supported).

## Gestures

Default keys for columns, headers and position are NVDA+control, but you can
customize them from add-on settings (not "Input gestures" dialog!).

Note that your keyboard could have problems processing some key
combinations, so try all add-on gestures and adjust them for better results.

See also add-on preferences for numpad mode, keyboard layout (without
numpad), and the four available actions for columns.

* NVDA+kontrol+brojke 1 do 0 (modus tipkovnice) ili 1 do 9 (modus numeričke
  tipkovnice): standardno je postavljeno: jednom pritisnuto, čita odabrani
  stupac, dvaput pritisnuto, kopira stupac;
* NVDA+kontrol+Minus na numeričkoj tipkovnici (modus numeričke tipkovnice):
  kao u tipkovničkom modusu, NVDA+kontrol+0 čita ili kopira deseti stupac,
  dvadeseti stupac itd.;
* NVDA+kontrol+- (modus tipkovnice, američki raspored tipkovnice): u popisu
  s 10 i više stupaca promijeni interval i obradu stupaca od 11. do 20., od
  21. do 30. itd. (u postavkama promijeni zadnji znak u skladu s tvojim
  rasporedom tipkovnice);
* NVDA+kontrol+Plus na numeričkoj tipkovnici (modus numeričke tipkovnice):
  kao prethodna naredba;
* NVDA+kontrol+enter (Enter u modusu numeričke tipkovnice): otvori upravljač
  zaglavlja;
* NVDA+control+delete (numpadDelete in numpad mode): read relative current
  item position (i.e.: item 7 of 10);
* Strelice i NVDA+tabulator (u praznom popisu): ponovi poruku „0 elemenata”;
* NVDA+downArrow (desktop layout) or NVDA+a (laptop layout): start say all
  (this gesture depends on original one under "Input gestures"/"System
  caret");
* NVDA+shift+upArrow (desktop layout) or NVDA+shift+s (laptop layout):
  report amount and names of current selected list items (like previous
  command for customization);
* NVDA+control+f: open find dialog (not customizable);
* NVDA+f3: find next occurrence of previously entered text (not
  customizable);
* NVDA+shift+f3: find previous occurrence (not customizable).

## Support

This add-on provide a general support for more common lists (see below), and
some specific applications. Main author (Alberto Buffolino) cannot guarantee
compatibility/functionality for those applications he not uses, like Outlook
and Windows Mail, but he'll be happy to collaborate with their users or
accept a pull request for them.

Podržani popisi:

* SysListView32;
* DirectUIHWND (prisutno u 64-bitnom sustavu);
* WindowsForms10.SysListView32.* (programi koji koriste .NET);
* višestupčan stablasti prikaz kao u RSSOwlnix;
* Mozilla tablica (popis poruka od Thunderbirda, podržava grupiranje po
  temama).


[[!tag dev stable]]


[stable]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview

[dev]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview-dev
