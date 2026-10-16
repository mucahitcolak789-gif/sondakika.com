# Haber sitesi (otomatik güncellenen)

**Nasıl çalışır:** `fetch_news.py` RSS kaynaklarından haberleri çekip `news.json` yazar.
GitHub Actions bunu her 15 dakikada bir otomatik çalıştırır. `index.html` ise
`news.json`'u okuyup gösterir ve açık kaldığı sürece 5 dakikada bir kendini yeniler.

## Kurulum (ücretsiz, ~5 dk)
1. GitHub'da yeni bir repo aç, bu klasördeki tüm dosyaları (`.github` klasörü dahil) yükle.
2. **Settings → Pages → Branch: main / root** seç. Site `kullaniciadi.github.io/repo-adi` adresinde yayına girer.
3. **Actions** sekmesinde "Haberleri güncelle" akışını bir kez **Run workflow** ile elle çalıştır (ilk `news.json` oluşsun).
4. Bundan sonrası kendi kendine döner.

## Bilgisayarında denemek
```
python fetch_news.py
python -m http.server 8000
```
Sonra tarayıcıda `http://localhost:8000` aç (dosyaya çift tıklayarak açarsan `news.json` yüklenmez).

## Özelleştirme
- Kaynak eklemek/çıkarmak: `fetch_news.py` içindeki `FEEDS` listesi.
- Reklam: `index.html` içinde AdSense kodunu ekle, `adSlot()` içindeki div'e reklam birimini koy.
- Not: Kaynak sitelerin RSS adresleri zamanla değişebilir; bir kaynak hata verirse Actions logunda görürsün, diğerleri çalışmaya devam eder.
- Haber metninin tamamını kopyalama; sadece başlık + kısa özet + kaynağa link göstermek telif açısından güvenlidir (script zaten böyle yapıyor).
