import src.lib.Puzzle.Criteria.Common as Common
import src.lib.Puzzle.Criteria.Length as Length

# TODO: Stop instantiating the Criteria here. Instead, define the class and params here, but only instantiate them when loading the puzzle
#   "2026-03-25": [(Common.HasDoubleLetters,None), (Common.EndsWithLetter,{"letter":"r"}), (Length.AtLeastLength,{"length":8})],
puzzle_config = {
    "2026-03-27": [Common.EndsWithLetter("r"), Length.AtLeastLength(8), Common.HasDoubleLetters()],
    "2026-03-23": [Common.StartsWithLetter("b"), Common.EndsWithLetter("t"), Length.ExactLength(7)],
}