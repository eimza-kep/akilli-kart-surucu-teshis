import unittest
import sys
from diagnose_token import match_usb_vendor, check_installed_pkcs11, run_diagnostics, detect_platform_os

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

    def test_check_installed_pkcs11(self):
        res = check_installed_pkcs11(os_type="linux")
        self.assertIn("found", res)
        self.assertIn("missing", res)
        total = len(res["found"]) + len(res["missing"])
        self.assertGreaterEqual(total, 3)

    def test_run_diagnostics(self):
        report = run_diagnostics()
        self.assertIn("platform", report)
        self.assertIn("summary", report)
        self.assertIn("drivers_installed", report)

if __name__ == "__main__":
    unittest.main()
