#!/usr/bin/env bash
# ==============================================================================
# Akıllı Kart ve E-İmza Donanım / Sürücü Teşhis Aracı (macOS & Linux) v1.3
# ==============================================================================
# macOS Sequoia (15.x), Sonoma, Ventura (Apple Silicon M1-M4 & Intel) ve
# Linux (Ubuntu, Debian, Fedora, Arch, RHEL) için tek tıkla e-imza donanım,
# akıllı kart okuyucu, pcscd servisi, Apple CryptoTokenKit ve PKCS#11 teşhis betiği.
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}   AKILLI KART VE E-İMZA SÜRÜCÜ TEŞHİS ARACI (macOS / Linux) v1.3${NC}"
echo -e "${CYAN}==================================================================${NC}"

# 1. İşletim Sistemi ve Mimari Tespiti
OS="$(uname -s)"
ARCH="$(uname -m)"

echo -e "\n${BLUE}[1/6] Sistem Bilgileri:${NC}"
echo "  İşletim Sistemi : $OS"
echo "  İşlemci Mimarisi: $ARCH"

IS_MACOS=false
IS_LINUX=false
IS_APPLE_SILICON=false

if [ "$OS" = "Darwin" ]; then
    IS_MACOS=true
    MACOS_VER=$(sw_vers -productVersion 2>/dev/null || echo "Bilinmiyor")
    echo "  macOS Sürümü    : $MACOS_VER"
    if [ "$ARCH" = "arm64" ]; then
        IS_APPLE_SILICON=true
        echo -e "  ${GREEN}✓ Apple Silicon (M1/M2/M3/M4) Donanımı Tespit Edildi${NC}"
    fi
