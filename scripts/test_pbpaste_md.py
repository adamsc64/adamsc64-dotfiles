import importlib.util
import pathlib
import unittest

SCRIPT_PATH = pathlib.Path(__file__).with_name("pbpaste-md.py")
SPEC = importlib.util.spec_from_file_location("pbpaste_md", SCRIPT_PATH)
pbpaste_md = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(pbpaste_md)


class TestDecodeClipboardHtml(unittest.TestCase):
    def test_decodes_applescript_hex_payload(self):
        encoded = "«data HTML3c623e48656c6c6f3c2f623e»"
        self.assertEqual(pbpaste_md.decode_clipboard_html(encoded), "<b>Hello</b>")

    def test_rejects_unexpected_payload(self):
        with self.assertRaises(ValueError):
            pbpaste_md.decode_clipboard_html("not-html")


class TestCleanHtml(unittest.TestCase):
    def test_removes_styles_and_head_content(self):
        html = (
            "<html><head><title>Ignored</title></head><body>"
            '<p style="color:red">Hello <span style="font-weight:bold">there</span></p>'
            "</body></html>"
        )
        cleaned = pbpaste_md.clean_html(html)
        self.assertNotIn("style=", cleaned)
        self.assertNotIn("Ignored", cleaned)
        self.assertIn("Hello", cleaned)
        self.assertIn("there", cleaned)

    def test_unwraps_leading_bold_wrapper(self):
        html = "<html><body><b><p>Wrapped</p></b></body></html>"
        self.assertEqual(pbpaste_md.clean_html(html).strip(), "<p>Wrapped</p>")


class TestHtmlToMarkdown(unittest.TestCase):
    def test_converts_clean_html_to_markdown(self):
        markdown = pbpaste_md.html_to_markdown("<p><strong>Hello</strong> world</p>")
        self.assertEqual(markdown.strip(), "**Hello** world")


if __name__ == "__main__":
    unittest.main()
