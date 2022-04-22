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
* Mukautettavat syötekomennot laskinnäppäimistöllä tai ilman;
* "0 kohdetta" -ilmoitus luettelon ollessa tyhjä (ei valitettavasti toimi
  Win8:n/10:n kansioissa);
* Tuki jatkuvalle luvulle;
* Valittujen kohteiden ilmoittaminen (määrä ja nimet);
* Luettelohaku (kohteiden monivalinnalla, mikäli valittuna/sitä tuetaan).

## Syötekomennot

Sarakkeisiin, otsikoihin ja sijaintiin liitetyt oletusnäppäimet ovat NVDA ja
Ctrl, mutta niitä on myös mahdollista mukauttaa lisäosan asetuksista (ei
"Syötekomennot"-valintaikkunasta!).

Huomaa, että näppäimistöllä voi olla ongelmia joidenkin näppäinyhdistelmien
käsittelyssä, joten kokeile kaikkia lisäsyötekomentoja ja muuta niitä
parempien tulosten saamiseksi.

Katso myös lisäosan asetuksista laskinnäppäimistötila, näppäinasettelu
(ilman laskinnäppäimistöä) sekä neljä käytettävissä olevaa saraketoimintoa.

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
  näppäinasettelu): aloita jatkuva luku (tämä syötekomento riippuu
  alkuperäisestä komennosta kohdassa
  "Syötekomennot"/"Järjestelmäkohdistin");
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

* SysListView32;
* DirectUIHWND (64-bittisissä järjestelmissä);
* WindowsForms10.SysListView32.* (.NET-sovelluskehystä käyttävissä
  sovelluksissa);
* Monisarakkeinen puunäkymä, kuten RSSOwlnixissä;
* Mozilla-taulukko (tyypillisesti Thunderbirdin viestiluettelossa,
  ketjuryhmittelyä tuetaan).


[[!tag dev stable]]


[stable]: https://addons.nvda-project.org/files/get.php?file=cr

[dev]: https://addons.nvda-project.org/files/get.php?file=cr-dev