elif [ "$OS" = "Linux" ]; then
    IS_LINUX=true
    if [ -f /etc/os-release ]; then
        DISTRO=$(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')
        echo "  Linux Dağıtımı  : $DISTRO"
    fi
fi

# 2. Akıllı Kart Servis Kontrolü (pcscd / com.apple.ifdreader)
echo -e "\n${BLUE}[2/6] Akıllı Kart Servis Durumu:${NC}"

if [ "$IS_MACOS" = true ]; then
    if pgrep -x "com.apple.ifdreader" >/dev/null || pgrep -f "SmartCard" >/dev/null; then
        echo -e "  ${GREEN}✓ macOS CryptoTokenKit / SmartCard servisi aktif ve çalışıyor.${NC}"
    else
        echo -e "  ${YELLOW}⚠ SmartCard servisi arka planda hazır bekliyor (Tak-Çalıştır).${NC}"
    fi
elif [ "$IS_LINUX" = true ]; then
    if systemctl is-active --quiet pcscd 2>/dev/null; then
        echo -e "  ${GREEN}✓ pcscd (PC/SC Akıllı Kart Daemon) servisi ÇALIŞIYOR.${NC}"
    else
        echo -e "  ${RED}✗ pcscd servisi çalışmıyor veya durdurulmuş!${NC}"
        echo -e "    Çözüm: 'sudo systemctl enable --now pcscd' komutuyla başlatın."
    fi
fi

# 3. macOS CryptoTokenKit (TKSmartCardSlotManager) Denetimi
if [ "$IS_MACOS" = true ]; then
    echo -e "\n${BLUE}[3/6] Apple CryptoTokenKit Durumu:${NC}"
    if command -v security >/dev/null; then
        CTK_STATUS=$(security smartcards status 2>/dev/null || true)
        if [[ "$CTK_STATUS" != *"disabled"* ]]; then
            echo -e "  ${GREEN}✓ CryptoTokenKit (Modern macOS Akıllı Kart Altyapısı) AKTİF.${NC}"
        else
            echo -e "  ${YELLOW}⚠ CryptoTokenKit devre dışı bırakılmış görünüyor.${NC}"
        fi

        # Takılı modern token listesi
        TOKENS=$(security smartcards token -l 2>/dev/null || true)
        if [ -n "$TOKENS" ]; then
            echo -e "  ${GREEN}✓ CryptoTokenKit Tarafından Tanınan Tokenlar:${NC}"
            echo "$TOKENS" | while read -r line; do echo "    $line"; done
        else
            echo "    (CryptoTokenKit üzerinde henüz eşleşmiş token kaydı bulunmuyor)"
        fi
    fi
fi

# 4. Takılı USB Kart Okuyucu Kontrolü
STEP_TITLE="[4/6]"
if [ "$IS_MACOS" = false ]; then STEP_TITLE="[3/5]"; fi
echo -e "\n${BLUE}${STEP_TITLE} Takılı USB Kart Okuyucu Donanımları:${NC}"

READERS_FOUND=0

if [ "$IS_MACOS" = true ]; then
    if command -v system_profiler >/dev/null; then
        USB_READERS=$(system_profiler SPUSBDataType 2>/dev/null | grep -Ei "CCID|Smart Card|Token|ACS|SafeNet|Omnikey|Feitian|Gemalto" || true)
        if [ -n "$USB_READERS" ]; then
            echo -e "  ${GREEN}✓ Takılı Kart Okuyucular:${NC}"
            echo "$USB_READERS" | while read -r line; do echo "    $line"; done
            READERS_FOUND=1
        fi
    fi
elif [ "$IS_LINUX" = true ]; then
    if command -v lsusb >/dev/null; then
        USB_READERS=$(lsusb | grep -Ei "072f:|0529:|076b:|096e:|08e6:|SmartCard|CCID|Token" || true)
        if [ -n "$USB_READERS" ]; then
            echo -e "  ${GREEN}✓ Takılı Kart Okuyucular:${NC}"
            echo "$USB_READERS" | while read -r line; do echo "    $line"; done
            READERS_FOUND=1
        fi
    fi
fi

if [ "$READERS_FOUND" -eq 0 ]; then
    echo -e "  ${YELLOW}⚠ Takılı bir Akıllı Kart Okuyucu veya USB Token tespit edilemedi.${NC}"
    echo "    (Cihazı farklı bir USB portuna veya Type-C dönüştürücüye takıp tekrar deneyin)"
fi

# 5. Yüklü PKCS#11 E-İmza Kütüphaneleri
STEP_PKCS="[5/6]"
if [ "$IS_MACOS" = false ]; then STEP_PKCS="[4/5]"; fi
echo -e "\n${BLUE}${STEP_PKCS} PKCS#11 Sürücü Kütüphaneleri Taraması:${NC}"

LIBS_TO_CHECK=()

if [ "$IS_MACOS" = true ]; then
    LIBS_TO_CHECK=(
        "/opt/homebrew/lib/libakisp11.dylib:TÜBİTAK AKİS (Homebrew Apple Silicon arm64)"
        "/usr/local/lib/libakisp11.dylib:TÜBİTAK AKİS (/usr/local/lib)"
        "/Applications/AKIS/libakisp11.dylib:TÜBİTAK AKİS (Resmi Uygulama)"
        "/Applications/AKIS.app/Contents/Resources/libakisp11.dylib:TÜBİTAK AKİS App Paketi"
        "/Library/Frameworks/AkiS.framework/AkiS:TÜBİTAK AKİS Framework"
        "/Library/Frameworks/eToken.framework/Versions/A/libeToken.dylib:SafeNet / Thales eToken"
        "/usr/local/lib/libeTPKCS11.dylib:SafeNet eTPKCS11"
        "/opt/homebrew/lib/libeTPKCS11.dylib:SafeNet (Homebrew arm64)"
        "/Library/Frameworks/bit4ipki.framework/bit4ipki:TÜRKTRUST / Bit4id"
        "/Library/OpenSC/lib/opensc-pkcs11.dylib:OpenSC PKCS#11"
        "/opt/homebrew/lib/opensc-pkcs11.dylib:OpenSC (Apple Silicon arm64)"
    )
elif [ "$IS_LINUX" = true ]; then
    LIBS_TO_CHECK=(
        "/usr/lib/libakisp11.so:TÜBİTAK AKİS (/usr/lib)"
        "/usr/local/lib/libakisp11.so:TÜBİTAK AKİS (/usr/local/lib)"
        "/usr/lib/x86_64-linux-gnu/libakisp11.so:TÜBİTAK AKİS (Debian/Ubuntu 64-bit)"
        "/usr/lib/aarch64-linux-gnu/libakisp11.so:TÜBİTAK AKİS (ARM64 Linux)"
        "/usr/lib/libeTPKCS11.so:SafeNet eToken PKCS#11"
        "/usr/lib/libbit4ipki.so:TÜRKTRUST Bit4id"
        "/usr/lib/libasepkcs.so:E-Tuğra Asekey"
        "/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so:OpenSC 64-bit"
        "/usr/lib/opensc-pkcs11.so:OpenSC Standart"
    )
fi

FOUND_COUNT=0
for item in "${LIBS_TO_CHECK[@]}"; do
    FILE="${item%%:*}"
    DESC="${item##*:}"
    if [ -f "$FILE" ] || [ -d "$FILE" ]; then
        echo -e "  ${GREEN}✓ [BULUNDU]${NC} $DESC -> $FILE"
        FOUND_COUNT=$((FOUND_COUNT + 1))
    fi
done

if [ "$FOUND_COUNT" -eq 0 ]; then
    echo -e "  ${YELLOW}⚠ Sistemde yüklü standart bir PKCS#11 sürücüsü bulunamadı.${NC}"
    if [ "$IS_MACOS" = true ]; then
        echo "    Öneri (macOS Sequoia & Apple Silicon):"
        echo "    1) Kamu SM AKİS güncel arm64 paketini kurun."
        echo "    2) Veya Homebrew ile OpenSC kurun: 'brew install opensc'"
    elif [ "$IS_LINUX" = true ]; then
        echo "    Öneri: 'sudo apt install pcscd opensc' veya AKİS .deb/.rpm paketini yükleyin."
    fi
fi

# 6. Sonuç ve Özet
echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                       TEŞHİS ÖZETİ                              ${NC}"
echo -e "${CYAN}==================================================================${NC}"
if [ "$FOUND_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Sisteminiz e-imza kullanımı için gerekli sürücülere sahip.${NC}"
    echo "  UYAP, EBYS veya tarayıcılarda imzalama yaparken yukarıda bulunan"
    echo "  PKCS#11 kütüphanesini referans gösterebilirsiniz."
else
    echo -e "${YELLOW}⚠ Sürücü kurulumu yapılması tavsiye edilir.${NC}"
fi
echo -e "${CYAN}==================================================================${NC}\n"
