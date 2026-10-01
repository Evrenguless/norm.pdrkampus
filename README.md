# PDR Norm — okul bazında ihtiyaç araştırması

Okulun öğrenci sayısını, araştırma dayanağına göre hesaplanan rehberlik normunu ve aynı yıl personel verisi mevcutsa okul açığını gösterir. Önerilen eşiklerle norm düzenlemesinin etkisi karşılaştırılır.

## Çalıştırma

Bağımlılık gerektirmeyen statik uygulama. `dist/` dizinini herhangi bir statik sunucuda açın; ES modülleri ve JSON yüklemesi için dosyayı çift tıklamak yerine HTTP üzerinden servis edin.

```sh
npm test
npm run check
python -m http.server 8080 --directory dist
```

## Araştırma veri hattı

Bayburt pilotu 1 Ekim 2026 itibarıyla 125 aktif okul hedefiyle uzlaştırılmıştır. Öğrenci sayısı kamuya açık kaynakta doğrulanamayan okullar veri setinde tahmin edilmeden `null` bırakılır; PDR personel sayısı bilinmiyorsa genel öğretmen sayısı bunun yerine kullanılmaz.

Veri toplama artık il bağımsızdır:

```sh
python scripts/collect_students.py --config research/bayburt/config.json
python scripts/run_all.py --province bayburt
python scripts/run_all.py
```

Yeni il eklemek için `research/_template/` şablonu kopyalanır; `config.json` içine il ve ilçeler, `seeds.json` içine doğrulanacak MEB okul uç noktaları yazılır. Aynı `scripts/collect_students.py` motoru tüm illerde kullanılır.

## Hukuki durum

Hesap motoru 2021 tarihli MEB okul sitesindeki yönetmelik kopyasının Madde 21 metni için test edilmiştir. MEB güncel mevzuat listesi erişildi; bağlantılı konsolide metin erişim hatası verdi. **Güncel yürürlük doğrulaması tamamlanmadı.** Sonuçlar resmî norm onayı değildir. Mevzuat değişikliği kesinleştiğinde sürümlü bir kural seti eklenmeli; mevcut araştırma dayanağı geriye dönük korunmalıdır.

## Dosyalar

- `dist/engine.js`: temel norm, istisnalar, özel eğitim grup hesabı, MESEM, RAM, belirsizlik ve senaryo farkı.
- `dist/import.js`: CSV/JSON doğrulama, boş değer, yinelenen okul/yıl ve bağlantı kontrolleri.
- `dist/data/schools.json`: kaynaklı okul anlık görüntüleri.
- `dist/data/dictionary.json`: veri sözlüğü.
- `docs/METHODOLOGY.md`: veri toplama, kontrol ve yayın ölçütleri.
- `scripts/collect_students.py`: tüm iller için ortak okul sayfası tarayıcısı.
- `scripts/run_all.py`: tek ili veya tüm yapılandırılmış illeri çalıştırır.
- `research/<il>/config.json`: il adı, ilçeler ve tarama ayarları.
- `research/_template/`: yeni il için minimum dosya şablonu.
- `tests/`: eşik ve veri doğrulama testleri.

CSV veya JSON içe aktarma yalnızca tarayıcı oturumundadır; sunucuya yüklemez. Ortak veri seti `dist/data/schools.json` dosyasıyla, inceleme sonrası sürümlenir. Paylaşım bağlantısı senaryo eşiklerini ve filtreleri taşır, yerel içe aktarılan veriyi taşımaz. Sunucu/üyelik gerektirmeden kaynaklı veri kamuya uygun bir statik platformda yayımlanabilir. İlk önizleme özel erişimlidir.

## Doğrulama

20 otomatik test: eşik sınırları, yatılılık, ilçe istisnası, özel eğitim çift sayım önleme, RAM, MESEM, aynı yıl personel eşleşmesi, okul açığı toplama, belirsiz senaryo farkı, CSV/JSON ve güvenli bağlantılar. WebMCP desteklenirse görünür senaryo/özet işlemleri kayıt edilir; destekli tarayıcı bağlamında doğrulama bu ortamda yapılamadı. Görsel tarayıcı testi yapılmadı.

## Tarihsel resmî veri
2021 Bayburt il içi ihtiyaç cetvelinin Rehberlik satırları ayrı bir JSON ve yöntem ekranında bulunur. Beş satırdaki ihtiyaç toplamı 5; bu güncel il açığı değildir. Öğrenci sayısı ve eğitim yılı bulunmadığından güncel hesap verileriyle birleştirilmez.

## Araştırma odağı
Öğrenci verilerinden norm ihtiyacı ve düzenlemenin ilave norm etkisi hesaplanır. Ana tablolar personel sayısı gerektirmez. Senaryo ekranında seçili kayıtların il ve ilçe bazında kısmi toplamları gösterilir. Personel verisi ileride doğrulanırsa ayrıntı/CSV üzerinden açık hesabı ayrıca incelenebilir.
