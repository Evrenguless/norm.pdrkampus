# Veri ve norm araştırma yöntemi — v0.1

## Amaç ve ölçüler

1. **Hesaplanan norm:** Kaynaklı okul girdilerine araştırma kuralının uygulanması.
2. **Resmî onaylı norm:** MEM/MEB norm cetveli ile doğrulanmış değer. Bu sürümde yok.
3. **Okul açığı:** max(0, hesaplanan norm − aynı yıl mevcut PDR öğretmeni). Öğretmen verisi yoksa sonuç bilinmiyor.
4. **Düzenleme norm etkisi:** Senaryo normu − dayanak normu. Mevcut kadro bilinmeden atama açığı değildir.
5. **Toplam okul açığı:** Okul açıkları toplamı. Bir okulun norm fazlası diğer okul açığından düşülmez.

## Hukuki kaynak kaydı

- Yönetmelik: MEB'ye Bağlı Eğitim Kurumları Yönetici ve Öğretmenlerinin Norm Kadrolarına İlişkin Yönetmelik, 2014/6459, RG 18.06.2014/29034.
- Motor dayanağı: https://safranaotml.meb.k12.tr/meb_iys_dosyalar/78/05/967379/dosyalar/2021_10/04114838_MEB-Norm-Kadro-Yonetmeligi.pdf — Madde 21, PDF sayfa 7–8.
- Güncel katalog: https://www.meb.gov.tr/mevzuat/liste.php?ara=6 — 1 Ekim 2026'da erişildi, norm yönetmeliği bağlantısı mevcut.
- Katalogdaki güncel metin bağlantısı: https://www.mevzuat.gov.tr/Metin.Aspx?MevzuatIliski=0&MevzuatKod=21.5.20146459&sourceXmlSearch=norm — erişim zaman aşımı.
- https://www.mevzuat.gov.tr/MevzuatMetin/21.5.20146459.pdf — erişilemedi.

Sonuç: Madde 21'in erişilen kopyası modellenmiştir; **2026 yürürlük doğrulaması açık iş**. Eski 2013 MEB duyuru metni kurallar değiştiği için motor dayanağı yapılmadı.

## Dayanak kural özeti

İlkokul 300; anaokulu/ortaokul/İHO/lise 150; MESEM 200 çırak/kursiyer; özel eğitim grup toplamı 25 ile 1 temel norm. Yatılı/pansiyonlu kurumlarda temel norm öğrenci sayısından bağımsızdır. İlçe merkezi istisnası bütün ilgili kurumlardan hareketle doğrulanır; yalnızca ilçe adının “Merkez” olması yeterli değildir.

Özel eğitimde 100, diğer kurumlarda 500 ve katlarında ilave norm. Bu, temel norma eklenir; ceil(öğrenci/500) ile aynı değildir. RAM: ilk 100.000 nüfus 4; kalan her 50.000 için 1; kalan en az 25.000 için bir daha.

Aynı bina/bahçedeki özel eğitim kurumlarının tüm grup öğrenci sayısı ve normun verileceği en yüksek öğrencili kurum doğrulanır. Eşitlik durumunda atama/dağıtım belgesi olmadan alıcı belirlenmez. Bu sürüm eksik grupları hesaplamaz. İlköğretim ve ortaöğretimde ortak binayı otomatik birleştirmez.

Madde 21/4'teki yerleşim merkezi atama sıralaması ayrı bir süreçtir; mevcut kadro/yerleşim envanteri olmadan atama sayısı ilan edilmez.

## Veri toplama akışı

1. İl MEM kurum listesi ve okul/kurum kodlarıyla **tam envanter** oluştur.
2. Faaliyet, resmî/özel ayrımı, kademe ve okul türünü kontrol et. RAM ve okul dışı kurumlar ayrı kapsam.
3. Okul sayfası, stratejik plan veya tarihli brifingden öğrenci sayısını çıkar. Sayı, yıl, sayfa/tablo ve kaynak tarihini birlikte kaydet.
4. Pansiyon ve ilçe merkezi istisnasını ayrıca doğrula. Öğrenci sayısından pansiyon bilgisi türetme.
5. İl/ilçe norm ihtiyaç cetveli veya resmî okul personel tablosundan **Rehberlik/PDR alanına ait** mevcut kadroyu çıkar. Genel öğretmen sayısını kullanma. Geçici görevlendirme ve kadrolu personeli sonraki veri modelinde ayrı tanımla.
6. Her okul/yıl için ikinci kontrol yap; çelişkili değerleri ezmek yerine kaynak anlık görüntülerini sakla.
7. Aynı yıl/kapsam il toplamlarıyla karşılaştır; kapsama giren toplam okul ve öğrenci sayısına göre veri kapsamasını hesapla.
8. Ancak tam ve uyumlu envanterden il/Türkiye toplamı yayımla; eksik alt kümeyi açıkça etiketle.

