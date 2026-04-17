import unittest

from count_words import count_separators


class TestCountSeparators(unittest.TestCase):
    def test_counts_words_in_simple_sentence(self):
        # "one two three" has 2 separators between 3 words
        self.assertEqual(count_separators("one two three"), 2)

    def test_counts_newline_as_separator(self):
        self.assertEqual(count_separators("one\ntwo"), 1)

    def test_multiple_spaces_count_as_one(self):
        self.assertEqual(count_separators("one   two"), 1)

    def test_em_dash_counts_as_separator(self):
        self.assertEqual(count_separators("one—two"), 1)

    def test_en_dash_counts_as_separator(self):
        self.assertEqual(count_separators("one–two"), 1)

    def test_empty_string_returns_zero(self):
        self.assertEqual(count_separators(""), 0)

    def test_single_word_returns_zero(self):
        self.assertEqual(count_separators("word"), 0)

    def test_mixed_separators_each_count_once(self):
        # "a b\nc" — 2 separators
        self.assertEqual(count_separators("a b\nc"), 2)


if __name__ == "__main__":
    unittest.main()
