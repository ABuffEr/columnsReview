# Spalten-Betrachter #

* Autoren: Alberto Buffolino, Łukasz Golonka, andere Entwickler
* [Stabile Version herunterladen][stable]
* [Entwicklerversion herunterladen][dev]
* NVDA-Kompatibilität: 2017.3 und neuer

Columns Review is an add-on to enhance NVDA experience with lists.

Zu den Funktionen gehören:

* customizable actions on column header and/or content (available actions
  are read, copy, spell and show in browse mode);
* ability to cycle between columns in ten-by-ten intervals;
* Vereinfachte Überschriften-Verwaltung (Maus-Klicks);
* Ausgabe der aktuellen Positionsinformation bei Bedarf (bspw. Eintrag 7 von
  10)
* customizable gestures with or without numpad;
* Die Ansage "0 Einträge", wenn die Liste lehr ist (derzeit nicht in Windows
  8/10-Ordnern)
* Unterstützung für alles lesen;
* Ansage der markierten Einträge (Anzahl und Namen der Einträge);
* list search (with item multiselection, if checked/supported).

## Gesten

Die Standard-Tastenkombinationen für Spalten, Überschriften und Position
beinhalten NVDA+Steuerung. Dies kann in den Erweiterungseinstellungen, (aber
nicht in den "Tastenbefehlen") geändert werden.

Note that your keyboard could have problems processing some key
combinations, so try all add-on gestures and adjust them for better results.

See also add-on preferences for numpad mode, keyboard layout (without
numpad), and the four available actions for columns.

* NVDA+Steuerung+Ziffern von 1 bis 0 (Tastaturmodus) oder von 1 bis 9
  (Nummernblockmodus): einmal drücken: die ausgewählte Spalte wird
  vorgelesen; zweimal drücken: die Spalte wird in die Zwischenablage
  kopiert;
* NVDA+Steuerung+nummernblock Minus (Nummernblockmodus): wie
  NVDA+Steuerung+0 im Tastatur-Modus, Lesen oder Kopieren der 10ten, 20ten
  Spalte usw.;
* NVDA+control+- (keyboard mode, EN-US layout): in a list with 10+ columns,
  change interval and process columns from 11 to 20, from 21 to 30, and so
  on (change last char according to your layout, from settings);
* NVDA+control+numpadPlus (numpad mode): like previous command;
* NVDA+Steuerung+Eingabe (nummernblock Eingabe im Nummernblockmodus):
  Spaltenüberschriften-Manager öffnen;
* NVDA+control+delete (numpadDelete in numpad mode): read relative current
  item position (i.e.: item 7 of 10);
* Pfeiltasten und NVDA+tab (in einer leeren Liste): Nachricht "0 Elemente"
  wird wiederholt;
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

Unterstützte Listen sind:

* SysListView32;
* DirectUIHWND (in 64-Bit-Systemen vorhanden);
* WindowsForms10.SysListView32.* (Anwendungen, die .NET verwenden);
* multi-column treeview like as that presents in RSSOwlnix;
* Mozilla-Tabelle (typischerweise Thunderbird-Nachrichtenliste, gruppierte
  Beiträge werden unterstützt).


[[!tag dev stable]]


[stable]: https://addons.nvda-project.org/files/get.php?file=cr

[dev]: https://addons.nvda-project.org/files/get.php?file=cr-dev
