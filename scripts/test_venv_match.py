import tempfile
import unittest
from pathlib import Path

from venv_match import find_matches


class VenvMatchTests(unittest.TestCase):
    def test_returns_matches_sorted_shallowest_first(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shallow = root / "alpha"
            deep = root / "team" / "alpha" / "project"
            (shallow / ".git").mkdir(parents=True)
            (deep / ".git").mkdir(parents=True)

            result = find_matches(root, "alpha")

            self.assertEqual(result, [str(shallow), str(deep)])

    def test_returns_empty_list_when_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "alpha" / ".git").mkdir(parents=True)

            result = find_matches(root, "nomatch")

            self.assertEqual(result, [])
