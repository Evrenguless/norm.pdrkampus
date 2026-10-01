# Ardahan öğrenci verisi — toplu tarama

Bu klasör Türkiye geneli ortak veri hattının Bayburt sonrası ilk ölçek testidir.

- İlçeler: Merkez, Çıldır, Damal, Göle, Hanak, Posof.
- Güncel roster başlangıç hedefi: 11 anaokulu, 77 ilkokul, 52 ortaokul, 27 lise ve ayrıca 5 özel eğitim kurumu.
- BİLSEM okul-norm okul evreninden ayrı tutulur.
- `seeds.json` ilk keşif dalgasıdır; `inventory-target.json` içindeki `discovery_status: partial` kaldırılmadan il tamamlanmış sayılmaz.
- Öğrenci sayısı bulunmayan kayıtlara tahmin atanmaz.

Çalıştırma:

```sh
python scripts/run_all.py --province ardahan
```
