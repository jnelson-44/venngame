import unittest
from src.lib.Puzzle.Criteria.Common import *

class TestCommonCriteria(unittest.TestCase):
    def test_ends_with(self):
        """The entry ends with a specific letter"""
        crit = EndsWith("t")

        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertTrue(crit.is_satisfied_by("rest"))
        self.assertTrue(crit.is_satisfied_by("testt"))
        self.assertFalse(crit.is_satisfied_by("testtr"))

        crit = EndsWith("er")

        self.assertTrue(crit.is_satisfied_by("tester"))
        self.assertTrue(crit.is_satisfied_by("er"))
        self.assertFalse(crit.is_satisfied_by("ertest"))
        self.assertFalse(crit.is_satisfied_by("testre"))

    def test_starts_with(self):
        """The entry begins with a specific letter"""
        crit = StartsWith("t")

        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertTrue(crit.is_satisfied_by("ttest"))
        self.assertTrue(crit.is_satisfied_by("testr"))
        self.assertFalse(crit.is_satisfied_by("rtestt"))

        crit = StartsWith("str")

        self.assertTrue(crit.is_satisfied_by("stress"))
        self.assertTrue(crit.is_satisfied_by("str"))
        self.assertFalse(crit.is_satisfied_by("tstress"))

    def test_has_double_letters(self):
        """The entry contains a sequence two or more letters"""
        crit = HasDoubleLetters()

        self.assertTrue(crit.is_satisfied_by("llama"))
        self.assertTrue(crit.is_satisfied_by("rabbit"))
        self.assertTrue(crit.is_satisfied_by("rabbbit"))
        self.assertTrue(crit.is_satisfied_by("hostess"))
        self.assertFalse(crit.is_satisfied_by("unremarkable"))
