<#
.SYNOPSIS
    Windows E-İmza & Akıllı Kart Okuyucu Donanım ve Sürücü Teşhis Aracı

.DESCRIPTION
    Bu betik, Windows üzerinde e-imza cihazlarının (USB Token / Akıllı Kart) neden çalışmadığını
    teşhis eder: Windows Akıllı Kart Servislerini (SCardSvr), USB aygıt kimliklerini (PnP) ve
    yüklü sürücü yazılımlarını (AKİS, SafeNet, ACS) kontrol ederek doğrudan indirme linkleri sunar.

.NOTES
    Yazar: E-İmza & Dijital Dönüşüm Portalı (https://eimza-kep.github.io/eimza-blog/)
    Lisans: MIT
#>

[CmdletBinding()]
param(
    [switch]$FixServices = $false
)

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==========================================================================================" -ForegroundColor Cyan
Write-Host "        WINDOWS E-İMZA & AKILLI KART SÜRÜCÜ TEŞHİS ARACI v1.0                             " -ForegroundColor Yellow
Write-Host "==========================================================================================`n" -ForegroundColor Cyan

# ------------------------------------------------------------------------------
# 1. Windows Akıllı Kart Hizmetleri Denetimi
# ------------------------------------------------------------------------------
Write-Host "[1/3] Windows Hizmetleri Denetleniyor..." -ForegroundColor White

$servicesToCheck = @("SCardSvr", "ScDeviceEnum")
$servicesOk = $true

foreach ($sName in $servicesToCheck) {
    $svc = Get-Service -Name $sName -ErrorAction SilentlyContinue
    if ($svc) {
        $statusColor = if ($svc.Status -eq "Running") { "Green" } else { "Red" }
        Write-Host ("  - Hizmet: {0,-15} | Durum: {1,-10} | Başlangıç: {2}" -f $sName, $svc.Status, $svc.StartType) -ForegroundColor $statusColor
        
        if ($svc.Status -ne "Running") {
            $servicesOk = $false
            if ($FixServices) {
                Write-Host "    [!] $sName hizmeti başlatılıyor ve Otomatik yapılıyor..." -ForegroundColor Yellow
                try {
                    Set-Service -Name $sName -StartupType Automatic -Status Running -ErrorAction Stop
                    Write-Host "    [OK] Hizmet başarıyla başlatıldı!" -ForegroundColor Green
                } catch {
                    Write-Host "    [HATA] Hizmet başlatılamadı. Lütfen yönetici (Admin) olarak çalıştırın." -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "  - Hizmet: $sName bulunamadı!" -ForegroundColor Red
        $servicesOk = $false
    }
}

if (-not $servicesOk -and -not $FixServices) {
    Write-Host "`n  ⚠️  Hizmetler kapalı görünüyor! Otomatik başlatmak için betiği '-FixServices' ile çalıştırın." -ForegroundColor Yellow
}

# ------------------------------------------------------------------------------
# 2. Takılı Akıllı Kart Okuyucular ve USB Donanımları
# ------------------------------------------------------------------------------
Write-Host "`n[2/3] Takılı USB Token ve Akıllı Kart Okuyucular Taranıyor..." -ForegroundColor White

$pnpDevices = Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue | Where-Object {
    $_.PNPClass -eq "SmartCardReader" -or 
    $_.Name -like "*Smart Card*" -or 
    $_.Name -like "*Card Reader*" -or 
    $_.Name -like "*Token*" -or 
    $_.Name -like "*Gemalto*" -or 
    $_.Name -like "*SafeNet*" -or 
    $_.Name -like "*ACS*" -or 
    $_.Name -like "*Identiv*" -or
    $_.Name -like "*Omnikey*"
}

if ($pnpDevices.Count -gt 0) {
    Write-Host "  Bulunan Aygıtlar ($($pnpDevices.Count) Adet):" -ForegroundColor Green
    foreach ($dev in $pnpDevices) {
        $stateColor = if ($dev.Status -eq "OK") { "Green" } else { "Red" }
        Write-Host "  --------------------------------------------------------" -ForegroundColor Gray
        Write-Host "  Ad:            $($dev.Name)" -ForegroundColor White
        Write-Host "  Durum:         $($dev.Status)" -ForegroundColor $stateColor
        Write-Host "  Üretici:       $($dev.Manufacturer)" -ForegroundColor Gray
        Write-Host "  Donanım Kimliği: $($dev.HardwareID[0])" -ForegroundColor DarkGray
    }
} else {
    Write-Host "  [!] Takılı bir Akıllı Kart Okuyucu veya e-İmza USB cihazı tespit edilemedi." -ForegroundColor Yellow
    Write-Host "      - USB Token'ı farklı bir USB 2.0 veya 3.0 portuna takmayı deneyin." -ForegroundColor Gray
    Write-Host "      - Cihazınızın üzerindeki LED ışığının yandığından emin olun." -ForegroundColor Gray
}

# ------------------------------------------------------------------------------
# 3. Yüklü Sürücü ve Middleware Yazılımları
# ------------------------------------------------------------------------------
Write-Host "`n[3/3] Yüklü E-İmza Yazılımları (Middleware) Kontrol Ediliyor..." -ForegroundColor White

$installedApps = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*, 
                                  HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
                 Select-Object DisplayName, DisplayVersion, Publisher |
                 Where-Object { 
                    $_.DisplayName -like "*AKIS*" -or 
                    $_.DisplayName -like "*SafeNet*" -or 
                    $_.DisplayName -like "*Gemalto*" -or 
                    $_.DisplayName -like "*Kamu SM*" -or 
                    $_.DisplayName -like "*ACS*" -or
                    $_.DisplayName -like "*E-Tugra*" -or
                    $_.DisplayName -like "*TURKTRUST*" -or
                    $_.DisplayName -like "*Akıllı Kart*"
                 }

if ($installedApps.Count -gt 0) {
    Write-Host "  Yüklü Sürücüler:" -ForegroundColor Green
    foreach ($app in $installedApps) {
        Write-Host ("  - {0,-35} | Sürüm: {1,-10} | {2}" -f $app.DisplayName, $app.DisplayVersion, $app.Publisher) -ForegroundColor White
    }
} else {
    Write-Host "  [!] Sistemde AKİS, SafeNet veya Kamu SM sürücüsü tespit edilemedi!" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# Öneriler & Resmi Sürücü İndirme Bağlantıları
# ------------------------------------------------------------------------------
Write-Host "`n==========================================================================================" -ForegroundColor Cyan
Write-Host "                      RESMİ SÜRÜCÜ İNDİRME BAĞLANTILARI                                    " -ForegroundColor Yellow
Write-Host "==========================================================================================" -ForegroundColor Cyan
Write-Host "E-imza modelinize göre resmi üretici sürücülerini aşağıdan indirebilirsiniz:" -ForegroundColor White
Write-Host "1. AKİS (Akıllı Kart İşletim Sistemi - TÜBİTAK):" -ForegroundColor Cyan
Write-Host "   👉 https://akiskart.bilgem.tubitak.gov.tr/destek/" -ForegroundColor White
Write-Host "2. Kamu SM Sürücü Deposu (Tüm İşletim Sistemleri):" -ForegroundColor Cyan
Write-Host "   👉 https://kamusm.bilgem.tubitak.gov.tr/islemler/surucu_indirme/" -ForegroundColor White
Write-Host "3. SafeNet Authentication Client (Thales/Gemalto eToken):" -ForegroundColor Cyan
Write-Host "   👉 https://www.turktrust.com.tr/tr/suruculer" -ForegroundColor White
Write-Host "4. ACS ACR38 / ACR39 Sürücüleri:" -ForegroundColor Cyan
Write-Host "   👉 https://www.acs.com.hk/en/driver/4/acr38u-pocketmate-smart-card-reader/" -ForegroundColor White

Write-Host "`nDetaylı Çözüm Kılavuzu: https://eimza-kep.github.io/eimza-blog/posts/windows-11-akilli-kart-taninmiyor-cozumu.html" -ForegroundColor Yellow
Write-Host "==========================================================================================`n" -ForegroundColor Cyan
