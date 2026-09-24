#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Akıllı Kart ve E-İmza Donanım / Sürücü Teşhis Aracı
Windows, Linux ve macOS ortamlarında takılı akıllı kart okuyucuları ve PKCS#11 sürücülerini denetler.
"""

import os
import sys
import json
from pathlib import Path

# Force UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

KNOWN_PKCS11_LIBS = {
    "AKİS (TÜBİTAK BİLGEM)": {
        "win": [
            r"C:\Windows\System32\akisp11.dll",
            r"C:\Windows\SysWOW64\akisp11.dll"
        ],
        "linux": [
            "/usr/lib/libakisp11.so",
            "/usr/local/lib/libakisp11.so",
            "/usr/lib/x86_64-linux-gnu/libakisp11.so"
        ],
        "darwin": [
            "/usr/local/lib/libakisp11.dylib",
            "/Library/Frameworks/AkiS.framework/AkiS"
        ]
    },
    "SafeNet / Thales eToken": {
        "win": [
            r"C:\Windows\System32\eTPKCS11.dll",
            r"C:\Windows\SysWOW64\eTPKCS11.dll"
        ],
        "linux": [
            "/usr/lib/libeTPKCS11.so",
            "/usr/local/lib/libeTPKCS11.so"
        ],
        "darwin": [
            "/usr/local/lib/libeTPKCS11.dylib"
        ]
    },
    "OpenSC (Açık Kaynak Kart Desteği)": {
        "win": [
            r"C:\Program Files\OpenSC Project\OpenSC\pkcs11\opensc-pkcs11.dll",
            r"C:\Program Files (x86)\OpenSC Project\OpenSC\pkcs11\opensc-pkcs11.dll"
        ],
        "linux": [
            "/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so",
            "/usr/lib/opensc-pkcs11.so"
        ],
        "darwin": [
            "/Library/OpenSC/lib/opensc-pkcs11.so",
            "/usr/local/lib/opensc-pkcs11.so"
        ]
    }
}

KNOWN_USB_VENDORS = {
    "072f": "ACS (Advanced Card Systems - ACR38/ACR39)",
    "04e6": "SCM Microsystems / Identiv",
    "0529": "Aladdin / SafeNet (eToken Pro / 5100 / 5110)",
    "096e": "Feitian Technologies (ePass2003 / Rockey)",
    "08e6": "Gemalto / Thales",
    "076b": "Omnikey (HID Global)"
}

def detect_platform_os():
    if sys.platform.startswith("win"):
        return "win"
    elif sys.platform.startswith("darwin"):
        return "darwin"
    else:
        return "linux"

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
    os_type = detect_platform_os()
    pkcs11_res = check_installed_pkcs11(os_type)

    report = {
        "platform": sys.platform,
        "os_category": os_type,
        "drivers_installed": pkcs11_res["found"],
        "drivers_missing": pkcs11_res["missing"],
        "summary": "OK" if pkcs11_res["found"] else "NO_DRIVERS_FOUND"
    }
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="E-İmza & Akıllı Kart Sürücü Teşhis Aracı")
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı ver")
    args = parser.parse_args()

    report = run_diagnostics()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("=" * 65)
    print("  AKILLI KART & E-İMZA SÜRÜCÜ TEŞHİS RAPORU")
    print("=" * 65)
    print(f"İşletim Sistemi: {sys.platform} ({report['os_category']})")
    print("\n[+] Tespit Edilen PKCS#11 Sürücüleri:")
    if report["drivers_installed"]:
        for d in report["drivers_installed"]:
            print(f"  ✓ {d['name']}: {d['path']}")
    else:
        print("  ! Kurulu PKCS#11 e-imza kütüphanesi bulunamadı.")

    print("\n[-] Sistemde Bulunamayan Sürücüler:")
    for d in report["drivers_missing"]:
        print(f"  ✗ {d['name']}")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
