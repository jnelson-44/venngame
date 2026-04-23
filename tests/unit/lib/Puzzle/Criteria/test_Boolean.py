import unittest
from src.lib.Puzzle.Criteria import *

# Test Criterion that always passes
class AlwaysPasses(Criterion):
    def __init__(self):
        super().__init__("Always true")
    def is_satisfied_by(self, solution:str) -> bool:
        return True

# Test Criterion that always fails
class AlwaysFails(Criterion):
    def __init__(self):
        super().__init__("Always false")
    def is_satisfied_by(self, solution:str) -> bool:
        return False


class TestBooleanCriteria(unittest.TestCase):
    def test_negation_criterion(self):
        self.assertFalse(Not(AlwaysPasses()).is_satisfied_by("test"))
        self.assertTrue(Not(AlwaysFails()).is_satisfied_by("test"))

        crit_default_label = Not(AlwaysPasses())
        self.assertEqual("Not always true", crit_default_label.label)

        crit_custom_label = Not(AlwaysPasses(), "Custom label")
        self.assertEqual("Custom label", crit_custom_label.label)

    def test_intersection_criterion(self):
        self.assertTrue(And(AlwaysPasses(), AlwaysPasses()).is_satisfied_by("test"))
        self.assertFalse(And(AlwaysPasses(), AlwaysFails()).is_satisfied_by("test"))
        self.assertFalse(And(AlwaysFails(), AlwaysPasses()).is_satisfied_by("test"))
        self.assertFalse(And(AlwaysFails(), AlwaysFails()).is_satisfied_by("test"))

        crit_default_label = And(AlwaysPasses(), AlwaysFails())
        self.assertEqual("Always true and always false", crit_default_label.label)

        crit_custom_label = And(AlwaysPasses(), AlwaysFails(), "Custom label")
        self.assertEqual("Custom label", crit_custom_label.label)

    def test_union_criterion(self):
        self.assertTrue(Or(AlwaysPasses(), AlwaysPasses()).is_satisfied_by("test"))
        self.assertTrue(Or(AlwaysPasses(), AlwaysFails()).is_satisfied_by("test"))
        self.assertTrue(Or(AlwaysFails(), AlwaysPasses()).is_satisfied_by("test"))
        self.assertFalse(Or(AlwaysFails(), AlwaysFails()).is_satisfied_by("test"))

        crit_default_label = Or(AlwaysPasses(), AlwaysFails())
        self.assertEqual("Always true or always false", crit_default_label.label)

        crit_custom_label = Or(AlwaysPasses(), AlwaysFails(), "Custom label")
        self.assertEqual("Custom label", crit_custom_label.label)

    def test_fluent_interface(self):
        crit = AlwaysPasses().Or(AlwaysFails())
        self.assertTrue(crit.is_satisfied_by("test"))

        crit = AlwaysFails().Or(AlwaysFails()).Or(AlwaysPasses())
        self.assertTrue(crit.is_satisfied_by("test"))

        crit = AlwaysFails().Or(AlwaysFails().Or(AlwaysPasses()))
        self.assertTrue(crit.is_satisfied_by("test"))

        crit = AlwaysFails().Or(AlwaysFails())
        self.assertFalse(crit.is_satisfied_by("test"))

        crit = AlwaysFails().And(AlwaysPasses())
        self.assertFalse(crit.is_satisfied_by("test"))

        crit = AlwaysPasses().And(Not(AlwaysFails())).Labeled("Test Label")
        self.assertTrue(crit.is_satisfied_by("test"))
        self.assertEqual("Test Label", crit.label)

