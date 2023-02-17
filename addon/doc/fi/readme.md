# Sarakkeiden tarkastelu #

* Tekijät: Alberto Buffolino, Łukasz Golonka, muut avustajat
* Lataa [vakaa versio][stable]
* Lataa [kehitysversio][dev]
* Yhteensopivuus: NVDA 2017.3 ja uudemmat

Sarakkeiden tarkastelu on lisäosa, joka parantaa NVDA:n käyttökokemusta
luetteloissa.

Sen ominaisuuksia ovat mm.:

* Mukautettavat toiminnot sarakeotsakkeille ja/tai -sisällölle
  (käytettävissä olevat toiminnot ovat lue, kopioi, tavaa ja näytä
  selaustilassa);
* Mahdollisuus liikkua sarakkeiden välillä kymmenen ryhmissä;
* Yksinkertaistettu otsakkeiden hallinta (hiiren napsautukset);
* Nykyisen kohteenn suhteellisen sijainnin lukeminen tarvittaessa
  (esim. kohde 7 / 10);
<<<<<<< HEAD
* Mukautettavat syötekomennot laskinnäppäimistöllä tai ilman;
=======
* Mukautettavat näppäinkomennot laskinnäppäimistöllä tai ilman;
>>>>>>> f01149847a0c0701779677222e1be2cdf522509e
* "0 kohdetta" -ilmoitus luettelon ollessa tyhjä (ei valitettavasti toimi
  Win8:n/10:n kansioissa);
* Tuki jatkuvalle luvulle;
* Valittujen kohteiden ilmoittaminen (määrä ja nimet);
* Luettelohaku (kohteiden monivalinnalla, mikäli valittuna/sitä tuetaan).

<<<<<<< HEAD
## Syötekomennot

Default keys for columns, headers and position are NVDA+control, but you can
customize them from add-on settings (not "Input gestures" dialog!).

Huomaa, että näppäimistöllä voi olla ongelmia joidenkin näppäinyhdistelmien
käsittelyssä, joten kokeile kaikkia lisäsyötekomentoja ja muuta niitä
=======
## Näppäinkomennot

Sarakkeisiin, otsikoihin ja sijaintiin liitetyt oletusnäppäimet ovat NVDA ja
Ctrl, mutta niitä on myös mahdollista mukauttaa lisäosan asetuksista (ei
"Näppäinkomennot"-valintaikkunasta!).

Huomaa, että näppäimistöllä voi olla ongelmia joidenkin näppäinyhdistelmien
käsittelyssä, joten kokeile kaikkia lisänäppäinkomentoja ja muuta niitä
>>>>>>> f01149847a0c0701779677222e1be2cdf522509e
parempien tulosten saamiseksi.

Katso myös lisäosan asetuksista laskinnäppäimistötila, näppäinasettelu
(ilman laskinnäppäimistöä) sekä neljä käytettävissä olevaa saraketoimintoa.

<<<<<<< HEAD
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
* NVDA+control+delete (numpadDelete in numpad mode): read relative current
  item position (i.e.: item 7 of 10);
* Arrows and NVDA+tab (in empty list): repeat "0 items" message;
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

Lists supported are:
=======
* NVDA+Ctrl+numerot 1-0 (näppäimistötila) tai numerot 1-9
  (laskinnäppäimistötila): lukee kerran painettaessa valitun sarakkeen tai
  kopioi sen kahdesti painettaessa leikepöydälle;
* NVDA+Ctrl+numeronäppäimistön miinus (laskinnäppäimistötila): kuten
  NVDA+Ctrl+0 näppäimistötilassa, lukee 10., 20., jne. sarakkeen tai kopioi
  sen leikepöydälle;
* NVDA+Ctrl+- (näppäimistötila, yhdysvaltalainen näppäinasettelu): muuttaa
  väliä ja käsittelee sarakkeet 11-20, 21-30 jne. luettelossa, jossa on
  enemmän kuin 10 saraketta (muuta komennon viimeinen merkki käyttämäsi
  näppäinasettelun mukaiseksi lisäosan asetuksista);
* NVDA+Ctrl+laskinnäppäimistön plus (laskinnäppäimistötila): kuten edellinen
  komento;
* NVDA+Ctrl+Enter (laskinnäppäimistön Enter laskinnäppäimistötilassa): avaa
  sarakeotsikoiden hallinnan;
* NVDA+Ctrl+Del (laskimen Del laskinnäppäimistötilassa): lue kohteen
  nykyinen, suhteellinen sijainti (esim. kohde 7 / 10);
* Nuolinäppäimet ja NVDA+Sarkain (tyhjässä listassa): toistaa "0 kohdetta"
  -ilmoitusta.
* NVDA+Alanuoli (pöytäkoneen näppäinasettelu) tai NVDA+A (kannettavan
  näppäinasettelu): aloita jatkuva luku (tämä näppäinkomento on riippuvainen
  alkuperäisestä komennosta kohdassa
  "Näppäinkomennot"/"Järjestelmäkohdistin");
* NVDA+Vaihto+Ylänuoli (pöytäkoneen näppäinasettelu) tai NVDA+Vaihto+S
  (kannettavan näppäinasettelu): lue valittujen luettelokohteiden määrä ja
  nimet (kuten aiemmassa mukautuskomennossa);
* NVDA+Ctrl+F: avaa Etsi-valintaikkuna (ei mukautettavissa);
* NVDA+F3: etsi aiemmin  annetun tekstin seuraava esiintymä (ei
  mukautettavissa);
* NVDA+Vaihto+F3: etsi edellinen esiintymä (ei mukautettavissa).

## Tuki

Tämä lisäosa tarjoaa tuen yleisemmille luetteloille (katso alta) ja
tietyille sovelluksille. Päätekijä (Alberto Buffolino) ei voi taata
yhteensopivuutta/toiminnallisuutta sovelluksille, joita hän ei käytä, kuten
Outlook ja Windows Mail, mutta hän tekee mielellään yhteistyötä sovellusten
käyttäjien kanssa tai hyväksyy vetopyynnön tuen lisäämiseksi.

Tuettuja luetteloita ovat:
>>>>>>> f01149847a0c0701779677222e1be2cdf522509e

* SysListView32;
* DirectUIHWND (64-bittisissä järjestelmissä);
* WindowsForms10.SysListView32.* (.NET-sovelluskehystä käyttävissä
  sovelluksissa);
<<<<<<< HEAD
* multi-column treeview like as that presents in RSSOwlnix;
=======
* Monisarakkeinen puunäkymä, kuten RSSOwlnixissä;
>>>>>>> f01149847a0c0701779677222e1be2cdf522509e
* Mozilla-taulukko (tyypillisesti Thunderbirdin viestiluettelossa,
  ketjuryhmittelyä tuetaan).


[[!tag dev stable]]


[stable]: https://addons.nvda-project.org/files/get.php?file=cr

[dev]: https://addons.nvda-project.org/files/get.php?file=cr-dev
