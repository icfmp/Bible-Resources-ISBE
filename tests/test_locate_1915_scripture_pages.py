import unittest
from scripts.locate_1915_scripture_pages import locate

class PrintLocatorTests(unittest.TestCase):
    def test_compound_headword_does_not_require_semicolon_heading(self):
        pages = ["some content", "ROBBER, rob'er. See theft.\nother", "Robber running title"]
        self.assertEqual(locate(pages,"ROBBER; ROBBERY")[0]["page"],2)
    def test_running_header_not_print_certification(self):
        pages = ["THE INTERNATIONAL STANDARD BIBLE ENCYCLOPAEDIA PORCUPINE",
                 "PORCUPINE, por'ku-pin."]
        self.assertEqual(locate(pages,"PORCUPINE")[0]["page"],2)

if __name__=="__main__":
    unittest.main()
