import unittest
from unittest.mock import patch
from src.lib.Puzzle import *

class TestPuzzle(unittest.TestCase):
    def setUp(self):
        # Set up Config mocking
        self.config_patcher = patch.dict(Config.puzzle_config, clear=True,
            values={
                "2026-04-31": [],
                "2026-05-01": [],
                "2026-03-15": [],
                "2026-02-01": [],
                "2026-05-06": [],
            }
        )
        self.config_patcher.start()

        # Set up Date mocking
        #  NOTE: Mock return values are defined within each individual test case, below
        self.date_patcher = patch("src.lib.Puzzle.date")
        self.mock_date = self.date_patcher.start()

    def tearDown(self):
        self.config_patcher.stop()
        self.date_patcher.stop()


    def test_get_by_id(self):
        """A Puzzle can be directly grabbed by its ID"""
        self.assertEqual(get_by_id("2026-04-31").id, "2026-04-31")
        self.assertEqual(get_by_id("2026-03-15").id, "2026-03-15")
        self.assertEqual(get_by_id("2026-03-20"), None)

    def test_get_current_directly_selects_today(self):
        """Get Current: Ensure that the current day's puzzle is returned directly if it exists"""
        self.mock_date.today.return_value = date(2026, 2, 1)
        self.assertEqual(get_current().id, "2026-02-01")

    def test_get_current_falls_back_to_latest(self):
        """Get Current: Ensure the most-recent, unpassed date is returned, despite unordered config"""
        self.mock_date.today.return_value = date(2026, 3, 17)
        self.assertEqual(get_current().id, "2026-03-15")

    def test_get_current_returns_earliest_if_unconfigured(self):
        """Get Current: Ensure the earliest configured is returned if today is less than such"""
        self.mock_date.today.return_value = date(2023, 2, 1)
        self.assertEqual(get_current().id, "2026-02-01")