İstenen bilgi yalnızca okul düzeyindeki toplamlar ve alan kadrolarıdır; öğrenci ya da öğretmen kişisel bilgisi gerekmez. Kaynakta kişi adları bulunsa dahi envantere aktarılmaz.

## Bayburt kontrol kaynakları

- https://bayburt.meb.gov.tr/ — ana sayfa 14.103 öğrenci / 133 okul-kurum; dönemi açıklanmayan sayaç. Payda olarak henüz kullanılmaz.
- https://bayburt.meb.gov.tr/www/karne-heycani/icerik/2700/tr — 26.06.2026, 2025–2026'da 14.537 öğrenci karne aldı. Kapsamı tam okul türü listesiyle eşleştirilmelidir.
- https://sgb.meb.gov.tr/istatistik_2026/resmi_istatistik2.html — 2025–2026 örgün eğitim istatistikleri. İl, kademe ve resmî/özel kapsam kontrolü için kullanılacak; tek tek okul hesabının yerine geçmez.
- https://istatistik.meb.gov.tr/OgrenciSayisi/Index — il/kademe sorguları.

18 okul kaydı ana sayfa anlık görüntüleridir. Şair Celali için arama özeti 165 gösterirken açılan kaynak 168 gösterdi; açılan sayfadaki 168 alındı ve kayıtta gözlem tarihi tutuldu. Bu fark güncelleme/önbellek ihtimalinin doğrulamada neden önemli olduğunu gösterir.

## Eksik bilgi ve sınırlar

- `null` ve CSV boş hücre: bilinmiyor. Sıfır ancak kaynak sıfır diyorsa yazılır.
- Eksik yatılılık/ilçe istisnası: alt–üst norm aralığı. Bu aralık istatistiksel güven aralığı değildir; eksik koşulların mümkün sonuçlarıdır.
- Senaryo farkı aynı eksik koşulun her iki modelde aynı değeri almasıyla hesaplanır. Aynı senaryo seçildiğinde fark daima sıfırdır.
- Eğitim yılı olmayan sayılar yeni yıla taşınmaz. Personel verisi başka yıldaysa açık hesaplanmaz.
- Senaryolar yalnızca eşikleri değiştirir; “her X öğrenciye bir PDR” oran modeli ayrı bir politika tanımıdır, bu sürüm onunla eşdeğer değildir.
- Kapsamı eksik toplamlar resmî onaylı kadro, dolu kadro veya Türkiye toplamı olarak sunulmaz.

## Tamamlanma ölçütleri

- Güncel konsolide mevzuatın Madde 21'i ve varsa uygulama yazıları doğrulandı.
- Bayburt tam resmî okul/kurum envanteri ve kurum kodları doğrulandı.
- Her okulda aynı eğitim yılı öğrenci sayısı, istisnalar ve PDR alan kadrosu kontrol edildi.
- Özel eğitim grupları, MESEM çırak sayıları ve RAM görev bölgeleri tamamlandı.
- Hesaplanan norm resmî norm cetveliyle satır satır karşılaştırıldı; farklar açıklanıp kaydedildi.
- İl toplamı yayımlanmadan önce kapsam raporu ve tekrar üretilebilir testler hazırlandı.

Bu ölçütler tamamlanana kadar v0.1 bir kaynak toplama ve hesaplama platformudur; doğrulanmış ihtiyaç araştırmasının tamamlanmış sonucu değildir.


## Tarihsel karşılaştırma: 2021 Bayburt ihtiyaç cetveli

Resmî PDF sayfa 2 görsel olarak doğrulandı. Rehberlik için listelenen beş okulda norm toplamı 6, mevcut 1, bildirilen ihtiyaç 5. Bu bir ihtiyaç listesidir; tüm il norm/personel envanteri değildir. Yayın yılı 2021 eğitim yılı yerine kullanılmaz. Öğrenci sayısı bulunmadığından hesap motorunun öğrenci eşiklerini bu belgeyle doğruladığımız iddia edilmez. Kayıtlar `dist/data/historical-norms.json` içinde tutulur ve güncel okul hesaplarına katılmaz.

Pilot liste 25 okul kaydı içerir. Eğitim yılı belirsiz resmî web sayfası görüntüleri, 2026 eğitim yılı verisi olarak etiketlenmez. Şehit Oktay Altuntaş sayfasındaki 136 değeri, farklı arama önbelleklerindeki 105/137 değerleriyle tutarsızdır; güncel yıl doğrulaması gerektirir.
