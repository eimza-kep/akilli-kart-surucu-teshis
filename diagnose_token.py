#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Akıllı Kart ve E-İmza Donanım / Sürücü Teşhis Aracı v1.3
=========================================================
Windows, Linux ve macOS (macOS 15 Sequoia, Apple Silicon M1-M4) ortamlarında
takılı akıllı kart okuyucuları, Akıllı Kart Servisini (SCardSvr / pcscd),
Apple CryptoTokenKit (TKSmartCardSlotManager) durumunu ve Türkiye ESHS
sağlayıcılarının (AKİS, SafeNet, TÜRKTRUST, E-Tuğra, E-Güven vb.)
PKCS#11 sürücülerini denetler.

Özellikler:
- Sıfır Harici Bağımlılık (Pure Python Standart Kütüphane)
- Apple Silicon (M1/M2/M3/M4) ve macOS Sequoia (15.x) CryptoTokenKit desteği
- Windows Akıllı Kart Servisi (SCardSvr) ve PC/SC Sürücü Taraması
- Linux pcscd ve OpenSC Sürücü Taraması
- VID/PID donanım eşleme tablosu
- Markdown ve JSON formatında raporlama
- CI/CD ve otomasyonlar için --strict modu

Yazar: E-İmza & Dijital Dönüşüm Portalı (https://eimzabilgi.site/)
Lisans: MIT
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path

# Windows konsolunda UTF-8 çıktı desteği
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

KNOWN_PKCS11_LIBS = {
    "AKİS (TÜBİTAK BİLGEM / Kamu SM)": {
        "win": [
            r"C:\Windows\System32\akisp11.dll",
            r"C:\Windows\SysWOW64\akisp11.dll"
        ],
        "linux": [
            "/usr/lib/libakisp11.so",
            "/usr/local/lib/libakisp11.so",
            "/usr/lib/x86_64-linux-gnu/libakisp11.so",
            "/usr/lib/aarch64-linux-gnu/libakisp11.so"
        ],
        "darwin": [
            "/usr/local/lib/libakisp11.dylib",
            "/opt/homebrew/lib/libakisp11.dylib",
            "/Applications/AKIS/libakisp11.dylib",
            "/Applications/AKIS.app/Contents/Resources/libakisp11.dylib",
            "/Library/Frameworks/AkiS.framework/AkiS"
        ]
    },
    "SafeNet / Thales eToken (E-Güven & TÜRKTRUST)": {
        "win": [
            r"C:\Windows\System32\eTPKCS11.dll",
            r"C:\Windows\SysWOW64\eTPKCS11.dll"
        ],
        "linux": [
            "/usr/lib/libeTPKCS11.so",
            "/usr/local/lib/libeTPKCS11.so"
        ],
        "darwin": [
            "/usr/local/lib/libeTPKCS11.dylib",
            "/opt/homebrew/lib/libeTPKCS11.dylib",
            "/Library/Frameworks/eToken.framework/Versions/A/libeToken.dylib"
        ]
    },
    "TÜRKTRUST / Bit4id (Palma & Minisign)": {
        "win": [
            r"C:\Windows\System32\bit4ipki.dll",
            r"C:\Windows\SysWOW64\bit4ipki.dll",
            r"C:\Windows\System32\aetpkss1.dll"
        ],
        "linux": [
            "/usr/lib/libbit4ipki.so"
        ],
        "darwin": [
            "/Library/Frameworks/bit4ipki.framework/bit4ipki",
            "/usr/local/lib/libbit4ipki.dylib"
        ]
    },
    "E-Tuğra / EBG Bilişim (CardOS & Asekey)": {
        "win": [
            r"C:\Windows\System32\siecap11.dll",
            r"C:\Windows\SysWOW64\siecap11.dll",
            r"C:\Windows\System32\asepkcs.dll"
        ],
        "linux": [
            "/usr/lib/libasepkcs.so"
        ],
        "darwin": []
    },
    "OpenSC (Açık Kaynak Kart Desteği)": {
        "win": [
            r"C:\Program Files\OpenSC Project\OpenSC\pkcs11\opensc-pkcs11.dll",
            r"C:\Program Files (x86)\OpenSC Project\OpenSC\pkcs11\opensc-pkcs11.dll"
        ],
        "linux": [
            "/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so",
            "/usr/lib/opensc-pkcs11.so",
            "/usr/lib/aarch64-linux-gnu/opensc-pkcs11.so"
        ],
        "darwin": [
            "/Library/OpenSC/lib/opensc-pkcs11.so",
            "/Library/OpenSC/lib/opensc-pkcs11.dylib",
            "/usr/local/lib/opensc-pkcs11.so",
            "/opt/homebrew/lib/opensc-pkcs11.dylib"
        ]
    }
}

KNOWN_USB_VENDORS = {
    "072f": "ACS (Advanced Card Systems - ACR38/ACR39)",
    "04e6": "SCM Microsystems / Identiv",
    "0529": "Aladdin / SafeNet (eToken Pro / 5100 / 5110)",
    "096e": "Feitian Technologies (ePass2003 / Rockey)",
    "08e6": "Gemalto / Thales (Gemplus / IDBridge)",
    "2047": "Texas Instruments (MSP430 Token)",
    "076b": "Omnikey (HID Global)"
}

def detect_platform_os():
    """İşletim sistemi türünü normalize eder ('win', 'darwin', 'linux')."""
    if sys.platform.startswith("win"):
        return "win"
    elif sys.platform.startswith("darwin"):
        return "darwin"
    else:
        return "linux"

def get_system_architecture():
    """İşlemci mimarisini tespit eder (Apple Silicon arm64, x86_64 vb.)."""
    machine = platform.machine().lower()
    is_apple_silicon = False
    if sys.platform == "darwin" and ("arm64" in machine or "aarch64" in machine):
        is_apple_silicon = True
    return {
        "machine": machine,
        "processor": platform.processor(),
        "is_apple_silicon": is_apple_silicon,
        "is_64bit": sys.maxsize > 2**32
    }

def check_smartcard_service():
    """Akıllı kart sistem servisinin (SCardSvr / pcscd / CryptoTokenKit) durumunu kontrol eder."""
    os_type = detect_platform_os()
    status = "BILINMIYOR"
    detail = ""

    if os_type == "win":
        try:
            res = subprocess.run(["sc", "query", "SCardSvr"], capture_output=True, text=True, timeout=5)
            if "RUNNING" in res.stdout:
                status = "CALISIYOR"
                detail = "Windows Akıllı Kart Hizmeti (SCardSvr) Aktif"
            elif "STOPPED" in res.stdout:
                status = "DURDURULDU"
                detail = "Windows Akıllı Kart Hizmeti durdurulmuş (net start SCardSvr gerekli)"
            else:
                status = "BULUNAMADI"
                detail = res.stdout.strip()
        except Exception as e:
            status = "HATA"
            detail = str(e)
    elif os_type == "darwin":
        try:
            res = subprocess.run(["pgrep", "-f", "SmartCard"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                status = "CALISIYOR"
                detail = "macOS CryptoTokenKit / SmartCard servisi aktif"
            else:
                status = "HAZIRDA_BEKLIYOR"
                detail = "macOS SmartCard servisi arka planda hazır bekliyor (Tak-Çalıştır)"
        except Exception as e:
            status = "KONTROL_EDILEMEDI"
            detail = str(e)
    else:
        try:
            res = subprocess.run(["systemctl", "is-active", "pcscd"], capture_output=True, text=True, timeout=5)
            if "active" in res.stdout:
                status = "CALISIYOR"
                detail = "Linux pcscd servisi aktif"
            else:
                status = "DURDURULDU"
                detail = "pcscd servisi çalışmıyor (sudo systemctl start pcscd)"
        except Exception as e:
            status = "KONTROL_EDILEMEDI"
            detail = str(e)

    return {"status": status, "detail": detail}

def check_macos_cryptotokenkit():
    """
    macOS Sequoia (15.x) ve Sonoma/Ventura üzerinde Apple CryptoTokenKit (TKSmartCardSlotManager)
    ve 'security smartcards' durumunu denetler.
    """
    if detect_platform_os() != "darwin":
        return {
            "supported": False,
            "message": "CryptoTokenKit yalnızca macOS platformunda desteklenmektedir."
        }

    status_info = {
        "supported": True,
        "ctk_enabled": True,
        "tokens": [],
        "slots": [],
        "details": ""
    }

    try:
        # security smartcards status
        res_status = subprocess.run(["security", "smartcards", "status"], capture_output=True, text=True, timeout=5)
        if res_status.returncode == 0:
            status_info["details"] = res_status.stdout.strip()
            if "disabled" in res_status.stdout.lower():
                status_info["ctk_enabled"] = False
    except Exception:
        pass

    try:
        # security smartcards token -l
        res_tokens = subprocess.run(["security", "smartcards", "token", "-l"], capture_output=True, text=True, timeout=5)
        if res_tokens.returncode == 0:
            lines = res_tokens.stdout.splitlines()
            for line in lines:
                line_clean = line.strip()
                if line_clean and not line_clean.startswith("#"):
                    status_info["tokens"].append(line_clean)
    except Exception:
        pass

    return status_info

def check_installed_pkcs11(os_type=None):
    """Sistemde kurulu PKCS#11 kütüphanelerini denetler."""
    if os_type is None:
        os_type = detect_platform_os()

    found_drivers = []
    missing_drivers = []

    for name, targets in KNOWN_PKCS11_LIBS.items():
        paths = targets.get(os_type, [])
        installed = False
        located_path = None
        for p in paths:
            if Path(p).exists():
                installed = True
                located_path = p
                break
        
        info = {
            "name": name,
            "installed": installed,
            "path": located_path
        }
        if installed:
            found_drivers.append(info)
        else:
            missing_drivers.append(info)

    return {
        "found": found_drivers,
        "missing": missing_drivers
    }

def match_usb_vendor(vendor_id):
    """Hex Vendor ID üzerinden üreticiyi eşleştirir."""
    vid = vendor_id.lower().replace("0x", "").strip()
    return KNOWN_USB_VENDORS.get(vid, "Bilinmeyen Kart Okuyucu Donanımı")

def run_diagnostics():
    """Kapsamlı sistem ve sürücü teşhisini yürütür."""
    os_type = detect_platform_os()
    arch_info = get_system_architecture()
    pkcs11_res = check_installed_pkcs11(os_type)
    svc_status = check_smartcard_service()

    ctk_info = None
    if os_type == "darwin":
        ctk_info = check_macos_cryptotokenkit()

    is_healthy = len(pkcs11_res["found"]) > 0 and svc_status["status"] in ["CALISIYOR", "HAZIRDA_BEKLIYOR"]

    report = {
        "platform": sys.platform,
        "os_category": os_type,
        "architecture": arch_info,
        "smartcard_service": svc_status,
        "cryptotokenkit": ctk_info,
        "drivers_installed": pkcs11_res["found"],
        "drivers_missing": pkcs11_res["missing"],
        "summary": "OK" if is_healthy else "ISSUES_DETECTED"
    }
    return report

def generate_markdown_report(report):
    """Teşhis raporunu Markdown formatında oluşturur."""
    md = "# Akıllı Kart & E-İmza Sürücü Teşhis Raporu v1.3\n\n"
    md += f"- **İşletim Sistemi:** `{report['platform']}` ({report['os_category']})\n"
    
    arch = report.get("architecture", {})
    silicon_tag = " (🍏 Apple Silicon M1-M4)" if arch.get("is_apple_silicon") else ""
    md += f"- **Mimari:** `{arch.get('machine', 'Bilinmiyor')}`{silicon_tag}\n"
    md += f"- **Akıllı Kart Servisi:** `{report['smartcard_service']['status']}` - {report['smartcard_service']['detail']}\n"
    
    if report.get("cryptotokenkit") and report["cryptotokenkit"].get("supported"):
        ctk = report["cryptotokenkit"]
        ctk_status = "✅ Aktif" if ctk.get("ctk_enabled") else "⚠️ Devre Dışı"
        md += f"- **Apple CryptoTokenKit:** {ctk_status}\n"
        if ctk.get("tokens"):
            md += f"- **Tespit Edilen Tokenlar:** `{', '.join(ctk['tokens'])}`\n"

    md += f"- **Genel Durum:** {'✅ Tüm Bileşenler Hazır' if report['summary'] == 'OK' else '⚠️ Eksikler Tespit Edildi'}\n\n"

    md += "## Tespit Edilen PKCS#11 Sürücüleri\n\n"
    if report["drivers_installed"]:
        for d in report["drivers_installed"]:
            md += f"- ✅ **{d['name']}:** `{d['path']}`\n"
    else:
        md += "> ⚠️ Sistemde geçerli bir e-imza PKCS#11 kütüphanesi bulunamadı.\n"

    md += "\n## Kurulu Olmayan Sürücüler\n\n"
    for d in report["drivers_missing"]:
        md += f"- ❌ {d['name']}\n"

    return md

def main():
    import argparse
    parser = argparse.ArgumentParser(description="E-İmza & Akıllı Kart Sürücü Teşhis Aracı v1.3")
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı ver")
    parser.add_argument("--markdown", action="store_true", help="Markdown formatında rapor üret")
    parser.add_argument("--strict", action="store_true", help="Hata veya eksik sürücü tespit edilirse exit code 1 üret")
    args = parser.parse_args()

    report = run_diagnostics()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.markdown:
        print(generate_markdown_report(report))
    else:
        print("=" * 75)
        print("      AKILLI KART & E-İMZA SÜRÜCÜ TEŞHİS RAPORU v1.3")
        print("=" * 75)
        arch = report.get("architecture", {})
        silicon_str = " [Apple Silicon M1-M4]" if arch.get("is_apple_silicon") else ""
        print(f"İşletim Sistemi:     {sys.platform} ({report['os_category']}) {arch.get('machine')}{silicon_str}")
        print(f"Akıllı Kart Servisi: {report['smartcard_service']['status']} ({report['smartcard_service']['detail']})")
        
        if report.get("cryptotokenkit") and report["cryptotokenkit"].get("supported"):
            ctk = report["cryptotokenkit"]
            print(f"CryptoTokenKit:      {'Aktif' if ctk.get('ctk_enabled') else 'Devre Dışı'}")
            if ctk.get("tokens"):
                print(f"Takılı Tokenlar:     {', '.join(ctk['tokens'])}")

        print("\n[+] Tespit Edilen PKCS#11 Sürücüleri:")
        if report["drivers_installed"]:
            for d in report["drivers_installed"]:
                print(f"  ✓ {d['name']}: {d['path']}")
        else:
            print("  ! Kurulu PKCS#11 e-imza kütüphanesi bulunamadı.")

        print("\n[-] Sistemde Bulunamayan Sürücüler:")
        for d in report["drivers_missing"]:
            print(f"  ✗ {d['name']}")

        print("\n" + "=" * 75)

    if args.strict and report["summary"] != "OK":
        sys.exit(1)

if __name__ == "__main__":
    main()
