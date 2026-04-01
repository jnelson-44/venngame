from src.lib.Puzzle.Criteria import Criterion
from math import inf

class LengthCriterion(Criterion):
    def __init__(self, min_len:float = 0, max_len:float = inf):

        if min_len < 0 or min_len > max_len or max_len == 0:
            raise ValueError(f"Invalid LengthCriterion inputs {min_len} and {max_len}")

        label = f"Between {min_len} and {max_len} letters long"

        if min_len == max_len:
            label = f"Is {min_len} letters"
        elif min_len <= 0:
            label = f"At most {max_len} letters"
        elif max_len == inf:
            label = f"At least {min_len} letters"

        super().__init__(label)

        self.min_len = min_len
        self.max_len = max_len

    def is_satisfied_by(self, solution:str) -> bool:
        return self.min_len <= len(solution) <= self.max_len



class AtLeastLength(LengthCriterion):
    def __init__(self, length:int):
        super().__init__(min_len=length)


class AtMostLength(LengthCriterion):
    def __init__(self, length:int):
        super().__init__(max_len=length)


class ExactLength(LengthCriterion):
    def __init__(self, length:int):
        super().__init__(min_len=length, max_len=length)
