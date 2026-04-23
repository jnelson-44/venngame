import unittest
from src.lib.Puzzle.Criteria.Common import *

class TestCommonCriteria(unittest.TestCase):
    def test_ends_with(self):
        """The entry ends with a specific letter"""
        crit = EndsWith("t")
        self.assertEqual("Ends with T", crit.label)

        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertTrue(crit.is_satisfied_by("rest"))
        self.assertTrue(crit.is_satisfied_by("testt"))
        self.assertFalse(crit.is_satisfied_by("testtr"))

        crit = EndsWith("er")
        self.assertEqual("Ends with ER", crit.label)

        self.assertTrue(crit.is_satisfied_by("tester"))
        self.assertTrue(crit.is_satisfied_by("er"))
        self.assertFalse(crit.is_satisfied_by("ertest"))
        self.assertFalse(crit.is_satisfied_by("testre"))

    def test_starts_with(self):
        """The entry begins with a specific letter"""
        crit = StartsWith("t")
        self.assertEqual("Begins with T", crit.label)

        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertTrue(crit.is_satisfied_by("ttest"))
        self.assertTrue(crit.is_satisfied_by("testr"))
        self.assertFalse(crit.is_satisfied_by("rtestt"))

        crit = StartsWith("str")
        self.assertEqual("Begins with STR", crit.label)

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

    def test_multiplicity(self):
        """The entry contains N occurrences of a letter"""
        crit = Multiplicity(3, "P")
        self.assertEqual("Has exactly 3 Ps", crit.label)

        self.assertTrue(crit.is_satisfied_by("pppython"))
        self.assertTrue(crit.is_satisfied_by("pytphonp"))
        self.assertFalse(crit.is_satisfied_by("pythonppp"))
        self.assertFalse(crit.is_satisfied_by("pythonp"))

    def test_at_least(self):
        """The entry contains at least N occurrences of a letter"""
        crit = AtLeast(3, "P")
        self.assertEqual("Has at least 3 Ps", crit.label)

        self.assertTrue(crit.is_satisfied_by("pppython"))
        self.assertTrue(crit.is_satisfied_by("pytphonp"))
        self.assertTrue(crit.is_satisfied_by("pythonppp"))
        self.assertFalse(crit.is_satisfied_by("pythonp"))

    def test_at_most(self):
        """The entry contains at most N occurrences of a letter"""
        crit = AtMost(3, "P")
        self.assertEqual("Has at most 3 Ps", crit.label)

        self.assertTrue(crit.is_satisfied_by("pppython"))
        self.assertTrue(crit.is_satisfied_by("pytphonp"))
        self.assertFalse(crit.is_satisfied_by("pythonppp"))
        self.assertTrue(crit.is_satisfied_by("pythonp"))
