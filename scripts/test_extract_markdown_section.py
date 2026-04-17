import unittest

from count_words import count_separators
from extract_markdown_section import (
    extract_section,
    get_footnotes,
    get_section,
    word_count_from_chapter_one,
)

# Note: count_separators tests live in test_count_words.py

SIMPLE_DOC = """\
# 1\\. Introduction

Some intro text.

# 2\\. Methods

Some methods text.

# 3\\. Results

Some results text.

[^1]: First footnote.
[^2]: Second footnote.
"""

DOC_WITH_FOOTNOTE_REFS = """\
# 1\\. Introduction

Text with a footnote[^1] and another[^2].

# 2\\. Methods

Other text[^2].

[^1]: First footnote.
[^2]: Second footnote.
"""

DOC_WITH_IMAGE = """\
# 1\\. Introduction

Normal line.
<data:image/png;base64,abc123>
Another line.

# 2\\. Methods

Methods text.

[^1]: Footnote one.
"""

SINGLE_SECTION_DOC = """\
# 1\\. Only Section

Only content here.
"""

DOC_WITH_SUBSECTIONS = """\
### 2\\. Animals {#2.-animals}

Intro to animals.

#### 2.1 Mammals {#2.1-mammals}

Mammals are warm-blooded[^1].

#### 2.2 Reptiles {#2.2-reptiles}

Reptiles are cold-blooded[^2].

### 3\\. Plants {#3.-plants}

Plants use photosynthesis.

[^1]: Warm-blooded footnote.
[^2]: Cold-blooded footnote.
"""


class TestGetSection(unittest.TestCase):
    def _lines(self, text):
        return text.splitlines(keepends=True)

    def test_extracts_first_section(self):
        lines = self._lines(SIMPLE_DOC)
        result = get_section(lines, "1")
        result_text = "".join(result)
        self.assertIn("Introduction", result_text)
        self.assertIn("Some intro text.", result_text)
        self.assertNotIn("Methods", result_text)

    def test_extracts_middle_section(self):
        lines = self._lines(SIMPLE_DOC)
        result = get_section(lines, "2")
        result_text = "".join(result)
        self.assertIn("Methods", result_text)
        self.assertIn("Some methods text.", result_text)
        self.assertNotIn("Introduction", result_text)
        self.assertNotIn("Results", result_text)

    def test_extracts_last_section_stops_at_footnotes(self):
        lines = self._lines(SIMPLE_DOC)
        result = get_section(lines, "3")
        result_text = "".join(result)
        self.assertIn("Results", result_text)
        self.assertNotIn("[^1]:", result_text)

    def test_returns_empty_for_missing_section(self):
        lines = self._lines(SIMPLE_DOC)
        result = get_section(lines, "99")
        self.assertEqual(result, [])

    def test_excludes_image_lines(self):
        lines = self._lines(DOC_WITH_IMAGE)
        result = get_section(lines, "1")
        result_text = "".join(result)
        self.assertNotIn("<data:image", result_text)
        self.assertIn("Normal line.", result_text)
        self.assertIn("Another line.", result_text)

    def test_single_section_doc(self):
        lines = self._lines(SINGLE_SECTION_DOC)
        result = get_section(lines, "1")
        result_text = "".join(result)
        self.assertIn("Only content here.", result_text)


class TestGetFootnotes(unittest.TestCase):
    def _lines(self, text):
        return text.splitlines(keepends=True)

    def test_returns_referenced_footnotes_only(self):
        lines = self._lines(DOC_WITH_FOOTNOTE_REFS)
        section = get_section(lines, "1")
        footnotes = get_footnotes(section, lines)
        self.assertEqual(len(footnotes), 2)
        self.assertTrue(any("First footnote." in f for f in footnotes))
        self.assertTrue(any("Second footnote." in f for f in footnotes))

    def test_returns_only_footnotes_used_in_section(self):
        lines = self._lines(DOC_WITH_FOOTNOTE_REFS)
        # Section 2 only references [^2]
        section = get_section(lines, "2")
        footnotes = get_footnotes(section, lines)
        self.assertEqual(len(footnotes), 1)
        self.assertTrue(any("Second footnote." in f for f in footnotes))

    def test_no_footnotes_when_none_referenced(self):
        lines = self._lines(SIMPLE_DOC)
        section = get_section(lines, "1")
        footnotes = get_footnotes(section, lines)
        self.assertEqual(footnotes, [])


