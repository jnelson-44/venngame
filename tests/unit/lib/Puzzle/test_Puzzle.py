import unittest
from unittest.mock import patch, AsyncMock

from src.lib.Puzzle.Criteria import Common, Length
from src.lib.Puzzle import *

class TestPuzzle(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Set up generic Puzzle
        self.criteria = [
            Common.EndsWithLetter("r"),
            Length.AtLeastLength(8),
            Common.HasDoubleLetters()
        ]
        self.puzzle = Puzzle("test-puzz", self.criteria)

        # Set up Dictionary mocking
        self.word_exists_patcher = patch(
            "src.lib.Puzzle.Dictionary.word_exists",
            new_callable=AsyncMock
        )
        self.mock_word_exists = self.word_exists_patcher.start()
        # Allow all words for the test cases in this file
        self.mock_word_exists.return_value = True

    def tearDown(self):
        self.word_exists_patcher.stop()

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

    async def test_successful_solve(self):
        """A valid submission is marked as True"""
        result = await self.puzzle.solve_with(["tester", "something", "rabbit", "reservoir", "rebuttal", "butter", "abattoir"])
        self.assertTrue(result)

    async def test_solution_failure_too_few(self):
        """A ValueError is raised if there are too few submissions"""
        with self.assertRaises(ValueError):
            # The configured test puzzle requires 7 regions; providing six
            await self.puzzle.solve_with(["one", "two", "three", "four", "five", "six"])

    async def test_solution_failure_unmapped_region(self):
        """A ValueError is raised if there is any submission of Region 0"""
        with self.assertRaises(ValueError):
            # "test" is the invalid input for this puzzle; place in the middle to triangulate
            await self.puzzle.solve_with(["something", "rabbit", "reservoir", "test", "rebuttal", "butter", "abattoir"])

    async def test_solution_failure_overlapping_regions(self):
        """A ValueError is raised if there are multiple submissions from the same region"""
        with self.assertRaises(ValueError):
            # "rabbit" and "sabbath" overlap regions in an otherwise complete set
            await self.puzzle.solve_with(["tester", "something", "rabbit", "sabbath", "rebuttal", "butter", "abattoir"])

    def test_get_criteria_by_mask(self):
        self.assertEqual([], self.puzzle.get_criteria_by_mask(0))

        b = [self.puzzle.criteria[1]]
        self.assertEqual(b, self.puzzle.get_criteria_by_mask(2))

        ac = [self.puzzle.criteria[0], self.puzzle.criteria[2]]
        self.assertEqual(ac, self.puzzle.get_criteria_by_mask(5))

        abc = [self.puzzle.criteria[0], self.puzzle.criteria[1], self.puzzle.criteria[2]]
        self.assertEqual(abc, self.puzzle.get_criteria_by_mask(7))