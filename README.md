# Windows E-İmza & Akıllı Kart Okuyucu Teşhis Aracı 🔍💳

[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg)](https://microsoft.com)
[![PowerShell](https://img.shields.io/badge/PowerShell-5.1%2B%20%7C%207%2B-blueviolet.svg)](https://github.com/PowerShell/PowerShell)
[![Blog](https://img.shields.io/badge/Rehber-E--%C4%B0mza%20Blog-22c55e.svg)](https://eimza-kep.github.io/eimza-blog/)

Windows 10 ve özellikle **Windows 11** güncellemelerinden sonra en sık karşılaşılan e-imza sorunlarının başında:

> **"Akıllı kart takılı değil"**  
> **"Kart okuyucu bulunamadı"**  
> **"Smart Card Resource Manager has stopped"**  
> veya Aygıt Yöneticisi'nde kart okuyucunun yanında **sarı ünlem işareti** çıkması gelir.

Bu araç; Windows sistem hizmetlerini, USB kart okuyucu donanımlarını ve yüklü sürücüleri (AKİS, SafeNet, ACS, Kamu SM) saniyeler içinde tarayarak **hatayı tespit eder ve doğrudan resmi sürücü indirme bağlantılarını sunar.**

---

## 🖥️ Teşhis Ekranı Çıktısı

```text
==========================================================================================
        WINDOWS E-İMZA & AKILLI KART SÜRÜCÜ TEŞHİS ARACI v1.0                             
==========================================================================================

[1/3] Windows Hizmetleri Denetleniyor...
  - Hizmet: SCardSvr        | Durum: Running    | Başlangıç: Automatic
  - Hizmet: ScDeviceEnum    | Durum: Running    | Başlangıç: Manual

[2/3] Takılı USB Token ve Akıllı Kart Okuyucular Taranıyor...
  Bulunan Aygıtlar (1 Adet):
  --------------------------------------------------------
  Ad:            ACS CCID USB Smart Card Reader
  Durum:         OK
  Üretici:       Advanced Card Systems Ltd.
  Donanım Kimliği: USB\VID_072F&PID_90CC&REV_0100

[3/3] Yüklü E-İmza Yazılımları (Middleware) Kontrol Ediliyor...
  Yüklü Sürücüler:
  - AKIS Kart İzleme Aracı               | Sürüm: 2.1.2      | TÜBİTAK BİLGEM
```

---

## 🚀 Hızlı Kullanım

### 1. Doğrudan Çalıştırma
* Repoyu indirin ve **`diagnose.bat`** dosyasına çift tıklayın.

### 2. Hizmetleri Otomatik Onarma (Önerilen)
Eğer Windows Akıllı Kart Hizmeti (`SCardSvr`) kapalıysa veya çökmüşse, tek komutla otomatik başlatmak ve başlangıç türünü "Otomatik" yapmak için:
```powershell
.\Diagnose-SmartCard.ps1 -FixServices
```

---

## 📥 Resmi Sürücü İndirme Bağlantıları (En Sık Kullanılanlar)

1. **AKİS (Akıllı Kart İşletim Sistemi - TÜBİTAK UEKAE):**  
   Türkiye'deki e-imzaların %80'inde kullanılan milli işletim sistemi.  
   👉 [AKİS Resmi İndirme Portalı](https://akiskart.bilgem.tubitak.gov.tr/destek/)
2. **Kamu SM Sürücü Deposu:**  
   TÜBİTAK Kamu SM tarafından dağıtılan kart okuyucu ve sertifika araçları.  
   👉 [Kamu SM Sürücü Sayfası](https://kamusm.bilgem.tubitak.gov.tr/islemler/surucu_indirme/)
3. **SafeNet Authentication Client (Thales / Gemalto eToken):**  
   TÜRKTRUST ve E-Güven tarafından sıklıkla verilen siyah/mavi USB token'lar.  
   👉 [TÜRKTRUST Sürücüleri](https://www.turktrust.com.tr/tr/suruculer)
4. **ACS ACR38 / ACR39 Sürücüleri:**  
   En yaygın cep tipi kart okuyucu kasanın sürücüsü.  
   👉 [ACS Resmi İndirme Sayfası](https://www.acs.com.hk/en/driver/4/acr38u-pocketmate-smart-card-reader/)

---

## 📚 Detaylı Rehberler

* 📄 [Windows 11'de 'Akıllı Kart Tanınmıyor' Hatası ve e-İmza Sürücü Çözümleri](https://eimza-kep.github.io/eimza-blog/posts/windows-11-akilli-kart-taninmiyor-cozumu.html)
* 📄 [E-İmza Cihazları (USB Token) Nasıl Çalışır? Çipin İçindeki Teknik Dünya](https://eimza-kep.github.io/eimza-blog/posts/e-imza-cihazlari-nasil-calisir-teknik-rehber.html)
* 📄 [Hekimler İçin SGK Medula e-Reçete: e-İmza Kurulumu ve Sertifika Okunamadı Hatası](https://eimza-kep.github.io/eimza-blog/posts/medula-e-recete-e-imza-kurulum-sorunlari.html)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile sunulmaktadır.
