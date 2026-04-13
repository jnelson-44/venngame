import unittest
from src.lib.Puzzle.Criteria.Length import *

class TestLengthCriteria(unittest.TestCase):
    def test_at_least(self):
        """The entry is at least N letters long"""
        crit = AtLeastLength(4)

        self.assertEqual("At least 4 letters", crit.label)
        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertTrue(crit.is_satisfied_by("testy"))
        self.assertTrue(crit.is_satisfied_by("testiness"))
        self.assertFalse(crit.is_satisfied_by("tst"))

    def test_at_most(self):
        """The entry is at most N letters long"""
        crit = AtMostLength(4)

        self.assertEqual("At most 4 letters", crit.label)
        self.assertTrue(crit.is_satisfied_by("t"))
        self.assertTrue(crit.is_satisfied_by("te"))
        self.assertTrue(crit.is_satisfied_by("tst"))
        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertFalse(crit.is_satisfied_by("testiness"))

    def test_exactly(self):
        """The entry is exactly N letters long"""
        crit = ExactLength(4)

        self.assertEqual("Is 4 letters", crit.label)
        self.assertTrue(crit.is_satisfied_by("four"))
        self.assertFalse(crit.is_satisfied_by(""))
        self.assertFalse(crit.is_satisfied_by("t"))
        self.assertFalse(crit.is_satisfied_by("te"))
        self.assertFalse(crit.is_satisfied_by("tst"))
        self.assertFalse(crit.is_satisfied_by("testy"))
        self.assertFalse(crit.is_satisfied_by("testiness"))

    def test_range(self):
        """The range is between N and M letters long"""
        crit = LengthCriterion(3,5)

        self.assertEqual("Between 3 and 5 letters long", crit.label)
        self.assertFalse(crit.is_satisfied_by(""))
        self.assertFalse(crit.is_satisfied_by("t"))
        self.assertFalse(crit.is_satisfied_by("tr"))
        self.assertTrue(crit.is_satisfied_by("tru"))
        self.assertTrue(crit.is_satisfied_by("true"))
        self.assertTrue(crit.is_satisfied_by("truef"))
        self.assertFalse(crit.is_satisfied_by("trueph"))

    def test_range_bad(self):
        """Throw a ValueException on bad Range input"""
        with self.assertRaises(ValueError):
            LengthCriterion(5, 3)
        with self.assertRaises(ValueError):
            LengthCriterion(0, 0)
