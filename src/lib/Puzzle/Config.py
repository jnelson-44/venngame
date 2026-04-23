import src.lib.Puzzle.Criteria.Common as Common
import src.lib.Puzzle.Criteria.Length as Length
from src.lib.Puzzle.Criteria import Not

puzzle_config = {
    "2026-04-22": [
        Common.StartsWith("r"),
        Not(Length.ExactLength(6)).Labeled("Isn't 6 letters"),
        Common.HasDoubleLetters().And(Common.EndsWith("s"))
    ],
    "2026-03-27": [
        Common.EndsWith("r"),
        Length.AtLeastLength(8),
        Common.HasDoubleLetters()
    ],
    "2026-03-23": [
        Common.StartsWith("b"),
        Common.EndsWith("t"),
        Length.ExactLength(7)
    ],
    "2026-03-22": [
        Common.AtLeast(3, "s"),
        Common.EndsWith("ing"),
        Length.ExactLength(5).Or(Length.ExactLength(7)).Labeled("Is exactly 5 or 7 letters")
    ],
    "2026-03-21": [
        Common.Multiplicity(2, "r"),
        Common.StartsWith("sh").Or(Common.StartsWith("st")),
        Length.AtMostLength(6)
    ],
}