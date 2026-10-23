# Akıllı Kart ve E-İmza Sürücü Teşhis Aracı 🩺🔏

[![Python CI](https://github.com/eimza-kep/akilli-kart-surucu-teshis/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/akilli-kart-surucu-teshis/actions)
[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Win | Linux | macOS](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue.svg)](https://github.com)
[![Apple Silicon](https://img.shields.io/badge/macOS-Apple%20Silicon%20M1--M4%20%7C%20Sequoia-black.svg)](diagnose_smartcard.sh)
[![Blog](https://img.shields.io/badge/Rehber-E--%C4%B0mza%20Rehberi-22c55e.svg)](https://eimzabilgi.site/)

Windows (10/11), Linux ve macOS (**macOS 15 Sequoia, Apple Silicon M1-M4 arm64**) sistemlerinde e-imza USB token cihazlarının, akıllı kart okuyucularının, **Windows Akıllı Kart Hizmetinin (SCardSvr)**, Linux **pcscd** ve macOS **Apple CryptoTokenKit (TKSmartCardSlotManager)** altyapısının yanı sıra Türkiye'deki yetkili ESHS sağlayıcılarına (TÜBİTAK Kamu SM / AKİS, SafeNet / Thales, TÜRKTRUST, E-Tuğra, E-Güven vb.) ait **PKCS#11 sürücülerinin** kurulu olup olmadığını denetleyen açık kaynaklı tanı ve onarım asistanı.

---

## ✨ Öne Çıkan Özellikler (v1.3)

* 🍏 **macOS Sequoia (15.x) & Apple Silicon (M1-M4):** Apple'ın modern CryptoTokenKit (`security smartcards`) mimarisi ve Homebrew arm64 kütüphane yollarını denetler.
* 🖥️ **Çoklu Platform:** Windows (10/11), Linux (Ubuntu, Debian, Fedora, Arch) ve macOS ortamlarını otomatik tespit eder.
* ⚙️ **Akıllı Kart Servis Teşhisi:** `SCardSvr` (Windows), `pcscd` (Linux) ve CryptoTokenKit (macOS) hizmet sağlığını kontrol eder.
* 📦 **Türkiye ESHS Kapsamı:** TÜBİTAK AKİS, SafeNet eToken, TÜRKTRUST Palma, E-Tuğra CardOS/Asekey ve OpenSC kütüphanelerini tarar.
* 🔌 **USB Donanım Eşleme:** VID/PID kodlarına göre ACS, Identiv, Aladdin, Feitian ve Omnikey kart okuyucuları tanır.
* 🚦 **CI/CD & Otomasyon Desteği:** `--strict` parametresi ile eksik sürücü veya servis durması durumunda `exit code 1` üretir.
* 📊 **Esnek Raporlama:** Renkli terminal çıktısı, Bash/PowerShell, JSON ve Markdown formatlarında rapor üretir.

---

## 🛠️ Kurulum ve Yerel Geliştirme (Local Setup)

### Sistem Gereksinimleri
- Python 3.8 veya üzeri
- `git`
- (Windows için) Akıllı kart servis denetimi için `sc.exe` (varsayılan mevcuttur)
- (macOS için) Terminal ve CryptoTokenKit araçları (`security`)
- (Linux için) `pcscd` ve `systemctl`

### 1. Depoyu Klonlama ve Çalışma Ortamı
```bash
# Depoyu klonlayın
git clone https://github.com/eimza-kep/akilli-kart-surucu-teshis.git
cd akilli-kart-surucu-teshis

# Sanal ortam (virtualenv) oluşturma ve aktifleştirme (Opsiyonel)
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 2. Birim Testleri Çalıştırma
```bash
python test_diagnose.py
```
veya `unittest` keşif mekanizmasıyla:
```bash
python -m unittest discover -v
```

---

## 🚀 Hızlı Başlangıç ve Kullanım Kılavuzu

### 1. Python İle Çapraz Platform Hızlı Teşhis
```bash
python diagnose_token.py
```

### 2. macOS (Sequoia & Apple Silicon) ve Linux İçin Tek Tıkla Shell Teşhisi
macOS Sequoia (M1/M2/M3/M4) ve Linux dağıtımlarında doğrudan çalıştırmak için:
```bash
chmod +x diagnose_smartcard.sh
./diagnose_smartcard.sh
```

### 3. Windows PowerShell Doğrudan Onarım
Windows ortamında tek tıkla `SCardSvr` servisini onarmak ve kartı denetlemek için:
```powershell
powershell -ExecutionPolicy Bypass -File .\Diagnose-SmartCard.ps1
```

### 4. Markdown ve JSON Raporu Üretme
```bash
# Markdown formatında rapor oluşturma
python diagnose_token.py --markdown

# Otomasyon ve izleme sistemleri için JSON çıktısı
python diagnose_token.py --json

# CI/CD pipeline'larında kontrol (Hata varsa exit code 1)
python diagnose_token.py --strict
```

---

## 🍏 macOS Sequoia (15.x) ve Apple Silicon (M1-M4) CryptoTokenKit Kılavuzu

macOS 15 (Sequoia) ve Apple Silicon mimarisinde eski 32-bit veya x86_64 `.dylib` sürücüleri sandbox kısıtlamalarına takılabilmektedir. Bu asistan, Apple'ın modern **CryptoTokenKit** altyapısını ve Homebrew arm64 yollarını otomatik denetler.

### Yararlı Terminal Komutları (macOS):
```bash
# 1. CryptoTokenKit durumunu kontrol etme:
security smartcards status

# 2. Takılı ve CryptoTokenKit tarafından tanınan tokenları listeleme:
security smartcards token -l

# 3. Apple Silicon (arm64) OpenSC PKCS#11 sürücüsünü Homebrew ile kurma:
brew install opensc
```

---

## 🔧 Akıllı Kart Servis Sorunlarını Giderme (Troubleshooting)

| Platform | Belirti | Çözüm Komutu |
|:---|:---|:---|
| **Windows** | `SCardSvr Durduruldu` | Yönetici CMD/PowerShell: `net start SCardSvr` |
| **Linux** | `pcscd servisi çalışmıyor` | Terminal: `sudo systemctl enable --now pcscd` |
| **macOS** | `Token algılanmıyor` | `security smartcards token -l` ile kontrol edin, USB Type-C portunu değiştirin |

---

## 📦 Desteklenen PKCS#11 Kütüphane Yolları

| ESHS / Sağlayıcı | Windows (DLL) | Linux (SO) | macOS (Dylib/Framework) |
|:---|:---|:---|:---|
| **TÜBİTAK AKİS** | `akisp11.dll` | `libakisp11.so` | `/opt/homebrew/lib/libakisp11.dylib`, `libakisp11.dylib` |
| **SafeNet / Thales** | `eTPKCS11.dll` | `libeTPKCS11.so` | `libeTPKCS11.dylib`, `eToken.framework` |
| **TÜRKTRUST** | `bit4ipki.dll`, `aetpkss1.dll` | `libbit4ipki.so` | `bit4ipki.framework` |
| **E-Tuğra** | `siecap11.dll`, `asepkcs.dll` | `libasepkcs.so` | — |
| **OpenSC** | `opensc-pkcs11.dll` | `opensc-pkcs11.so` | `/opt/homebrew/lib/opensc-pkcs11.dylib` |

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
* 📄 [E-İmza Kartı Takılı Ama Okumuyor Hatası Kesin Çözüm Adımları](https://eimzabilgi.site/yazilar/e-imza-karti-okumuyor-hatasi-kesin-cozum.html)
* 📄 [Windows 11 Güncellemesi Sonrası Akıllı Kart Servis Onarımı](https://eimzabilgi.site/yazilar/windows-11-eimza-akis-kurulum-sorunlari.html)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
