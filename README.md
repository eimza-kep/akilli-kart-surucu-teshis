# Akıllı Kart ve E-İmza Sürücü Teşhis Aracı 🩺🔏

[![Python CI](https://github.com/eimza-kep/akilli-kart-surucu-teshis/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/akilli-kart-surucu-teshis/actions)
[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Win | Linux | Mac](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue.svg)](https://github.com)
[![Blog](https://img.shields.io/badge/Rehber-E--%C4%B0mza%20Rehberi-22c55e.svg)](https://eimza-rehberi.pages.dev/)

Windows (10/11), Linux ve macOS sistemlerinde e-imza USB token cihazlarının, akıllı kart okuyucularının, **Windows Akıllı Kart Hizmetinin (SCardSvr)** ve Türkiye'deki yetkili ESHS sağlayıcılarına (TÜBİTAK Kamu SM / AKİS, SafeNet / Thales, TÜRKTRUST, E-Tuğra, E-Güven vb.) ait **PKCS#11 sürücülerinin** kurulu olup olmadığını denetleyen açık kaynaklı tanı asistanı.

---

## ✨ Öne Çıkan Özellikler

* 🖥️ **Çoklu Platform:** Windows, Linux ve macOS ortamlarını otomatik tespit eder.
* ⚙️ **Akıllı Kart Servis Kontrolü:** `SCardSvr` (Windows) ve `pcscd` (Linux) hizmet durumunu denetler.
* 📦 **Türkiye ESHS Kapsamı:** AKİS, SafeNet, TÜRKTRUST Palma, E-Tuğra CardOS/Asekey ve OpenSC kütüphanelerini tarar.
* 🔌 **USB Donanım Eşleme:** VID/PID kodlarına göre ACS, Identiv, Aladdin, Feitian ve Omnikey okuyucuları tanır.
* 📊 **Çoklu Çıktı:** Terminal, JSON ve Markdown formatında teşhis raporu üretir.

---

## 🚀 Hızlı Başlangıç

### 1. Python İle Hızlı Teşhis
```bash
python diagnose_token.py
```

### 2. Markdown ve JSON Raporu
```bash
# Markdown formatında rapor oluşturma
python diagnose_token.py --markdown

# Otomasyon için JSON çıktısı
python diagnose_token.py --json
```

### 3. Windows PowerShell Doğrudan Onarım
Windows ortamında tek tıkla servisi onarmak ve kartı denetlemek için:
```powershell
powershell -ExecutionPolicy Bypass -File .\Diagnose-SmartCard.ps1
```

---

## 🔗 E-Dönüşüm Açık Kaynak Ekosistemi

Bu araç [eimza-kep](https://github.com/eimza-kep) organizasyonunun açık kaynak e-dönüşüm araçları ekosisteminin bir parçasıdır:

* 🇹🇷 **[awesome-turkiye-e-donusum](https://github.com/eimza-kep/awesome-turkiye-e-donusum):** Türkiye E-Dönüşüm kütüphane, mevzuat ve araçlar listesi.
* 🔓 **[eimza-pin-bloke-asistani](https://github.com/eimza-kep/eimza-pin-bloke-asistani):** USB token PIN kilitlendiğinde PUK kodu ile sıfırlama terminali.
* 📄 **[python-pdf-eimza-dogrulayici](https://github.com/eimza-kep/python-pdf-eimza-dogrulayici):** PDF belgelerindeki PAdES e-imzaları doğrulama aracı.
* ⏱️ **[mali-muhur-eimza-suresi-kontrol](https://github.com/eimza-kep/mali-muhur-eimza-suresi-kontrol):** Sertifika kalan gün denetimi ve bildirim scripti.
* 🔧 **[gib-java-guvenlik-cozucu](https://github.com/eimza-kep/gib-java-guvenlik-cozucu):** GİB portalları için Java istisna ve güvenlik onarım aracı.

---

## 📚 İlgili Teknik Rehberler
* 📄 [E-İmza Kartı Takılı Ama Okumuyor Hatası Kesin Çözüm Adımları](https://eimza-rehberi.pages.dev/yazilar/e-imza-karti-okumuyor-hatasi-kesin-cozum.html)
* 📄 [Windows 11 Güncellemesi Sonrası Akıllı Kart Servis Onarımı](https://eimza-rehberi.pages.dev/yazilar/windows-11-eimza-akis-kurulum-sorunlari.html)
* 📄 [Mac (macOS Sonoma / Sequoia) Üzerinde E-İmza ve AKİS Kurulumu](https://eimza-rehberi.pages.dev/yazilar/mac-macos-eimza-kurulumu-akis-kart-okuyucu.html)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.