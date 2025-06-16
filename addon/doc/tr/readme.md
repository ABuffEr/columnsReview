# Sütun incelemesi #

* Yazar: Alberto Buffolino, Łukasz Golonka, diğer katkıda bulunanlar
* [kararlı sürümü][stable] indir
* [geliştirme sürümünü][dev] indir
* NVDA uyumluluğu: 2017.3 ve sonrası

Sütun İncelemesi, listelerle NVDA deneyimini geliştirmek için bir
eklentidir.

Özellikleri şunları içerir:

* sütun başlığı ve/veya içerik üzerinde özelleştirilebilir eylemler (mevcut
  eylemler okuma, kopyalama, kodlama ve tarama kipinde gösterme);
* onar on aralıklarla sütunlar arasında geçiş yapma yeteneği;
* basitleştirilmiş başlık yönetimi (fare tıklamaları);
* göreli geçerli öğe konumunun isteğe bağlı okuması (öğe 7/10 gibi);
* numaratörün kullanıldığı ya da kullanılmadığı özelleştirilebilir
  hareketler;
* Liste boşken "0 öğe" duyurusu (maalesef Win8/10 klasörlerinde çalışmıyor);
* tümünü okuma desteği;
* seçilen öğelerin bildirimi (miktar ve öğe adları);
* liste araması (işaretliyse/destekleniyorsa öğe çoklu seçimli).

## Hareketler

Sütunlar, başlıklar ve konum için varsayılan tuşlar NVDA+kontroldür, ancak
bunları eklenti ayarlarından özelleştirebilirsiniz ("Girdi hareketleri"
iletişim kutusu değil!).

Klavyenizin bazı tuş kombinasyonlarını işlemede sorun yaşayabileceğini
unutmayın, bu nedenle tüm eklenti hareketlerini deneyin ve daha iyi sonuçlar
için gerekli ayarları yapın.

Ayrıca numaratör modu, klavye düzeni (numaratör olmadan) ve sütunlar için
kullanılabilen dört eylem için eklenti tercihlerine bakın.

* 1'den 0'a (klavye modu) veya 1'den 9'a (sayısal tuş takımı modu)
  NVDA+kontrol+haneleri: varsayılan olarak, bir kez basıldığında seçilen
  sütunu okuyun, iki kez basıldığında kopyalayın;
* NVDA+kontrol+numaratörEksi (numaratör modu): klavye modunda NVDA+kontrol+0
  gibi, 10., 20., vb. sütunu okuyun veya kopyalayın;
* NVDA+control+- (varsayılan, EN-US düzeni, klavye modu): 10'dan fazla
  sütunlu bir listede, aralığı değiştirmenize ve 11'den 20'ye, 21'den 30'a
  vb. sütunları okumanıza yarar; düzeninize göre son karakteri değiştirmek
  için ayarlara bakın;
* NVDA+kontrol+numaratörArtı (numaratör modu): önceki komuta benzer;
* NVDA+control+enter (numaratörde numaratörEnter): sütun başlıkları
  yöneticisini açar;
* NVDA+kontrol+sil (numaratörde numaratör sil): göreli geçerli öğe konumunu
  oku (öğe 7/10 gibi);
* Oklar ve NVDA+sekmesi (boş listede): "0 öğe" mesajını tekrarlar;
* NVDA+aşağı ok (masaüstü düzeni) veya NVDA+a (dizüstü düzeni): tümünü oku
  (bu hareket "Girdi hareketleri"/"Sistem düzenleme imleci" altındaki
  orijinal harekete  bağlıdır);
* NVDA+shift+yukarı ok (masaüstü düzeni) veya NVDA+shift+s (dizüstü düzeni):
  mevcut seçili liste öğelerinin miktarını ve adlarını bildir (önceki komut
  gibi NVDA'nın seçilen öğelerin bildirimiyle ilgili girdi hareketine
  bağlı);
* NVDA+control+f: bul iletişim kutusunu aç (özelleştirilemez);
* NVDA+f3: sonrakini bul (özelleştirilemez);
* NVDA+shift+f3: öncekini bul (özelleştirilemez).

## Destek

Bu eklenti, daha yaygın listeler (aşağıya bakın) ve bazı özel uygulamalar
için genel bir destek sağlar. Ana yazar (Alberto Buffolino), Outlook ve
Windows Mail gibi kullanmadığı uygulamalar için uyumluluğu/işlevselliği
garanti edemez, ancak kullanıcılarıyla işbirliği yapmaktan veya onlar için
bir çekme talebini kabul etmekten memnuniyet duyacaktır.

Desteklenen listeler :

* SysListView32;
* DirectUIHWND (64 bit sistemlerde bulunur);
* WindowsForms10.SysListView32.* (.NET kullanan uygulamalar);
* rssOwlnix'te olduğu gibi çok sütunlu ağaç görünümü;
* Mozilla tablosu (tipik olarak Thunderbird mesaj listesi, konu bazında
  gruplandırmalar desteklenir).


[[!tag dev stable]]


[stable]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview

[dev]: https://www.nvaccess.org/addonStore/legacy?file=columnsReview-dev
