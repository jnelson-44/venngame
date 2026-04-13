import unittest

from src.lib.Puzzle.Criteria import Common, Length
from src.lib.Puzzle import *

class TestPuzzle(unittest.TestCase):
    def setUp(self):
        self.criteria = [
            Common.EndsWithLetter("r"),
            Length.AtLeastLength(8),
            Common.HasDoubleLetters()
        ]
        self.puzzle = Puzzle("test-puzz", self.criteria)

    def test_get_name(self):
        """Primitive test case: Get the name of the Puzzle"""
        result = self.puzzle.id
        self.assertEqual("test-puzz", result)

    def test_region_mapping(self):
        """Each Region is correctly mapped"""
        test_cases = [
            {"word": "test",      "expected_region": 0, "expected_criteria_matches": []},
            {"word": "tester",    "expected_region": 1, "expected_criteria_matches": [self.criteria[0]]},
            {"word": "something", "expected_region": 2, "expected_criteria_matches": [self.criteria[1]]},
            {"word": "rabbit",    "expected_region": 4, "expected_criteria_matches": [self.criteria[2]]},
            {"word": "reservoir", "expected_region": 3, "expected_criteria_matches": [self.criteria[0], self.criteria[1]]},
            {"word": "rebuttal",  "expected_region": 6, "expected_criteria_matches": [self.criteria[1], self.criteria[2]]},
            {"word": "butter",    "expected_region": 5, "expected_criteria_matches": [self.criteria[0], self.criteria[2]]},
            {"word": "abattoir",  "expected_region": 7, "expected_criteria_matches": [self.criteria[0], self.criteria[1], self.criteria[2]]},
        ]

        for case in test_cases:
            with self.subTest(msg=f"Region {case["expected_region"]}"):
                res = self.puzzle.get_region_for_word(case["word"])
                self.assertEqual(res[0], case["expected_region"], msg=f"Region ID test failed for Region {case["expected_region"]} using word {case["word"]}")
                self.assertEqual(res[1], case["expected_criteria_matches"], msg=f"Criteria test failed for Region {case["expected_region"]} using word {case["word"]}")

    def test_successful_solve(self):
        """A valid submission is marked as True"""
        result = self.puzzle.solve_with(["tester", "something", "rabbit", "reservoir", "rebuttal", "butter", "abattoir"])
        self.assertTrue(result)

    def test_solution_failure_too_few(self):
        """A ValueError is raised if there are too few submissions"""
        with self.assertRaises(ValueError):
            # The configured test puzzle requires 7 regions; providing six
            self.puzzle.solve_with(["one", "two", "three", "four", "five", "six"])

    def test_solution_failure_unmapped_region(self):
        """A ValueError is raised if there is any submission of Region 0"""
        with self.assertRaises(ValueError):
            # "test" is the invalid input for this puzzle; place in the middle to triangulate
            self.puzzle.solve_with(["something", "rabbit", "reservoir", "test", "rebuttal", "butter", "abattoir"])

    def test_solution_failure_overlapping_regions(self):
        """A ValueError is raised if there are multiple submissions from the same region"""
        with self.assertRaises(ValueError):
            # "rabbit" and "sabbath" overlap regions in an otherwise complete set
            self.puzzle.solve_with(["tester", "something", "rabbit", "sabbath", "rebuttal", "butter", "abattoir"])