class TestExtractSection(unittest.TestCase):
    def test_extract_section_includes_content(self):
        result = extract_section(SIMPLE_DOC, "1")
        self.assertIn("Introduction", result)
        self.assertIn("Some intro text.", result)

    def test_extract_section_includes_footnotes(self):
        result = extract_section(DOC_WITH_FOOTNOTE_REFS, "1")
        self.assertIn("First footnote.", result)
        self.assertIn("Second footnote.", result)

    def test_extract_section_excludes_other_sections(self):
        result = extract_section(SIMPLE_DOC, "2")
        self.assertNotIn("Introduction", result)
        self.assertNotIn("Results", result)

    def test_extract_missing_section_returns_newlines(self):
        result = extract_section(SIMPLE_DOC, "99")
        # Empty section + blank footnotes section = just whitespace/newlines
        self.assertEqual(result.strip(), "")


class TestExtractSubsection(unittest.TestCase):
    def test_extract_subsection_includes_content(self):
        result = extract_section(DOC_WITH_SUBSECTIONS, "2.1")
        self.assertIn("Mammals", result)
        self.assertIn("Mammals are warm-blooded", result)

    def test_extract_subsection_excludes_other_subsections(self):
        result = extract_section(DOC_WITH_SUBSECTIONS, "2.1")
        self.assertIn("Mammals", result)
        self.assertNotIn("Reptiles", result)
        self.assertNotIn("Plants", result)

    def test_extract_subsection_includes_correct_footnote(self):
        result = extract_section(DOC_WITH_SUBSECTIONS, "2.1")
        self.assertIn("Warm-blooded footnote.", result)
        self.assertNotIn("Cold-blooded footnote.", result)

    def test_extract_second_subsection(self):
        result = extract_section(DOC_WITH_SUBSECTIONS, "2.2")
        self.assertIn("Reptiles", result)
        self.assertIn("Cold-blooded footnote.", result)
        self.assertNotIn("Mammals", result)



DOC_WITH_PREAMBLE = """\
**[1\\. Introduction	2](#1.-introduction)**

**[2\\. Methods	5](#2.-methods)**

# 1\\. Introduction

First word second word third word.

# 2\\. Methods

Methods text.

[^1]: A footnote.
"""

DOC_WITHOUT_CHAPTER_ONE = """\
Some preamble text.

More preamble.
"""


class TestWordCountFromChapterOne(unittest.TestCase):
    def test_ignores_preamble_before_chapter_one(self):
        count = word_count_from_chapter_one(DOC_WITH_PREAMBLE)
        preamble_count = count_separators(
            "**[1\\. Introduction	2](#1.-introduction)**\n\n"
            "**[2\\. Methods	5](#2.-methods)**\n\n"
        )
        full_count = count_separators(DOC_WITH_PREAMBLE)
        self.assertLess(count, full_count)
        self.assertEqual(count, full_count - preamble_count)

    def test_returns_zero_when_no_chapter_one(self):
        self.assertEqual(word_count_from_chapter_one(DOC_WITHOUT_CHAPTER_ONE), 0)

    def test_includes_chapter_one_heading_in_count(self):
        # The count starts from (and includes) the chapter 1 heading line
        result = word_count_from_chapter_one(DOC_WITH_PREAMBLE)
        self.assertGreater(result, 0)


if __name__ == "__main__":
    unittest.main()
