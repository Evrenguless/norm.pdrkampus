# PDR Norm — okul bazında ihtiyaç araştırması

Okulun öğrenci sayısını, araştırma dayanağına göre hesaplanan rehberlik normunu ve aynı yıl personel verisi mevcutsa okul açığını gösterir. Önerilen eşiklerle norm düzenlemesinin etkisi karşılaştırılır.

## Çalıştırma

Bağımlılık gerektirmeyen statik uygulama. `dist/` dizinini herhangi bir statik sunucuda açın; ES modülleri ve JSON yüklemesi için dosyayı çift tıklamak yerine HTTP üzerinden servis edin.

```sh
npm test
npm run check
python -m http.server 8080 --directory dist
```

## İlk veri seti

- Bayburt'tan resmî okul internet sayfalarında öğrenci sayısı yayımlanan 25 kurum.
- Gözlem tarihi: 1 Ekim 2026. Öğrenci sayılarının eğitim yılı ve güncelleme tarihi kaynaklarda belirtilmiyor.
- PDR personel sayıları bilinmiyor; genel öğretmen sayısı yerine geçirilmedi.
- Bu liste Bayburt okul envanterinin tamamı değildir; il veya Türkiye geneli açık yayımlanamaz.
- Özel eğitim ortak bina/bahçe ve MESEM çırak verisi eksik olan kayıtlar hesap dışındadır.

## Hukuki durum

Hesap motoru 2021 tarihli MEB okul sitesindeki yönetmelik kopyasının Madde 21 metni için test edilmiştir. MEB güncel mevzuat listesi erişildi; bağlantılı konsolide metin erişim hatası verdi. **Güncel yürürlük doğrulaması tamamlanmadı.** Sonuçlar resmî norm onayı değildir. Mevzuat değişikliği kesinleştiğinde sürümlü bir kural seti eklenmeli; mevcut araştırma dayanağı geriye dönük korunmalıdır.

## Dosyalar

- `dist/engine.js`: temel norm, istisnalar, özel eğitim grup hesabı, MESEM, RAM, belirsizlik ve senaryo farkı.
- `dist/import.js`: CSV/JSON doğrulama, boş değer, yinelenen okul/yıl ve bağlantı kontrolleri.
- `dist/data/schools.json`: kaynaklı okul anlık görüntüleri.
- `dist/data/dictionary.json`: veri sözlüğü.
- `docs/METHODOLOGY.md`: veri toplama, kontrol ve yayın ölçütleri.
- `tests/`: eşik ve veri doğrulama testleri.

CSV veya JSON içe aktarma yalnızca tarayıcı oturumundadır; sunucuya yüklemez. Ortak veri seti `dist/data/schools.json` dosyasıyla, inceleme sonrası sürümlenir. Paylaşım bağlantısı senaryo eşiklerini ve filtreleri taşır, yerel içe aktarılan veriyi taşımaz. Sunucu/üyelik gerektirmeden kaynaklı veri kamuya uygun bir statik platformda yayımlanabilir. İlk önizleme özel erişimlidir.

## Doğrulama

20 otomatik test: eşik sınırları, yatılılık, ilçe istisnası, özel eğitim çift sayım önleme, RAM, MESEM, aynı yıl personel eşleşmesi, okul açığı toplama, belirsiz senaryo farkı, CSV/JSON ve güvenli bağlantılar. WebMCP desteklenirse görünür senaryo/özet işlemleri kayıt edilir; destekli tarayıcı bağlamında doğrulama bu ortamda yapılamadı. Görsel tarayıcı testi yapılmadı.

## Tarihsel resmî veri
2021 Bayburt il içi ihtiyaç cetvelinin Rehberlik satırları ayrı bir JSON ve yöntem ekranında bulunur. Beş satırdaki ihtiyaç toplamı 5; bu güncel il açığı değildir. Öğrenci sayısı ve eğitim yılı bulunmadığından güncel hesap verileriyle birleştirilmez.
