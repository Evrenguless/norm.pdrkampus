# Bayburt öğrenci verisi — toplu tarama

Amaç: kamuya açık resmî okul sitelerindeki öğrenci sayılarını hızla toplamak, okul kademelerine göre JSON olarak saklamak. Arayüz geliştirme bu aşamanın kapsamı değildir.

- `students-by-grade.json`: kademe grupları, okul kayıtları ve tarama özeti.
- `seeds.json`: keşfedilen aday alan adları; adaylar kesin okul envanteri değildir.
- `scripts/collect_students.py`: Python standart kütüphanesiyle çalışan tekrar kullanılabilir tarayıcı. Sekiz eşzamanlı görev; kurum başına ana sayfa ve gerekirse iki bilgi sayfası.
- `checkpoint.json`: ara tarama kayıtları.

```sh
python scripts/collect_students.py --seeds research/bayburt/seeds.json --output research/bayburt
```

Her kayıt öğrenci sayısını, okul adını, il/ilçeyi, kademeyi, kaynak URL'sini, görüldüğü tarihi, kısa kanıtı ve denenen sayfaları taşır. Sayısı bulunamayan kayıt `null` olarak kalır. Ana sayfa/bilgi sayfası farklı zamanlarda farklı sayılar verebilir; JSON yalnızca belirtilen kaynak görüntüsüdür.

Eğitim yılı sayfadaki haberlerden çıkarılmaz. Birden çok farklı sayı bulunursa otomatik tek sayı seçilmez. Özel eğitim ayrı gruptur; I/II/III kademeleri kurum adında korunur. RAM ve okul olmayan kurumlar ayrı tutulur. MESEM'in genel öğrenci sayısı çırak/kursiyer sayısı sayılmaz. PDR sayısı toplanmaz.

MEB merkezî okul dizininin kamuya açık HTML sayfasına erişildi. Bağlı veri uç noktası “Erişim yetkiniz yok!” döndürdüğü için bu uç noktadan envanter alınmadı; kamuya açık okul sayfalarıyla ilerlenir. Tohum listesinde arama sonucu PDF'lerine ev sahipliği yapan başka illerin kurumları da bulunabilir: sayfa Bayburt kimliği göstermedikçe Bayburt kaydı sayılmaz.

İl genelindeki bütün aktif kurumların tam listesi doğrulanmadı. Bu veri seti il öğrenci toplamı veya aynı eğitim yılına ait eksiksiz istatistik olarak sunulamaz. Eski platform verileri değiştirilmedi; kaynaklardaki farklı değerler araştırma dosyasında ayrıca incelenir.


## 2026-10-01 Bayburt kapanış durumu

- Güncel okul envanteri: **125 okul** (Merkez 100, Demirözü 16, Aydıntepe 9).
- Öğrenci sayısı doğrulanmış/ikincil kaynakla işaretlenmiş: **116 okul**.
- Kamuya açık doğrulanabilir öğrenci sayısı bulunamayan: **9 okul**. Bunlar veri setinde bilerek `null` bırakıldı; tahmin veya sıfır ataması yapılmadı.
- Ham taramada bulunan fakat güncel il envanterinde yer almayan Fatma Ersoy Anaokulu ve Bayburt Güzel Sanatlar Lisesi güncel 125 okul hesabından çıkarıldı; ham kanıt `checkpoint.json` içinde korunuyor.
- Güncel listede olup ayrı canlı MEB uç noktası doğrulanamayan Veyselefendi İmam Hatip Ortaokulu ve Yunus Emre İmam Hatip Ortaokulu envantere manuel-kaynaklı kayıt olarak eklendi.
- Bilinen okul öğrenci sayılarının toplamı: **13632**. Bu, 9 okulun sayısı eksik olduğu için il toplamı değildir.
- Son üretilen veri: `students-by-grade.json`.
