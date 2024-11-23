# Columns Review #

* Author: Alberto Buffolino, Łukasz Golonka, other contributors
* Pobierz [stabilna wersja][stabilna]
* Pobierz [wersja rozwojowa][dev]
* Zgodność z NVDA: 2017.3 i później

Columns Review to dodatek zwiększający doświadczenie NVDA z listami.

Jego funkcje obejmują:

* konfigurowalne działania na nagłówku kolumny i/lub treści (dostępne akcje
  to czytanie, kopiowanie, pisownia i wyświetlanie w trybie przeglądania);
* możliwość przełączania się między kolumnami w odstępach dziesięć na
  dziesięć;
* uproszczone zarządzanie nagłówkami (kliknięcia myszą);
* odczyt na żądanie względnej bieżącej pozycji pozycji (tj.: pozycja 7 z
  10);
* konfigurowalne gesty z klawiaturą numeryczną lub bez;
* Ogłoszenie "0 elementów", gdy lista jest pusta (nie działa niestety w
  folderach Win8 / 10);
* powiedz całe wsparcie;
* raport wybranych pozycji (ilość i nazwy towarów);
* wyszukiwanie na liście (z wielokrotnym wyborem elementów, jeśli jest
  zaznaczone/obsługiwane).

## Z&darzenia wejścia...

Domyślne kolumn, nagłówków i pozycji to NVDA +control, ale możesz je
dostosować za pomocą ustawień dodatkowych (nie okna dialogowego Gesty
wprowadzania!).

Pamiętaj, że klawiatura może mieć problemy z przetwarzaniem niektórych
kombinacji, więc wypróbuj wszystkie gesty dodatkowe i dostosuj je, aby
uzyskać lepsze wyniki.

Zobacz także preferencje dodatków dla trybu klawiatury numerycznej, układu
klawiatury (bez klawiatury numerycznej) i czterech dostępnych akcji dla
kolumn.

* NVDA + sterowanie + cyfry od 1 do 0 (tryb klawiatury) lub od 1 do 9 (tryb
  klawiatury numerycznej): domyślnie przeczytaj wybraną kolumnę, jeśli
  zostanie naciśnięta raz, skopiuj ją, jeśli naciśniesz ją dwukrotnie;
* NVDA + control + numpadMinus (tryb klawiatury numerycznej): jak NVDA +
  control + 0 w trybie klawiatury, przeczytaj lub skopiuj kolumnę 10,20
  itp.;
* NVDA + control +- (tryb klawiatury, układ EN-US): na liście z ponad 10
  kolumnami zmień interwał i przetwarzaj kolumny od 11 do 20, od 21 do 30 i
  tak dalej (zmień ostatni znak zgodnie z układem, z ustawień);
* NVDA+control+numpadPlus (tryb numpad): podobnie jak poprzednie polecenie;
* NVDA+control+enter (numpadEnter w trybie numpad): otwórz menedżera
  nagłówków;
* NVDA+control+delete (numpadDelete w trybie klawiatury numerycznej): odczyt
  względnie bieżącej pozycji elementu (tj.: pozycja 7 z 10);
* Strzałki i karta NVDA+ (na pustej liście): powtórz komunikat "0
  elementów";
* NVDA+downArrow (układ pulpitu) lub NVDA+a (układ laptopa): zacznij mówić
  wszystko (ten gest zależy od oryginalnego w sekcji "Gesty
  wejściowe"/"Karetka systemu");
* NVDA+shift+upArrow (układ pulpitu) lub NVDA+shift+s (układ laptopa): ilość
  raportów i nazwy bieżących wybranych elementów listy (np. poprzednie
  polecenie dostosowywania);
* NVDA+control+f: otwórz okno dialogowe wyszukiwania (nie można go
  dostosować);
* NVDA+f3: znajdź następne wystąpienie wcześniej wprowadzonego tekstu (nie
  można go dostosować);
* NVDA+shift+f3: znajdź poprzednie wystąpienie (nie można go dostosować).

## Wsparcie

Ten dodatek zapewnia ogólną obsługę bardziej popularnych list (patrz
poniżej) i niektórych konkretnych aplikacji. Główny autor (Alberto
Buffolino) nie może zagwarantować kompatybilności /funkcjonalności dla tych
aplikacji, których nie używa, takich jak Outlook i Poczta systemu Windows,
ale chętnie współpracuje z ich użytkownikami lub akceptuje dla nich żądanie
ściągnięcia.

Obsługiwane listy to:

* SysListView32;
* DirectUIHWND (obecny w systemach 64-bitowych);
* WindowsForms10.SysListView32.* (aplikacje korzystające z platformy .NET);
* wielokolumnowy widok drzewa, taki jak w RSSOwlnix;
* Tabela Mozilli (typowo, lista wiadomości Thunderbirda, obsługiwane
  grupowanie wątków).


[[!tag dev stable]]


[stable]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview

[dev]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview-dev
