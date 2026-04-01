import unittest
from src.lib.Puzzle.Criteria.Common import *

class TestCommonCriteria(unittest.TestCase):
    def test_ends_with_letter(self):
        """The entry ends with a specific letter"""
        crit = EndsWithLetter("t")

        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertTrue(crit.is_satisfied_by("rest"))
        self.assertTrue(crit.is_satisfied_by("testt"))
        self.assertFalse(crit.is_satisfied_by("testtr"))

    def test_starts_with_letter(self):
        """The entry begins with a specific letter"""
        crit = StartsWithLetter("t")

        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertTrue(crit.is_satisfied_by("ttest"))
        self.assertTrue(crit.is_satisfied_by("testr"))
        self.assertFalse(crit.is_satisfied_by("rtestt"))

    def test_has_double_letters(self):
        """The entry contains a sequence two or more letters"""
        crit = HasDoubleLetters()

        self.assertTrue(crit.is_satisfied_by("llama"))
        self.assertTrue(crit.is_satisfied_by("rabbit"))
        self.assertTrue(crit.is_satisfied_by("rabbbit"))
        self.assertTrue(crit.is_satisfied_by("hostess"))
        self.assertFalse(crit.is_satisfied_by("unremarkable"))
