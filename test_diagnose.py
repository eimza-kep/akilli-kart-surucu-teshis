import unittest
import sys
from unittest.mock import patch, MagicMock
from diagnose_token import (
    match_usb_vendor,
    check_installed_pkcs11,
    run_diagnostics,
    detect_platform_os,
    get_system_architecture,
    check_smartcard_service,
    check_macos_cryptotokenkit,
    generate_markdown_report,
    KNOWN_PKCS11_LIBS
)

class TestSmartCardDiagnose(unittest.TestCase):
    def test_match_usb_vendor(self):
        self.assertIn("ACS", match_usb_vendor("072f"))
        self.assertIn("SafeNet", match_usb_vendor("0529"))
        self.assertIn("Omnikey", match_usb_vendor("076b"))
        self.assertIn("Feitian", match_usb_vendor("096e"))
        self.assertEqual("Bilinmeyen Kart Okuyucu Donanımı", match_usb_vendor("ffff"))

    def test_detect_platform_os(self):
        os_type = detect_platform_os()
        self.assertIn(os_type, ["win", "darwin", "linux"])

    def test_get_system_architecture(self):
        arch = get_system_architecture()
        self.assertIn("machine", arch)
        self.assertIn("is_apple_silicon", arch)
        self.assertIn("is_64bit", arch)
        self.assertIsInstance(arch["is_apple_silicon"], bool)

    def test_check_installed_pkcs11_linux(self):
        res = check_installed_pkcs11(os_type="linux")
        self.assertIn("found", res)
        self.assertIn("missing", res)
        total = len(res["found"]) + len(res["missing"])
        self.assertGreaterEqual(total, 4)

    def test_check_installed_pkcs11_darwin(self):
        res = check_installed_pkcs11(os_type="darwin")
        self.assertIn("found", res)
        self.assertIn("missing", res)
        total = len(res["found"]) + len(res["missing"])
        self.assertGreaterEqual(total, 4)

        # Ensure Apple Silicon Homebrew paths exist in definitions
        akis_paths = KNOWN_PKCS11_LIBS["AKİS (TÜBİTAK BİLGEM / Kamu SM)"]["darwin"]
        self.assertTrue(any("/opt/homebrew" in p for p in akis_paths))

    def test_check_smartcard_service(self):
        svc = check_smartcard_service()
        self.assertIn("status", svc)
        self.assertIn("detail", svc)

    def test_check_macos_cryptotokenkit_non_darwin(self):
        if detect_platform_os() != "darwin":
            ctk = check_macos_cryptotokenkit()
            self.assertFalse(ctk["supported"])
            self.assertIn("macOS", ctk["message"])

    @patch("diagnose_token.detect_platform_os", return_value="darwin")
    @patch("subprocess.run")
    def test_check_macos_cryptotokenkit_mock_darwin(self, mock_run, mock_detect):
        # Mock security smartcards status and token -l
        def fake_run(args, **kwargs):
            m = MagicMock()
            m.returncode = 0
            if "status" in args:
                m.stdout = "CryptoTokenKit enabled"
            elif "token" in args:
                m.stdout = "com.apple.ctk.piv\ncom.tubitak.akis.token"
            return m

        mock_run.side_effect = fake_run

        ctk = check_macos_cryptotokenkit()
        self.assertTrue(ctk["supported"])
        self.assertTrue(ctk["ctk_enabled"])
        self.assertEqual(len(ctk["tokens"]), 2)
        self.assertIn("com.tubitak.akis.token", ctk["tokens"])

    def test_run_diagnostics_and_markdown(self):
        report = run_diagnostics()
        self.assertIn("platform", report)
        self.assertIn("summary", report)
        self.assertIn("smartcard_service", report)
        self.assertIn("architecture", report)

        md = generate_markdown_report(report)
        self.assertIn("Sürücü Teşhis Raporu", md)
        self.assertIn(report["platform"], md)

    def test_markdown_with_apple_silicon_ctk(self):
        fake_report = {
            "platform": "darwin",
            "os_category": "darwin",
            "architecture": {
                "machine": "arm64",
                "is_apple_silicon": True
            },
            "smartcard_service": {
                "status": "CALISIYOR",
                "detail": "CryptoTokenKit aktif"
            },
            "cryptotokenkit": {
                "supported": True,
                "ctk_enabled": True,
                "tokens": ["com.apple.piv.token"]
            },
            "drivers_installed": [
                {"name": "AKİS", "path": "/opt/homebrew/lib/libakisp11.dylib"}
            ],
            "drivers_missing": [],
            "summary": "OK"
        }
        md = generate_markdown_report(fake_report)
        self.assertIn("Apple Silicon M1-M4", md)
        self.assertIn("CryptoTokenKit", md)
        self.assertIn("com.apple.piv.token", md)
        self.assertIn("libakisp11.dylib", md)

if __name__ == "__main__":
    unittest.main()
